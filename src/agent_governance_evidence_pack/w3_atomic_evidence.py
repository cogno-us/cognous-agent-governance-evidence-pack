"""W3 C8 bounded atomic failure-history evidence projection.

Separate from legacy Evidence Pack schema 0.2.0 and transformation 0.3.2.
No control result, authorization, or independent effect assurance is inferred.
"""
from __future__ import annotations

from typing import Any

TRANSFORMATION_VERSION = "agep-w3-atomic-failure-trace/0.1.0"
REPLAY_RUNTIME_REVISION = "bd398f16c4cee329d2d0213afc3236ca9232d29e"
REPLAY_PRODUCER_PROFILE = "local-atomic-w2-failure-history@bd398f16"
RECONSTRUCTION_VERSION = "0.2.0"

class W3EvidenceContractError(ValueError):
    pass

def transform_atomic_failure_reconstruction(bundle: dict[str, Any]) -> dict[str, Any]:
    """Preserve exact producer semantics; project into non-authorizing review data.

    Returns a supplemental trace, not a validated EvidencePack or approval.
    """
    if not isinstance(bundle, dict) or bundle.get("bundle_version") != RECONSTRUCTION_VERSION:
        raise W3EvidenceContractError("unsupported reconstruction version")
    profiles=bundle.get("producer_profiles")
    if not isinstance(profiles,list) or len(profiles)!=1 or not isinstance(profiles[0],dict):
        raise W3EvidenceContractError("exactly one atomic producer profile required")
    p=profiles[0]
    if p.get("profile_id")!=REPLAY_PRODUCER_PROFILE or p.get("revision")!=REPLAY_RUNTIME_REVISION:
        raise W3EvidenceContractError("unsupported producer profile or revision")
    if p.get("format_name")!="failure_records_v1":
        raise W3EvidenceContractError("unsupported source evidence generation")
    records=bundle.get("records")
    if not isinstance(records,list):
        raise W3EvidenceContractError("records must be array")
    byid={}
    for r in records:
        if not isinstance(r,dict):
            raise W3EvidenceContractError("record not object")
        rid=r.get("record_id")
        if not isinstance(rid,str) or not rid or rid in byid:
            raise W3EvidenceContractError("duplicate or missing source record id")
        if r.get("producer_profile_id")!=REPLAY_PRODUCER_PROFILE:
            raise W3EvidenceContractError("mixed producer profile")
        if r.get("record_type") not in ("atomic_failure","atomic_attempt","atomic_observation"):
            raise W3EvidenceContractError("unsupported atomic source record")
        byid[rid]=r
    links=bundle.get("links",[])
    if not isinstance(links,list):
        raise W3EvidenceContractError("links must be array")
    for l in links:
        if not isinstance(l,dict) or l.get("from_record_id") not in byid or l.get("to_record_id") not in byid:
            raise W3EvidenceContractError("dangling source lineage link")
        if byid[l["from_record_id"]]["record_type"]!="atomic_failure" or byid[l["to_record_id"]]["record_type"]!="atomic_attempt":
            raise W3EvidenceContractError("contradictory failure-to-attempt lineage")
    semantics=bundle.get("semantics",{})
    if not isinstance(semantics,dict) or semantics.get("external_effect_execution") is not False or semantics.get("independent_effect_verification") is not False:
        raise W3EvidenceContractError("non-authorizing replay semantics required")
    status=bundle.get("status")
    if status not in ("reconstruction_complete","reconstruction_partial","incomplete","redacted"):
        raise W3EvidenceContractError("unknown reconstruction completeness")
    reports=bundle.get("import_reports")
    if not isinstance(reports,list) or len(reports)!=1 or not isinstance(reports[0],dict):
        raise W3EvidenceContractError("source import report required")
    counts={key:sum(r["record_type"]==key for r in records) for key in
        ("atomic_failure","atomic_attempt","atomic_observation")}
    return {
        "transformation_version":TRANSFORMATION_VERSION,
        "source_bundle_id":bundle.get("bundle_id"),
        "source_producer_revision":REPLAY_RUNTIME_REVISION,
        "source_producer_profile":REPLAY_PRODUCER_PROFILE,
        "reconstruction_status":status,
        "retained_records":records,
        "retained_links":links,
        "retained_import_findings":reports[0].get("findings",[]),
        "source_counts":counts,
        "delivery_verification":"not_independently_verified",
        "current_execution_authority":"not_provided",
        "tenant_authorization_verification":"not_performed",
        "approval":"not_inferred",
        "non_authorizing":True,
    }
