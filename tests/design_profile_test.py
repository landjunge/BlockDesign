"""PR3 profile-drift regression cases; pure own fixtures, no services or models."""

from copy import deepcopy
from types import SimpleNamespace

import pytest
from design_workflow import DesignWorkflow, FixedBridgeClient
from design_workflow_counter_test import fixed_identity
from design_workflow_test import prepared
from project_store import ContractError, ProjectStore, encoded


class MemoryClient:
    principal = "local"

    def __init__(self):
        self.identity = fixed_identity()
        self.calls = []
        self.responses = {}

    def profile_identity(self):
        return {**self.identity, "principal": self.principal}

    async def submit(self, packet):
        self.calls.append(("submit", packet["task_id"]))
        task = {
            "id": packet["task_id"],
            "operation": packet["operation"],
            "args": deepcopy(packet["arguments"]),
            "principal": self.principal,
            "state": "completed",
            "result": {"success": True, "value": {"synthetic": True}},
        }
        self.responses[task["id"]] = task
        return deepcopy(task)

    async def task(self, identity):
        self.calls.append(("read", identity))
        return deepcopy(self.responses[identity])


def pinned(tmp_path):
    projects, project, _, saved, workflow, public = prepared(tmp_path)
    cwd = tmp_path / "source-one"
    cwd.mkdir()
    workflow.client = MemoryClient()
    workflow.profiles = {
        project: {"cwd": cwd, "source_file": "own.html", "preview_file": "own.png"}
    }
    value = workflow.load(project, public["id"])
    workflow.check_operator_profile(value, bind=True)
    return projects, project, saved, workflow, value


@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["refresh", "decision", "issue", "start", "answer"])
@pytest.mark.parametrize(
    "change",
    [
        "cwd",
        "source_file",
        "preview_file",
        "principal",
        "endpoint_ref",
        "config_ref",
        "state_root_ref",
    ],
)
async def test_profile_drift_before_first_return_never_calls_backend(
    tmp_path, action, change
):
    projects, project, saved, workflow, value = pinned(tmp_path)
    # Persisted original identity has an unresolved start but no adopted return.
    value["operations"]["start"] = {"task_id": "old-unknown"}
    workflow.save(value)
    profile = workflow.profiles[project]
    if change == "cwd":
        other = tmp_path / "source-two"
        other.mkdir()
        profile["cwd"] = other
    elif change in {"source_file", "preview_file"}:
        profile[change] = "changed-" + profile[change]
    elif change == "principal":
        workflow.client.principal = "different-principal"
    else:
        workflow.client.identity[change] = "f" * 64
    with pytest.raises(ContractError, match="designProfileChanged"):
        await workflow.action(project, value["id"], action)
    assert workflow.client.calls == []
    reloaded = workflow.load(project, value["id"])
    assert (
        "returned" not in reloaded
        and reloaded["operator_profile"] == value["operator_profile"]
    )
    assert projects.read(project)["head"] == saved["head"]
    public = workflow.public(reloaded)
    assert public["profile_drift"] and not public["client_available"]
    assert "operator_profile" not in public


@pytest.mark.asyncio
async def test_unchanged_profile_survives_reload_and_reuses_exact_operation(tmp_path):
    projects, project, _, workflow, value = pinned(tmp_path)
    pin = deepcopy(value["operator_profile"])
    first = await workflow.operation(
        value, "probe", "handoff.status", {"handoff_id": "synthetic"}
    )
    reloaded = DesignWorkflow(
        ProjectStore(projects.root), workflow.client, workflow.profiles
    )
    restored = reloaded.load(project, value["id"])
    assert reloaded.check_operator_profile(restored) == pin
    second = await reloaded.operation(
        restored, "probe", "handoff.status", {"handoff_id": "synthetic"}
    )
    assert first == second == {"synthetic": True}
    assert [kind for kind, _ in workflow.client.calls] == ["submit", "read"]
    assert not reloaded.public(restored)["profile_drift"]


