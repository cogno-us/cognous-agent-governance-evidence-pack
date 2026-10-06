from __future__ import annotations

import copy
import json
import os
import sys
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
    assert lifecycle["current_permission"] == "not_evaluated_from_historical_records"
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


@pytest.mark.parametrize("mutation", ["payload", "actor", "destination_target", "destination_amount", "proposal_commitment", "dangling_attempt"])
def test_actual_pinned_success_tampering_is_rejected(mutation: str):
    manifest = _manifest()
    bundle = _success_bundle()
    if mutation == "payload":
        proposal = _records(bundle, "runtime_proposal")[0]
        proposal["data"]["payload"]["refund_reason"] = "tampered"
    elif mutation == "actor":
        proposal = _records(bundle, "runtime_proposal")[0]
        proposal["data"]["actor"] = "urn:cognous:identity:attacker"
    elif mutation == "destination_target":
        destination = _records(bundle, "destination_effect")[0]
        destination["data"]["target"] = "urn:cognous:synthetic-account:attacker"
    elif mutation == "destination_amount":
        destination = _records(bundle, "destination_effect")[0]
        destination["data"]["amount"] = 5000.0
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
    assert levels["source_asserted_runtime_evidence"]["status"] == "source_asserted"
    assert levels["tested"]["status"] == "unavailable"
    assert levels["implemented"]["status"] == "not_established_by_import"
    assert levels["tested_in_this_repository"]["status"] == "not_evaluated_during_import"
    assert levels["operationally_observed"]["status"] == "unavailable"



def test_missing_test_provenance_keeps_tested_unavailable_for_held_decision():
    bundle = _strip_execution(_success_bundle(), "hold")
    bundle["metadata"].pop("fixture_provenance", None)
    bundle["metadata"].pop("scenario", None)
    bundle["metadata"].pop("test_provenance", None)
    pack = import_manifest_reconstruction(_manifest(), bundle)
    levels = pack.metadata["traceable_import"]["control_evidence_levels"]
    assert levels["semantic_validation_performed_during_import"]["status"] == "recorded_no_execution"
    assert levels["source_asserted_runtime_evidence"]["status"] == "unavailable"
    assert levels["attributable_test_run_evidence"]["status"] == "unavailable"
    assert levels["tested"]["status"] == "unavailable"
    assert levels["tested_in_this_repository"]["status"] == "not_evaluated_during_import"


@pytest.mark.parametrize("malformed", [{}, [], False, "   "])
def test_malformed_test_provenance_values_leave_tested_unavailable_with_finding(malformed):
    bundle = _strip_execution(_success_bundle(), "hold")
    bundle["metadata"]["test_provenance"] = {
        "test_run_id": malformed,
        "producer": malformed,
        "scope": malformed,
        "result": malformed,
    }
    pack = import_manifest_reconstruction(_manifest(), bundle)
    trace = pack.metadata["traceable_import"]
    levels = trace["control_evidence_levels"]
    assert levels["attributable_test_run_evidence"]["status"] == "unavailable"
    assert levels["tested"]["status"] == "unavailable"
    finding = next(item for item in trace["import_findings"] if item["code"] == "T_TEST_PROVENANCE_INVALID")
    assert finding["path"] == "reconstruction_bundle.metadata.test_provenance"
    assert set(finding["invalid_fields"]) == {"test_run_id", "producer", "scope", "result"}


def test_failed_attributed_test_result_is_preserved_and_rendered_as_source_assertion():
    bundle = _strip_execution(_success_bundle(), "hold")
    bundle["metadata"]["test_provenance"] = {
        "test_run_id": "neg-hold-failed-002",
        "producer": "cognous-agent-control-plane integration harness",
        "revision": "283500652d47a692fb0b99a1172a6d5faffbd9a7",
        "scope": "revoked authority before execution -> held decision, no external effect",
        "result": "failed",
    }
    pack = import_manifest_reconstruction(_manifest(), bundle)
    levels = pack.metadata["traceable_import"]["control_evidence_levels"]
    attributed = levels["attributable_test_run_evidence"]
    assert attributed["status"] == "attributable_source_asserted"
    assert attributed["test_run_id"] == "neg-hold-failed-002"
    assert attributed["producer"] == "cognous-agent-control-plane integration harness"
    assert attributed["scope"] == "revoked authority before execution -> held decision, no external effect"
    assert attributed["result"] == "failed"
    assert levels["tested"]["status"] == "attributable_test_evidence_present_scope_bounded"
    assert levels["tested"]["result"] == "failed"

    out = render_traceable_markdown(pack)
    assert "### Attributed test-run evidence (source assertion)" in out
    assert "neg-hold-failed-002" in out
    assert "cognous-agent-control-plane integration harness" in out
    assert "revoked authority before execution -&gt; held decision, no external effect" in out
    assert "| result | failed |" in out
    assert "| attribution_status | attributable_source_asserted |" in out
    assert "source-supplied" in out


