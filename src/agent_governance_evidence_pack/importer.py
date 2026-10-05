"""Traceable Manifest/Reconstruction import with semantic checks."""
from __future__ import annotations

import hashlib, json
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any

from .models import ActionInventoryItem, ActionType, AgentOverview, AuthorityModelSummary, ControlStatus, DeploymentContext, DeploymentEnvironment, EvidencePack, PolicyControlSummary, ReplayBundleInventoryItem, ReviewStatus, ValidationSummary

TRANSFORMATION_VERSION="agep-manifest-reconstruction-import/0.2.1"
CANONICALIZATION_PROFILE="json-canonical-sort-keys-no-whitespace"
MANIFEST_REVISION="46c950bed37fe3812000895430bc0312d29e37ce"
REPLAY_REVISION="f12648313cedc2cf06145d397fa56cdea18cc800"
CONTROL_PLANE_REVISION="283500652d47a692fb0b99a1172a6d5faffbd9a7"
MOLTBOT_SAFE_REVISION="6b0ba1185bcd390f71df947dda349415e4105f5f"
ALVORADA_REVISION="fb3d97938969a89e149e8ff8db2756091d1233fc"
SUPPORTED_MANIFEST_VERSION="1.1"
SUPPORTED_RECONSTRUCTION_VERSION="0.2.0"

class ImportContractError(ValueError): pass

def canonical_bytes(v:Any)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256(v:Any)->str: return "sha256:"+hashlib.sha256(canonical_bytes(v)).hexdigest()
def _obj(v,p):
    if not isinstance(v,dict): raise ImportContractError(f"{p} must be an object")
    return v
def _arr(v,p):
    if not isinstance(v,list): raise ImportContractError(f"{p} must be an array")
    return v
def _first(d,*ks):
    for k in ks:
        if k in d: return d[k]
    return None
def _version(d): return str(_first(d,"manifest_version","version","schema_version")) if _first(d,"manifest_version","version","schema_version") is not None else None
def _mid(d): return str(_first(d,"manifest_id","id","name")) if _first(d,"manifest_id","id","name") is not None else None

def _actions(m):
    for k in ("actions","tool_actions","action_inventory","declared_actions"):
        if isinstance(m.get(k),list): return [x for x in m[k] if isinstance(x,dict)]
    out=[]
    for t in m.get("tools",[]) if isinstance(m.get("tools"),list) else []:
        if isinstance(t,dict):
            for a in t.get("actions",[]) if isinstance(t.get("actions"),list) else []:
                if isinstance(a,dict):
                    b=dict(a); b.setdefault("tool_name",t.get("tool_name") or t.get("name") or t.get("tool_id")); out.append(b)
    return out

def _req(v):
    if v is None: return True,"missing_treated_required"
    if isinstance(v,bool): return v,"bool"
    if isinstance(v,str):
        n=v.lower().strip()
        if n in {"required","require","true","yes","human_review","approval_required"}: return True,"string"
        if n in {"not_required","optional","false","no","none"}: return False,"string"
        return True,"unknown_string_treated_required"
    if isinstance(v,dict):
        for k in ("required","enabled","applies","review_required","reliance_required","authority_required"):
            if k in v: return _req(v[k])[0],f"dict.{k}"
        for k in ("mode","level","default"):
            if k in v: return _req(v[k])[0],f"dict.{k}"
        return True,"dict_without_flag_treated_required"
    return True,"unsupported_shape_treated_required"

def _atype(v):
    try: return ActionType(str(v))
    except Exception: return ActionType.other

def _bver(b):
    v=_first(b,"reconstruction_bundle_version","bundle_version","format_version","version")
    if v is None and isinstance(b.get("metadata"),dict): v=_first(b["metadata"],"reconstruction_bundle_version","bundle_version","format_version")
    return str(v) if v is not None else None

def _record_type(r): return str(r.get("record_type") or "unknown")
def _data(r): return _obj(r.get("data",{}),"record.data")
def _rid(r,i): return str(r.get("record_id") or f"records[{i}]")
def _ident(r,d,*names):
    ids=r.get("identifiers") if isinstance(r.get("identifiers"),dict) else {}
    for n in names:
        if d.get(n) not in (None,""): return str(d[n])
        if ids.get(n) not in (None,""): return str(ids[n])
    return None

def _group(records):
    g=defaultdict(list)
    for i,r in enumerate(records):
        r=_obj(r,f"records[{i}]"); g[_record_type(r)].append((i,r,_data(r)))
    return g

