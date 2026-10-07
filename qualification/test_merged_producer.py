"""Accepted Replay / repaired Control Plane compatibility qualification."""
from __future__ import annotations

import copy
from html import unescape
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from agent_governance_evidence_pack import (
    ImportContractError,
    import_manifest_reconstruction,
    render_traceable_markdown,
    validate_evidence_pack,
)

REPLAY_REVISION = "459e4ba62fca49364aebb0050cd5fb2dd5a71bfa"
CONTROL_PLANE_REVISIONS = (
    "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "d3dadee70bd319812b207389ab1e0f6efe511916",
)
PERSISTENCE_REVISION = CONTROL_PLANE_REVISIONS[1]
EXECUTOR_REVISION = "c3c3ee7188b9367cf70b08074b9c40a5c70c94ac"
MANIFEST_REVISION = "46c950bed37fe3812000895430bc0312d29e37ce"


def _material_trace(markdown: str) -> dict:
    return json.loads(unescape(markdown.split("<pre>")[-1].split("</pre>")[0]))


@pytest.fixture(scope="module")
def repaired_cases(tmp_path_factory):
    required_env = (
        "AGEP_ACCEPTED_REPLAY_ROOT",
        "AGEP_PERSISTENCE_CONTROL_PLANE_ROOT",
        "AGEP_ACCEPTED_EXECUTOR_ROOT",
        "AGEP_MANIFEST_FIXTURE",
    )
    if not all(os.environ.get(name) for name in required_env):
        pytest.fail("accepted merged producer checkouts not configured")
    output = tmp_path_factory.mktemp("agep-control-plane-store")
    subprocess.run(
        [
            sys.executable,
            "scripts/qualify_merged_producer.py",
            str(output),
        ],
        check=True, timeout=120,
        env=os.environ.copy(),
    )
    data = json.loads((output / "cases.json").read_text())
    data["results"] = json.loads((output / "results.json").read_text())
    return data


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
    assert trace["transformation_version"] == "agep-manifest-reconstruction-import/0.3.2"
    assert trace["selected_revisions"]["replay"] == REPLAY_REVISION
    assert trace["selected_revisions"]["control_plane"] == PERSISTENCE_REVISION
    supported_cp = trace["supported_revision_sets"]["control_plane"]
    assert CONTROL_PLANE_REVISIONS[0] in supported_cp
    assert CONTROL_PLANE_REVISIONS[1] in supported_cp
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
    assert (
        trace["control_evidence_levels"]["tested_in_this_repository"]["status"]
        == "not_evaluated_during_import"
    )

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
    trace = import_manifest_reconstruction(
        repaired_cases["manifest"], repaired_cases["cases"]["restart"]["bundle"]
    ).metadata["traceable_import"]
    cp_ids = {
        row["attempt_id"]
        for row in trace["lifecycle_records"]["control_plane_attempt_transition"]
    }
    executor_ids = {
        row["attempt_id"]
        for row in trace["lifecycle_records"]["destination_attempt"]
    }
    assert cp_ids and executor_ids and cp_ids.isdisjoint(executor_ids)
    assert trace["derived_counts"]["control_plane_attempt_count"] == len(cp_ids)
    assert trace["derived_counts"]["executor_attempt_count"] == len(executor_ids)


@pytest.mark.parametrize(
    "name",
    ["success", "lost_ack", "restart", "rejected_restart", "partial", "prior_absence"],
)
def test_actual_producer_store_evidence_remains_non_effecting(repaired_cases, name):
    result = repaired_cases["results"]["scenarios"][name]
    assert result["records_unchanged"] is True
    assert result["effect_count_before_import"] == result["effect_count_after_import"]


def test_dependency_combination_is_explicit_and_excludes_odes_gax(repaired_cases):
    q = repaired_cases["results"]["evidence_pack_qualification"]
    assert q["replay_revision"] == REPLAY_REVISION
    assert q["control_plane_revision"] == PERSISTENCE_REVISION
    assert q["executor_revision"] == EXECUTOR_REVISION
    assert q["producer_profile"] == "2.0.0"
    assert q["execution_envelope"] == "0.2.0"
    assert q["reconstruction_bundle"] == "0.2.0"
    assert q["odes_gax"] == "not exercised on this repaired-Control-Plane path"


@pytest.mark.parametrize(
    "mutation",
    ["unsupported_revision", "contradictory_profile", "operation_lineage", "attempt_lineage"],
)
def test_repaired_path_rejects_revision_profile_and_lineage_contradictions(
    repaired_cases, mutation
):
    bundle = copy.deepcopy(repaired_cases["cases"]["success"]["bundle"])
    cp_profile = next(
        p
        for p in bundle["producer_profiles"]
        if p["repository"] == "cogno-us/cognous-agent-control-plane"
    )
    if mutation == "unsupported_revision":
        bundle["metadata"]["control_plane_revision"] = (
            "248d899634d9db3518e831bc7ab568a48733f824"
        )
    elif mutation == "contradictory_profile":
        cp_profile["profile_id"] = "control-plane-bounded-run@2ea9528e"
    elif mutation == "operation_lineage":
        effect = next(
            r for r in bundle["records"] if r["record_type"] == "destination_effect"
        )
        effect["data"]["target"] = "urn:cognous:synthetic-account:substituted"
    else:
        result = next(
            r for r in bundle["records"] if r["record_type"] == "execution_result"
        )
        result["data"]["attempt_id"] = "missing-attempt"
        result["identifiers"]["attempt_id"] = "missing-attempt"
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(repaired_cases["manifest"], bundle)


@pytest.mark.parametrize("bad", [{}, [], False, "   "])
def test_missing_or_malformed_test_provenance_remains_unavailable(
    repaired_cases, bad
):
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
    assert any(
        finding["code"] == "T_TEST_PROVENANCE_INVALID"
        for finding in trace["import_findings"]
    )


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
    assert (
        levels["attributable_test_run_evidence"]["status"]
        == "attributable_source_asserted"
    )
    markdown = render_traceable_markdown(pack)
    assert "| result | failed |" in markdown
    assert "source-supplied" in markdown


def test_historical_v2_selected_revision_is_not_relabelled(repaired_cases):
    bundle = copy.deepcopy(repaired_cases["cases"]["success"]["bundle"])
    old_cp = CONTROL_PLANE_REVISIONS[0]
    bundle["metadata"]["control_plane_revision"] = old_cp
    cp_profile = next(
        p
        for p in bundle["producer_profiles"]
        if p["repository"] == "cogno-us/cognous-agent-control-plane"
    )
    cp_profile["revision"] = old_cp
    cp_profile["profile_id"] = "control-plane-bounded-run@2ea9528e"
    contract = bundle["metadata"]["moltbot_producer_contract"]
    contract["control_plane_revision"] = old_cp
    bundle["import_reports"][0]["source_revision"] = old_cp
    bundle["import_reports"][0]["adapter_profile"] = "control-plane-bounded-run@2ea9528e"
    for record in bundle["records"]:
        if record["producer_profile_id"] == "control-plane-bounded-run@d3dadee7":
            record["producer_profile_id"] = "control-plane-bounded-run@2ea9528e"
            record["record_id"] = record["record_id"].replace(
                "control-plane-bounded-run@d3dadee7",
                "control-plane-bounded-run@2ea9528e",
            )
    # This hand-edited bundle should fail closed rather than be silently relabelled.
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(repaired_cases["manifest"], bundle)
