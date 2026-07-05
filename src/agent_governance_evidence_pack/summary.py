"""
Summary statistics for an Agent Governance Evidence Pack.
"""

from __future__ import annotations

from .models import EvidencePack, RiskSeverity, RiskStatus, ValidationSeverity


def summarize_evidence_pack(pack: EvidencePack) -> dict:
    """Return a summary dict with key counts and status fields."""
    privileged_action_count = sum(
        1
        for a in pack.action_inventory
        if a.authority_required or a.review_required
    )
    authority_required_count = sum(
        1 for a in pack.action_inventory if a.authority_required
    )
    review_required_count = sum(
        1 for a in pack.action_inventory if a.review_required
    )
    reliance_required_count = sum(
        1 for a in pack.action_inventory if a.reliance_required
    )
    blocked_action_total = sum(b.count for b in pack.blocked_actions)
    reliance_total = sum(r.count for r in pack.reliance_summary)
    signed_bundle_count = sum(1 for b in pack.replay_bundles if b.signed)
    redacted_bundle_count = sum(1 for b in pack.replay_bundles if b.redacted)
    open_risk_count = sum(
        1 for r in pack.risk_register if r.status == RiskStatus.open
    )
    critical_open_risk_count = sum(
        1
        for r in pack.risk_register
        if r.severity == RiskSeverity.critical and r.status == RiskStatus.open
    )

    validation_error_count = 0
    validation_warning_count = 0
    if pack.validation_summary:
        validation_error_count = pack.validation_summary.error_count
        validation_warning_count = pack.validation_summary.warning_count

    return {
        "pack_id": pack.pack_id,
        "title": pack.title,
        "review_status": pack.review_status.value,
        "agent_name": pack.agent_overview.agent_name,
        "environment": pack.deployment_context.environment.value,
        "tool_count": len(pack.tool_inventory),
        "action_count": len(pack.action_inventory),
        "privileged_action_count": privileged_action_count,
        "authority_required_action_count": authority_required_count,
        "review_required_action_count": review_required_count,
        "reliance_required_action_count": reliance_required_count,
        "blocked_action_total": blocked_action_total,
        "reliance_total": reliance_total,
        "replay_bundle_count": len(pack.replay_bundles),
        "signed_replay_bundle_count": signed_bundle_count,
        "redacted_replay_bundle_count": redacted_bundle_count,
        "open_risk_count": open_risk_count,
        "critical_open_risk_count": critical_open_risk_count,
        "review_record_count": len(pack.review_records),
        "validation_error_count": validation_error_count,
        "validation_warning_count": validation_warning_count,
    }
