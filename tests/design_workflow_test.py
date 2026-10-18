"""Own isolated CAS/ThreadDesk/Bridge with a deterministic non-model CLI fixture."""

import asyncio
import base64
import json
import os
import socket
import sys
from pathlib import Path

import pytest
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from design_source_test import png
from design_workflow import DesignWorkflow, FixedBridgeClient, descriptor
from kirabridge.bridge_core.bridge import INPUTS, Bridge
from kirabridge.bridge_core.config import (
    AgentConfig,
    Config,
    PrincipalConfig,
    ThreadDeskConfig,
)
from kirabridge.mcp_gateway.http import create_http_app
from project_store import ContractError, ProjectStore, encoded
from project_store_test import body

TD_SOURCE = (
    Path(os.environ["BD_TEST_THREADDESK_SOURCE"])
    if os.environ.get("BD_TEST_THREADDESK_SOURCE")
    else None
)
HTML = b'<!doctype html><style>#action{position:absolute;left:20px;top:40px;background:#228899}</style><button id="action">Own synthetic button</button>'
SESSION = "f0100000-0000-4000-8000-000000000003"


def prepared(tmp_path):
    from uuid import uuid4

    projects = ProjectStore(tmp_path / "projects")
    project = str(uuid4())
    document = body()
    document["state"]["design"] = projects.import_design(
        {
            "preview_base64": base64.b64encode(png()).decode(),
            "html_base64": base64.b64encode(HTML).decode(),
        }
    )
    saved = projects.save(project, document, {}, None)
    workflow = DesignWorkflow(projects)
    value = workflow.prepare(
        project, saved["head"], "Move action to x100/y80 and return preview."
    )
    return projects, project, document, saved, workflow, value


def test_exact_descriptor_repeat_source_and_stale_snapshot(tmp_path):
    projects, project, document, saved, workflow, value = prepared(tmp_path)
    assert value["source_commit_verified"] is False
    assert value["state"] == "prepared" and not value["client_available"]
    assert (
        workflow.prepare(
            project, saved["head"], "Move action to x100/y80 and return preview."
        )
        == value
    )
    original = workflow.load(project, value["id"])
    assert projects.raw(value["descriptor_sha256"], 200000) == encoded(
        original["descriptor"]
    )
    document["state"]["revision"] += 1
    projects.save(project, document, {}, saved["head"])
    with pytest.raises(ContractError, match="designStale"):
        workflow.current(original)
    with pytest.raises(ContractError, match="designStale"):
        workflow.prepare(project, saved["head"], "changed")


@pytest.mark.asyncio
async def test_missing_backend_is_explicit_and_does_not_start(tmp_path):
    projects, project, _, _, workflow, value = prepared(tmp_path)
    for action in ["issue", "start", "refresh"]:
        with pytest.raises(ContractError, match="designProfileUnavailable"):
            await workflow.action(project, value["id"], action)
    assert workflow.load(project, value["id"])["operations"] == {}
    assert len(list(projects.folder(project).glob("commits/*.json"))) == 1


def test_unknown_ids_and_unresolved_duplicate_element_never_become_handoff(tmp_path):
    projects, project, document, saved, workflow, value = prepared(tmp_path)
    with pytest.raises(ContractError):
        workflow.load(project, "../" + value["id"])
    from uuid import uuid4

    with pytest.raises(ContractError):
        workflow.load(str(uuid4()), value["id"])
    loaded = projects.read(project)
    # A known old-source reference must not be silently upgraded by a claim.
    loaded["body"]["state"]["boxes"] = [
        {
            "id": "sample",
            "type": "Button",
            "label": "same",
            "color": "#ffffff",
            "radius": 0,
            "font": {},
            "layer": 1,
            "x": 1,
            "y": 1,
            "width": 10,
            "height": 10,
        }
    ]
    loaded["body"]["state"]["design"]["bindings"] = {
        "sample": {
            "action": "move",
            "source_element": {
                "artifact_sha256": "f" * 64,
                "element_id": "id:action",
                "resolution": "unique",
            },
        }
    }
    with pytest.raises(ContractError, match="designUnresolved"):
        descriptor(loaded, "move")


