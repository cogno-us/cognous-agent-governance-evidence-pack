from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

from agent_governance_evidence_pack import (
    ImportContractError,
    import_manifest_reconstruction,
    render_traceable_markdown,
    validate_evidence_pack,
)
from agent_replay_bundle.importers import import_bounded_workflow


MOLTBOT_REVISION = "1d308faf664c504b6e310db3c7a310153ef7b067"
REPLAY_REVISION = "f63ce914504dd06813c4ccd199b0570dbd8dd427"
ODES_REVISION = "cba83a1c06f718a8afd76178f36e5cc15896347d"
PROFILE_ID = "urn:cognous:profiles:moltbot-safe-executor-producer"
PROFILE_VERSION = "1.0.0"


def _root(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} not configured")
    path = Path(value)
    if not path.exists():
        pytest.skip(f"{name} does not exist: {path}")
    return path


def _load_moltbot_fixture():
    cp_root = _root("AGEP_PINNED_CONTROL_PLANE_ROOT")
    molt_root = _root("AGEP_PINNED_MOLTBOT_ROOT")
    manifest = _root("AGEP_PINNED_MANIFEST_FIXTURE")

    for entry in (str(cp_root / "src"), str(molt_root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    os.environ["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(cp_root)
    os.environ["MOLTBOT_SAFE_MANIFEST_FIXTURE"] = str(manifest)

    helper_path = molt_root / "tests" / "test_safe_executor.py"
    spec = importlib.util.spec_from_file_location(
        "agep_accepted_moltbot_fixture", helper_path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest() -> dict:
    return json.loads(
        _root("AGEP_PINNED_MANIFEST_FIXTURE").read_text(encoding="utf-8")
    )


def _export_sources(workflow, proposal, request, result, destination):
    from engine.producer_contract import export_execution_artifacts

    cp = workflow.records.load().model_dump(mode="json")
    proposal_data = proposal.model_dump(mode="json", exclude_none=False)
    producer = export_execution_artifacts(
        request,
        result,
        destination,
        repository_revision=MOLTBOT_REVISION,
        source_asserted_provenance={
            "test_source": "agep_accepted_profile_integration"
        },
    )
    return cp, proposal_data, producer


def _bundle(cp, proposal, producer):
    return import_bounded_workflow(
        cp,
        proposal=proposal,
        moltbot_export=producer,
    ).model_dump(mode="json")


def _pack(bundle):
    return import_manifest_reconstruction(_manifest(), bundle)


def _integrated(tmp_path):
    h = _load_moltbot_fixture()
    return h, h._integrated(tmp_path)


def _effect_records(bundle: dict) -> list[dict]:
    return [
        r for r in bundle["records"]
        if r["record_type"] == "destination_effect"
    ]


def _assert_public_pack(pack):
    report = validate_evidence_pack(pack)
    assert report.valid is True
    rendered = render_traceable_markdown(pack)
    trace = pack.metadata["traceable_import"]
    contract = trace["executor_producer_contract"]
    assert contract["interface_profile_id"] == PROFILE_ID
    assert contract["interface_profile_version"] == PROFILE_VERSION
    assert contract["repository_revision"] == MOLTBOT_REVISION
    assert contract["provenance"]["source_asserted"]["repository_revision"] == MOLTBOT_REVISION
    assert contract["provenance"]["independently_established"] == []
    assert trace["supported_revisions"]["replay"] == REPLAY_REVISION
    assert trace["supported_revisions"]["moltbot_safe"] == MOLTBOT_REVISION
    assert trace["supported_revisions"]["odes"] == ODES_REVISION
    assert trace["lifecycle_summary"]["independent_verification"] == "unavailable"
    assert "Executor producer contract" in rendered
    assert PROFILE_ID in rendered
    assert MOLTBOT_REVISION in rendered
    assert "independently_established_count" in rendered
    assert "does not authenticate the producer" in rendered
    return trace, rendered


def test_actual_accepted_success_import_validate_and_render(tmp_path):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    result = executor.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    assert result.status == "executed"
    cp, p, producer = _export_sources(
        workflow, proposal, request, result, destination
    )
    bundle = _bundle(cp, p, producer)
    pack = _pack(bundle)
    trace, rendered = _assert_public_pack(pack)

    assert trace["lifecycle_summary"]["authorization"] == "authorized"
    assert trace["lifecycle_summary"]["current_permission"] == "not_evaluated_from_historical_records"
    assert trace["lifecycle_summary"]["destination_observed"] == "applied"
    assert trace["derived_counts"]["distinct_effect_count"] == 1
    assert trace["derived_counts"]["executor_attempt_count"] == 1
    assert "applied" in rendered
    for ref in trace["source_record_refs"]:
        assert ref["hash"] == ref["local_content_commitment"]


def test_actual_reconciliation_preserves_one_effect_and_attempt_namespaces(tmp_path):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    first = executor.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    assert first.status == "executed"
    restarted_destination = h.DurableRefundDestination(destination.root)
    restarted = h.PinnedControlPlaneExecutor(
        workflow=workflow,
        destination=restarted_destination,
        policy=h.policy(request.operation),
    )
    reconciled = restarted.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    assert reconciled.status == "reconciled"

    cp, p, producer = _export_sources(
        workflow, proposal, request, reconciled, restarted_destination
    )
    assert producer["attempt_identity"]["namespace"] == "control_plane"
    bundle = _bundle(cp, p, producer)
    pack = _pack(bundle)
    trace, rendered = _assert_public_pack(pack)

    assert trace["derived_counts"]["distinct_effect_count"] == 1
    assert trace["derived_counts"]["destination_effect_count"] == 1
    cp_attempt_id = producer["attempt_identity"]["attempt_id"]
    attributed = [
        r for r in bundle["records"]
        if r["record_type"] == "moltbot_attributed_control_plane_attempt"
    ]
    assert len(attributed) == 1
    assert attributed[0]["data"]["attempt_id"] == cp_attempt_id
    executor_ids = {
        r["data"]["attempt_id"]
        for r in bundle["records"]
        if r["record_type"] == "destination_attempt"
    }
    assert cp_attempt_id not in executor_ids
    assert "Control Plane and executor attempt IDs are separate namespaces" in rendered


@pytest.mark.parametrize("mode,expected_ack,expected_observed", [
    ("lost_ack", "unknown", "applied"),
    ("partial", "unknown", "partial"),
])
def test_actual_lost_ack_and_partial_preserve_material_lifecycle(
    tmp_path, mode, expected_ack, expected_observed
):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    result = executor.execute(
        envelope=request,
        proposal=proposal,
        decision=decision,
        now=helper.NOW,
        simulate=mode,
    )
    cp, p, producer = _export_sources(
        workflow, proposal, request, result, destination
    )
    bundle = _bundle(cp, p, producer)
    pack = _pack(bundle)
    trace, rendered = _assert_public_pack(pack)

    assert trace["lifecycle_summary"]["acknowledgement"] == expected_ack
    assert trace["lifecycle_summary"]["destination_observed"] == expected_observed
    assert expected_observed in rendered


@pytest.mark.parametrize("state", ["absent", "unknown"])
def test_actual_historical_absent_unknown_preserve_unavailability(tmp_path, state):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated

    if state == "absent":
        result = executor.observe_historical(request)
    else:
        from engine.safe_executor import ExecutionResult

        result = ExecutionResult(
            status="observed",
            decision_id=request.decision_id,
            effect_id=request.effect_id,
            attempt_id=None,
            attempted=False,
            acknowledged=False,
            observed_state="unknown",
            newly_executed=False,
            observation={
                "effect_id": request.effect_id,
                "state": "unknown",
                "destination_state": {},
            },
        )

    cp, p, producer = _export_sources(
        workflow, proposal, request, result, destination
    )
    bundle = _bundle(cp, p, producer)
    assert _effect_records(bundle) == []
    pack = _pack(bundle)
    trace, rendered = _assert_public_pack(pack)

    assert trace["derived_counts"]["distinct_effect_count"] == 1
    assert trace["derived_counts"]["destination_effect_count"] == 0
    assert trace["lifecycle_summary"]["destination_observed"] in {
        state, "unavailable"
    }
    assert trace["lifecycle_summary"]["independent_verification"] == "unavailable"
    assert "unavailable" in rendered


def test_actual_execution_time_denied_has_no_fabricated_effect(tmp_path):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    grant = resolver.contexts[helper.PROFILE]["grant"]
    resolver.statuses[grant["grant_id"]].status = "revoked"

    denied = executor.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    assert denied.status == "denied"
    cp, p, producer = _export_sources(
        workflow, proposal, request, denied, destination
    )
    bundle = _bundle(cp, p, producer)
    assert _effect_records(bundle) == []
    pack = _pack(bundle)
    trace, rendered = _assert_public_pack(pack)

    assert trace["derived_counts"]["destination_effect_count"] == 0
    assert trace["lifecycle_summary"]["current_permission"] == "not_evaluated_from_historical_records"
    assert "Historical authorization is retained evidence" in rendered


def test_actual_control_plane_hold_has_no_execution_or_effect(tmp_path):
    h = _load_moltbot_fixture()
    p = h.proposal()
    resolver = h.resolver_for(p)
    grant = resolver.contexts[h.PROFILE]["grant"]
    resolver.statuses[grant["grant_id"]].status = "revoked"
    workflow = h.BoundedAuthorizationWorkflow(
        manifest=h.manifest(),
        resolver=resolver,
        destination=h.LocalRefundDestination(tmp_path / "cp-placeholder.json"),
        records=h.BoundedRecordStore(tmp_path / "cp-run.json", "run-held"),
    )
    decision = workflow.decide(p, now=h.NOW)
    assert decision.result in {"hold", "deny", "denied"}

    cp = workflow.records.load().model_dump(mode="json")
    bundle = import_bounded_workflow(
        cp,
        proposal=p.model_dump(mode="json", exclude_none=False),
        moltbot_export=None,
    ).model_dump(mode="json")
    assert _effect_records(bundle) == []

    pack = _pack(bundle)
    report = validate_evidence_pack(pack)
    assert report.valid is True
    trace = pack.metadata["traceable_import"]
    rendered = render_traceable_markdown(pack)
    assert trace["derived_counts"]["destination_effect_count"] == 0
    assert trace["lifecycle_summary"]["execution_attempted"] == "no"
    assert trace["control_evidence_levels"]["tested_in_this_repository"]["status"] == "not_evaluated_during_import"
    assert "not_evaluated_during_import" in rendered


@pytest.mark.parametrize("mutation", ["revision", "profile", "attempt_lineage", "operation"])
def test_actual_versioned_tamper_is_rejected(tmp_path, mutation):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    result = executor.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    cp, p, producer = _export_sources(
        workflow, proposal, request, result, destination
    )
    bundle = _bundle(cp, p, producer)

    if mutation == "revision":
        contract = bundle["metadata"]["moltbot_producer_contract"]
        contract["repository_revision"] = "unsupported"
        contract["provenance"]["source_asserted"]["repository_revision"] = "unsupported"
    elif mutation == "profile":
        bundle["metadata"]["moltbot_producer_contract"]["interface_profile_id"] = "urn:unsupported"
    elif mutation == "attempt_lineage":
        result_record = next(
            r for r in bundle["records"] if r["record_type"] == "execution_result"
        )
        result_record["data"]["attempt_id"] = "dangling-attempt"
        result_record["identifiers"]["attempt_id"] = "dangling-attempt"
    else:
        envelope_record = next(
            r for r in bundle["records"] if r["record_type"] == "execution_envelope"
        )
        envelope_record["data"]["operation"]["amount"] = 999.0

    with pytest.raises(ImportContractError):
        _pack(bundle)


@pytest.mark.parametrize("case", ["missing", "malformed", "failed"])
def test_actual_profile_test_provenance_does_not_inflate_assurance(tmp_path, case):
    h, integrated = _integrated(tmp_path)
    helper, proposal, resolver, workflow, decision, destination, executor, request = integrated
    result = executor.execute(
        envelope=request, proposal=proposal, decision=decision, now=helper.NOW
    )
    cp, p, producer = _export_sources(
        workflow, proposal, request, result, destination
    )
    bundle = _bundle(cp, p, producer)

    if case == "missing":
        bundle["metadata"].pop("test_provenance", None)
    elif case == "malformed":
        bundle["metadata"]["test_provenance"] = {
            "test_run_id": [],
            "producer": False,
            "scope": {},
            "result": " ",
        }
    else:
        bundle["metadata"]["test_provenance"] = {
            "test_run_id": "accepted-profile-failed-001",
            "producer": "synthetic accepted-profile integration harness",
            "revision": MOLTBOT_REVISION,
            "scope": "accepted executor -> Replay -> Evidence Pack",
            "result": "failed",
        }

    pack = _pack(bundle)
    report = validate_evidence_pack(pack)
    assert report.valid is True
    trace = pack.metadata["traceable_import"]
    levels = trace["control_evidence_levels"]
    rendered = render_traceable_markdown(pack)

    assert levels["tested_in_this_repository"]["status"] == "not_evaluated_during_import"
    assert trace["lifecycle_summary"]["independent_verification"] == "unavailable"

    if case == "missing":
        assert levels["attributable_test_run_evidence"]["status"] == "unavailable"
        assert levels["tested"]["status"] == "unavailable"
    elif case == "malformed":
        assert levels["attributable_test_run_evidence"]["status"] == "unavailable"
        assert any(
            item["code"] == "T_TEST_PROVENANCE_INVALID"
            for item in trace["import_findings"]
        )
    else:
        assert levels["attributable_test_run_evidence"]["status"] == "attributable_source_asserted"
        assert levels["attributable_test_run_evidence"]["result"] == "failed"
        assert levels["tested"]["result"] == "failed"
        assert "accepted-profile-failed-001" in rendered
        assert "| result | failed |" in rendered
        assert "source-supplied" in rendered
