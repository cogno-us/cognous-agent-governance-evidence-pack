"""Renderer addendum for traceable imported evidence packs."""
from __future__ import annotations
from html import escape as html_escape
from .models import EvidencePack
from .renderer import render_markdown

def _escape(v: object) -> str:
    if v is None: return ""
    return html_escape(str(v), quote=False).replace("|", "\\|")
def _or_dash(v: object) -> str: return "—" if v in (None,"",[],{}) else str(v)

def render_traceable_markdown(pack: EvidencePack) -> str:
    base=render_markdown(pack); trace=pack.metadata.get("traceable_import") if isinstance(pack.metadata,dict) else None
    if not isinstance(trace,dict): return base
    parts=[base.rstrip(),"","## 16. Traceability and Import Provenance",""]
    parts.append("This section is generated from `metadata.traceable_import`. It is review support only. It does not certify deployment approval, compliance, operational effectiveness, or independent audit."); parts.append("")
    def table(title,heads,rows,empty):
        parts.append(f"### {title}"); parts.append("")
        if rows:
            parts.append("| "+" | ".join(heads)+" |"); parts.append("|"+"|".join(["---"]*len(heads))+"|")
            for r in rows: parts.append("| "+" | ".join(_escape(_or_dash(x)) for x in r)+" |")
        else: parts.append(empty)
        parts.append("")
    arts=trace.get("input_artifacts") if isinstance(trace.get("input_artifacts"),list) else []
    table("Input artifacts",["Role","Artifact ID","Version","Hash","Trusted Revision"],[[a.get("artifact_role"),a.get("artifact_id"),a.get("version"),a.get("hash"),a.get("trusted_revision")] for a in arts if isinstance(a,dict)],"No input artifact metadata recorded.")
    parts += ["### Transformation","","| Field | Value |","|---|---|",f"| Transformation Version | {_escape(trace.get('transformation_version'))} |",f"| Canonicalization Profile | {_escape(trace.get('canonicalization_profile'))} |",""]
    c=trace.get("derived_counts") if isinstance(trace.get("derived_counts"),dict) else {}; rows=[]
    for k in ["proposal_count","decision_count","distinct_effect_count","control_plane_attempt_count","executor_attempt_count","attempt_transition_record_count","authorization_granted_count","authorization_held_count","authorization_denied_count"]:
        if k in c: rows.append([k,c[k]])
    for k,v in sorted((c.get("destination_observation_counts") or {}).items()): rows.append([f"destination_observation.{k}",v])
    for k,v in sorted((c.get("acknowledgement_counts") or {}).items()): rows.append([f"acknowledgement.{k}",v])
    table("Derived counts",["Count","Value"],rows,"No derived counts recorded.")
    if isinstance(c.get("counting_rules"),list):
        parts.append("Counting rules:"); [parts.append(f"- {_escape(r)}") for r in c["counting_rules"]]; parts.append("")
    life=trace.get("lifecycle_summary") if isinstance(trace.get("lifecycle_summary"),dict) else {}
    table("Lifecycle and effect status",["Dimension","Value"],[[k,life.get(k)] for k in ["authorization","execution_attempted","acknowledgement","destination_observed","independent_verification"] if k in life],"No lifecycle summary recorded.")
    if isinstance(life.get("notes"),list):
        for n in life["notes"]: parts.append(f"- {_escape(n)}")
        parts.append("")
    levels=trace.get("control_evidence_levels") if isinstance(trace.get("control_evidence_levels"),dict) else {}
    table("Control evidence levels",["Level","Status","Evidence"],[[k,v.get("status"),", ".join(str(x) for x in v.get("evidence",[])) if isinstance(v,dict) and isinstance(v.get("evidence"),list) else ""] for k,v in levels.items() if isinstance(v,dict)],"No control evidence level metadata recorded.")
    findings=trace.get("import_findings") if isinstance(trace.get("import_findings"),list) else []
    table("Import findings and unresolved limitations",["Code","Severity","Path/Source","Message"],[[f.get("code"),f.get("severity"),f.get("path") or f.get("source"),f.get("message")] for f in findings if isinstance(f,dict)],"No import findings recorded.")
    unresolved=trace.get("unresolved_issues") if isinstance(trace.get("unresolved_issues"),list) else []
    table("Unresolved issues",["Code","Severity","Message"],[[u.get("code"),u.get("severity"),u.get("message")] for u in unresolved if isinstance(u,dict)],"No unresolved issues recorded.")
    refs=trace.get("source_record_refs") if isinstance(trace.get("source_record_refs"),list) else []
    table("Supporting source-record references",["Record ID","Type","Producer Profile","Source Path","Hash"],[[r.get("record_id"),r.get("record_type"),r.get("producer_profile_id"),r.get("source_path"),r.get("hash")] for r in refs[:50] if isinstance(r,dict)],"No source-record references recorded.")
    if len(refs)>50: parts += [f"Only the first 50 of {_escape(len(refs))} source-record references are rendered. Full references remain in JSON metadata.",""]
    return "\n".join(parts).rstrip()+"\n"
