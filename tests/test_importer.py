from __future__ import annotations
import pytest
from agent_governance_evidence_pack.importer import ImportContractError, import_manifest_reconstruction, sha256
from agent_governance_evidence_pack.trace_renderer import render_traceable_markdown

def manifest():
    return {"manifest_id":"refund-manifest","manifest_version":"1.1","agent_name":"RefundAgent","business_purpose":"Review refund requests.","actions":[{"action_id":"refund.issue","tool_name":"refund_api","action_type":"write","description":"Issue a bounded refund.","authority_required":True,"review_requirement":{"required":True},"reliance_requirement":{"required":True},"default_action":"hold"},{"action_id":"refund.lookup","tool_name":"crm","action_type":"read","authority_required":False,"review_requirement":{"required":False},"reliance_requirement":{"required":True},"default_action":"allow"}]}

def proposal(m):
    return {"proposal_id":"proposal-1","run_id":"run-1","actor":"RefundAgent","principal":"customer-ops","manifest_id":m["manifest_id"],"manifest_version":m["manifest_version"],"manifest_digest":sha256(m),"action_id":"refund.issue","adapter_id":"refund_api","target":"refunds/123","payload":{"amount":25,"currency":"USD"},"payload_commitment":sha256({"amount":25,"currency":"USD"}),"requested_permissions":["refund:issue"],"amount":25,"unit":"USD"}

def bundle(m):
    p=proposal(m); binding={k:p[k] for k in ["actor","principal","manifest_id","manifest_version","manifest_digest","action_id","adapter_id","target","payload_commitment","requested_permissions","amount","unit"]}; binding.update({"effect_id":"effect-1","grant_id":"grant-1","grant_revision":"1"})
    return {"reconstruction_bundle_version":"0.2.0","bundle_id":"rb-1","run_id":"run-1","status":"reconstruction_complete","generated_at":"2026-10-05T00:00:00Z","producer_profiles":[{"profile_id":"reconstruction-bundle-0.2.0","repository":"cogno-us/cognous-agent-replay-bundle","revision":"f12648313cedc2cf06145d397fa56cdea18cc800"},{"profile_id":"control-plane-bounded-run","repository":"cogno-us/cognous-agent-control-plane","revision":"283500652d47a692fb0b99a1172a6d5faffbd9a7"},{"profile_id":"moltbot-safe-envelope","repository":"cogno-us/moltbot-safe","revision":"6b0ba1185bcd390f71df947dda349415e4105f5f"}],"records":[{"record_id":"p1","producer_profile_id":"manifest","record_type":"runtime_proposal","source_sequence":0,"source_path":"proposal","identifiers":{"run_id":"run-1","action_id":"refund.issue"},"data":p},{"record_id":"d1","producer_profile_id":"control","record_type":"runtime_decision","source_sequence":1,"source_path":"decisions[0]","identifiers":{"decision_id":"decision-1","effect_id":"effect-1"},"data":{"decision_id":"decision-1","run_id":"run-1","result":"authorized","effect_id":"effect-1","binding":binding}},{"record_id":"e1","producer_profile_id":"moltbot","record_type":"execution_envelope","source_sequence":2,"source_path":"execution_envelope","identifiers":{"decision_id":"decision-1","effect_id":"effect-1"},"data":{"decision_id":"decision-1","effect_id":"effect-1","operation":p}},{"record_id":"cp-a1","producer_profile_id":"control","record_type":"control_plane_attempt_transition","source_sequence":3,"source_path":"attempts[0]","identifiers":{"decision_id":"decision-1","effect_id":"effect-1","attempt_id":"attempt-cp-1"},"data":{"decision_id":"decision-1","effect_id":"effect-1","attempt_id":"attempt-cp-1","acknowledgement":{"received":True}}},{"record_id":"dest-a1","producer_profile_id":"moltbot","record_type":"destination_attempt","source_sequence":4,"source_path":"destination_attempts[0]","identifiers":{"decision_id":"decision-1","effect_id":"effect-1","attempt_id":"attempt-dest-1"},"data":{"decision_id":"decision-1","effect_id":"effect-1","attempt_id":"attempt-dest-1","acknowledgement":{"status":"success"}}},{"record_id":"dest-evt1","producer_profile_id":"moltbot","record_type":"destination_attempt_event","source_sequence":5,"source_path":"destination_attempt_events[0]","identifiers":{"effect_id":"effect-1","attempt_id":"attempt-dest-1"},"data":{"effect_id":"effect-1","attempt_id":"attempt-dest-1","event":"restart_recovered"}},{"record_id":"obs1","producer_profile_id":"moltbot","record_type":"effect_observation","source_sequence":6,"source_path":"observations[0]","identifiers":{"effect_id":"effect-1"},"data":{"effect_id":"effect-1","state":"applied","destination_state":{"amount":25,"unit":"USD"}}},{"record_id":"de1","producer_profile_id":"moltbot","record_type":"destination_effect","source_sequence":7,"source_path":"destination_effects[0]","identifiers":{"effect_id":"effect-1"},"data":{"effect_id":"effect-1","state":"applied","amount":25,"unit":"USD"}}]}

