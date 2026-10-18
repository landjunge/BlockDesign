"""Legacy execution claims retain original local barrier; no service/model use."""

from copy import deepcopy

import pytest
from design_profile_test import pinned
from design_workflow_test import prepared
from project_store import ContractError


def shared_source(tmp_path):
    projects, previous_project, _, workflow, previous = pinned(tmp_path)
    _, current_project, _, _, _, public = prepared(tmp_path)
    workflow.profiles[current_project] = deepcopy(workflow.profiles[previous_project])
    current = workflow.load(current_project, public["id"])
    workflow.check_operator_profile(current, bind=True)
    del workflow.profiles[previous_project]
    return projects, workflow, previous, current


@pytest.mark.parametrize(
    "field", ["bridge_task_id", "run_id", "active_task_id", "return_id"]
)
def test_legacy_execution_receipt_without_operation_map_blocks_even_after_profile_removal(
    tmp_path, field
):
    _, workflow, previous, current = shared_source(tmp_path)
    previous.update(state="unknown", **{field: "historical-unresolved"})
    previous["operations"] = {}
    workflow.save(previous)
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, workflow.profiles[current["project_id"]])
    # No original pin means unknown source, not permission to use today's profile.
    previous.pop("operator_profile")
    previous.pop("operator_profile_sha256")
    workflow.save(previous)
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, workflow.profiles[current["project_id"]])
    # A separately recorded explicit terminal operator decision keeps its old meaning.
    previous["decision"] = "rejected"
    workflow.save(previous)
    workflow.guard_start(current, workflow.profiles[current["project_id"]])


@pytest.mark.parametrize("phase", ["unknown", "running", "awaiting_answer"])
def test_legacy_possible_execution_phase_is_not_proof_of_no_start(tmp_path, phase):
    _, workflow, previous, current = shared_source(tmp_path)
    previous.update(state=phase, operations={})
    workflow.save(previous)
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, workflow.profiles[current["project_id"]])


@pytest.mark.parametrize("phase", ["prepared", "issued_no_execution"])
def test_pure_prepared_or_issued_without_execution_claim_does_not_invent_start(
    tmp_path, phase
):
    _, workflow, previous, current = shared_source(tmp_path)
    previous.update(state=phase, operations={"issue": {"task_id": "only-issued"}})
    previous["issued"] = {"handoff_id": "issued-only"}
    previous.pop("operator_profile")
    previous.pop("operator_profile_sha256")
    workflow.save(previous)
    workflow.guard_start(current, workflow.profiles[current["project_id"]])


def test_legacy_answer_operation_without_initial_start_map_retains_possible_execution(
    tmp_path,
):
    _, workflow, previous, current = shared_source(tmp_path)
    previous.update(
        state="issued_no_execution",
        operations={"answer_old_question": {"task_id": "unknown-answer"}},
    )
    workflow.save(previous)
    with pytest.raises(ContractError, match="designBusy"):
        workflow.guard_start(current, workflow.profiles[current["project_id"]])
