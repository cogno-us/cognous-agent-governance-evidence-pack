"""W3-P4 composed candidate qualification: W2-shaped atomic bytes -> Replay -> Evidence.

These tests exercise real consumer implementations together; producer fixtures are
derived from accepted W2 test expectations, not live destination export.
"""
import pytest

from agent_replay_bundle.w3_atomic_import import (
    W2_RUNTIME_REVISION, import_w2_atomic_failure_history,
    AtomicEvidenceContractError,
)
from agent_governance_evidence_pack.w3_atomic_evidence import (
    transform_atomic_failure_reconstruction, W3EvidenceContractError,
)

def reconstruct(**args):
    return import_w2_atomic_failure_history(
        runtime_revision=W2_RUNTIME_REVISION,effect_id="effect-1",
        decision_id="decision-1",**args)

def test_predispatch_denial_chain_keeps_absent_attempt_and_incomplete_observation():
    row={"failure_id":"failure-1","effect_id":"effect-1","decision_id":"decision-1",
        "attempt_id":None,"failure_class":"policy_denial","reason_code":"local_policy_rejected",
        "stage":"pre_dispatch"}
    bundle=reconstruct(failure_records=[row],attempt_records=[])
    projection=transform_atomic_failure_reconstruction(bundle.model_dump(mode="json"))
    assert projection["source_counts"]=={
        "atomic_failure":1,"atomic_attempt":0,"atomic_observation":0}
    assert projection["reconstruction_status"]=="reconstruction_partial"
    assert projection["approval"]=="not_inferred"
    assert projection["retained_import_findings"][0]["path"]=="observation"

def test_lost_ack_and_reconciliation_do_not_infer_retry():
    row={"failure_id":"failure-2","effect_id":"effect-1","decision_id":"decision-1",
        "attempt_id":"attempt-1","failure_class":"dispatch_error",
        "reason_code":"acknowledgement_unavailable","stage":"post_dispatch"}
    bundle=reconstruct(failure_records=[row],
        attempt_records=[{"attempt_id":"attempt-1","effect_id":"effect-1","decision_id":"decision-1"}],
        observation={"status":"applied","effect_id":"effect-1","retry_eligible":False})
    projection=transform_atomic_failure_reconstruction(bundle.model_dump(mode="json"))
    assert projection["source_counts"]=={
        "atomic_failure":1,"atomic_attempt":1,"atomic_observation":1}
    assert len(projection["retained_links"])==1
    assert projection["delivery_verification"]=="not_independently_verified"
    assert projection["retained_records"][-1]["data"]["retry_eligible"] is False

def test_tampered_source_lineage_rejected_at_replay():
    with pytest.raises(AtomicEvidenceContractError):
        reconstruct(failure_records=[{"failure_id":"failure-3",
            "effect_id":"different-effect","decision_id":"decision-1",
            "stage":"pre_dispatch","failure_class":"authority_hold",
            "reason_code":"current_authority_rejected","attempt_id":None}])

def test_tampered_bundle_lineage_rejected_at_evidence():
    row={"failure_id":"failure-4","effect_id":"effect-1","decision_id":"decision-1",
        "attempt_id":None,"failure_class":"policy_denial",
        "reason_code":"local_policy_rejected","stage":"pre_dispatch"}
    bundle=reconstruct(failure_records=[row],attempt_records=[]).model_dump(mode="json")
    bundle["links"].append({"from_record_id":bundle["records"][0]["record_id"],
        "to_record_id":"invented-attempt","basis":"forged","link_type":"explicit"})
    with pytest.raises(W3EvidenceContractError):
        transform_atomic_failure_reconstruction(bundle)
