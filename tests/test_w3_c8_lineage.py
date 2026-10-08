import pytest
from agent_governance_evidence_pack.w3_c8_lineage import project_c8_lineage,C8EvidenceError
def source():
    return {"bundle_version":"0.2.0","bundle_id":"b","status":"reconstruction_partial",
        "semantics":{"external_effect_execution":False,"independent_effect_verification":False},
        "import_reports":[{"adapter_profile":"c8-retained-sqlite-and-explicit-stop/0.1",
           "findings":[{"code":"C8-STOP","value_state":"unavailable"}]}],
        "records":[{"record_id":"one","record_type":"execution_claims_v1","data":{}}]}
def test_preserves_source_loss():
    out=project_c8_lineage(source())
    assert out["source_findings"][0]["code"]=="C8-STOP"
    assert out["current_execution_authority"]=="not_provided"
def test_rejects_authority_promotion():
    s=source();s["semantics"]["external_effect_execution"]=True
    with pytest.raises(C8EvidenceError):project_c8_lineage(s)