def _norm(v):
    n=str(v or "").lower().strip()
    if n in {"allow","allowed","authorized","grant","granted","approved"}: return "authorized"
    if n in {"hold","held","escalate","pending","requires_review","review"}: return "hold"
    if n in {"deny","denied","block","blocked","reject","rejected"}: return "deny"
    return n or "unknown"
def _dresult(d): return _norm(d.get("result") or d.get("decision") or d.get("authorization") or d.get("status"))
def _binding(d):
    b=d.get("binding") or d.get("authorization_binding") or d.get("effect_binding")
    return b if isinstance(b,dict) else None
def _ack(v):
    if isinstance(v,bool): return "received" if v else "unknown"
    if isinstance(v,str):
        n=v.lower().strip()
        if n in {"received","acknowledged","ack","success","succeeded","ok","true"}: return "received"
        if n in {"lost","missing","timeout","unknown","none","false"}: return "unknown"
        return n
    if isinstance(v,dict):
        if any(bool(v.get(k)) for k in ("received","acknowledged","success","succeeded")): return "received"
        for k in ("state","status","result","acknowledgement_status"):
            if k in v: return _ack(v[k])
    return "unknown"
def _obs(d):
    s=d.get("state") or d.get("observed_state") or d.get("result") or d.get("destination_state_status")
    if isinstance(s,dict): s=s.get("state") or s.get("status")
    n=str(s or "unknown").lower().strip()
    if n in {"applied","present","delivered","success","succeeded"}: return "applied"
    if n in {"partial","partially_applied"}: return "partial"
    if n in {"absent","not_found","not_applied"}: return "absent"
    return n or "unknown"
def _same(a,b,label):
    if a is not None and b is not None and a!=b: raise ImportContractError(f"contradictory retained producer evidence: {label} expected {a!r}, got {b!r}")

def _validate_manifest(m):
    if _version(m)!=SUPPORTED_MANIFEST_VERSION: raise ImportContractError(f"unsupported Manifest version {_version(m)!r}; expected {SUPPORTED_MANIFEST_VERSION}")
    if not _mid(m): raise ImportContractError("manifest identity is required")
    acts=_actions(m)
    if not acts: raise ImportContractError("manifest must declare at least one action")
    f=[]
    for i,a in enumerate(acts):
        if "review_requirement" not in a: f.append({"code":"M_REVIEW_UNKNOWN","severity":"warning","path":f"manifest.actions[{i}].review_requirement","message":"review_requirement absent; treated as required rather than false"})
        if "reliance_requirement" not in a: f.append({"code":"M_RELIANCE_UNKNOWN","severity":"warning","path":f"manifest.actions[{i}].reliance_requirement","message":"reliance_requirement absent; treated as required rather than false"})
    return acts,f

def _validate_headers(m,b):
    acts,findings=_validate_manifest(m)
    if _bver(b)!=SUPPORTED_RECONSTRUCTION_VERSION: raise ImportContractError(f"unsupported Reconstruction Bundle version {_bver(b)!r}; expected {SUPPORTED_RECONSTRUCTION_VERSION}")
    if not isinstance(b.get("records"),list) or not b["records"]: raise ImportContractError("reconstruction bundle must contain a nonempty records array")
    if not isinstance(b.get("producer_profiles"),list) or not b["producer_profiles"]: raise ImportContractError("reconstruction bundle must include producer_profiles")
    trusted={"cogno-us/cognous-agent-replay-bundle":REPLAY_REVISION,"cogno-us/cognous-agent-control-plane":CONTROL_PLANE_REVISION,"cogno-us/moltbot-safe":MOLTBOT_SAFE_REVISION,"cogno-us/cognous-agent-action-manifest":MANIFEST_REVISION,"cogno-us/constitutional-governance-for-institutions":ALVORADA_REVISION}
    for i,p in enumerate(b["producer_profiles"]):
        if not isinstance(p,dict): raise ImportContractError(f"producer_profiles[{i}] must be an object")
        repo,rev=p.get("repository"),p.get("revision")
        if repo in trusted and rev not in (None,trusted[repo]): raise ImportContractError(f"producer_profiles[{i}].revision for {repo} conflicts with pinned supported revision")
    return acts,findings

