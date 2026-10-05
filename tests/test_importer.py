from __future__ import annotations

import pytest

from agent_governance_evidence_pack.importer import (
    ImportErrorDetail,
    build_evidence_pack_from_artifacts,
    derive_counts,
    _index_records,
)
from agent_governance_evidence_pack.trace_renderer import render_traceable_markdown


def _manifest() -> dict:
    return {
        "manifest_id": "refund-agent-manifest",
        "manifest_version": "1.1",
        "agent": {"name": "RefundAgent", "description": "Handles bounded refund proposals."},
        "business_purpose": "Draft and execute bounded refund operations only under approved authority.",
        "deployment_context": {"environment": "staging", "systems_touched": ["refund-api"]},
        "actions": [
            {
                "action_id": "issue_refund",
                "action_name": "Issue refund",
                "tool_name": "refund_api",
                "action_type": "external_send",
                "authority_required": True,
                "review_required": True,
                "control_status": "implemented",
            }
        ],
    }


def _record(record_type: str, record_id: str, identifiers: dict, data: dict) -> dict:
    return {
        "record_id": record_id,
        "producer_profile_id": "control-plane-bounded-run@28350065",
        "record_type": record_type,
        "source_path": record_id,
        "identifiers": identifiers,
        "data": data,
    }


def _reconstruction(state: str = "applied", *, include_observation: bool = True) -> dict:
    records = [
        _record(
            "run_frame",
            "rec-frame",
            {"run_id": "run-1", "frame_id": "frame-1"},
            {"actor": "RefundAgent", "environment": "staging", "task": "Issue approved refund."},
        ),
        _record(
            "runtime_proposal",
            "rec-proposal",
            {"run_id": "run-1", "action_id": "issue_refund"},
            {"action_id": "issue_refund", "target": "customer-123"},
        ),
        _record(
            "runtime_decision",
            "rec-decision",
            {"run_id": "run-1", "decision_id": "decision-1", "effect_id": "effect-1"},
            {"result": "allow", "binding": {"grant_id": "grant-1"}, "effect_id": "effect-1"},
        ),
        _record(
            "control_plane_attempt_transition",
            "rec-attempt-start",
            {"run_id": "run-1", "decision_id": "decision-1", "effect_id": "effect-1", "attempt_id": "cp-attempt-1"},
            {"status": "started", "attempt_id": "cp-attempt-1"},
        ),
        _record(
            "control_plane_attempt_transition",
            "rec-attempt-ack-lost",
            {"run_id": "run-1", "decision_id": "decision-1", "effect_id": "effect-1", "attempt_id": "cp-attempt-1"},
            {"status": "acknowledgement_lost", "attempt_id": "cp-attempt-1"},
        ),
        _record(
            "reliance_record",
            "rec-reliance",
            {"run_id": "run-1", "reliance_id": "rel-1"},
            {"source_name": "CRM", "source_type": "database", "scope": "refund eligibility"},
        ),
    ]
    if include_observation:
        records.append(_record(
            "effect_observation",
            "rec-observation",
            {"run_id": "run-1", "effect_id": "effect-1"},
            {"state": state, "effect_id": "effect-1"},
        ))
    return {
        "bundle_version": "0.2.0",
        "bundle_id": "rb-1",
        "run_id": "run-1",
        "status": "reconstruction_complete",
        "records": records,
        "import_reports": [],
        "metadata": {"source_generated_at": "2026-10-05T00:00:00Z"},
    }


def test_importer_derives_traceable_counts_without_inflating_lifecycle_records() -> None:
    pack = build_evidence_pack_from_artifacts(_manifest(), _reconstruction())
    trace = pack.metadata["traceable_import"]
    counts = trace["derived_counts"]

    assert counts["proposal_count"] == 1
    assert counts["decision_count"] == 1
    assert counts["distinct_effect_count"] == 1
    assert counts["control_plane_attempt_count"] == 1
    assert counts["attempt_transition_record_count"] == 2
    assert trace["lifecycle_summary"]["destination_observed"] == "applied"
    assert pack.review_status.value == "draft"
    assert not pack.review_records


def test_importer_keeps_missing_observation_unresolved_not_zero() -> None:
    pack = build_evidence_pack_from_artifacts(_manifest(), _reconstruction(include_observation=False))
    trace = pack.metadata["traceable_import"]

    assert trace["derived_counts"]["coverage_denominators"]["destination_observations"] == 0
    assert trace["lifecycle_summary"]["destination_observed"] == "unavailable"
    assert any(r.risk_id == "missing-destination-observation" for r in pack.risk_register)


def test_counts_keep_control_plane_and_executor_attempts_separate() -> None:
    reconstruction = _reconstruction()
    reconstruction["records"].append(_record(
        "execution_attempt",
        "rec-executor-attempt",
        {"run_id": "run-1", "effect_id": "effect-1", "attempt_id": "exec-attempt-1"},
        {"attempt_id": "exec-attempt-1", "status": "completed"},
    ))
    counts = derive_counts(_index_records(reconstruction))

    assert counts["control_plane_attempt_count"] == 1
    assert counts["executor_attempt_count"] == 1
    assert counts["distinct_effect_count"] == 1


def test_importer_rejects_unsupported_manifest_version() -> None:
    manifest = _manifest()
    manifest["manifest_version"] = "9.9"
    with pytest.raises(ImportErrorDetail):
        build_evidence_pack_from_artifacts(manifest, _reconstruction())


def test_traceable_renderer_surfaces_limitations_and_source_refs() -> None:
    pack = build_evidence_pack_from_artifacts(_manifest(), _reconstruction(state="partial"))
    rendered = render_traceable_markdown(pack)

    assert "Traceability and Import Provenance" in rendered
    assert "distinct_effect_count" in rendered
    assert "destination_observed" in rendered
    assert "partial" in rendered
    assert "Supporting source-record references" in rendered
    assert "does not certify deployment approval" in rendered
