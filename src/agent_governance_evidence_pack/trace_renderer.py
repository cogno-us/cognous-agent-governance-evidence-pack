"""Renderer addendum for traceable imported evidence packs."""

from __future__ import annotations

from .models import EvidencePack
from .renderer import render_markdown


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|") if value is not None else ""


def _or_dash(value: object) -> str:
    if value in (None, "", [], {}):
        return "—"
    return str(value)


def render_traceable_markdown(pack: EvidencePack) -> str:
    """Render the normal pack plus traceability sections when import metadata exists."""
    base = render_markdown(pack)
    trace = pack.metadata.get("traceable_import") if isinstance(pack.metadata, dict) else None
    if not isinstance(trace, dict):
        return base

    parts: list[str] = [base.rstrip(), "", "## 16. Traceability and Import Provenance", ""]
    parts.append("This section is generated from `metadata.traceable_import`. It is review support only. It does not certify deployment approval, compliance, operational effectiveness, or independent audit.")
    parts.append("")

    parts.append("### Input artifacts")
    parts.append("")
    artifacts = trace.get("input_artifacts") if isinstance(trace.get("input_artifacts"), list) else []
    if artifacts:
        parts.append("| Role | Artifact ID | Version | Hash |")
        parts.append("|---|---|---|---|")
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            parts.append(
                f"| {_escape(artifact.get('artifact_role'))} | {_escape(artifact.get('artifact_id'))} | {_escape(_or_dash(artifact.get('version')))} | `{_escape(artifact.get('hash'))}` |"
            )
    else:
        parts.append("No input artifact metadata recorded.")
    parts.append("")

    parts.append("### Transformation")
    parts.append("")
    parts.append("| Field | Value |")
    parts.append("|---|---|")
    parts.append(f"| Transformation Version | {_escape(trace.get('transformation_version'))} |")
    parts.append(f"| Canonicalization Profile | {_escape(trace.get('canonicalization_profile'))} |")
    parts.append("")

    counts = trace.get("derived_counts") if isinstance(trace.get("derived_counts"), dict) else {}
    parts.append("### Derived counts")
    parts.append("")
    if counts:
        parts.append("| Count | Value |")
        parts.append("|---|---:|")
        for key in [
            "proposal_count", "decision_count", "distinct_effect_count",
            "control_plane_attempt_count", "executor_attempt_count",
            "attempt_transition_record_count", "authorization_granted_count", "authorization_held_count",
        ]:
            if key in counts:
                parts.append(f"| {_escape(key)} | {_escape(counts[key])} |")
        obs = counts.get("destination_observation_counts")
        if isinstance(obs, dict):
            for key, value in sorted(obs.items()):
                parts.append(f"| destination_observation.{_escape(key)} | {_escape(value)} |")
    else:
        parts.append("No derived counts recorded.")
    parts.append("")

    rules = counts.get("counting_rules") if isinstance(counts, dict) else []
    if isinstance(rules, list) and rules:
        parts.append("Counting rules:")
        for rule in rules:
            parts.append(f"- {_escape(rule)}")
        parts.append("")

    lifecycle = trace.get("lifecycle_summary") if isinstance(trace.get("lifecycle_summary"), dict) else {}
    parts.append("### Lifecycle and effect status")
    parts.append("")
    if lifecycle:
        parts.append("| Dimension | Value |")
        parts.append("|---|---|")
        for key in ["authorization", "execution_attempted", "acknowledgement", "destination_observed", "independent_verification"]:
            if key in lifecycle:
                parts.append(f"| {_escape(key)} | {_escape(lifecycle[key])} |")
        notes = lifecycle.get("notes")
        if isinstance(notes, list) and notes:
            parts.append("")
            for note in notes:
                parts.append(f"- {_escape(note)}")
    else:
        parts.append("No lifecycle summary recorded.")
    parts.append("")

    levels = trace.get("control_evidence_levels") if isinstance(trace.get("control_evidence_levels"), dict) else {}
    parts.append("### Control evidence levels")
    parts.append("")
    if levels:
        parts.append("| Level | Status | Evidence |")
        parts.append("|---|---|---|")
        for level, item in levels.items():
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence")
            if isinstance(evidence, list):
                evidence_text = ", ".join(str(v) for v in evidence) or "—"
            else:
                evidence_text = _or_dash(evidence)
            parts.append(f"| {_escape(level)} | {_escape(item.get('status'))} | {_escape(evidence_text)} |")
    else:
        parts.append("No control evidence level metadata recorded.")
    parts.append("")

    findings = trace.get("import_findings") if isinstance(trace.get("import_findings"), list) else []
    parts.append("### Import findings and unresolved limitations")
    parts.append("")
    if findings:
        parts.append("| Code | Severity | Path/Source | Message |")
        parts.append("|---|---|---|---|")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            parts.append(
                f"| {_escape(finding.get('code'))} | {_escape(finding.get('severity'))} | {_escape(_or_dash(finding.get('path') or finding.get('source')))} | {_escape(finding.get('message'))} |"
            )
    else:
        parts.append("No import findings recorded.")
    parts.append("")

    refs = trace.get("source_record_refs") if isinstance(trace.get("source_record_refs"), list) else []
    parts.append("### Supporting source-record references")
    parts.append("")
    if refs:
        parts.append("| Record ID | Type | Producer Profile | Source Path | Hash |")
        parts.append("|---|---|---|---|---|")
        for ref in refs[:50]:
            if not isinstance(ref, dict):
                continue
            parts.append(
                f"| {_escape(ref.get('record_id'))} | {_escape(ref.get('record_type'))} | {_escape(ref.get('producer_profile_id'))} | {_escape(ref.get('source_path'))} | `{_escape(ref.get('hash'))}` |"
            )
        if len(refs) > 50:
            parts.append(f"\nOnly the first 50 of {len(refs)} source-record references are rendered. Full references remain in JSON metadata.")
    else:
        parts.append("No source-record references recorded.")
    parts.append("")

    return "\n".join(parts).rstrip() + "\n"
