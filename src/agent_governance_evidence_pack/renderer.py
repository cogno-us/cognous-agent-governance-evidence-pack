"""Markdown renderer for Agent Governance Evidence Pack."""
from __future__ import annotations
from html import escape as html_escape
from .models import EvidencePack
from .summary import summarize_evidence_pack


def _escape(value: object) -> str:
    if value is None:
        return ""
    return html_escape(str(value), quote=False).replace("|", "\\|").replace("\r", "&#13;").replace("\n", "&#10;").replace("`", "&#96;").replace("[", "&#91;").replace("]", "&#93;")


def _yn(value: bool) -> str:
    return "Yes" if value else "No"


def _or_dash(value: object) -> str:
    if value is None:
        return "—"
    text = str(value).strip()
    return text if text else "—"


def render_markdown(pack: EvidencePack) -> str:
    parts: list[str] = []
    summary = summarize_evidence_pack(pack)
    parts.append(f"# {_escape(pack.title)}\n")
    parts.extend([
        "| Field | Value |",
        "|---|---|",
        f"| Pack ID | {_escape(pack.pack_id)} |",
        f"| Version | {_escape(pack.pack_version)} |",
        f"| Generated At | {_escape(pack.generated_at)} |",
        f"| Review Status | {_escape(pack.review_status.value)} |",
        f"| Agent | {_escape(pack.agent_overview.agent_name)} |",
        f"| Environment | {_escape(pack.deployment_context.environment.value)} |",
        f"| Owner | {_escape(_or_dash(pack.agent_overview.owner))} |",
        f"| Business Unit | {_escape(_or_dash(pack.agent_overview.business_unit))} |",
        "",
    ])
    parts.append("## 1. Executive Summary\n")
    parts.append(f"**{_escape(pack.agent_overview.agent_name)}** is represented in this evidence pack for the **{_escape(pack.deployment_context.environment.value)}** environment. Business purpose: {_escape(pack.agent_overview.business_purpose)}")
    parts.append("")
    parts.append(f"The pack records **{summary['tool_count']}** tool(s), **{summary['action_count']}** action(s), **{summary['privileged_action_count']}** privileged/review-sensitive action(s), and **{summary['replay_bundle_count']}** replay/reconstruction bundle reference(s).")
    parts.append("")
    if pack.validation_summary:
        v = pack.validation_summary
        parts.append(f"Validation summary: {v.valid_bundle_count} valid bundle(s), {v.invalid_bundle_count} invalid bundle(s), {v.error_count} error(s), {v.warning_count} warning(s).")
        if v.summary:
            parts.append(_escape(v.summary))
    else:
        parts.append("No validation summary recorded.")
    parts.append("")
    parts.append(f"**{summary['open_risk_count']}** open risk(s) ({summary['critical_open_risk_count']} critical)." if summary['open_risk_count'] else "No open risks recorded. Absence of incident records does not prove absence of incidents.")
    if pack.review_status.value == "approved_with_conditions" and any(record.notes and record.notes.strip() for record in pack.review_records):
        parts.append("This evidence pack is approved with conditions; see Section 14 for review notes.")
    parts.append("")

    def kv(title: str, pairs: list[tuple[str, object]]) -> None:
        parts.append(f"## {title}\n")
        for key, value in pairs:
            parts.append(f"**{_escape(key)}:** {_escape(_or_dash(value))}\n")
        parts.append("")

    kv("2. Agent Overview", [("Agent Name", pack.agent_overview.agent_name), ("Description", pack.agent_overview.agent_description), ("Business Purpose", pack.agent_overview.business_purpose), ("Owner", pack.agent_overview.owner), ("Business Unit", pack.agent_overview.business_unit), ("User Population", pack.agent_overview.user_population), ("Lifecycle Stage", pack.agent_overview.lifecycle_stage)])
    kv("3. Deployment Context", [("Environment", pack.deployment_context.environment.value), ("Deployment Name", pack.deployment_context.deployment_name), ("Deployment Date", pack.deployment_context.deployment_date), ("Systems Touched", ", ".join(pack.deployment_context.systems_touched) or None), ("Data Domains", ", ".join(pack.deployment_context.data_domains) or None), ("Geographic Scope", pack.deployment_context.geographic_scope), ("Notes", pack.deployment_context.notes)])

    def table(title: str, heads: list[str], rows: list[list[object]], empty: str) -> None:
        parts.append(f"## {title}\n")
        if rows:
            parts.append("| " + " | ".join(heads) + " |")
            parts.append("|" + "|".join(["---"] * len(heads)) + "|")
            for row in rows:
                parts.append("| " + " | ".join(_escape(_or_dash(value)) for value in row) + " |")
        else:
            parts.append(empty)
        parts.append("")

    table("4. Tool Inventory", ["Tool Name", "Description", "External System", "Data Classification", "Access Mode", "Control Status"], [[t.tool_name, t.description, t.external_system, t.data_classification, t.access_mode, t.control_status.value] for t in pack.tool_inventory], "No tools recorded.")
    table("5. Action Inventory", ["Action Name", "Tool", "Type", "Authority Required", "Review Required", "Reliance Required", "Default Posture", "Control Status"], [[a.action_name, a.tool_name, a.action_type.value, _yn(a.authority_required), _yn(a.review_required), _yn(a.reliance_required), a.default_posture, a.control_status.value] for a in pack.action_inventory], "No actions recorded.")
    if pack.authority_model:
        kv("6. Authority Model", [("Summary", pack.authority_model.summary), ("Authority Scopes", ", ".join(pack.authority_model.authority_scopes) or None), ("Privileged Action Types", ", ".join(t.value for t in pack.authority_model.privileged_action_types) or None), ("Expiration Required", _yn(pack.authority_model.expiration_required)), ("Human Approval Required", _yn(pack.authority_model.human_approval_required)), ("Notes", pack.authority_model.notes)])
    else:
        parts.extend(["## 6. Authority Model\n", "No authority model recorded.", ""])
    table("7. Policy Controls", ["Control Name", "Description", "Status", "Evidence Reference"], [[p.control_name, p.description, p.control_status.value, p.evidence_reference] for p in pack.policy_controls], "No policy controls recorded.")
    table("8. Blocked-Action Summary", ["Action Name", "Action Type", "Tool", "Count", "Reason Summary", "Evidence Reference"], [[b.action_name, b.action_type.value if b.action_type else None, b.tool_name, b.count, b.reason_summary, b.evidence_reference] for b in pack.blocked_actions], "No blocked actions recorded.")
    table("9. Reliance Summary", ["Source Name", "Source Type", "Count", "Scope Summary", "Evidence Reference"], [[r.source_name, r.source_type, r.count, r.scope_summary, r.evidence_reference] for r in pack.reliance_summary], "No reliance records recorded.")
    table("10. Replay Bundle Inventory", ["Bundle ID", "Run ID", "Status", "Generated At", "Signed", "Redacted", "Validation Status", "Evidence Reference"], [[r.bundle_id, r.run_id, r.status, r.generated_at, _yn(r.signed), _yn(r.redacted), r.validation_status, r.evidence_reference] for r in pack.replay_bundles], "No replay bundles recorded.")
    parts.append("## 11. Validation Summary\n")
    if pack.validation_summary:
        v = pack.validation_summary
        parts.append(f"**Valid Bundles:** {v.valid_bundle_count} | **Invalid Bundles:** {v.invalid_bundle_count} | **Errors:** {v.error_count} | **Warnings:** {v.warning_count}\n")
        if v.summary:
            parts.append(f"{_escape(v.summary)}\n")
    else:
        parts.append("No validation summary recorded.")
    parts.append("")
    table("12. Redaction and Export Summary", ["Export ID", "Type", "Redacted Fields", "Generated At", "Intended Recipient", "Evidence Reference"], [[e.export_id, e.export_type, ", ".join(e.redacted_fields), e.generated_at, e.intended_recipient, e.evidence_reference] for e in pack.redaction_exports], "No redaction or export records recorded.")
    table("13. Risk Register", ["Risk ID", "Title", "Severity", "Status", "Mitigation", "Owner", "Evidence Reference"], [[r.risk_id, r.title, r.severity.value, r.status.value, r.mitigation, r.owner, r.evidence_reference] for r in pack.risk_register], "No risks recorded. Missing incident records do not prove that no incidents occurred.")
    table("14. Review Records", ["Reviewer", "Role", "Reviewed At", "Decision", "Notes"], [[r.reviewer, r.reviewer_role, r.reviewed_at, r.decision.value, r.notes] for r in pack.review_records], "No review records recorded. Default review status remains unreviewed/draft unless supplied by an attributable human reviewer.")
    parts.extend(["## 15. Known Limitations\n", "This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, policy controls are sufficient, compliance obligations are satisfied, deployment is approved, controls are operationally effective, or independent audit has occurred. Schema validity and successful reconstruction are review aids only.", ""])
    return "\n".join(parts)