def _semantic(m,b):
    acts,findings=_validate_headers(m,b); g=_group(b["records"])
    props=g.get("runtime_proposal",[])+g.get("action_proposal",[])
    if len(props)!=1: raise ImportContractError("importer supports exactly one retained proposal/envelope operation")
    _,_,prop=props[0]
    if prop.get("manifest_id") is not None: _same(_mid(m),str(prop.get("manifest_id")),"proposal.manifest_id")
    if prop.get("manifest_version") is not None: _same(_version(m),str(prop.get("manifest_version")),"proposal.manifest_version")
    if prop.get("manifest_digest") is not None: _same(sha256(m),prop.get("manifest_digest"),"proposal.manifest_digest")
    decisions=g.get("runtime_decision",[])+g.get("policy_decision",[])
    if not decisions: raise ImportContractError("reconstruction bundle must retain at least one decision")
    decs={}; effects={}; auth=Counter(); amount_by_effect={}
    for i,r,d in decisions:
        did=_ident(r,d,"decision_id") or f"decision@{i}"; res=_dresult(d); auth[res]+=1; bind=_binding(d)
        if res!="authorized" and bind: raise ImportContractError(f"decision {did} result {res!r} cannot carry an authorization/effect binding")
        if res=="authorized" and not bind: raise ImportContractError(f"decision {did} is authorized but has no binding")
        if bind:
            for field in ("actor","principal","manifest_id","manifest_version","manifest_digest","action_id","adapter_id","target","payload_commitment","requested_permissions"):
                if field in bind and field in prop: _same(prop.get(field),bind.get(field),f"decision {did} binding.{field}")
            eid=str(d.get("effect_id") or bind.get("effect_id") or "")
            if eid: effects[eid]=did; amount_by_effect[eid]=bind.get("amount",prop.get("amount"))
        decs[did]=d
    for typ in ("execution_envelope","destination_attempt","destination_attempt_event","effect_observation","destination_effect","reconciliation","control_plane_attempt","control_plane_attempt_transition"):
        for i,r,d in g.get(typ,[]):
            eid=_ident(r,d,"effect_id") or d.get("effect_id"); did=_ident(r,d,"decision_id") or d.get("decision_id")
            if eid and str(eid) not in effects: raise ImportContractError(f"{typ} {i} has dangling effect_id {eid}")
            if did and str(did) not in decs: raise ImportContractError(f"{typ} {i} has dangling decision_id {did}")
            op=d.get("operation") if isinstance(d.get("operation"),dict) else d
            if typ=="execution_envelope":
                for field in ("actor","principal","manifest_id","manifest_version","action_id","adapter_id","target","payload_commitment","amount","unit"):
                    if field in prop and field in op: _same(prop.get(field),op.get(field),f"execution_envelope.operation.{field}")
            if typ in {"destination_effect","effect_observation","reconciliation"} and eid in amount_by_effect:
                dst=d.get("destination_state") if isinstance(d.get("destination_state"),dict) else d
                if isinstance(dst,dict) and dst.get("amount") is not None: _same(amount_by_effect[str(eid)],dst.get("amount"),f"{typ}.amount")
            if typ=="reconciliation" and d.get("result")=="applied" and isinstance(d.get("observation"),dict) and _obs(d["observation"])!="applied": raise ImportContractError("reconciliation applied result conflicts with embedded observation")
    return acts,findings,auth

def _make_actions(acts,findings):
    out=[]
    for i,a in enumerate(acts):
        auth,asrc=_req(a.get("authority_required") if "authority_required" in a else a.get("authority_requirement")); rev,rsrc=_req(a.get("review_required") if "review_required" in a else a.get("review_requirement")); rel,relsrc=_req(a.get("reliance_required") if "reliance_required" in a else a.get("reliance_requirement"))
        for code,src in (("AUTH",asrc),("REVIEW",rsrc),("RELIANCE",relsrc)):
            if "missing" in src or "unknown" in src: findings.append({"code":f"M_{code}_UNCERTAIN","severity":"warning","path":f"manifest.actions[{i}]","message":f"{code.lower()} requirement treated as required due to {src}."})
        out.append(ActionInventoryItem(action_name=str(a.get("action_name") or a.get("action_id") or a.get("name") or f"action_{i}"),tool_name=str(a.get("tool_name") or a.get("tool_id") or a.get("adapter_id") or "unknown_tool"),action_type=_atype(a.get("action_type") or a.get("type")),description=a.get("description"),authority_required=auth,review_required=rev,reliance_required=rel,default_posture=str(a.get("default_action") or a.get("default_posture") or "unknown"),control_status=ControlStatus.implemented if (auth or rev or rel) else ControlStatus.partial))
    return out

