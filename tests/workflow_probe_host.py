"""Isolated browser fixture: real product APIs, MCP Bridge and ThreadDesk; no model.

Started only by workflow_browser.py, never by the product. Uses a deterministic
own CLI fixture in place of Codex and fixed operator project paths.
"""

import asyncio
import base64
import json
import os
import secrets
import socket
import sys
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import design_workflow_test as fixture
from design_workflow import DesignWorkflow, FixedBridgeClient
from kirabridge.bridge_core.bridge import Bridge
from kirabridge.mcp_gateway.http import create_http_app
from project_store import ProjectStore
from server import Handler


async def serve(folder):
    source = folder / "source-project"
    source.mkdir()
    original = (folder / "original.html").read_bytes()
    (source / "own-demo.html").write_bytes(original)
    fixture.png = lambda *_: (folder / "expected.png").read_bytes()
    store = ProjectStore(folder / "projects")
    project = str(uuid4())
    document = json.loads((folder / "document.json").read_text())
    design = store.import_design(
        {
            "preview_base64": base64.b64encode(
                (folder / "original.png").read_bytes()
            ).decode(),
            "html_base64": base64.b64encode(original).decode(),
        }
    )
    box = document["state"]["boxes"][0]
    design["bindings"][box["id"]] = {
        "action": "move",
        "source_element": {
            "artifact_sha256": design["source"]["artifact_sha256"],
            "element_id": "id:action",
            "resolution": "unique",
        },
    }
    document["state"]["design"] = design
    store.save(project, document, {"name": "Own synthetic code/preview test"}, None)
    profile = {
        "cwd": source,
        "source_file": "own-demo.html",
        "preview_file": "returned.png",
    }
    config, counter = fixture.configuration(folder, store, profile)
    # Rendering fixture already contains the code-agent replacement result.
    script = Path(config.agents["codex"].executable)
    script.write_text(
        script.read_text().replace(
            '.replace(b"top:40px",b"top:80px")',
            '.replace(b"top:40px",b"top:80px").replace(b"#228899",b"#2255aa")',
        )
    )
    os.environ["BD_SYNTHETIC_TOKEN"] = secrets.token_urlsafe(40)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(64)
    config.port = sock.getsockname()[1]
    bridge = Bridge(config)
    runtime = uvicorn.Server(
        uvicorn.Config(create_http_app(bridge), log_level="critical", access_log=False)
    )
    async with bridge:
        running = asyncio.create_task(runtime.serve(sockets=[sock]))
        servers = []
        try:
            async with asyncio.timeout(5):
                while not runtime.started:
                    await asyncio.sleep(0.01)
            for controlled in (True, False):
                server = ThreadingHTTPServer(
                    ("127.0.0.1", 0), partial(Handler, directory=str(ROOT))
                )
                server.projects = (
                    store
                    if controlled
                    else ProjectStore(folder / "unconfigured-projects")
                )
                if not controlled:
                    server.projects.import_design(
                        {
                            "preview_base64": base64.b64encode(
                                (folder / "original.png").read_bytes()
                            ).decode(),
                            "html_base64": base64.b64encode(original).decode(),
                        }
                    )
                    server.projects.save(
                        project, document, {"name": "Own unconfigured test"}, None
                    )
                server.adapter = SimpleNamespace(
                    status=lambda: {"ok": False, "error": "no_model_in_probe"}
                )
                server.design_workflow = DesignWorkflow(
                    server.projects,
                    FixedBridgeClient(config, "local") if controlled else None,
                    {project: profile} if controlled else None,
                )
                threading.Thread(target=server.serve_forever, daemon=True).start()
                servers.append(server)
            (folder / "ready.json").write_text(
                json.dumps(
                    {
                        "configured_url": f"http://127.0.0.1:{servers[0].server_port}",
                        "unconfigured_url": f"http://127.0.0.1:{servers[1].server_port}",
                        "project_id": project,
                        "counter": str(counter),
                    }
                )
            )
            async with asyncio.timeout(180):
                while not (folder / "stop").exists():
                    await asyncio.sleep(0.1)
        finally:
            (folder / "bridge-final.json").write_text(
                json.dumps(
                    {
                        "tasks": [
                            dict(row)
                            for row in bridge.store.db.execute(
                                "SELECT id,operation,state,error FROM tasks"
                            )
                        ],
                        "workflows": [
                            {
                                k: v
                                for k, v in json.loads(path.read_text()).items()
                                if k
                                in {
                                    "id",
                                    "state",
                                    "last_error",
                                    "last_exception_type",
                                    "operations",
                                }
                            }
                            for path in store.folder(project).glob(
                                "design-workflows/*.json"
                            )
                        ],
                    },
                    indent=2,
                )
            )
            for server in servers:
                await asyncio.to_thread(server.shutdown)
                server.server_close()
            runtime.should_exit = True
            await asyncio.wait_for(running, 8)
            sock.close()


if __name__ == "__main__":
    asyncio.run(serve(Path(sys.argv[1])))
