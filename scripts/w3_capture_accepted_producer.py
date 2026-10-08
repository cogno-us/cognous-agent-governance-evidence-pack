"""Pinned W1/W2 runtime evidence production and consumer qualification.

Invokes accepted Runtime test helpers directly. Fails if expected durable
records are not actually returned by accepted producer code. Never synthesizes
failure rows. Writes stable JSON without transient clocks/UUID assumptions.
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

from agent_replay_bundle.w3_atomic_import import (
    import_w2_atomic_failure_history,W2_RUNTIME_REVISION,
)
from agent_governance_evidence_pack.w3_atomic_evidence import transform_atomic_failure_reconstruction

def run(root: Path):
    from engine.atomic_local_control_plane_executor import AtomicLocalControlPlaneExecutor
    from engine.safe_executor import LocalExecutionPolicy
    from test_local_authority_effect import setup_atomic,policy
    cases={}
    for scenario in ("refusal","lost_ack"):
        with tempfile.TemporaryDirectory() as temp:
            _, env, destination, claim=setup_atomic(Path(temp))
            allowed=policy(env.operation)
            if scenario=="refusal":
                denied=LocalExecutionPolicy(
                    allowed_institutions=allowed.allowed_institutions,
                    allowed_authority_domains=allowed.allowed_authority_domains,
                    allowed_adapters=frozenset({"urn:cognous:adapter:not-this-one"}),
                    allowed_actions=allowed.allowed_actions,
                    allowed_target_prefixes=allowed.allowed_target_prefixes,
                    allowed_units=allowed.allowed_units,
                    max_amount=allowed.max_amount,
                    max_effects=allowed.max_effects,
                )
                result=AtomicLocalControlPlaneExecutor(workflow=object(),destination=destination,policy=denied).execute(
                    envelope=env,claim_id=claim.claim_id)
            else:
                result=AtomicLocalControlPlaneExecutor(workflow=object(),destination=destination,policy=allowed).execute(
                    envelope=env,claim_id=claim.claim_id,simulate="lost_ack",attempt_id="w3-pinned-lost-ack")
            failures=destination.failure_history(env.effect_id)
            assert failures and all(x["effect_id"]==env.effect_id and x["decision_id"]==env.decision_id for x in failures)
            if scenario=="refusal":
                assert result.attempted is False and failures[0]["attempt_id"] is None
                attempts=[]
                obs=None
            else:
                assert result.status=="unknown" and result.attempt_id=="w3-pinned-lost-ack"
                assert failures[0]["attempt_id"]==result.attempt_id
                attempts=[{"attempt_id":result.attempt_id,"effect_id":env.effect_id,"decision_id":env.decision_id}]
                obs=destination.reconcile_claim(claim.claim_id, __import__("engine.safe_executor",fromlist=["snapshot_envelope"]).snapshot_envelope(env))
                assert obs["retry_eligible"] is False
            bundle=import_w2_atomic_failure_history(
                runtime_revision=W2_RUNTIME_REVISION,effect_id=env.effect_id,
                decision_id=env.decision_id,failure_records=failures,
                attempt_records=attempts,observation=obs)
            projection=transform_atomic_failure_reconstruction(bundle.model_dump(mode="json"))
            assert projection["non_authorizing"] is True
            assert projection["source_counts"]["atomic_failure"]==len(failures)
            cases[scenario]={
                "producer_revision":W2_RUNTIME_REVISION,
                "producer_api":"AtomicAuthorityEffectDestination.failure_history",
                "producer_result":{"status":result.status,"attempted":result.attempted,
                    "acknowledged":result.acknowledged,"attempt_id":result.attempt_id},
                "failure_records":failures,
                "attempt_records":attempts,
                "reconciliation":obs,
                "reconstruction_status":bundle.status,
                "transformation_version":projection["transformation_version"],
                "source_counts":projection["source_counts"],
            }
    root.mkdir(parents=True,exist_ok=True)
    (root/"producer-cases.json").write_text(
        json.dumps(cases,sort_keys=True,indent=2,default=str)+"\n",encoding="utf8")
    print("W3 PINNED PRODUCER CASES: "+",".join(cases)+"; consumer projection PASS")

if __name__=="__main__":
    run(Path(sys.argv[1]))
