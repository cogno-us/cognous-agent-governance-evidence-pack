from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from agent_governance_evidence_pack.importer import ImportContractError, import_manifest_reconstruction
from agent_governance_evidence_pack.trace_renderer import render_traceable_markdown


def _path_from_env(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} not supplied; pinned producer checkout is required for this integration test")
    path = Path(value)
    if not path.exists():
        pytest.skip(f"{name} path does not exist: {path}")
    return path


def _manifest() -> dict:
    return json.loads(_path_from_env("UPSTREAM_MANIFEST_EXAMPLE").read_text(encoding="utf-8"))


def _success_bundle() -> dict:
    return json.loads(_path_from_env("UPSTREAM_REPLAY_SUCCESS_EXAMPLE").read_text(encoding="utf-8"))


def _lost_ack_bundle() -> dict:
    return json.loads(_path_from_env("UPSTREAM_REPLAY_LOST_ACK_EXAMPLE").read_text(encoding="utf-8"))


def _records(bundle: dict, record_type: str) -> list[dict]:
    return [record for record in bundle["records"] if record["record_type"] == record_type]


def test_actual_pinned_success_imports_and_preserves_acknowledgement_unknown():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    trace = pack.metadata["traceable_import"]
    counts = trace["derived_counts"]
    lifecycle = trace["lifecycle_summary"]
    assert pack.validation_summary.valid_bundle_count == 1
    assert trace["replay_semantic_validation"]["status"] == "executed"
    assert counts["control_plane_attempt_count"] == 1
    assert counts["executor_attempt_count"] == 1
    assert counts["destination_effect_count"] == 1
    assert counts["effect_observation_count"] == 1
    assert lifecycle["acknowledgement"] == "unknown"
    assert lifecycle["control_plane_transition_statuses"]["acknowledged"] == 1
    assert lifecycle["destination_observed"] == "unknown"


def test_actual_lost_ack_keeps_unknown_and_applied_observation_visible():
    pack = import_manifest_reconstruction(_manifest(), _lost_ack_bundle())
    lifecycle = pack.metadata["traceable_import"]["lifecycle_summary"]
    counts = pack.metadata["traceable_import"]["derived_counts"]
    assert lifecycle["acknowledgement"] == "unknown"
    assert counts["effect_observation_state_counts"].get("applied") == 1


@pytest.mark.parametrize("mutation", ["payload", "destination_target", "proposal_commitment", "dangling_attempt"])
def test_actual_pinned_success_tampering_is_rejected(mutation: str):
    manifest = _manifest()
    bundle = _success_bundle()
    if mutation == "payload":
        proposal = _records(bundle, "runtime_proposal")[0]
        proposal["data"]["payload"]["refund_reason"] = "tampered"
    elif mutation == "destination_target":
        destination = _records(bundle, "destination_effect")[0]
        destination["data"]["target"] = "urn:cognous:synthetic-account:attacker"
    elif mutation == "proposal_commitment":
        decision = _records(bundle, "runtime_decision")[0]
        decision["data"]["binding"]["proposal_commitment"] = "sha256:" + "0" * 64
    elif mutation == "dangling_attempt":
        result = _records(bundle, "execution_result")[0]
        result["data"]["attempt_id"] = "nonexistent-attempt"
        result["identifiers"]["attempt_id"] = "nonexistent-attempt"
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(manifest, bundle)


def test_manifest_requirements_do_not_imply_implemented_controls():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    assert all(action.control_status.value == "planned" for action in pack.action_inventory)
    levels = pack.metadata["traceable_import"]["control_evidence_levels"]
    assert levels["tested"]["status"] == "unavailable"
    assert levels["implemented"]["status"] == "not_inferred_from_manifest"


def test_renderer_escapes_html_and_table_breaks():
    manifest = copy.deepcopy(_manifest())
    manifest["agent_name"] = "<b>Bad|Agent</b>"
    out = render_traceable_markdown(import_manifest_reconstruction(manifest, _success_bundle()))
    assert "<b>" not in out
    assert "&lt;b&gt;Bad\\|Agent&lt;/b&gt;" in out


def test_empty_unversioned_bundle_rejected():
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(_manifest(), {"records": []})
