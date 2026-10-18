"""Only operator profile/startup paths; no model, network, database or server."""

import builtins
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import launch
import workflow_profile as profiles


def private(path, text):
    path.write_text(text)
    path.chmod(0o600)
    return path


@pytest.fixture
def own(tmp_path, monkeypatch):
    root = tmp_path.resolve()
    source = root / "source"
    source.mkdir()
    config = private(
        root / "bridge.toml",
        "\n".join(
            [
                f"data_dir = {json.dumps(str(root / 'never-created-state'))}",
                "[principals.operator]",
                'token_env = "BD_PROFILE_TEST_TOKEN"',
                f"roots = [{json.dumps(str(source))}]",
                'capabilities = ["bridge.health", "task.read"]',
            ]
        ),
    )
    project = str(uuid4())
    value = {
        "format": "blockdesigner.workflow-profile.v1",
        "bridge_config": str(config),
        "principal": "operator",
        "projects": {
            project: {
                "cwd": str(source),
                "source_file": "own.html",
                "preview_file": "own.png",
            }
        },
    }
    path = private(root / "workflow.json", json.dumps(value))
    monkeypatch.setenv("BD_PROFILE_TEST_TOKEN", "synthetic-only-" + "b" * 48)
    monkeypatch.delenv("BD_WORKFLOW_PROFILE", raising=False)
    return root, project, path, value


def save(own):
    own[2].write_text(json.dumps(own[3]))
    return str(own[2])


def no_effect(*args, **kwargs):
    raise AssertionError("No network/process/database/startup is allowed in this test")


def test_valid_fixed_local_client_no_network_dispatch_or_state_creation(
    own, monkeypatch
):
    import socket
    import sqlite3
    import subprocess

    # Import SDK dependencies before guarding actual profile/client construction.
    from kirabridge.local_runtime import peer

    assert callable(peer)
    monkeypatch.setattr(socket.socket, "connect", no_effect)
    monkeypatch.setattr(socket.socket, "bind", no_effect)
    monkeypatch.setattr(socket, "create_connection", no_effect)
    monkeypatch.setattr(sqlite3, "connect", no_effect)
    monkeypatch.setattr(subprocess, "Popen", no_effect)
    client, mapping = profiles.load_workflow_profile(save(own))
    assert client.principal == "operator"
    assert client.peer.url == "http://127.0.0.1:8765/mcp"
    assert mapping == own[3]["projects"]
    assert not (own[0] / "never-created-state").exists()
    assert not (own[0] / "source" / "own.html").exists()


def test_no_profile_keeps_unavailable_default_without_import(own, monkeypatch):
    monkeypatch.setattr(profiles, "private_bytes", no_effect)
    assert profiles.load_workflow_profile() is None


def test_explicit_option_overrides_environment_and_server_reuses_fixed_profile(
    own, monkeypatch
):
    monkeypatch.setenv("BD_WORKFLOW_PROFILE", "/missing/foreign-profile.json")
    client, mapping = profiles.load_workflow_profile(save(own))
    assert client.principal == "operator"
    assert own[1] in mapping


@pytest.mark.parametrize("change", ["shared", "symlink", "relative", "oversized"])
def test_unsafe_profile_file_rejected_without_changes(own, monkeypatch, change):
    path = own[2]
    if change == "shared":
        path.chmod(0o640)
    elif change == "symlink":
        path = path.parent / "linked.json"
        path.symlink_to(own[2])
    elif change == "relative":
        monkeypatch.chdir(own[0])
        path = Path("workflow.json")
    else:
        path.write_bytes(b"x" * (profiles.MAX_PROFILE_BYTES + 1))
    before = own[2].read_bytes(), own[2].stat().st_mode
    with pytest.raises(profiles.WorkflowProfileError, match="Private absolute"):
        profiles.load_workflow_profile(str(path))
    assert (own[2].read_bytes(), own[2].stat().st_mode) == before


def test_foreign_owner_rejected(own, monkeypatch):
    original = os.fstat

    def foreign(fd):
        observed = original(fd)
        return SimpleNamespace(st_mode=observed.st_mode, st_uid=os.getuid() + 1)

    monkeypatch.setattr(profiles.os, "fstat", foreign)
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(str(own[2]))
    assert error.value.code == "workflow_profile_file"


@pytest.mark.parametrize(
    "change", ["extra_secret", "duplicate", "too_many", "bad_id", "traversal"]
)
def test_invalid_bounded_schema_and_no_browser_endpoint_or_token(own, change):
    if change == "extra_secret":
        own[3]["token"] = "not-accepted-secret"
    elif change == "too_many":
        base = own[3]["projects"][own[1]]
        own[3]["projects"] = {
            str(uuid4()): base for _ in range(profiles.MAX_PROJECTS + 1)
        }
    elif change == "bad_id":
        own[3]["projects"] = {"not-a-project-uuid": own[3]["projects"][own[1]]}
    elif change == "traversal":
        own[3]["projects"][own[1]]["source_file"] = "../foreign.html"
    save(own)
    if change == "duplicate":
        own[2].write_text('{"format":1,"format":2}')
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(str(own[2]))
    assert error.value.code == "workflow_profile_schema"
    assert "not-accepted-secret" not in str(error.value)