def configuration(tmp_path, projects, profile, question=False):
    if TD_SOURCE is None or not TD_SOURCE.is_dir():
        pytest.skip(
            "BD_TEST_THREADDESK_SOURCE must select the reviewed actual M2/get_return source"
        )
    workspace = tmp_path / "thread-workspace"
    workspace.mkdir(mode=0o700)
    wrapper = tmp_path / "owned-td"
    wrapper.write_text(
        f"#!{sys.executable}\nimport os,sys,json\n"
        f'os.environ["THREADDESK_SOURCE_ROOTS"]={json.dumps([str(projects.root)])!r}\n'
        f"sys.path.insert(0,{str(TD_SOURCE)!r})\n"
        "from threaddesk.ui.mcp_stdio import main\nmain()\n"
    )
    wrapper.chmod(0o700)
    cli, counter = tmp_path / "owned-codex", tmp_path / "calls.jsonl"
    cli.write_text(
        f"#!{sys.executable}\nimport json,sys,pathlib,base64\n"
        "prompt=sys.stdin.read()\n"
        f'with open({str(counter)!r},"a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\n'
        f'print(json.dumps({{"type":"thread.started","thread_id":{SESSION!r}}}),flush=True)\n'
        'print(json.dumps({"type":"turn.started"}),flush=True)\n'
        f'if {question!r} and "resume" not in sys.argv:\n'
        ' reply={"kind":"question","text":"Which colour?","files":[],"test_results":[],"open_issues":[]}\n'
        "else:\n"
        f" source=pathlib.Path({profile['source_file']!r})\n"
        ' source.write_bytes(source.read_bytes().replace(b"left:20px",b"left:100px").replace(b"top:40px",b"top:80px"))\n'
        f" pathlib.Path({profile['preview_file']!r}).write_bytes(base64.b64decode({base64.b64encode(png(24, 24)).decode()!r}))\n"
        f' reply={{"kind":"result","text":"Own HTML changed; PNG fixture unverified", "files":{[profile["source_file"], profile["preview_file"]]!r},"test_results":[],"open_issues":["PNG relationship not automatically verified"]}}\n'
        'print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":json.dumps(reply)}}),flush=True)\n'
        'print(json.dumps({"type":"turn.completed"}),flush=True)\n'
    )
    cli.chmod(0o700)
    policy = PrincipalConfig(
        capabilities=[*INPUTS, "bridge.health", "task.read"],
        roots=[str(tmp_path)],
        agents=["codex"],
        approval_mode="automatic",
        token_env="BD_SYNTHETIC_TOKEN",
    )
    config = Config(
        data_dir=str(tmp_path / "bridge-state"),
        principals={"local": policy},
        agents={
            "codex": AgentConfig(
                kind="codex", executable=str(cli), sandbox_mode="workspace-write"
            )
        },
        threaddesk=ThreadDeskConfig(
            enabled=True,
            command=str(wrapper),
            args=[],
            workspace=str(workspace),
            source_root=str(TD_SOURCE),
        ),
    )
    return config, counter