def test_attributed_negative_test_evidence_has_precise_scope_without_implying_repo_tests():
    bundle = _strip_execution(_success_bundle(), "hold")
    bundle["metadata"]["test_provenance"] = {
        "test_run_id": "neg-hold-001",
        "producer": "cognous-agent-control-plane integration harness",
        "revision": "283500652d47a692fb0b99a1172a6d5faffbd9a7",
        "scope": "revoked authority before execution -> held decision, no external effect",
        "result": "passed",
    }
    pack = import_manifest_reconstruction(_manifest(), bundle)
    levels = pack.metadata["traceable_import"]["control_evidence_levels"]
    assert levels["semantic_validation_performed_during_import"]["status"] == "recorded_no_execution"
    assert levels["attributable_test_run_evidence"]["status"] == "attributable_source_asserted"
    assert levels["attributable_test_run_evidence"]["test_run_id"] == "neg-hold-001"
    assert levels["tested"]["status"] == "attributable_test_evidence_present_scope_bounded"
    assert levels["tested"]["scope"] == "revoked authority before execution -> held decision, no external effect"
    assert levels["tested_in_this_repository"]["status"] == "not_evaluated_during_import"
    assert pack.metadata["traceable_import"]["lifecycle_summary"]["execution_attempted"] == "no"


def test_source_record_hash_compatibility_alias_matches_local_commitment():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    for ref in pack.metadata["traceable_import"]["source_record_refs"]:
        assert ref["hash"] == ref["local_content_commitment"]
        assert ref["hash"].startswith("sha256:")


def test_renderer_distinguishes_source_and_local_commitments_and_source_assertions():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    refs = pack.metadata["traceable_import"]["source_record_refs"]
    proposal_ref = next(ref for ref in refs if ref["record_type"] == "runtime_proposal")
    assert proposal_ref["source_commitments"]
    source = proposal_ref["source_commitments"][0]
    assert source["verification_status"] == "checked_match"
    assert source["canonicalization_profile"] == "json-sort-keys-compact-utf8-no-nan"
    assert proposal_ref["local_commitment_verification_status"] == "computed_during_import"
    assert proposal_ref["source_content_commitment"] == source["value"]
    assert proposal_ref["source_canonicalization_profile"] == source["canonicalization_profile"]
    out = render_traceable_markdown(pack)
    assert "### Source-supplied commitments" in out
    assert "### Locally computed record commitments" in out
    assert "Evidence Class (source assertion)" in out
    assert source["value"] in out
    assert proposal_ref["local_content_commitment"] in out
    assert "checked_match" in out
    assert "computed_during_import" in out
    assert "not the importer’s independent assurance" in out

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



def test_traceability_preserves_producer_revision_and_provenance_status():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    trace = pack.metadata["traceable_import"]
    profiles = {item["repository"]: item for item in trace["producer_profiles"]}
    assert profiles["cogno-us/cognous-agent-control-plane"]["revision"] == "283500652d47a692fb0b99a1172a6d5faffbd9a7"
    assert profiles["cogno-us/cognous-agent-control-plane"]["revision_check"] == "declared_revision_matches_accepted_pin"
    assert profiles["cogno-us/cognous-agent-control-plane"]["independent_provenance_verification"] == "not_performed"
    ref = trace["source_record_refs"][0]
    assert ref["evidence_class"] == "producer_reported"
    assert ref["local_content_commitment"].startswith("sha256:")
    assert ref["source_asserted_provenance"] == "source_asserted_and_contract_compared"


def test_conflicting_declared_producer_revision_is_rejected():
    bundle = _success_bundle()
    bundle["producer_profiles"][0]["revision"] = "0" * 40
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(_manifest(), bundle)


def test_source_assurance_label_does_not_create_independent_verification():
    bundle = _success_bundle()
    bundle["records"][0]["evidence_class"] = "independently_checked"
    pack = import_manifest_reconstruction(_manifest(), bundle)
    lifecycle = pack.metadata["traceable_import"]["lifecycle_summary"]
    assert lifecycle["independent_verification"] == "unavailable"
    assert pack.metadata["traceable_import"]["source_record_refs"][0]["evidence_class"] == "independently_checked"


def test_conversion_losses_preserve_replay_findings():
    bundle = _strip_execution(_success_bundle(), "hold")
    pack = import_manifest_reconstruction(_manifest(), bundle)
    losses = pack.metadata["traceable_import"]["conversion_losses"]
    assert any(item["code"] == "TEST_NO_EXECUTION" for item in losses)
    assert any(item["value_state"] == "absent" for item in losses)


