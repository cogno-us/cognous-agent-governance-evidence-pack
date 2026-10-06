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


def _strip_execution(bundle: dict, result: str = "hold") -> dict:
    out = copy.deepcopy(bundle)
    kept = []
    for record in out["records"]:
        if record["record_type"] in {"runtime_proposal", "runtime_decision"}:
            kept.append(record)
    out["records"] = kept
    out["links"] = []
    out["commitments"] = [item for item in out.get("commitments", []) if item.get("label") == "payload_commitment"]
    decision = _records(out, "runtime_decision")[0]
    decision["data"]["result"] = result
    decision["data"].pop("binding", None)
    decision["data"].pop("effect_id", None)
    decision["identifiers"].pop("effect_id", None)
    out["status"] = "reconstruction_partial"
    for report in out.get("import_reports", []):
        report["complete"] = False
        report.setdefault("findings", []).append({"code": "TEST_NO_EXECUTION", "category": "missing_dependency", "severity": "warning", "path": "moltbot_export", "message": "No execution evidence supplied for held or denied decision.", "value_state": "absent"})
    return out


def _mutate_observations(bundle: dict, state: str) -> dict:
    out = copy.deepcopy(bundle)
    for record in out["records"]:
        if record["record_type"] == "effect_observation":
            record["data"]["state"] = state
        if record["record_type"] == "execution_result":
            record["data"]["observed_state"] = state
            if isinstance(record["data"].get("observation"), dict):
                record["data"]["observation"]["state"] = state
    if state in {"partial", "unknown"}:
        out["status"] = "reconstruction_partial"
        for report in out.get("import_reports", []):
            report["complete"] = False
    return out


def _add_reconciliation(bundle: dict, result: str = "applied") -> dict:
    out = copy.deepcopy(bundle)
    observation = copy.deepcopy(_records(out, "effect_observation")[0]["data"])
    observation["state"] = "applied" if result == "applied" else "absent"
    rec = {
        "record_id": "control-plane-bounded-run@28350065:reconciliation:test",
        "producer_profile_id": "control-plane-bounded-run@28350065",
        "record_type": "reconciliation",
        "source_sequence": max(r["source_sequence"] for r in out["records"]) + 1,
        "source_path": "reconciliations[test]",
        "recorded_at": observation.get("observed_at"),
        "identifiers": {"run_id": out["run_id"], "effect_id": observation["effect_id"]},
        "evidence_class": "producer_reported",
        "data": {"effect_id": observation["effect_id"], "result": result, "observation": observation},
    }
    out["records"].append(rec)
    return out


def _result_uses_control_plane_attempt(bundle: dict) -> dict:
    out = copy.deepcopy(bundle)
    cp_attempt = _records(out, "control_plane_attempt_transition")[-1]["data"]["attempt_id"]
    result = _records(out, "execution_result")[0]
    result["data"]["attempt_id"] = cp_attempt
    result["data"]["status"] = "reconciled"
    result["data"]["newly_executed"] = False
    result["identifiers"]["attempt_id"] = cp_attempt
    return out


def test_actual_pinned_success_imports_and_preserves_acknowledgement_receipt():
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
    assert lifecycle["authorization"] == "authorized"
    assert lifecycle["acknowledgement"] == "received"
    assert counts["acknowledgement_counts"]["control_plane_received"] == 1
    assert lifecycle["control_plane_transition_statuses"]["acknowledged"] == 1
    assert lifecycle["destination_observed"] == "applied"
    assert lifecycle["independent_verification"] == "unavailable"


def test_actual_lost_ack_keeps_unknown_and_applied_observation_visible():
    pack = import_manifest_reconstruction(_manifest(), _lost_ack_bundle())
    lifecycle = pack.metadata["traceable_import"]["lifecycle_summary"]
    counts = pack.metadata["traceable_import"]["derived_counts"]
    assert lifecycle["acknowledgement"] == "unknown"
    assert lifecycle["destination_observed"] == "applied"
    assert counts["effect_observation_state_counts"].get("applied") == 1


@pytest.mark.parametrize("result,summary", [("hold", "held"), ("deny", "denied")])
def test_actual_pinned_hold_or_deny_with_no_effect_is_valid(result: str, summary: str):
    pack = import_manifest_reconstruction(_manifest(), _strip_execution(_success_bundle(), result))
    trace = pack.metadata["traceable_import"]
    assert trace["replay_semantic_validation"]["status"] == "recorded_no_execution"
    assert trace["lifecycle_summary"]["authorization"] == summary
    assert trace["lifecycle_summary"]["execution_attempted"] == "no"
    assert trace["derived_counts"]["distinct_effect_count"] == 0
    assert trace["derived_counts"]["destination_observation_counts"] == {"unavailable": 1}


def test_actual_duplicate_restart_reconciliation_is_counted_separately():
    pack = import_manifest_reconstruction(_manifest(), _add_reconciliation(_success_bundle()))
    counts = pack.metadata["traceable_import"]["derived_counts"]
    assert counts["distinct_effect_count"] == 1
    assert counts["destination_effect_count"] == 1
    assert counts["effect_observation_count"] == 1
    assert counts["reconciliation_count"] == 1
    assert counts["reconciliation_state_counts"]["applied"] == 1


def test_actual_partial_delivery_preserved_as_partial():
    pack = import_manifest_reconstruction(_manifest(), _mutate_observations(_success_bundle(), "partial"))
    trace = pack.metadata["traceable_import"]
    assert trace["replay_semantic_validation"]["status"] == "executed_with_unresolved_evidence"
    assert trace["lifecycle_summary"]["destination_observed"] == "partial"
    assert trace["derived_counts"]["effect_observation_state_counts"]["partial"] == 1


def test_replay_supported_control_plane_attempt_reference_for_non_new_result():
    pack = import_manifest_reconstruction(_manifest(), _result_uses_control_plane_attempt(_success_bundle()))
    assert pack.metadata["traceable_import"]["replay_semantic_validation"]["status"] == "executed"


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
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    pack.title = "<b>Bad|Pack</b>"
    out = render_traceable_markdown(pack)
    assert "<b>" not in out
    assert "&lt;b&gt;Bad\\|Pack&lt;/b&gt;" in out


def test_replay_findings_and_redaction_derivation_are_preserved():
    bundle = _strip_execution(_success_bundle(), "hold")
    bundle["status"] = "redacted"
    bundle["derivation"] = {"relationship": "redacted_derivative", "source_bundle_id": "source-1", "derived_at": "2026-10-05T00:00:00Z"}
    pack = import_manifest_reconstruction(_manifest(), bundle)
    trace = pack.metadata["traceable_import"]
    assert trace["redaction_state"]["redacted"] is True
    assert trace["redaction_state"]["source"] in {"source_status_redacted", "source_derivation_redacted_derivative"}
    assert trace["replay_import_reports"]
    assert any(item["code"].startswith("REPLAY_") for item in trace["import_findings"])


def test_empty_unversioned_bundle_rejected():
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(_manifest(), {"records": []})