@pytest.mark.asyncio
@pytest.mark.parametrize("question", [False, True])
async def test_real_mcp_td_issued_bound_demo_return_reconnect_and_no_duplicate(
    tmp_path, monkeypatch, question
):
    projects, project, document, saved, _, value = prepared(tmp_path)
    source = tmp_path / "source-project"
    source.mkdir()
    (source / "own-demo.html").write_bytes(HTML)
    profile = {
        "cwd": source,
        "source_file": "own-demo.html",
        "preview_file": "returned.png",
    }
    config, counter = configuration(tmp_path, projects, profile, question=question)
    monkeypatch.setenv("BD_SYNTHETIC_TOKEN", "synthetic-only-" + "b" * 48)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(64)
    config.port = sock.getsockname()[1]
    bridge = Bridge(config)
    server = uvicorn.Server(
        uvicorn.Config(create_http_app(bridge), log_level="critical", access_log=False)
    )
    async with bridge:
        task = asyncio.create_task(server.serve(sockets=[sock]))
        try:
            async with asyncio.timeout(5):
                while not server.started:
                    await asyncio.sleep(0.01)
            workflow = DesignWorkflow(
                projects, FixedBridgeClient(config, "local"), {project: profile}
            )
            issued = await workflow.action(project, value["id"], "issue")
            assert issued["state"] == "issued_no_execution"
            assert not counter.exists()
            record = workflow.load(project, value["id"])
            assert all(
                r["verification"] == "verified"
                for r in record["issued"]["source"]["source_refs"]
            )
            assert record["issued"]["handoff"]["task_id"].endswith(":task")
            actual = workflow.client

            class LostReply:
                principal = actual.principal
                submits = 0

                async def task(self, identity):
                    return await actual.task(identity)

                async def submit(self, packet):
                    result = await actual.submit(packet)
                    if packet["operation"] == "handoff.start":
                        self.submits += 1
                        raise ContractError("designBridgeUnknown")
                    return result

            lost = LostReply()
            workflow.client = lost
            with pytest.raises(ContractError, match="designBridgeUnknown"):
                await workflow.action(project, value["id"], "start")
            uncertain = workflow.load(project, value["id"])
            assert uncertain["state"] == "unknown" and uncertain["bridge_task_id"]
            await bridge.tasks.wait("local", uncertain["bridge_task_id"])
            # Explicit re-query reads the same pre-persisted task, never resubmits.
            await workflow.action(project, value["id"], "start")
            assert lost.submits == 1
            workflow.client = actual
            if question:
                waiting = await workflow.action(project, value["id"], "refresh")
                assert waiting["state"] == "awaiting_answer"
                assert waiting["question"] == "Which colour?"
                assert (source / "own-demo.html").read_bytes() == HTML
                answering = await workflow.action(
                    project, value["id"], "answer", {"text": "blue"}
                )
                await bridge.tasks.wait("local", answering["active_task_id"])
            returned = await workflow.action(project, value["id"], "refresh")
            assert (
                returned["state"] == "delivered_unverified"
                and returned["reply_verification"] == "unverified"
            )
            assert returned["run_id"] and returned["session_id"] == SESSION
            assert b"left:100px;top:80px" in (source / "own-demo.html").read_bytes()
            assert projects.read(project)["head"] == saved["head"]
            if not question:

                class ForeignReturn:
                    principal = actual.principal

                    async def submit(self, packet):
                        return await actual.submit(packet)

                    async def task(self, identity):
                        received = await actual.task(identity)
                        if (
                            received["operation"] == "handoff.inbox"
                            and received["state"] == "completed"
                        ):
                            received["result"]["value"]["items"][0]["return"][
                                "run_id"
                            ] = "foreign-run"
                        return received

                workflow.client = ForeignReturn()
                with pytest.raises(ContractError, match="taskConflict"):
                    await workflow.action(project, value["id"], "refresh")
                assert projects.read(project)["head"] == saved["head"]
                assert (
                    workflow.load(project, value["id"])["returned"]
                    == returned["returned"]
                )
                workflow.client = actual
            # New host/client object reconnects; repeat start reads the stored Bridge task.
            reopened = DesignWorkflow(
                ProjectStore(projects.root),
                FixedBridgeClient(config, "local"),
                {project: profile},
            )
            await reopened.action(project, value["id"], "start")
            again = await reopened.action(project, value["id"], "refresh")
            assert again["return_id"] == returned["return_id"]
            expected_turns = 2 if question else 1
            assert len(counter.read_text().splitlines()) == expected_turns
            if question:
                assert SESSION in json.loads(counter.read_text().splitlines()[1])
            accepted = await reopened.action(
                project,
                value["id"],
                "decision",
                {
                    "choice": "accepted",
                    "note": "Synthetic protocol check only; PNG unverified.",
                },
            )
            assert (
                accepted["state"] == "accepted"
                and not accepted["project_completion_verified"]
            )
            assert projects.read(project)["head"] == saved["head"]
            with pytest.raises(ContractError, match="taskConflict"):
                await reopened.action(
                    project,
                    value["id"],
                    "decision",
                    {"choice": "rejected", "note": "Different duplicate decision."},
                )
            assert reopened.load(project, value["id"])["decision"] == "accepted"
            # Conflicting subsequent bytes and foreign/stale state cannot change design/decision.
            (source / "own-demo.html").write_text("foreign later code")
            with pytest.raises(ContractError, match="taskConflict"):
                await reopened.action(project, value["id"], "refresh")
            document["state"]["revision"] += 1
            projects.save(project, document, {}, saved["head"])
            with pytest.raises(ContractError, match="designStale"):
                await reopened.action(project, value["id"], "start")
            assert len(counter.read_text().splitlines()) == expected_turns
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, 8)
            sock.close()
