"""Actual own HTML render + isolated product/MCP/ThreadDesk browser acceptance.

No user profile, real model, provider or product runtime. Requires existing local
Playwright/Chrome, Bridge Python and reviewed source paths explicitly in env.
"""

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / ".runtime/workflow-20261018"
    / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
)
HTML = '<!doctype html><style>body{background:#edf3f7}#action{position:absolute;left:20px;top:40px;width:160px;height:40px;border:0;border-radius:6px;color:white;background:#228899;font:16px system-ui}</style><button id="action">Own synthetic button</button>'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run():
    OUT.mkdir(parents=True)
    bridge_python = os.environ["BD_TEST_BRIDGE_PYTHON"]
    assert Path(bridge_python).is_file()
    report = {
        "kind": "own synthetic source/MCP fixture, not live/model acceptance",
        "source": {},
        "cases": [],
        "errors": [],
        "unexpected_requests": [],
    }
    with TemporaryDirectory(prefix="bd-code-probe-") as temp, sync_playwright() as p:
        # macOS /var is a symlink; the actual descriptor boundary deliberately
        # requires a canonical no-symlink operator path, just like pytest tmp_path.
        folder = Path(temp).resolve()
        browser = p.chromium.launch(channel="chrome", headless=False)
        server = None
        try:
            rendered = browser.new_context(
                viewport={"width": 1000, "height": 640},
                java_script_enabled=False,
                service_workers="block",
            )
            rendered.route("**/*", lambda route: route.abort())
            page = rendered.new_page()
            page.set_content(HTML)
            assert page.locator("#action").bounding_box()["x"] == 20
            page.screenshot(path=str(folder / "original.png"))
            changed = (
                HTML.replace("left:20px", "left:100px")
                .replace("top:40px", "top:80px")
                .replace("#228899", "#2255aa")
            )
            page.set_content(changed)
            assert page.locator("#action").bounding_box()["x"] == 100
            assert page.locator("#action").bounding_box()["y"] == 80
            page.screenshot(path=str(folder / "expected.png"))
            (folder / "original.html").write_text(HTML)
            # Obtain an actual box through the existing reducer, not a second model.
            js = """import {createStore} from './src/core/store.js';
const s=createStore();s.dispatch({type:'create'});const id=s.getState().boxes[0].id;
s.dispatch({type:'patch',id,changes:{type:'Button',label:'Own synthetic button',x:100,y:80,width:160,height:40,radius:6,color:'#2255aa',font:{size:16,color:'#ffffff'}}});
const st=s.getState();console.log(JSON.stringify({format:1,state:{...st,ui:{language:'de',view:'design',zoom:.75}},history:{undo:[],redo:[]}}));"""
            data = subprocess.run(
                ["node", "--input-type=module", "-e", js],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            (folder / "document.json").write_text(data.stdout)
            env = {
                **os.environ,
                "BD_THREADDESK_SOURCE": os.environ["BD_TEST_THREADDESK_SOURCE"],
            }
            with (OUT / "fixture-host.log").open("w") as log:
                server = subprocess.Popen(
                    [
                        bridge_python,
                        str(ROOT / "tests/workflow_probe_host.py"),
                        str(folder),
                    ],
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=log,
                )
                deadline = time.monotonic() + 15
                while not (folder / "ready.json").exists():
                    assert time.monotonic() < deadline and server.poll() is None
                    time.sleep(0.05)
                ready = json.loads((folder / "ready.json").read_text())
                context = browser.new_context(
                    viewport={"width": 1180, "height": 760},
                    service_workers="block",
                    reduced_motion="reduce",
                )
                own = [ready["configured_url"], ready["unconfigured_url"]]

                def guard(route):
                    if any(route.request.url.startswith(url + "/") for url in own):
                        return route.continue_()
                    report["unexpected_requests"].append(route.request.url)
                    route.abort()

                context.route("**/*", guard)
                ui = context.new_page()
                ui.on("pageerror", lambda e: report["errors"].append(str(e)))
                ui.goto(ready["configured_url"])
                ui.wait_for_function("() => Boolean(window.blockDesigner)")
                initial = ui.evaluate("blockDesigner.getState()")
                ui.locator("#code-panel").evaluate("(el)=>el.open=true")
                ui.locator("#code-order").fill(
                    "Move the exact action button to x100/y80 and make its background #2255aa. Return source and PNG."
                )
                ui.locator("#code-prepare").click()
                expect(ui.locator("#code-issue")).to_be_enabled()
                assert not Path(ready["counter"]).exists()
                ui.screenshot(path=str(OUT / "prepared-de-1180.png"))
                ui.locator("#code-issue").click()
                expect(ui.locator("#code-start")).to_be_enabled(timeout=15000)
                assert not Path(ready["counter"]).exists()
                ui.locator("#code-start").click()
                expect(ui.locator("#code-refresh")).to_be_enabled()
                for _ in range(8):
                    ui.locator("#code-refresh").click()
                    expect(ui.locator("#code-refresh")).to_be_enabled()
                    if ui.locator("#code-result").is_visible():
                        break
                    ui.wait_for_timeout(100)
                expect(ui.locator("#code-result")).to_be_visible()
                expect(ui.locator("#code-preview")).to_be_visible()
                ui.wait_for_function(
                    'document.querySelector("#code-preview").naturalWidth===1000'
                )
                assert len(Path(ready["counter"]).read_text().splitlines()) == 1
                assert (
                    ui.evaluate("blockDesigner.getState().revision")
                    == initial["revision"]
                )
                actual_source = (folder / "source-project/own-demo.html").read_bytes()
                assert actual_source == changed.encode()
                # Independently render actual changed source, not the promised future file.
                page.set_content(actual_source.decode())
                box = page.locator("#action").bounding_box()
                assert box["x"] == 100 and box["y"] == 80
                actual_png = page.screenshot(path=str(OUT / "actual-return-render.png"))
                delivered_png = (folder / "source-project/returned.png").read_bytes()
                assert digest(actual_png) == digest(delivered_png)
                response = ui.request.get(
                    ready["configured_url"]
                    + ui.locator("#code-preview").get_attribute("src")
                )
                assert response.ok and digest(response.body()) == digest(actual_png)
                ui.screenshot(path=str(OUT / "returned-de-1180.png"))
                ui.reload()
                ui.wait_for_function("() => Boolean(window.blockDesigner)")
                ui.locator("#code-panel").evaluate("(el)=>el.open=true")
                expect(ui.locator("#code-result")).to_be_visible()
                assert len(Path(ready["counter"]).read_text().splitlines()) == 1
                ui.locator("#code-note").fill(
                    "Own synthetic source and rendered PNG checked; no general project acceptance."
                )
                ui.locator("#code-accept").click()
                expect(ui.locator("#code-status")).to_contain_text(
                    "Betreiberentscheidung"
                )
                ui.locator('[data-language="en"]').click()
                expect(ui.locator("#code-status")).to_contain_text("changed")
                expect(ui.locator("#code-accept")).to_be_disabled()
                ui.screenshot(path=str(OUT / "historical-en-1180.png"))
                report["cases"].extend(
                    [
                        "exact_saved_source_and_selection",
                        "prepare_issue_no_execution",
                        "explicit_start_real_mcp_td_owned_fixture",
                        "actual_html_position_colour_changed",
                        "independent_render_png_hash_equal",
                        "return_unverified_no_design_mutation",
                        "reload_no_restart",
                        "explicit_separate_decision",
                        "language_saved_head_stale_blocks",
                    ]
                )
                # Unconfigured product path honestly denies execution, independent data root.
                ui.goto(ready["unconfigured_url"])
                ui.wait_for_function("() => Boolean(window.blockDesigner)")
                ui.locator('[data-language="en"]').click()
                ui.locator("#code-panel").evaluate("(el)=>el.open=true")
                ui.locator("#code-order").fill("Own unconfigured code request")
                ui.locator("#code-prepare").click()
                expect(ui.locator("#code-status")).to_contain_text(
                    "Backend project profile"
                )
                expect(ui.locator("#code-start")).to_be_disabled()
                expect(ui.locator("#code-issue")).to_be_disabled()
                ui.screenshot(path=str(OUT / "unconfigured-en-1180.png"))
                width = ui.evaluate(
                    "({scroll:document.documentElement.scrollWidth,width:innerWidth})"
                )
                assert width["scroll"] <= width["width"]
                report["cases"].append("default_profile_unavailable_no_execution_en")
                report["source"] = {
                    "original_html_sha256": digest(HTML.encode()),
                    "actual_html_sha256": digest(actual_source),
                    "actual_png_sha256": digest(actual_png),
                    "delivered_png_sha256": digest(delivered_png),
                    "button": box,
                    "agent_fixture_calls": len(
                        Path(ready["counter"]).read_text().splitlines()
                    ),
                }
                assert not report["errors"] and not report["unexpected_requests"]
                context.close()
        finally:
            if server:
                (folder / "stop").touch()
                try:
                    server.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    server.terminate()
                    server.wait(timeout=5)
                if (folder / "bridge-final.json").exists():
                    (OUT / "bridge-final.json").write_bytes(
                        (folder / "bridge-final.json").read_bytes()
                    )
            browser.close()
        report["files"] = {
            str(p.relative_to(ROOT)): digest(p.read_bytes())
            for p in [
                ROOT / "scripts/design_workflow.py",
                ROOT / "scripts/server.py",
                ROOT / "src/bridge/design-workflow.js",
                ROOT / "src/app.js",
                ROOT / "src/i18n.js",
                ROOT / "styles/blockdesigner.css",
                ROOT / "index.html",
            ]
        }
        (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(OUT / "report.json")


if __name__ == "__main__":
    run()