def test_success_counts_executor_attempt_and_structured_ack():
    p=import_manifest_reconstruction(manifest(),bundle(manifest())); c=p.metadata["traceable_import"]["derived_counts"]
    assert p.validation_summary.valid_bundle_count==1; assert c["executor_attempt_count"]==1; assert c["control_plane_attempt_count"]==1; assert c["acknowledgement_counts"]["received"]==2

def test_manifest_requirements_preserved():
    p=import_manifest_reconstruction(manifest(),bundle(manifest())); a={x.action_name:x for x in p.action_inventory}
    assert a["refund.issue"].authority_required is True and a["refund.issue"].review_required is True and a["refund.issue"].reliance_required is True
    assert a["refund.lookup"].review_required is False and a["refund.lookup"].reliance_required is True

def test_actor_tamper_rejected():
    m=manifest(); b=bundle(m); b["records"][0]["data"]["actor"]="OtherAgent"
    with pytest.raises(ImportContractError): import_manifest_reconstruction(m,b)

def test_destination_amount_tamper_rejected():
    m=manifest(); b=bundle(m); b["records"][-1]["data"]["amount"]=999
    with pytest.raises(ImportContractError): import_manifest_reconstruction(m,b)

def test_empty_unversioned_bundle_rejected():
    with pytest.raises(ImportContractError): import_manifest_reconstruction(manifest(),{"records":[]})

def test_hold_binding_rejected():
    m=manifest(); b=bundle(m); b["records"][1]["data"]["result"]="hold"
    with pytest.raises(ImportContractError): import_manifest_reconstruction(m,b)

def test_missing_observation_unavailable_not_success():
    m=manifest(); b=bundle(m); b["records"]=[r for r in b["records"] if r["record_type"] not in {"effect_observation","destination_effect"}]
    p=import_manifest_reconstruction(m,b); c=p.metadata["traceable_import"]["derived_counts"]
    assert c["destination_observation_counts"]=={"unavailable":1}

def test_partial_delivery_visible():
    m=manifest(); b=bundle(m)
    for r in b["records"]:
        if r["record_type"]=="effect_observation": r["data"]["state"]="partial"
    assert import_manifest_reconstruction(m,b).metadata["traceable_import"]["lifecycle_summary"]["destination_observed"]=="partial"

def test_renderer_escapes_html_and_table_breaks():
    m=manifest(); b=bundle(m); m["agent_name"]="<b>Bad|Agent</b>"
    out=render_traceable_markdown(import_manifest_reconstruction(m,b))
    assert "<b>" not in out and "&lt;b&gt;Bad\\|Agent&lt;/b&gt;" in out