def test_accepted_gax_imx_generated_replay_bundle_imports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = _path_from_env("UPSTREAM_GAX_ROOT")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    monkeypatch.setenv("UPSTREAM_MANIFEST_EXAMPLE", str(_path_from_env("UPSTREAM_MANIFEST_EXAMPLE")))
    monkeypatch.setenv("UPSTREAM_REPLAY_SUCCESS_EXAMPLE", str(_path_from_env("UPSTREAM_REPLAY_SUCCESS_EXAMPLE")))
    monkeypatch.setenv("MOLTBOT_SAFE_CONTROL_PLANE_ROOT", str(_path_from_env("UPSTREAM_CONTROL_PLANE_ROOT")))
    monkeypatch.setenv("MOLTBOT_SAFE_ROOT", str(_path_from_env("UPSTREAM_MOLTBOT_SAFE_ROOT")))
    from experiments.odex_gax_imx_reference.gax_ref_runtime import run_actual_outcome

    exchange = run_actual_outcome(tmp_path, "success")
    bundle = exchange["reconstruction_bundle"]
    pack = import_manifest_reconstruction(_manifest(), bundle)
    trace = pack.metadata["traceable_import"]
    assert trace["replay_semantic_validation"]["status"] == "executed"
    assert trace["supported_revisions"]["gax_imx_experimental_reference"] == "9ad378145d326799e3209136e47e82d66c6f69af"
    assert trace["lifecycle_summary"]["destination_observed"] == "applied"
    assert trace["lifecycle_summary"]["independent_verification"] == "unavailable"


def test_empty_unversioned_bundle_rejected():
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(_manifest(), {"records": []})


def _versioned_executor_bundle() -> dict:
    bundle = copy.deepcopy(_success_bundle())
    old_profile = "moltbot-safe-envelope-0.2.0@6b0ba118"
    new_profile = "moltbot-safe-executor-1.0.0@894e1c1"
    found = False
    for profile in bundle["producer_profiles"]:
        if profile.get("repository") == "cogno-us/moltbot-safe":
            profile.update(
                profile_id=new_profile,
                revision="894e1c115cb91229c474a906c51ea9af7999e675",
                format_name="Executor producer record",
                format_version="1.0.0",
                notes="Versioned source-asserted executor record.",
            )
            found = True
    assert found
    for record in bundle["records"]:
        if record.get("producer_profile_id") == old_profile:
            record["producer_profile_id"] = new_profile
            record["record_id"] = record["record_id"].replace(old_profile, new_profile)
    bundle.setdefault("metadata", {}).update(
        moltbot_safe_revision="894e1c115cb91229c474a906c51ea9af7999e675",
        moltbot_producer_profile_version="1.0.0",
        moltbot_provenance={
            "source_asserted": True,
            "independently_established": False,
            "state": "source_asserted",
        },
    )
    return bundle


def test_versioned_executor_profile_preserves_source_asserted_not_independent_provenance():
    pack = import_manifest_reconstruction(_manifest(), _versioned_executor_bundle())
    trace = pack.metadata["traceable_import"]
    assert trace["replay_semantic_validation"]["status"] == "executed"
    assert trace["lifecycle_summary"]["independent_verification"] == "unavailable"
    assert trace["control_evidence_levels"]["source_asserted_runtime_evidence"]["status"] == "source_asserted"


@pytest.mark.parametrize(
    "mutation",
    ["revision", "version", "profile", "provenance"],
)
def test_versioned_executor_profile_rejects_unsupported_or_contradictory_contract(mutation):
    bundle = _versioned_executor_bundle()
    producer = next(
        p for p in bundle["producer_profiles"]
        if p.get("repository") == "cogno-us/moltbot-safe"
    )
    if mutation == "revision":
        producer["revision"] = "deadbeef"
    elif mutation == "version":
        producer["format_version"] = "9.9.9"
    elif mutation == "profile":
        producer["profile_id"] = "unsupported"
    else:
        bundle["metadata"]["moltbot_provenance"]["source_asserted"] = False
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(_manifest(), bundle)


def test_legacy_executor_profile_remains_revision_pinned():
    pack = import_manifest_reconstruction(_manifest(), _success_bundle())
    source = next(
        p for p in _success_bundle()["producer_profiles"]
        if p.get("repository") == "cogno-us/moltbot-safe"
    )
    assert source["revision"] == "6b0ba1185bcd390f71df947dda349415e4105f5f"
    assert source["format_version"] == "0.2.0"
    assert pack.validation_summary.valid_bundle_count == 1
