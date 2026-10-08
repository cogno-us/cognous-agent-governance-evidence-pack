"""Exact-branch C8 source -> Replay -> Evidence integration (synthetic local process).

The controller actively performs each stop action and records the observation
at the boundary. This is not a production fleet-stop export.
"""
from __future__ import annotations
import json
import multiprocessing as mp
import tempfile
import time
from pathlib import Path

from engine.c8_source_evidence import LocalStopJournal,export_authority_rows
from engine.local_authority_effect import AtomicAuthorityEffectDestination
from engine.safe_executor import snapshot_envelope
from test_local_authority_effect import setup_tenant_atomic,effect_rows,BASE
from test_w2_stop_recovery import _blocked_worker,_attempt_rows
from agent_replay_bundle.w3_c8_lineage import import_c8_source,C8LineageError
from agent_governance_evidence_pack.w3_c8_lineage import project_c8_lineage

def run(output:Path):
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)
        env,destination,claim=setup_tenant_atomic(path)
        authority=export_authority_rows(destination.path,claim_id=claim.claim_id)
        assert authority["status"]=="source_rows_retained"
        assert authority["rows"]["execution_claims_v1"][0]["tenant_id"]==env.operation.tenant_id
        ctx=mp.get_context("spawn")
        reached=ctx.Event()
        proc=ctx.Process(target=_blocked_worker,
            args=(str(path),env,claim.claim_id,"after_commit",reached))
        proc.start()
        assert reached.wait(10)
        journal=LocalStopJournal(path/"stop-journal.sqlite")
        lifecycle="tenant-local-stop-after-commit"
        effect=env.effect_id
        journal.record(event_id="event-stop-request",sequence=1,lifecycle_id=lifecycle,effect_id=effect,
          kind="stop_requested",observation={"pid":proc.pid,"scope":"single_local_process"})
        proc.terminate()
        proc.join(10)
        assert proc.exitcode is not None
        journal.record(event_id="event-stop-ack",sequence=2,lifecycle_id=lifecycle,effect_id=effect,
          kind="stop_acknowledged",observation={"exitcode":proc.exitcode})
        assert not proc.is_alive()
        journal.record(event_id="event-closure",sequence=3,lifecycle_id=lifecycle,effect_id=effect,
          kind="dispatch_closed",observation={"local_worker_is_alive":False})
        reopened=AtomicAuthorityEffectDestination(path,clock=lambda:BASE)
        effects=effect_rows(reopened);attempts=_attempt_rows(reopened)
        time.sleep(0.02)
        assert effects==effect_rows(reopened) and attempts==_attempt_rows(reopened)
        journal.record(event_id="event-quiescence",sequence=4,lifecycle_id=lifecycle,effect_id=effect,
          kind="quiescence_observed",observation={"local_stores_unchanged":True})
        result=reopened.reconcile_claim(claim.claim_id,snapshot_envelope(env))
        assert result["status"]=="applied" and result["retry_eligible"] is False
        journal.record(event_id="event-reconciliation",sequence=5,lifecycle_id=lifecycle,effect_id=effect,
          kind="destination_reconciled",observation=result)
        stop=journal.export(lifecycle)
        bundle=import_c8_source(authority=authority,stop=stop)
        assert bundle.status=="reconstruction_complete"
        pack=project_c8_lineage(bundle.model_dump(mode="json"))
        assert pack["non_authorizing"] is True
        assert len([r for r in pack["source_records"] if r["record_type"]=="local_stop_event"])==5
        assert pack["reconstruction_status"]=="reconstruction_complete"
        # Real negative mutation tests: changes to retained source bytes fail closed.
        changed=json.loads(json.dumps(authority))
        changed["rows"]["authority_approvals_v1"][0]["tenant_id"]="tenant-adversary"
        try:import_c8_source(authority=changed,stop=stop)
        except C8LineageError:pass
        else:raise AssertionError("tenant substitution accepted")
        changed_stop=json.loads(json.dumps(stop))
        changed_stop["events"][1]["effect_id"]="wrong-effect"
        try:import_c8_source(authority=authority,stop=changed_stop)
        except C8LineageError:pass
        else:raise AssertionError("cross-effect stop accepted")
        # Additional source-derived authority and C7 omissions/mutations.
        for table,field,value in (
            ("authority_grants_v1","revision","stale-grant"),
            ("authority_approvals_v1","proposal_commitment",""),
            ("authority_policies_v1","version","stale-policy"),
            ("authority_policies_v1","tenant_id","wrong-tenant"),
        ):
            mutant=json.loads(json.dumps(authority))
            mutant["rows"][table][0][field]=value
            try:import_c8_source(authority=mutant,stop=stop)
            except C8LineageError:pass
            else:raise AssertionError(f"invalid {table}.{field} accepted")
        missing_stop=json.loads(json.dumps(stop))
        missing_stop["events"].pop(3)
        partial=import_c8_source(authority=authority,stop=missing_stop)
        assert partial.status=="reconstruction_partial"
        assert any(f.code=="C8-STOP" for f in partial.import_reports[0].findings)
        reordered=json.loads(json.dumps(stop))
        reordered["events"][1]["sequence"]=1
        try:import_c8_source(authority=authority,stop=reordered)
        except C8LineageError:pass
        else:raise AssertionError("stop sequence collision accepted")
        output.mkdir(parents=True,exist_ok=True)
        for name,value in (("authority.json",authority),("stop.json",stop),
                           ("reconstruction.json",bundle.model_dump(mode="json")),
                           ("projection.json",pack)):
            (output/name).write_text(json.dumps(value,sort_keys=True,indent=2,default=str)+"\n")
        print("W3 C8: actual tenant source rows + observed local C7 lifecycle -> Replay -> Evidence PASS")

if __name__=="__main__":
    import sys
    run(Path(sys.argv[1]))
