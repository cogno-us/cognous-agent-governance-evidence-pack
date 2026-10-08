"""C8 trace projection of explicitly retained source records; no authority."""
from __future__ import annotations
from typing import Any

class C8EvidenceError(ValueError):
    pass

def project_c8_lineage(bundle:dict[str,Any])->dict[str,Any]:
    if bundle.get("bundle_version")!="0.2.0":
        raise C8EvidenceError("unsupported Replay version")
    reports=bundle.get("import_reports")
    if not isinstance(reports,list) or len(reports)!=1:
        raise C8EvidenceError("exactly one import report required")
    profile=reports[0].get("adapter_profile","")
    if profile!="c8-retained-sqlite-and-explicit-stop/0.1":
        raise C8EvidenceError("unsupported C8 profile")
    sem=bundle.get("semantics",{})
    if sem.get("external_effect_execution") is not False or sem.get("independent_effect_verification") is not False:
        raise C8EvidenceError("Replay cannot authorize or independently attest")
    rows=bundle.get("records")
    if not isinstance(rows,list):raise C8EvidenceError("missing retained records")
    ids=set()
    for r in rows:
        if not isinstance(r,dict) or r.get("record_id") in ids:
            raise C8EvidenceError("duplicate or invalid source identity")
        ids.add(r["record_id"])
    return {"transformation_version":"agep-c8-lineage/0.1",
       "source_bundle_id":bundle.get("bundle_id"),
       "source_records":rows,
       "source_findings":reports[0].get("findings",[]),
       "reconstruction_status":bundle.get("status"),
       "source_asserted_metadata":bundle.get("metadata",{}),
       "independent_provenance_verification":False,
       "current_execution_authority":"not_provided",
       "stop_authority":"not_provided",
       "non_authorizing":True}