@pytest.mark.parametrize("configuration", ["removed", "remapped"])
def test_original_unresolved_source_blocks_after_profile_removal_or_remap(
    tmp_path, configuration
):
    projects, first, _, workflow, previous = pinned(tmp_path)
    _, second, _, _, _, public = prepared(tmp_path)
    original = deepcopy(workflow.profiles[first])
    workflow.profiles[second] = original
    current = workflow.load(second, public["id"])
    workflow.check_operator_profile(current, bind=True)
    previous["operations"]["start"] = {"task_id": "previous-unknown"}
    previous["state"] = "unknown"
    workflow.save(previous)
    if configuration == "removed":
        del workflow.profiles[first]
    else:
        unrelated = tmp_path / "unrelated"
        unrelated.mkdir()
        workflow.profiles[first] = {**original, "cwd": unrelated}
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, original)
    previous["decision"] = "rejected"
    workflow.save(previous)
    workflow.guard_start(current, original)


def test_legacy_unknown_source_is_never_guessed_from_new_configuration(tmp_path):
    _, project, _, workflow, previous = pinned(tmp_path)
    previous.pop("operator_profile")
    previous.pop("operator_profile_sha256")
    previous["operations"]["start"] = {"task_id": "legacy-unknown"}
    workflow.save(previous)
    with pytest.raises(ContractError, match="designProfileChanged"):
        workflow.check_operator_profile(previous, bind=True)
    _, other, _, _, _, public = prepared(tmp_path)
    workflow.profiles[other] = deepcopy(workflow.profiles[project])
    current = workflow.load(other, public["id"])
    workflow.check_operator_profile(current, bind=True)
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, workflow.profiles[other])


@pytest.mark.parametrize("evidence", ["issued", "bridge_task_id", "return_id"])
def test_legacy_receipt_without_operation_map_is_not_backfilled(tmp_path, evidence):
    _, _, _, workflow, value = pinned(tmp_path)
    value.pop("operator_profile")
    value.pop("operator_profile_sha256")
    value[evidence] = "historical-unpinned-claim"
    with pytest.raises(ContractError, match="designProfileChanged"):
        workflow.check_operator_profile(value, bind=True)


@pytest.mark.asyncio
async def test_profile_changes_while_receipt_is_pending_are_rejected(tmp_path):
    _, project, _, workflow, value = pinned(tmp_path)
    original = workflow.client.submit

    async def change_on_return(packet):
        result = await original(packet)
        workflow.profiles[project]["preview_file"] = "different.png"
        return result

    workflow.client.submit = change_on_return
    with pytest.raises(ContractError, match="designProfileChanged"):
        await workflow.operation(
            value, "start", "handoff.start", {"handoff_id": "synthetic"}, wait=False
        )
    assert len(workflow.client.calls) == 1 and "returned" not in value


def test_fixed_client_identity_excludes_token_and_is_explicitly_configured_only():
    client = FixedBridgeClient.__new__(FixedBridgeClient)
    client.peer = SimpleNamespace(
        id="daemon", url="http://127.0.0.1:8765/mcp", token="DO_NOT_EXPORT"
    )
    client.principal, client.config_ref, client.state_root_ref = "local", None, "b" * 64
    identity = client.profile_identity()
    assert "DO_NOT_EXPORT" not in encoded(identity).decode()
    assert identity["identity_scope"] == "configured_local_peer_not_remote_attestation"


def test_persisted_binding_scan_budget_fails_closed(tmp_path, monkeypatch):
    _, _, _, workflow, value = pinned(tmp_path)
    moments = iter([0, 3])
    monkeypatch.setattr(
        "design_workflow.time", SimpleNamespace(monotonic=lambda: next(moments))
    )
    with pytest.raises(ContractError, match="designWorkflowLimit"):
        workflow.guard_start(value, workflow.profiles[value["project_id"]])
