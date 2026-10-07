"""Accepted Replay / repaired Control Plane compatibility qualification."""
from __future__ import annotations

import copy
from html import unescape
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

import pytest

from agent_governance_evidence_pack import (
    ImportContractError,
    import_manifest_reconstruction,
    render_traceable_markdown,
    validate_evidence_pack,
)

REPLAY_REVISION = "043830b56595cecddfa65c064afd1c0b95e64792"
CONTROL_PLANE_REVISIONS = (
    "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "248d899634d9db3518e831bc7ab568a48733f825",
)
PERSISTENCE_REVISION = CONTROL_PLANE_REVISIONS[1]
EXECUTOR_REVISION = "177354e959cc78c59c1a776f018cfbfbf28c927b"
MANIFEST_REVISION = "46c950bed37fe3812000895430bc0312d29e37ce"


def _git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def _material_trace(markdown: str) -> dict:
    return json.loads(unescape(markdown.split("<pre>")[-1].split("</pre>")[0]))


@pytest.fixture(scope="module")
def repaired_cases(tmp_path_factory):
    replay_root = Path(os.environ["AGEP_ACCEPTED_REPLAY_ROOT"]).resolve()
    cp_root = Path(os.environ["AGEP_PERSISTENCE_CONTROL_PLANE_ROOT"]).resolve()
    executor_root = Path(os.environ["AGEP_ACCEPTED_EXECUTOR_ROOT"]).resolve()
    manifest_path = Path(os.environ["AGEP_MANIFEST_FIXTURE"]).resolve()

    assert _git_head(replay_root) == REPLAY_REVISION
    assert _git_head(cp_root) == PERSISTENCE_REVISION
    assert _git_head(executor_root) == EXECUTOR_REVISION
    assert _git_head(manifest_path.parents[1]) == MANIFEST_REVISION

    sys.path.insert(0, str(replay_root / "src"))
    from agent_replay_bundle import import_bounded_workflow

    generator_spec = importlib.util.spec_from_file_location(
        "agep_store_compat_generator",
        replay_root / "scripts" / "generate_producer_v2_examples.py",
    )
    generator = importlib.util.module_from_spec(generator_spec)
    assert generator_spec.loader is not None
    generator_spec.loader.exec_module(generator)

    manifest = json.loads(manifest_path.read_text())
    captured = []

    def inspect(*args, **kwargs):
        bundle = import_bounded_workflow(*args, **kwargs)
        source = bundle.model_dump(mode="json")
        before = copy.deepcopy(source)
        pack = import_manifest_reconstruction(manifest, source)
        report = validate_evidence_pack(pack)
        assert report.valid, report
        markdown = render_traceable_markdown(pack)
        assert source == before
        assert _material_trace(markdown) == pack.metadata["traceable_import"]
        captured.append(
            {
                "bundle": source,
                "pack": pack,
                "markdown": markdown,
            }
        )
        return bundle

    generator.import_bounded_workflow = inspect
    generated = tmp_path_factory.mktemp("agep-control-plane-store")
    env = os.environ.copy()
    env["ARB_V2_CONTROL_PLANE_ROOT"] = str(cp_root)
    env["ARB_V2_MOLTBOT_ROOT"] = str(executor_root)
    env["ARB_PINNED_MANIFEST_FIXTURE"] = str(manifest_path)

    old_env = os.environ.copy()
    os.environ.update(env)
    try:
        generator.main(generated)
    finally:
        os.environ.clear()
        os.environ.update(old_env)

    sources = json.loads((generated / "producer_v2_sources.json").read_text())
    results = json.loads((generated / "producer_v2_results.json").read_text())
    cases = dict(zip(sources, captured, strict=True))

    # Actual held/no-effect producer path against the repaired Control Plane.
    sys.path[:0] = [str(cp_root / "src"), str(executor_root)]
    os.environ["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(cp_root)
    os.environ["MOLTBOT_SAFE_MANIFEST_FIXTURE"] = str(manifest_path)
    fixture_spec = importlib.util.spec_from_file_location(
        "agep_store_held_fixture", executor_root / "tests" / "test_safe_executor.py"
    )
    fixture = importlib.util.module_from_spec(fixture_spec)
    assert fixture_spec.loader is not None
    fixture_spec.loader.exec_module(fixture)

    with tempfile.TemporaryDirectory() as temporary:
        h, proposal, resolver, workflow, _, destination, _, request = fixture._integrated(
            Path(temporary)
        )
        resolver.statuses[request.operation.grant_id].status = "revoked"
        workflow.records = h.BoundedRecordStore(Path(temporary) / "held.json", "run-1")
        decision = workflow.decide(proposal, now=h.NOW)
        assert decision.result == "hold"
        cp_before = workflow.records.path.read_bytes()

        def rows():
            with sqlite3.connect(destination.path) as db:
                return list(db.iterdump())

        destination_before = rows()
        held_bundle = import_bounded_workflow(
            workflow.records.load().model_dump(mode="json"),
            proposal=proposal.model_dump(mode="json", exclude_none=False),
            control_plane_revision=PERSISTENCE_REVISION,
        ).model_dump(mode="json")
        held_source_before = copy.deepcopy(held_bundle)
        held_pack = import_manifest_reconstruction(manifest, held_bundle)
        assert validate_evidence_pack(held_pack).valid
        held_markdown = render_traceable_markdown(held_pack)
        assert held_bundle == held_source_before
        assert _material_trace(held_markdown) == held_pack.metadata["traceable_import"]
        assert workflow.records.path.read_bytes() == cp_before
        assert rows() == destination_before
        assert destination.effect_count(request.operation.grant_id) == 0
        cases["held"] = {
            "bundle": held_bundle,
            "pack": held_pack,
            "markdown": held_markdown,
        }

    return {"manifest": manifest, "cases": cases, "results": results}


@pytest.mark.parametrize(
    "name",
    [
        "success",
        "lost_ack",
        "restart",
        "rejected_restart",
        "partial",
        "prior_absence",
        "denied",
        "held",
    ],
)
def test_repaired_control_plane_public_import_validate_render(repaired_cases, name):
    case = repaired_cases["cases"][name]
    bundle = copy.deepcopy(case["bundle"])
    before = copy.deepcopy(bundle)
    pack = import_manifest_reconstruction(repaired_cases["manifest"], bundle)
    report = validate_evidence_pack(pack)
    markdown = render_traceable_markdown(pack)
    assert report.valid
    assert bundle == before

    trace = pack.metadata["traceable_import"]
    assert trace["transformation_version"] == "agep-manifest-reconstruction-import/0.3.1"
    assert trace["selected_revisions"]["replay"] == REPLAY_REVISION
    assert trace["selected_revisions"]["control_plane"] == PERSISTENCE_REVISION
    assert trace["supported_revision_sets"]["control_plane"] == list(CONTROL_PLANE_REVISIONS)
    assert PERSISTENCE_REVISION in trace["supported_revision_sets"]["control_plane"]
    assert CONTROL_PLANE_REVISIONS[0] in trace["supported_revision_sets"]["control_plane"]
    if name == "held":
        assert "moltbot_safe" not in trace["selected_revisions"]
    else:
        assert trace["selected_revisions"]["moltbot_safe"] == EXECUTOR_REVISION
    assert _material_trace(markdown) == trace
    assert PERSISTENCE_REVISION in markdown
    assert REPLAY_REVISION in markdown

    life = trace["lifecycle_summary"]
    assert life["current_permission"] == "not_evaluated_from_historical_records"
    assert life["independent_verification"] == "unavailable"
    assert trace["reconstruction_completeness"] == case["bundle"]["status"]
    assert trace["control_evidence_levels"]["tested_in_this_repository"]["status"] == "not_evaluated_during_import"

    if name == "lost_ack":
        assert life["acknowledgement"] == "unknown"
        assert life["destination_observed"] == "applied"
    elif name in {"restart", "rejected_restart"}:
        assert life["destination_observed"] == "applied"
        recs = trace["lifecycle_records"]["reconciliation"]
        assert any(not row["observation_accepted"] for row in recs)
        assert recs[-1]["observation_accepted"] is True
        assert recs[-1]["observation"]["state"] == "applied"
    elif name == "partial":
        assert life["destination_observed"] == "partial"
    elif name == "prior_absence":
        rec = trace["lifecycle_records"]["reconciliation"][-1]
        assert rec["result"] == "observed_absent"
        assert rec["retry_eligible"] is False
        assert life["retry_permission"] == "not_established"
    elif name in {"denied", "held"}:
        assert life["execution_attempted"] == "no"


def test_attempt_namespaces_remain_separate(repaired_cases):
    trace = repaired_cases["cases"]["restart"]["pack"].metadata["traceable_import"]
    cp_ids = {
        row["attempt_id"]
        for row in trace["lifecycle_records"]["control_plane_attempt_transition"]
    }
    executor_ids = {
        row["attempt_id"] for row in trace["lifecycle_records"]["destination_attempt"]
    }
    assert cp_ids and executor_ids and cp_ids.isdisjoint(executor_ids)
    assert trace["derived_counts"]["control_plane_attempt_count"] == len(cp_ids)
    assert trace["derived_counts"]["executor_attempt_count"] == len(executor_ids)


@pytest.mark.parametrize("name", ["success", "lost_ack", "restart", "rejected_restart", "partial", "prior_absence"])
def test_actual_producer_store_evidence_remains_non_effecting(repaired_cases, name):
    result = repaired_cases["results"]["scenarios"][name]
    assert result["records_unchanged"] is True
    assert result["effect_count_before_import"] == result["effect_count_after_import"]


@pytest.mark.parametrize(
    "mutation",
    ["unsupported_revision", "contradictory_profile", "operation_lineage", "attempt_lineage"],
)
def test_repaired_path_rejects_revision_profile_and_lineage_contradictions(repaired_cases, mutation):
    bundle = copy.deepcopy(repaired_cases["cases"]["success"]["bundle"])
    cp_profile = next(
        p
        for p in bundle["producer_profiles"]
        if p["repository"] == "cogno-us/cognous-agent-control-plane"
    )
    if mutation == "unsupported_revision":
        bundle["metadata"]["control_plane_revision"] = "248d899634d9db3518e831bc7ab568a48733f824"
    elif mutation == "contradictory_profile":
        cp_profile["profile_id"] = "control-plane-bounded-run@2ea9528e"
    elif mutation == "operation_lineage":
        effect = next(r for r in bundle["records"] if r["record_type"] == "destination_effect")
        effect["data"]["target"] = "urn:cognous:synthetic-account:substituted"
    else:
        result = next(r for r in bundle["records"] if r["record_type"] == "execution_result")
        result["data"]["attempt_id"] = "missing-attempt"
        result["identifiers"]["attempt_id"] = "missing-attempt"
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(repaired_cases["manifest"], bundle)


@pytest.mark.parametrize("bad", [{}, [], False, "   "])
def test_missing_or_malformed_test_provenance_remains_unavailable(repaired_cases, bad):
    bundle = copy.deepcopy(repaired_cases["cases"]["success"]["bundle"])
    bundle["metadata"]["test_provenance"] = {
        "test_run_id": bad,
        "producer": bad,
        "scope": bad,
        "result": bad,
    }
    pack = import_manifest_reconstruction(repaired_cases["manifest"], bundle)
    trace = pack.metadata["traceable_import"]
    assert trace["control_evidence_levels"]["tested"]["status"] == "unavailable"
    assert any(f["code"] == "T_TEST_PROVENANCE_INVALID" for f in trace["import_findings"])


def test_failed_test_provenance_remains_source_asserted(repaired_cases):
    bundle = copy.deepcopy(repaired_cases["cases"]["success"]["bundle"])
    bundle["metadata"]["test_provenance"] = {
        "test_run_id": "store-compat-failed",
        "producer": "external synthetic harness",
        "scope": "persistence-repair compatibility",
        "result": "failed",
    }
    pack = import_manifest_reconstruction(repaired_cases["manifest"], bundle)
    trace = pack.metadata["traceable_import"]
    levels = trace["control_evidence_levels"]
    assert levels["tested"]["result"] == "failed"
    assert levels["attributable_test_run_evidence"]["status"] == "attributable_source_asserted"
    markdown = render_traceable_markdown(pack)
    assert "| result | failed |" in markdown
    assert "source-supplied" in markdown
