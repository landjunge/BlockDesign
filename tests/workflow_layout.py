"""Only the new button-wrap delta: own local store/HTTP + Chrome, no Bridge or TD service."""

import base64
import hashlib
import json
import sys
import threading
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
from design_source_test import png
from design_workflow import DesignWorkflow
from project_store import ProjectStore
from project_store_test import body
from server import Handler


class Quiet(Handler):
    def log_message(self, *_):
        pass


def run():
    out = (
        ROOT
        / ".runtime/workflow-layout-20261018"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid4().hex[:8]
        )
    )
    out.mkdir(parents=True)
    report = {
        "scope": "new CSS wrap only; no Bridge/ThreadDesk service/CLI/model",
        "languages": {},
    }
    with TemporaryDirectory(prefix="bd-layout-") as temp, sync_playwright() as p:
        projects = ProjectStore(Path(temp).resolve() / "projects")
        project, document = str(uuid4()), body()
        document["state"]["design"] = projects.import_design(
            {
                "preview_base64": base64.b64encode(png()).decode(),
                "html_base64": base64.b64encode(
                    b'<button id="own">Own layout only</button>'
                ).decode(),
            }
        )
        projects.save(project, document, {"name": "Own layout check only"}, None)
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(Quiet, directory=str(ROOT))
        )
        server.projects = projects
        server.adapter = SimpleNamespace(
            status=lambda: {"ok": False, "error": "model_not_started"}
        )
        server.design_workflow = DesignWorkflow(projects)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        browser = p.chromium.launch(channel="chrome", headless=False)
        url = f"http://127.0.0.1:{server.server_port}"
        errors = []
        try:
            context = browser.new_context(
                viewport={"width": 1180, "height": 760}, service_workers="block"
            )
            context.route(
                "**/*",
                lambda route: (
                    route.continue_()
                    if route.request.url.startswith(url + "/")
                    else route.abort()
                ),
            )
            page = context.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url)
            page.wait_for_function("() => Boolean(window.blockDesigner)")
            page.locator("#code-panel").evaluate("(el)=>el.open=true")
            for language in ["de", "en"]:
                page.locator(f'[data-language="{language}"]').click()
                page.locator("#code-order").fill("Own synthetic layout; no execution")
                page.locator("#code-prepare").click()
                expect(page.locator("#code-prepare")).to_be_enabled()
                page.locator("#code-issue").scroll_into_view_if_needed()
                rects = page.locator(".code-actions").first.evaluate("""el => {
                  const parent=el.getBoundingClientRect();
                  return [...el.querySelectorAll('button')].map(b=>{
                    const r=b.getBoundingClientRect();return {
                      text:b.textContent,whiteSpace:getComputedStyle(b).whiteSpace,
                      scroll:b.scrollWidth,client:b.clientWidth,height:r.height,
                      within:r.left>=parent.left-1 && r.right<=parent.right+1
                    };
                  });
                }""")
                assert len(rects) == 3
                assert all(
                    r["within"]
                    and r["whiteSpace"] == "normal"
                    and r["scroll"] <= r["client"] + 1
                    and r["height"] >= 40
                    for r in rects
                )
                assert page.locator("#code-start").is_disabled()
                report["languages"][language] = rects
                page.screenshot(path=str(out / f"buttons-{language}-1180.png"))
            assert (
                server.design_workflow.client is None
                and not server.design_workflow.profiles
            )
            records = list(projects.folder(project).glob("design-workflows/*.json"))
            assert records and all(
                not json.loads(path.read_text())["operations"] for path in records
            )
            assert not errors
            report["page_errors"] = errors
            report["css_sha256"] = hashlib.sha256(
                (ROOT / "styles/blockdesigner.css").read_bytes()
            ).hexdigest()
            context.close()
        finally:
            browser.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(out / "report.json")


if __name__ == "__main__":
    run()
