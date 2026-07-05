"""
Markdown renderer for Agent Governance Evidence Pack.
"""

from __future__ import annotations

from .models import EvidencePack
from .summary import summarize_evidence_pack


def _escape(value: object) -> str:
    """Escape pipe characters for use in markdown tables."""
    return str(value).replace("|", "\\|") if value is not None else ""


def _yn(value: bool) -> str:
    return "Yes" if value else "No"


def _or_dash(value: object) -> str:
    if value is None:
        return "—"
    s = str(value).strip()
    return s if s else "—"


def render_markdown(pack: EvidencePack) -> str:
    """Render an EvidencePack as a business-facing markdown document."""
    parts: list[str] = []
    summary = summarize_evidence_pack(pack)

    # ------------------------------------------------------------------ #
    # Title and metadata table
    # ------------------------------------------------------------------ #
    parts.append(f"# {_escape(pack.title)}\n")

    parts.append("| Field | Value |")
    parts.append("|---|---|")
    parts.append(f"| Pack ID | {_escape(pack.pack_id)} |")
    parts.append(f"| Version | {_escape(pack.pack_version)} |")
    parts.append(f"| Generated At | {_escape(pack.generated_at)} |")
    parts.append(f"| Review Status | {_escape(pack.review_status.value)} |")
    parts.append(f"| Agent | {_escape(pack.agent_overview.agent_name)} |")
    parts.append(f"| Environment | {_escape(pack.deployment_context.environment.value)} |")
    parts.append(f"| Owner | {_escape(_or_dash(pack.agent_overview.owner))} |")
    parts.append(f"| Business Unit | {_escape(_or_dash(pack.agent_overview.business_unit))} |")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 1. Executive Summary
    # ------------------------------------------------------------------ #
    parts.append("## 1. Executive Summary\n")
    env = pack.deployment_context.environment.value
    agent_name = pack.agent_overview.agent_name
    purpose = pack.agent_overview.business_purpose
    tool_count = summary["tool_count"]
    action_count = summary["action_count"]
    privileged_count = summary["privileged_action_count"]
    replay_count = summary["replay_bundle_count"]
    open_risks = summary["open_risk_count"]
    critical_risks = summary["critical_open_risk_count"]
    val_errors = summary["validation_error_count"]
    val_warnings = summary["validation_warning_count"]

    exec_lines = [
        f"**{agent_name}** is deployed in the **{env}** environment. "
        f"Business purpose: {purpose}",
        "",
        f"The agent has access to **{tool_count}** tool(s) and can propose **{action_count}** action(s), "
        f"of which **{privileged_count}** require authority or human review.",
        "",
    ]
    if replay_count:
        signed = summary["signed_replay_bundle_count"]
        exec_lines.append(
            f"**{replay_count}** replay bundle(s) are available ({signed} signed)."
        )
    else:
        exec_lines.append("No replay bundles are recorded in this evidence pack.")

    if pack.validation_summary:
        exec_lines.append(
            f"Validation summary: {pack.validation_summary.valid_bundle_count} valid bundle(s), "
            f"{pack.validation_summary.invalid_bundle_count} invalid, "
            f"{val_errors} error(s), {val_warnings} warning(s)."
        )

    exec_lines.append("")
    if open_risks:
        exec_lines.append(
            f"**{open_risks}** open risk(s) ({critical_risks} critical)."
        )
    else:
        exec_lines.append("No open risks recorded.")

    parts.append("\n".join(exec_lines))
    parts.append("")

    # ------------------------------------------------------------------ #
    # 2. Agent Overview
    # ------------------------------------------------------------------ #
    parts.append("## 2. Agent Overview\n")
    ao = pack.agent_overview
    parts.append(f"**Agent Name:** {_escape(ao.agent_name)}\n")
    if ao.agent_description:
        parts.append(f"**Description:** {_escape(ao.agent_description)}\n")
    parts.append(f"**Business Purpose:** {_escape(ao.business_purpose)}\n")
    if ao.owner:
        parts.append(f"**Owner:** {_escape(ao.owner)}\n")
    if ao.business_unit:
        parts.append(f"**Business Unit:** {_escape(ao.business_unit)}\n")
    if ao.user_population:
        parts.append(f"**User Population:** {_escape(ao.user_population)}\n")
    if ao.lifecycle_stage:
        parts.append(f"**Lifecycle Stage:** {_escape(ao.lifecycle_stage)}\n")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 3. Deployment Context
    # ------------------------------------------------------------------ #
    parts.append("## 3. Deployment Context\n")
    dc = pack.deployment_context
    parts.append(f"**Environment:** {_escape(dc.environment.value)}\n")
    if dc.deployment_name:
        parts.append(f"**Deployment Name:** {_escape(dc.deployment_name)}\n")
    if dc.deployment_date:
        parts.append(f"**Deployment Date:** {_escape(dc.deployment_date)}\n")
    if dc.systems_touched:
        parts.append(f"**Systems Touched:** {_escape(', '.join(dc.systems_touched))}\n")
    if dc.data_domains:
        parts.append(f"**Data Domains:** {_escape(', '.join(dc.data_domains))}\n")
    if dc.geographic_scope:
        parts.append(f"**Geographic Scope:** {_escape(dc.geographic_scope)}\n")
    if dc.notes:
        parts.append(f"**Notes:** {_escape(dc.notes)}\n")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 4. Tool Inventory
    # ------------------------------------------------------------------ #
    parts.append("## 4. Tool Inventory\n")
    if pack.tool_inventory:
        parts.append(
            "| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |"
        )
        parts.append("|---|---|---|---|---|---|")
        for tool in pack.tool_inventory:
            parts.append(
                f"| {_escape(tool.tool_name)} "
                f"| {_escape(_or_dash(tool.description))} "
                f"| {_escape(_or_dash(tool.external_system))} "
                f"| {_escape(_or_dash(tool.data_classification))} "
                f"| {_escape(_or_dash(tool.access_mode))} "
                f"| {_escape(tool.control_status.value)} |"
            )
    else:
        parts.append("No tools recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 5. Action Inventory
    # ------------------------------------------------------------------ #
    parts.append("## 5. Action Inventory\n")
    if pack.action_inventory:
        parts.append(
            "| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |"
        )
        parts.append("|---|---|---|---|---|---|---|")
        for action in pack.action_inventory:
            parts.append(
                f"| {_escape(action.action_name)} "
                f"| {_escape(action.tool_name)} "
                f"| {_escape(action.action_type.value)} "
                f"| {_yn(action.authority_required)} "
                f"| {_yn(action.review_required)} "
                f"| {_yn(action.reliance_required)} "
                f"| {_escape(action.control_status.value)} |"
            )
    else:
        parts.append("No actions recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 6. Authority Model
    # ------------------------------------------------------------------ #
    parts.append("## 6. Authority Model\n")
    if pack.authority_model:
        am = pack.authority_model
        parts.append(f"**Summary:** {_escape(am.summary)}\n")
        if am.authority_scopes:
            parts.append(f"**Authority Scopes:** {_escape(', '.join(am.authority_scopes))}\n")
        if am.privileged_action_types:
            parts.append(
                f"**Privileged Action Types:** "
                f"{_escape(', '.join(t.value for t in am.privileged_action_types))}\n"
            )
        parts.append(f"**Expiration Required:** {_yn(am.expiration_required)}\n")
        parts.append(f"**Human Approval Required:** {_yn(am.human_approval_required)}\n")
        if am.notes:
            parts.append(f"**Notes:** {_escape(am.notes)}\n")
    else:
        parts.append("No authority model recorded for this evidence pack.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 7. Policy Controls
    # ------------------------------------------------------------------ #
    parts.append("## 7. Policy Controls\n")
    if pack.policy_controls:
        parts.append("| Control Name | Description | Status | Evidence Reference |")
        parts.append("|---|---|---|---|")
        for pc in pack.policy_controls:
            parts.append(
                f"| {_escape(pc.control_name)} "
                f"| {_escape(pc.description)} "
                f"| {_escape(pc.control_status.value)} "
                f"| {_escape(_or_dash(pc.evidence_reference))} |"
            )
    else:
        parts.append("No policy controls recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 8. Blocked-Action Summary
    # ------------------------------------------------------------------ #
    parts.append("## 8. Blocked-Action Summary\n")
    if pack.blocked_actions:
        total_blocked = sum(b.count for b in pack.blocked_actions)
        parts.append(
            f"A total of **{total_blocked}** blocked action(s) are recorded in this evidence pack.\n"
        )
        parts.append(
            "| Action Name | Action Type | Tool | Count | Reason Summary | Evidence Reference |"
        )
        parts.append("|---|---|---|---|---|---|")
        for ba in pack.blocked_actions:
            parts.append(
                f"| {_escape(_or_dash(ba.action_name))} "
                f"| {_escape(_or_dash(ba.action_type.value if ba.action_type else None))} "
                f"| {_escape(_or_dash(ba.tool_name))} "
                f"| {_escape(ba.count)} "
                f"| {_escape(_or_dash(ba.reason_summary))} "
                f"| {_escape(_or_dash(ba.evidence_reference))} |"
            )
    else:
        parts.append("No blocked actions recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 9. Reliance Summary
    # ------------------------------------------------------------------ #
    parts.append("## 9. Reliance Summary\n")
    if pack.reliance_summary:
        total_reliance = sum(r.count for r in pack.reliance_summary)
        parts.append(
            f"A total of **{total_reliance}** reliance record(s) are recorded in this evidence pack.\n"
        )
        parts.append(
            "| Source Name | Source Type | Count | Scope Summary | Evidence Reference |"
        )
        parts.append("|---|---|---|---|---|")
        for rs in pack.reliance_summary:
            parts.append(
                f"| {_escape(rs.source_name)} "
                f"| {_escape(rs.source_type)} "
                f"| {_escape(rs.count)} "
                f"| {_escape(_or_dash(rs.scope_summary))} "
                f"| {_escape(_or_dash(rs.evidence_reference))} |"
            )
    else:
        parts.append("No reliance records recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 10. Replay Bundle Inventory
    # ------------------------------------------------------------------ #
    parts.append("## 10. Replay Bundle Inventory\n")
    if pack.replay_bundles:
        parts.append(
            "| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |"
        )
        parts.append("|---|---|---|---|---|---|---|---|")
        for bundle in pack.replay_bundles:
            parts.append(
                f"| {_escape(bundle.bundle_id)} "
                f"| {_escape(_or_dash(bundle.run_id))} "
                f"| {_escape(_or_dash(bundle.status))} "
                f"| {_escape(_or_dash(bundle.generated_at))} "
                f"| {_yn(bundle.signed)} "
                f"| {_yn(bundle.redacted)} "
                f"| {_escape(_or_dash(bundle.validation_status))} "
                f"| {_escape(_or_dash(bundle.evidence_reference))} |"
            )
    else:
        parts.append("No replay bundles recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 11. Validation Summary
    # ------------------------------------------------------------------ #
    parts.append("## 11. Validation Summary\n")
    if pack.validation_summary:
        vs = pack.validation_summary
        parts.append(
            f"**Valid Bundles:** {vs.valid_bundle_count} | "
            f"**Invalid Bundles:** {vs.invalid_bundle_count} | "
            f"**Errors:** {vs.error_count} | "
            f"**Warnings:** {vs.warning_count}\n"
        )
        if vs.summary:
            parts.append(f"{_escape(vs.summary)}\n")
    else:
        parts.append("No validation summary recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 12. Redaction and Export Summary
    # ------------------------------------------------------------------ #
    parts.append("## 12. Redaction and Export Summary\n")
    if pack.redaction_exports:
        parts.append(
            "| Export ID | Type | Redacted Fields | Generated At | Intended Recipient | Evidence Reference |"
        )
        parts.append("|---|---|---|---|---|---|")
        for exp in pack.redaction_exports:
            redacted_fields = ", ".join(exp.redacted_fields) if exp.redacted_fields else "—"
            parts.append(
                f"| {_escape(exp.export_id)} "
                f"| {_escape(exp.export_type)} "
                f"| {_escape(redacted_fields)} "
                f"| {_escape(_or_dash(exp.generated_at))} "
                f"| {_escape(_or_dash(exp.intended_recipient))} "
                f"| {_escape(_or_dash(exp.evidence_reference))} |"
            )
    else:
        parts.append("No redaction or export records recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 13. Risk Register
    # ------------------------------------------------------------------ #
    parts.append("## 13. Risk Register\n")
    if pack.risk_register:
        parts.append(
            "| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |"
        )
        parts.append("|---|---|---|---|---|---|---|")
        for risk in pack.risk_register:
            parts.append(
                f"| {_escape(risk.risk_id)} "
                f"| {_escape(risk.title)} "
                f"| {_escape(risk.severity.value)} "
                f"| {_escape(risk.status.value)} "
                f"| {_escape(_or_dash(risk.mitigation))} "
                f"| {_escape(_or_dash(risk.owner))} "
                f"| {_escape(_or_dash(risk.evidence_reference))} |"
            )
    else:
        parts.append("No risks recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 14. Review Records
    # ------------------------------------------------------------------ #
    parts.append("## 14. Review Records\n")
    if pack.review_records:
        parts.append("| Reviewer | Role | Reviewed At | Decision | Notes |")
        parts.append("|---|---|---|---|---|")
        for rr in pack.review_records:
            parts.append(
                f"| {_escape(rr.reviewer)} "
                f"| {_escape(_or_dash(rr.reviewer_role))} "
                f"| {_escape(_or_dash(rr.reviewed_at))} "
                f"| {_escape(rr.decision.value)} "
                f"| {_escape(_or_dash(rr.notes))} |"
            )
    else:
        parts.append("No review records recorded.")
    parts.append("")

    # ------------------------------------------------------------------ #
    # 15. Known Limitations
    # ------------------------------------------------------------------ #
    parts.append("## 15. Known Limitations\n")
    parts.append(
        "This evidence pack summarizes available runtime and governance records. "
        "It does not prove that model outputs are correct, that policies are sufficient, "
        "or that external compliance obligations have been satisfied."
    )
    parts.append("")

    return "\n".join(parts)