def _counts(b,auth):
    g=_group(b["records"]); prop=set(); dec=set(); eff=set(); cp=set(); ex=set(); trans=0; obs=Counter(); ack=Counter()
    for typ,entries in g.items():
        for i,r,d in entries:
            if typ in {"runtime_proposal","action_proposal"}: prop.add(_ident(r,d,"proposal_id","action_id","correlation_id") or _rid(r,i))
            if typ in {"runtime_decision","policy_decision"}: dec.add(_ident(r,d,"decision_id") or _rid(r,i)); eid=_ident(r,d,"effect_id") or d.get("effect_id"); eff.add(str(eid)) if eid else None
            if typ in {"control_plane_attempt","control_plane_attempt_transition"}: cp.add("cp:"+(_ident(r,d,"attempt_id") or _rid(r,i))); trans+=1; ack[_ack(d.get("acknowledgement") or d.get("ack") or d.get("acknowledgement_status"))]+=1
            if typ=="destination_attempt": ex.add("dest:"+(_ident(r,d,"attempt_id","destination_attempt_id") or _rid(r,i))); ack[_ack(d.get("acknowledgement") or d.get("ack") or d.get("acknowledgement_status"))]+=1
            if typ=="destination_attempt_event": trans+=1
            if typ in {"effect_observation","destination_effect","reconciliation"}: obs[_obs(d)]+=1
    return {"proposal_count":len(prop),"decision_count":len(dec),"distinct_effect_count":len(eff),"control_plane_attempt_count":len(cp),"executor_attempt_count":len(ex),"attempt_transition_record_count":trans,"authorization_granted_count":auth.get("authorized",0),"authorization_held_count":auth.get("hold",0),"authorization_denied_count":auth.get("deny",0),"destination_observation_counts":dict(sorted(obs.items())) or {"unavailable":1},"acknowledgement_counts":dict(sorted(ack.items())) or {"unknown":1},"coverage_denominators":{"effect_denominator":"distinct authorized effect_id values","control_plane_attempt_denominator":"unique Control Plane attempt IDs","executor_attempt_denominator":"unique destination_attempt IDs","observation_denominator":"observation/reconciliation records; missing is unavailable"},"counting_rules":["Repeated lifecycle records do not inflate attempt counts.","Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.","Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.","Missing observations are unavailable, not success or failure."]}

def _life(c):
    obs=c["destination_observation_counts"]; ack=c["acknowledgement_counts"]
    dest="applied" if obs.get("applied") else "partial" if obs.get("partial") else "absent" if obs.get("absent") else "unknown" if obs.get("unknown") else "unavailable"
    auth="authorized" if c["authorization_granted_count"] else "held" if c["authorization_held_count"] else "denied" if c["authorization_denied_count"] else "unknown"
    return {"authorization":auth,"execution_attempted":"yes" if c["control_plane_attempt_count"] or c["executor_attempt_count"] else "no","acknowledgement":"received" if ack.get("received") else "unknown","destination_observed":dest,"independent_verification":"unavailable","notes":["Reconstruction completeness does not mean effect completion.","HMAC/shared-secret integrity is not public issuer identity or independent review.","A software-generated pack cannot create human approval."]}

def _refs(b): return [{"record_id":_rid(r,i),"record_type":_record_type(r),"producer_profile_id":r.get("producer_profile_id"),"source_path":r.get("source_path") or f"records[{i}]","hash":sha256(r)} for i,r in enumerate(b.get("records",[])) if isinstance(r,dict)]

