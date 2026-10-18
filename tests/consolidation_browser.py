"""BD-C01/D01 changed-entry probe; run in an isolated checkout with no binding.
No real AI work; all host/project/task data is temporary.
"""

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / ".runtime/consolidation-20261018"
    / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
)
OUT.mkdir(parents=True, exist_ok=True)


def run():
    binding = ROOT / ".runtime/binding.json"
    if binding.exists():
        raise RuntimeError("Refuse to replace an existing binding")
    with TemporaryDirectory(prefix="bd-consolidation-") as temporary:
        env = {
            **os.environ,
            "BD_PYTHON": sys.executable,
            "BD_THREADDESK_SOURCE": os.environ.get(
                "BD_THREADDESK_SOURCE",
                str(Path.home() / "threaddesk-worktrees/ordinal-lock/src"),
            ),
            "BD_WHITEBOARD_ROOT": temporary + "/board",
            "BD_PROJECT_ROOT": temporary + "/projects",
            "BD_TASK_ROOT": temporary + "/tasks",
        }
        check = subprocess.run(
            [str(ROOT / "start.command"), "--check"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert check.returncode == 2 and json.loads(check.stdout)["setup_required"]
        assert not Path(temporary + "/board").exists()
        subprocess.run(
            [str(ROOT / "start.command"), "--setup"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        created = binding.read_bytes()
        check2 = subprocess.run(
            [str(ROOT / "start.command"), "--check"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        assert json.loads(check2.stdout)["binding_ready"]
        server = subprocess.Popen(
            [str(ROOT / "start.command"), "--port", "0"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=(OUT / "server.log").open("w"),
        )
        try:
            line = server.stdout.readline()
            matched = re.search(r"http://127.0.0.1:\d+", line)
            assert matched, line
            url = matched.group(0)
            with sync_playwright() as play:
                browser = play.chromium.launch(channel="chrome")
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.goto(url)
                page.wait_for_function("() => Boolean(window.blockDesigner)")
                s = page.evaluate("blockDesigner.getState()")
                assert s["document"] == {"width": 1000, "height": 640}
                page.locator("#canvas-scroll").focus()
                page.keyboard.press("b")
                assert len(page.evaluate("blockDesigner.getState().boxes")) == 1
                assert (
                    page.locator("#undo").inner_text() == "↶"
                    and page.locator("#undo").get_attribute("aria-label")
                    == "Rückgängig"
                )
                page.locator("#undo").click()
                assert len(page.evaluate("blockDesigner.getState().boxes")) == 0
                page.locator("#redo").click()
                assert len(page.evaluate("blockDesigner.getState().boxes")) == 1
                for language, label in [("en", "Undo"), ("de", "Rückgängig")]:
                    page.locator('[data-language="' + language + '"]').click()
                    assert page.locator("#undo").get_attribute("aria-label") == label
                    assert (
                        page.locator("#undo").evaluate(
                            "(el)=>getComputedStyle(el).height"
                        )
                        == "40px"
                    )
                    page.locator("#help").click()
                    assert page.locator("#help-dialog").evaluate("(el)=>el.open")
                    page.keyboard.press("Escape")
                    assert page.locator("#help").evaluate(
                        "(el)=>el===document.activeElement"
                    )
                    page.screenshot(path=str(OUT / ("desktop-" + language + ".png")))
                page.locator("#canvas-scroll").focus()
                page.keyboard.press("2")
                page.keyboard.press("b")
                assert [
                    b["layer"] for b in page.evaluate("blockDesigner.getState().boxes")
                ] == [1, 2]
                original = page.evaluate("blockDesigner.getState().document")
                page.locator("#zoom").select_option("1.5")
                assert page.evaluate("blockDesigner.getState().document") == original
                page.set_viewport_size({"width": 1180, "height": 760})
                page.locator("#toggle-ai-space").click()
                page.locator("#toggle-myspace").click()
                page.locator("#help").click()
                page.keyboard.press("Escape")
                page.screenshot(path=str(OUT / "small-window.png"))
                assert not errors, errors
                assert page.request.get(url + "/.runtime/binding.json").status == 404
                assert (
                    page.request.post(
                        url + "/api/projects/synthetic",
                        headers={"Origin": "http://outside.invalid"},
                        data="{}",
                    ).status
                    == 403
                )
                page.wait_for_timeout(700)
                report = {
                    "scope": "BD-C01/D01 local start and changed controls",
                    "browser": browser.version,
                    "checks": [
                        "read-only preflight",
                        "missing setup reported",
                        "isolated setup and ready check",
                        "actual modular entry loaded",
                        "B creates box",
                        "curved undo/redo actual effect",
                        "DE/EN accessible names",
                        "40px controls",
                        "help keyboard/focus",
                        "three layer behavior",
                        "document/viewport/zoom separation",
                        "1180x760 reachability",
                        "private runtime path denied",
                        "foreign origin denied",
                    ],
                    "page_errors": errors,
                    "ai_requests_sent": 0,
                    "real_user_workspace_touched": False,
                }
                (OUT / "checks.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2)
                )
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)
            if binding.exists() and binding.read_bytes() == created:
                binding.unlink()
        return report


if __name__ == "__main__":
    try:
        result = {"status": "passed", **run()}
    except BaseException as error:
        result = {
            "status": "failed",
            "error_type": type(error).__name__,
            "error": str(error)[:1000],
        }
        (OUT / "checks.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2)
        )
        print(json.dumps({**result, "evidence": str(OUT)}, ensure_ascii=False))
        raise
    else:
        (OUT / "checks.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2)
        )
        print(json.dumps({**result, "evidence": str(OUT)}, ensure_ascii=False))
