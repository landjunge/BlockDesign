"""Headed real Chrome + actual isolated project/import APIs; no Host/model setup.

All stores are temporary. Only own synthetic source is rendered, with JS disabled
and all requests blocked. The product receives a PNG, never executable HTML.
"""

import hashlib
import json
import sys
import threading
import time
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from project_store import ProjectStore
from server import Handler

OUT = (
    ROOT
    / ".runtime/import-20261018"
    / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
)
HTML = """<!doctype html><html lang="en"><meta charset="utf-8"><style>
body{background:#e5edf2;color:#19212b;font:20px system-ui;padding:40px}button{padding:12px 24px;margin:12px;background:#226d78;color:white;border:0}h1{font-size:32px}
</style><h1>Own synthetic reference / Eigene Testreferenz</h1>
<button id="primary-action">Continue / Weiter</button><button id="secondary-action">Continue / Weiter</button>
<p>Two similar buttons, two exact source IDs. No model, login or real project.</p>
<button id="duplicate">Duplicate</button><button id="duplicate">Duplicate</button>
<script>window.top.sourceEscaped=true;fetch('https://reference.invalid/secret')</script>
<img src="https://reference.invalid/tracker"><iframe src="https://reference.invalid/frame"></iframe>
</html>"""


class ProbeHandler(Handler):
    model_calls = 0
    hold_import = None
    import_started = threading.Event()

    def do_POST(self):
        if self.path == "/api/design/import" and type(self).hold_import is not None:
            type(self).import_started.set()
            if not type(self).hold_import.wait(10):
                return self.reply({"error": "synthetic_hold_timeout"}, 408)
        if self.path == "/api/tasks":
            type(self).model_calls += 1
            return self.reply({"error": "model_forbidden_in_probe"}, 403)
        return super().do_POST()

    def log_message(self, *_):
        pass


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    original = OUT / "own-source.html"
    original.write_text(HTML, encoding="utf-8")
    original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    with (
        TemporaryDirectory(prefix="bd-source-probe-") as temporary,
        sync_playwright() as playwright,
    ):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(ProbeHandler, directory=str(ROOT))
        )
        server.projects = ProjectStore(Path(temporary) / "projects")
        server.adapter = SimpleNamespace(
            status=lambda: {"ok": False, "error": "synthetic_offline_no_model"}
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}"
        browser = playwright.chromium.launch(channel="chrome", headless=False)
        errors, unexpected, cases = [], [], []
        try:
            render_context = browser.new_context(
                viewport={"width": 1000, "height": 640},
                java_script_enabled=False,
                service_workers="block",
            )
            render_context.route("**/*", lambda route: route.abort())
            rendered = render_context.new_page()
            rendered.set_content(HTML)
            rendered.screenshot(path=str(OUT / "own-preview.png"))
            render_context.close()
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                reduced_motion="reduce",
                service_workers="block",
            )

            def guard(route):
                if route.request.url.startswith(url + "/"):
                    return route.continue_()
                unexpected.append(route.request.url)
                return route.abort()

            context.route("**/*", guard)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(url)
            page.wait_for_function("() => Boolean(window.blockDesigner)")
            page.locator("#canvas-scroll").focus()
            for _ in range(3):
                page.keyboard.press("b")
            initial = page.evaluate("blockDesigner.getState()")
            ids = [b["id"] for b in initial["boxes"]]
            page.locator("#source-panel summary").click()
            page.locator("#source-png").set_input_files(str(OUT / "own-preview.png"))
            page.locator("#source-html").set_input_files(str(original))
            page.locator("#source-form button").click()
            page.wait_for_function("() => Boolean(blockDesigner.getState().design)")
            assert (
                page.evaluate("blockDesigner.getState().design.source.artifact_sha256")
                == original_hash
            )
            expect(page.locator("#canvas .source-background")).to_be_visible()
            assert (
                page.locator("#canvas .source-background").evaluate(
                    "el=>el.naturalWidth"
                )
                == 1000
            )
            assert page.evaluate("window.sourceEscaped") is None
            page.locator("#selection-panel summary").click()

            def choose(index, operation, element=""):
                target = page.locator('#canvas [data-box-id="' + ids[index] + '"]')
                target.focus()
                target.press("Enter")
                page.locator("#source-operation").select_option(operation)
                page.locator("#source-element").select_option(element)
                page.locator("#source-bind").click()
                page.wait_for_function(
                    "([id,operation])=>blockDesigner.getState().design.bindings[id]?.action===operation",
                    arg=[ids[index], operation],
                )

            choose(0, "move", "id:primary-action")
            choose(1, "replace", "id:secondary-action")
            choose(2, "new")
            assert page.evaluate("blockDesigner.getState().boxes") == initial["boxes"]
            descriptor = page.evaluate(
                "async()=>{const m=await import('/src/core/design.js'); return m.describeDesign(blockDesigner.getState(),'synthetic-project','synthetic-snapshot','Move first, replace second, add third');}"
            )
            assert descriptor["ready"] and not descriptor["execution_started"]
            assert [e["action"] for e in descriptor["descriptor"]["elements"]] == [
                "move",
                "replace",
                "new",
            ]
            for lang in ["de", "en"]:
                page.locator('[data-language="' + lang + '"]').click()
                choose(0, "move", "id:duplicate")
                expect(page.locator("#source-binding-state")).to_contain_text(
                    "Question" if lang == "en" else "Rückfrage"
                )
                page.screenshot(path=str(OUT / f"unknown-{lang}.png"), full_page=True)
                choose(0, "move", "id:primary-action")
                expect(page.locator("#source-binding-state")).to_contain_text(
                    "Exact reference" if lang == "en" else "Genauer Bezug"
                )
                page.screenshot(path=str(OUT / f"mapped-{lang}.png"), full_page=True)
                cases.append(
                    {
                        "lang": lang,
                        "case": "move_replace_new_and_explicit_ambiguous_question",
                        "passed": True,
                    }
                )
            page.locator("#zoom").select_option("1.5")
            project = context.request.get(url + "/api/projects").json()["projects"][0][
                "id"
            ]
            deadline = time.monotonic() + 10
            while (
                context.request.get(url + "/api/projects/" + project).json()["body"][
                    "state"
                ]["ui"]["zoom"]
                != 1.5
            ):
                assert time.monotonic() < deadline
                page.wait_for_timeout(100)
            before = page.evaluate("blockDesigner.getState()")
            page.reload()
            page.wait_for_function("() => Boolean(window.blockDesigner)")
            after = page.evaluate("blockDesigner.getState()")
            assert (
                after["boxes"] == before["boxes"]
                and after["design"] == before["design"]
                and after["ui"]["zoom"] == 1.5
            )
            assert (
                page.locator("#canvas .source-background").evaluate(
                    "el=>el.getBoundingClientRect().width"
                )
                == 1500
            )
            # Stale source does not silently rebind previous design instructions.
            changed = OUT / "changed-source.html"
            changed.write_text(HTML + "\n<!-- new immutable source -->")
            page.locator("#source-panel summary").click()
            page.locator("#source-png").set_input_files(str(OUT / "own-preview.png"))
            page.locator("#source-html").set_input_files(str(changed))
            page.locator("#source-form button").click()
            page.wait_for_function(
                "(old)=>blockDesigner.getState().design.source.artifact_sha256!==old",
                arg=original_hash,
            )
            page.locator("#selection-panel summary").click()
            target = page.locator('#canvas [data-box-id="' + ids[0] + '"]')
            target.focus()
            target.press("Enter")
            expect(page.locator("#source-binding-state")).to_contain_text(
                "Outdated reference"
            )
            check = page.evaluate(
                "async()=>{const m=await import('/src/core/design.js');return m.describeDesign(blockDesigner.getState(),'p','s','Move');}"
            )
            assert not check["ready"] and check["issues"][0]["reason"] == "stale"
            page.set_viewport_size({"width": 1024, "height": 700})
            page.locator("#source-binding-state").scroll_into_view_if_needed()
            page.locator("#source-bind").focus()
            page.screenshot(path=str(OUT / "small-stale-en.png"), full_page=True)
            # Actual HTTP boundaries, never a real external request.
            original_url = url + "/api/design/preview/" + original_hash
            assert context.request.get(original_url).status == 404
            assert (
                context.request.post(
                    url + "/api/design/import",
                    headers={"Origin": "https://reference.invalid"},
                    data={},
                ).status
                == 403
            )
            # Late upload must not attach to another project at the same revision.
            page.locator("#projects-panel button").click()
            page.wait_for_function(
                "() => blockDesigner.getState().revision===0 && blockDesigner.getState().design===null"
            )
            first_empty = context.request.get(url + "/api/projects").json()["projects"][
                0
            ]["id"]
            expect(page.locator("#projects-panel select")).to_have_value(first_empty)
            page.locator("#source-png").set_input_files(str(OUT / "own-preview.png"))
            page.locator("#source-html").set_input_files(str(original))
            ProbeHandler.hold_import = threading.Event()
            ProbeHandler.import_started.clear()
            page.locator("#source-form button").click()
            deadline = time.monotonic() + 3
            while not ProbeHandler.import_started.is_set():
                page.wait_for_timeout(50)
                assert time.monotonic() < deadline
            page.locator("#projects-panel button").click()
            expect(page.locator("#projects-panel select")).not_to_have_value(
                first_empty
            )
            page.locator('[data-language="en"]').click()
            ProbeHandler.hold_import.set()
            ProbeHandler.hold_import = None
            expect(page.locator("#status")).to_contain_text(
                "Document or source changed"
            )
            assert page.evaluate("blockDesigner.getState().design") is None
            assert (
                context.request.get(url + "/api/projects/" + first_empty).json()[
                    "body"
                ]["state"]["design"]
                is None
            )
            cases.append(
                {
                    "case": "late_upload_does_not_cross_equal_revision_projects",
                    "passed": True,
                }
            )
            assert hashlib.sha256(original.read_bytes()).hexdigest() == original_hash
            assert not errors and not unexpected and ProbeHandler.model_calls == 0, (
                errors,
                unexpected,
            )
            report = {
                "at": datetime.now(timezone.utc).isoformat(),
                "source_base": "b875912",
                "kind": "headed_real_chrome_actual_source_and_isolated_real_project_import_api",
                "cases": cases,
                "reload_zoom_stale_refused": True,
                "original_html_sha256": original_hash,
                "preview_sha256": hashlib.sha256(
                    (OUT / "own-preview.png").read_bytes()
                ).hexdigest(),
                "source_files": {
                    path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                    for path in [
                        "src/core/design.js",
                        "src/bridge/projects.js",
                        "src/panels/source.js",
                        "scripts/design_source.py",
                        "scripts/project_store.py",
                        "scripts/server.py",
                    ]
                },
                "model_calls": 0,
                "external_product_requests": unexpected,
                "page_errors": errors,
                "production_runtime_touched": False,
                "limits": [
                    "synthetic own reference only",
                    "PNG/static HTML ID analysis, not runtime DOM/function verification",
                    "no ThreadDesk/KiraBridge handoff or coding task",
                ],
            }
            (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            print(
                "PASS: real headed import, 3 actions, DE/EN questions, reload/zoom/stale and HTTP isolation; no models"
            )
            print("Evidence:", OUT.relative_to(ROOT))
        except Exception as error:
            (OUT / "failure.json").write_text(
                json.dumps(
                    {
                        "at": datetime.now(timezone.utc).isoformat(),
                        "error_type": type(error).__name__,
                        "passed": False,
                        "model_calls": ProbeHandler.model_calls,
                        "page_errors": errors,
                        "external_product_requests": unexpected,
                    },
                    indent=2,
                )
                + "\n"
            )
            raise
        finally:
            browser.close()
            server.shutdown()
            server.server_close()
            thread.join(3)


if __name__ == "__main__":
    run()