def import_manifest_reconstruction(manifest:dict[str,Any], reconstruction_bundle:dict[str,Any], *, title:str|None=None)->EvidencePack:
    m=deepcopy(_obj(manifest,"manifest")); b=deepcopy(_obj(reconstruction_bundle,"reconstruction_bundle"))
    acts,findings,auth=_semantic(m,b); counts=_counts(b,auth); actions=_make_actions(acts,findings)
    gen=str(b.get("generated_at") or (b.get("metadata",{}) if isinstance(b.get("metadata"),dict) else {}).get("source_generated_at") or "unavailable")
    if gen=="unavailable": findings.append({"code":"T_GENERATED_AT_UNAVAILABLE","severity":"warning","path":"reconstruction_bundle.generated_at","message":"No source generation timestamp supplied; importer did not invent one."})
    bundle_id=str(b.get("bundle_id") or b.get("reconstruction_bundle_id") or b.get("run_id") or "unknown_bundle")
    pack_id="agep-"+sha256({"manifest":sha256(m),"bundle":sha256(b),"transformation":TRANSFORMATION_VERSION})[7:23]
    pack=EvidencePack(pack_id=pack_id,pack_version="0.2.0",title=title or "Traceable Agent Governance Evidence Pack",generated_at=gen,review_status=ReviewStatus.draft,agent_overview=AgentOverview(agent_name=str(m.get("agent_name") or (m.get("agent",{}) if isinstance(m.get("agent"),dict) else {}).get("name") or "ImportedAgent"),business_purpose=str(m.get("business_purpose") or m.get("purpose") or "Imported from Manifest and Reconstruction Bundle; business purpose unavailable."),owner=m.get("owner") if isinstance(m.get("owner"),str) else None,business_unit=m.get("business_unit") if isinstance(m.get("business_unit"),str) else None),deployment_context=DeploymentContext(environment=DeploymentEnvironment.other,deployment_name=str(m.get("deployment_name") or "imported"),systems_touched=[],data_domains=[],notes="Generated from retained producer artifacts; does not establish deployment approval or operational effectiveness."),action_inventory=actions,authority_model=AuthorityModelSummary(summary="Authority evidence imported from retained runtime records. This is not a grant or approval.",authority_scopes=[],privileged_action_types=sorted({a.action_type for a in actions if a.authority_required},key=lambda x:x.value),expiration_required=True,human_approval_required=any(a.review_required for a in actions),notes="Authority Context profile references remain distinct from context-instance identifiers."),policy_controls=[PolicyControlSummary(control_name="Manifest declaration",description="Actions and requirements imported from Manifest v1.1.",control_status=ControlStatus.implemented,evidence_reference="metadata.traceable_import.input_artifacts[manifest]"),PolicyControlSummary(control_name="Reconstruction semantic checks",description="Proposal, decision, envelope, destination and observation evidence checked for supported records.",control_status=ControlStatus.implemented,evidence_reference="metadata.traceable_import.source_record_refs"),PolicyControlSummary(control_name="Independent operational verification",description="No independent real-world effect verification supplied.",control_status=ControlStatus.planned,evidence_reference="metadata.traceable_import.lifecycle_summary.independent_verification")],replay_bundles=[ReplayBundleInventoryItem(bundle_id=bundle_id,run_id=str(b.get("run_id") or ""),status=str(b.get("status") or "unknown"),generated_at=None if gen=="unavailable" else gen,signed=False,redacted=False,validation_status="semantically_valid",evidence_reference="metadata.traceable_import.source_record_refs")],validation_summary=ValidationSummary(valid_bundle_count=1,invalid_bundle_count=0,warning_count=len([f for f in findings if f.get("severity")=="warning"]),error_count=0,summary="Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit."),metadata={"traceable_import":{"transformation_version":TRANSFORMATION_VERSION,"canonicalization_profile":CANONICALIZATION_PROFILE,"supported_revisions":{"manifest":MANIFEST_REVISION,"replay":REPLAY_REVISION,"control_plane":CONTROL_PLANE_REVISION,"moltbot_safe":MOLTBOT_SAFE_REVISION,"alvorada":ALVORADA_REVISION},"input_artifacts":[{"artifact_role":"manifest","artifact_id":_mid(m),"version":_version(m),"hash":sha256(m),"trusted_revision":MANIFEST_REVISION},{"artifact_role":"reconstruction_bundle","artifact_id":bundle_id,"version":_bver(b),"hash":sha256(b),"trusted_revision":REPLAY_REVISION}],"source_record_refs":_refs(b),"derived_counts":counts,"lifecycle_summary":_life(counts),"control_evidence_levels":{"declared":{"status":"present","evidence":["manifest"]},"implemented":{"status":"supported_by_records","evidence":["reconstruction_bundle.records"]},"tested":{"status":"synthetic_environment_only","evidence":["tests/test_importer.py"]},"operationally_observed":{"status":"unavailable","evidence":[]},"independently_audited":{"status":"unavailable","evidence":[]}},"import_findings":findings,"manual_assessments":[],"unresolved_issues":[{"code":"U_INDEPENDENT_VERIFICATION_UNAVAILABLE","severity":"warning","message":"Destination observation is producer-retained unless independent verifier evidence is supplied."},{"code":"U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED","severity":"warning","message":"Synthetic import success cannot support operational effectiveness or deployment approval."}],"outcomes_and_burden":{"unresolved_delivery":"see lifecycle_summary.destination_observed","incidents":"unavailable_not_zero","remedies":"unavailable","measured_latency":"not_measured","human_review_effort":"not_measured","error_prevention":"not_measured","error_correction":"not_measured","comparison_baseline_reference":"unavailable"}}})
    return pack
