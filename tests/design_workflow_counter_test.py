"""Small new rejection paths, no model/network/runtime startup."""

import pytest
from design_workflow_test import prepared
from project_store import ContractError


@pytest.mark.asyncio
@pytest.mark.parametrize("mismatch", ["principal", "args", "id"])
async def test_foreign_task_receipt_is_not_accepted(tmp_path, mismatch):
    _, project, _, _, workflow, public = prepared(tmp_path)
    record = workflow.load(project, public["id"])

    class Client:
        principal = "local"

        async def submit(self, packet):
            task = {
                "id": packet["task_id"],
                "operation": packet["operation"],
                "args": packet["arguments"],
                "principal": self.principal,
                "state": "queued",
            }
            task[mismatch] = {"path": "/foreign"} if mismatch == "args" else "foreign"
            return task

    workflow.client = Client()
    with pytest.raises(ContractError, match="taskConflict"):
        await workflow.operation(
            record, "start", "handoff.start", {"handoff_id": "one"}, wait=False
        )
    assert workflow.load(project, public["id"])["state"] == "unknown"


@pytest.mark.asyncio
async def test_unknown_delivery_never_resubmits_even_when_task_lookup_is_unavailable(
    tmp_path,
):
    _, project, _, _, workflow, public = prepared(tmp_path)
    record = workflow.load(project, public["id"])

    class Client:
        principal = "local"
        count = 0

        async def submit(self, packet):
            self.count += 1
            raise ContractError("designBridgeUnknown")

        async def task(self, identity):
            raise ContractError("designBridgeUnknown")

    client = workflow.client = Client()
    for _ in range(2):
        with pytest.raises(ContractError, match="designBridgeUnknown"):
            await workflow.operation(
                record, "start", "handoff.start", {"handoff_id": "one"}, wait=False
            )
    assert client.count == 1
    assert (
        workflow.load(project, public["id"])["operations"]["start"]["delivery"]
        == "unknown_before_submit"
    )


@pytest.mark.asyncio
async def test_concurrent_action_denied_and_profile_paths_not_caller_supplied(tmp_path):
    _, project, _, _, workflow, public = prepared(tmp_path)
    workflow.active.acquire()
    try:
        with pytest.raises(ContractError, match="designBusy"):
            await workflow.action(project, public["id"], "start")
    finally:
        workflow.active.release()
    for name in ["../foreign.html", "/absolute.html", ".", "sub/path.html"]:
        with pytest.raises(ContractError, match="designProfileUnavailable"):
            workflow.fixed_file(
                {"cwd": tmp_path, "source_file": name}, "source_file", 1024
            )


def test_two_design_projects_share_one_unknown_source_run_barrier(tmp_path):
    _, first, _, _, workflow, one = prepared(tmp_path)
    _, second, _, _, _, two = prepared(tmp_path)
    assert first != second
    profile = {"cwd": tmp_path, "source_file": "same.html", "preview_file": "same.png"}
    workflow.profiles = {first: profile, second: profile}
    previous = workflow.load(first, one["id"])
    previous["operations"]["start"] = {"task_id": "unknown-existing"}
    previous["state"] = "unknown"
    workflow.save(previous)
    workflow.guard_start(previous, profile)
    current = workflow.load(second, two["id"])
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, profile)
    previous["decision"] = "rejected"
    workflow.save(previous)
    workflow.guard_start(current, profile)