@pytest.mark.parametrize(
    "change", ["unknown_principal", "remote_host", "invalid_config", "shared_config"]
)
def test_bridge_failures_are_safe_and_do_not_expose_validation_secrets(own, change):
    config = Path(own[3]["bridge_config"])
    if change == "unknown_principal":
        own[3]["principal"] = "other"
    elif change == "remote_host":
        config.write_text('host = "foreign.example"\n' + config.read_text())
    elif change == "invalid_config":
        config.write_text('port = "DO_NOT_EXPOSE_SECRET"\n')
    else:
        config.chmod(0o644)
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(save(own))
    assert error.value.code in {"workflow_profile_bridge", "workflow_profile_file"}
    assert "DO_NOT_EXPOSE_SECRET" not in str(error.value)
    assert str(config) not in str(error.value)


@pytest.mark.parametrize("change", ["outside_roots", "missing_cwd", "same_file"])
def test_source_profile_existing_boundary_reused(own, change):
    profile = own[3]["projects"][own[1]]
    if change == "outside_roots":
        profile["cwd"] = str(own[0])
    elif change == "missing_cwd":
        profile["cwd"] = str(own[0] / "missing")
    else:
        profile["preview_file"] = profile["source_file"]
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(save(own))
    assert error.value.code == "workflow_profile_project"


def test_missing_sdk_is_actionable_and_never_installs(own, monkeypatch):
    original = builtins.__import__

    def missing(name, *args, **kwargs):
        if name.startswith("kirabridge"):
            raise ImportError("private diagnostic must not leak")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(save(own))
    assert error.value.code == "workflow_profile_sdk"
    assert "BD_PYTHON" in str(error.value)
    assert "private diagnostic" not in str(error.value)


def test_readonly_check_with_profile_and_missing_host_never_sets_up(
    own, monkeypatch, capsys
):
    monkeypatch.setenv("BD_THREADDESK_SOURCE", str(own[0] / "missing-td"))
    monkeypatch.setenv("BD_WHITEBOARD_ROOT", str(own[0] / "never-created-whiteboard"))
    monkeypatch.setattr(launch, "PROJECT", own[0])
    (own[0] / "package.json").write_text('{"version":"synthetic"}')
    assert launch.main(["--check", "--workflow-profile", save(own)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["workflow_profile"] == {
        "configured": True,
        "project_count": 1,
        "network_checked": False,
        "dispatch_verified": False,
    }
    assert str(own[2]) not in json.dumps(report)
    assert not (own[0] / ".runtime").exists()
    assert not (own[0] / "never-created-whiteboard").exists()
    assert not (own[0] / "never-created-state").exists()


def test_launch_forwards_only_trusted_option_and_never_auto_starts_agent(
    own, monkeypatch
):
    calls = []
    monkeypatch.setattr(
        launch,
        "readiness",
        lambda profile: {
            "prerequisites_ready": True,
            "binding_ready": True,
            "setup_required": False,
        },
    )
    monkeypatch.setitem(sys.modules, "host", SimpleNamespace(setup=no_effect))
    monkeypatch.setitem(
        sys.modules, "server", SimpleNamespace(main=lambda args: calls.append(args))
    )
    monkeypatch.setenv("BD_WORKFLOW_PROFILE", str(own[2]))
    assert launch.main(["--port", "5193"]) == 0
    assert calls == [["--port", "5193", "--workflow-profile", str(own[2])]]


@pytest.mark.parametrize("configured", [False, True])
def test_actual_server_start_parser_wires_client_without_listening(
    own, monkeypatch, configured
):
    import server

    calls = []
    fake = SimpleNamespace(
        server_port=5193, serve_forever=lambda: calls.append("serve")
    )
    monkeypatch.setattr(server, "ThreadingHTTPServer", lambda *args: fake)
    monkeypatch.setattr(
        server,
        "Host",
        lambda: SimpleNamespace(context=lambda *args: None, thread_id="synthetic"),
    )
    monkeypatch.setattr(server, "AIAdapter", lambda host: None)
    monkeypatch.setattr(server, "ProjectStore", lambda root: SimpleNamespace(root=root))
    monkeypatch.setenv("BD_PROJECT_ROOT", str(own[0] / "never-created-project-store"))
    args = ["--port", "5193"]
    if configured:
        args += ["--workflow-profile", save(own)]
    server.main(args)
    assert calls == ["serve"]
    assert (fake.design_workflow.client is not None) is configured
    assert fake.design_workflow.profiles == (own[3]["projects"] if configured else {})
    assert not (own[0] / "never-created-project-store").exists()
    assert not (own[0] / "never-created-state").exists()


def test_invalid_profile_stops_actual_server_before_port_host_or_store(
    own, monkeypatch, capsys
):
    import server

    monkeypatch.setattr(server, "ThreadingHTTPServer", no_effect)
    monkeypatch.setattr(server, "Host", no_effect)
    monkeypatch.setattr(server, "ProjectStore", no_effect)
    own[2].chmod(0o644)
    with pytest.raises(SystemExit) as error:
        server.main(["--workflow-profile", str(own[2])])
    assert error.value.code == 2
    diagnostic = capsys.readouterr().err
    assert "workflow_profile_file" in diagnostic
    assert str(own[2]) not in diagnostic
