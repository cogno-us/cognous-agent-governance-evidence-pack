import copy
import pytest
from agent_governance_evidence_pack.w3_atomic_evidence import (
    W3EvidenceContractError, transform_atomic_failure_reconstruction,
    REPLAY_PRODUCER_PROFILE, REPLAY_RUNTIME_REVISION,
)

def sample():
    return dict(bundle_id="synthetic-case",bundle_version="0.2.0",
        producer_profiles=[dict(profile_id=REPLAY_PRODUCER_PROFILE,
            revision=REPLAY_RUNTIME_REVISION,format_name="failure_records_v1")],
        status="reconstruction_partial",
        records=[dict(record_id="failure-1",record_type="atomic_failure",
            producer_profile_id=REPLAY_PRODUCER_PROFILE,
            identifiers={"failure_id":"f-1","effect_id":"e-1","decision_id":"d-1"},
            data={"failure_class":"policy_denial","stage":"pre_dispatch","attempt_id":None})],
        links=[],import_reports=[{"complete":False,
            "findings":[{"category":"missing_dependency","path":"observation"}]}],
        semantics={"external_effect_execution":False,"independent_effect_verification":False})

def test_unresolved_refusal_preserved_without_approval():
    s=sample()
    out=transform_atomic_failure_reconstruction(s)
    assert out["source_counts"]["atomic_failure"]==1
    assert out["source_counts"]["atomic_attempt"]==0
    assert out["approval"]=="not_inferred"
    assert out["delivery_verification"]=="not_independently_verified"
    assert out["retained_records"]==s["records"]

@pytest.mark.parametrize("path,value",[
    ("bundle_version","0.3.0"),("status","completed"),
    ("semantics",{"external_effect_execution":True,"independent_effect_verification":False}),
    ("links",[{"from_record_id":"failure-1","to_record_id":"absent"}]),
])
def test_unsupported_semantics_fail_closed(path,value):
    s=sample()
    s[path]=value
    with pytest.raises(W3EvidenceContractError):
        transform_atomic_failure_reconstruction(s)
