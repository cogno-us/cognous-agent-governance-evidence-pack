"""Run in the accepted-generation environment; legacy/GAX runs separately."""
import copy
from html import unescape
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from agent_governance_evidence_pack import (ImportContractError, import_manifest_reconstruction,
    validate_evidence_pack, render_traceable_markdown)
from agent_governance_evidence_pack.importer import sha256


@pytest.fixture(scope="module")
def produced(tmp_path_factory):
    # This suite is an explicit gate, not optional coverage.
    assert os.environ.get("AGEP_V2_ODES_ROOT"), "configure accepted dependency checkouts"
    out = tmp_path_factory.mktemp("agep-v2")
    subprocess.run([sys.executable, "scripts/qualify_producer_v2.py", str(out)], check=True)
    data = json.loads((out / "cases.json").read_text())
    data["results"] = json.loads((out / "results.json").read_text())
    return data


def records(bundle, kind):
    return [r for r in bundle["records"] if r["record_type"] == kind]


@pytest.mark.parametrize("name", ["success", "rejected_wrong_effect", "rejected_stale",
    "rejected_malformed", "rejected_contradictory", "unavailable", "restart",
    "rejected_restart", "lost_ack", "partial", "prior_absence", "denied",
    "historical_applied", "historical_absent", "held"])
def test_actual_lifecycle(produced, name):
    case = produced["cases"][name]
    pack = import_manifest_reconstruction(produced["manifest"], case["bundle"])
    assert validate_evidence_pack(pack).valid
    text = render_traceable_markdown(pack)
    trace = pack.metadata["traceable_import"]
    # Machine-readable full material trace is equivalent, including nulls and rejections.
    rendered = json.loads(unescape(text.split("<pre>")[-1].split("</pre>")[0]))
    assert rendered == trace
    assert trace["input_artifacts"][1]["hash"] == sha256(case["bundle"])
    assert trace["input_artifacts"][1]["artifact_id"] == case["bundle"]["bundle_id"]
    for ref in trace["source_record_refs"]:
        assert ref["hash"] == ref["local_content_commitment"]
    assert pack.validation_summary.warning_count == sum(f["severity"] == "warning" for f in trace["import_findings"])
    life = trace["lifecycle_summary"]
    assert life["retry_permission"] == "not_established"
    assert life["independent_verification"] == "unavailable"
    assert life["destination_observed"] == case["package"]["provenance"]["execution_facts"]["destination_observed"]
    if name.startswith("rejected_") and name != "rejected_restart" or name == "unavailable":
        assert life["reconstruction_status"] == "reconstruction_complete"
        assert life["destination_observed"] == "unknown"
        assert life["acknowledgement"] == "received"
        assert records(case["bundle"], "execution_result")[0]["data"]["observation"] is None
    if name in {"restart", "rejected_restart"}:
        assert life["destination_observed"] == "applied"
        assert any(not r["observation_accepted"] for r in trace["lifecycle_records"]["reconciliation"])
    if name == "lost_ack":
        assert life["acknowledgement"] == "unknown" and life["destination_observed"] == "applied"
    if name == "partial":
        assert life["reconstruction_status"] == "reconstruction_complete" and life["destination_observed"] == "partial"
    if name == "prior_absence":
        assert any(r["result"] == "observed_absent" and r["retry_eligible"] is False for r in trace["lifecycle_records"]["reconciliation"])
    counts = trace["derived_counts"]
    assert counts["control_plane_attempt_count"] == len({r["data"]["attempt_id"] for r in records(case["bundle"], "control_plane_attempt_transition")})
    assert counts["executor_attempt_count"] == len({r["data"]["attempt_id"] for r in records(case["bundle"], "destination_attempt")})
    result = produced["results"]["scenarios"][name]
    assert result["records_unchanged"]
    assert result["effect_count_before_import"] == result["effect_count_after_import"]


@pytest.mark.parametrize('attack', ['promoted_rejection','completeness','effect','decision',
    'attempt','reconciliation','payload','target','amount','profile','revision',
    'copied_reconciliation','history','accepted_observation','missing_rejected'])
def test_adversarial_replay_sources(produced, attack):
    name = 'rejected_wrong_effect' if attack in {'promoted_rejection','completeness','missing_rejected','history'} else 'success'
    bundle = copy.deepcopy(produced['cases'][name]['bundle'])
    execution = records(bundle,'execution_result')[0]['data']
    if attack == 'promoted_rejection':
        rejected = records(bundle,'rejected_executor_observation')[0]['data']
        execution['observation'] = copy.deepcopy(rejected); execution['observed_state'] = 'applied'
    elif attack == 'completeness':
        assert bundle['status'] == 'reconstruction_complete'
        execution['status'] = 'executed'; execution['observed_state'] = 'applied'
    elif attack == 'effect': execution['effect_id'] = 'other'
    elif attack == 'decision': execution['decision_id'] = 'other'
    elif attack == 'attempt': records(bundle,'moltbot_attributed_control_plane_attempt')[0]['data']['attempt_id'] = 'fake'
    elif attack == 'reconciliation': records(bundle,'executor_control_plane_evidence')[0]['data']['reconciliation']['effect_id'] = 'other'
    elif attack in {'payload','target','amount'}:
        records(bundle,'destination_effect')[0]['data'][{'payload':'payload_json'}.get(attack,attack)] = {'payload':'{"fake":true}','target':'other','amount':999}[attack]
    elif attack == 'profile': bundle['metadata']['moltbot_producer_contract']['interface_profile_version'] = '9.0.0'
    elif attack == 'revision': bundle['metadata']['control_plane_revision'] = 'unknown'
    elif attack == 'copied_reconciliation':
        bundle['records'] = [r for r in bundle['records'] if r['record_type'] != 'reconciliation']
    elif attack == 'history': next(iter(bundle['metadata']['effect_observation_history'].values()))['latest_supported_destination_state'] = 'applied'
    elif attack == 'accepted_observation': records(bundle,'executor_observation')[0]['data']['effect_id'] = 'other'
    elif attack == 'missing_rejected': bundle['records'] = [r for r in bundle['records'] if r['record_type'] != 'rejected_executor_observation']
    with pytest.raises(ImportContractError):
        import_manifest_reconstruction(produced['manifest'], bundle)

@pytest.mark.parametrize("attack", ["delivery", "acknowledgement", "rejection", "uncertainty", "test_provenance", "counts", "warning_count", "downgrade"])
def test_pack_tampering_rejected_before_render(produced, attack):
    pack = import_manifest_reconstruction(produced["manifest"], produced["cases"]["rejected_wrong_effect"]["bundle"])
    trace = pack.metadata["traceable_import"]
    if attack == "delivery": trace["lifecycle_summary"]["destination_observed"] = "applied"
    elif attack == "acknowledgement": trace["lifecycle_summary"]["acknowledgement"] = "independently_verified"
    elif attack == "rejection": trace["lifecycle_records"].pop("rejected_executor_observation")
    elif attack == "uncertainty": trace["unresolved_issues"] = []
    elif attack == "test_provenance": trace["control_evidence_levels"]["tested"]["status"] = "independently_verified"
    elif attack == "counts": trace["derived_counts"]["executor_attempt_count"] += 1
    elif attack == "downgrade":
        trace.pop("retained_sources"); trace["transformation_version"] = "agep-manifest-reconstruction-import/0.2.6"
    elif attack == "warning_count": pack.validation_summary.warning_count = 0
    assert not validate_evidence_pack(pack).valid
    with pytest.raises(ValueError): render_traceable_markdown(pack)


@pytest.mark.parametrize("result", ["failed", "inconclusive", None])
def test_source_test_provenance_and_safe_rendering(produced, result):
    bundle = copy.deepcopy(produced["cases"]["success"]["bundle"])
    bundle["metadata"]["test_provenance"] = {"test_run_id": "<script>alert(1)</script>\n```", "producer": "synthetic",
        "scope": "fixture only", "result": result}
    pack = import_manifest_reconstruction(produced["manifest"], bundle)
    trace = pack.metadata["traceable_import"]
    rendered = render_traceable_markdown(pack)
    assert "<script>" not in rendered
    levels = trace["control_evidence_levels"]
    if result:
        assert levels["tested"]["result"] == result and f"| result | {result} |" in rendered
    else:
        assert levels["tested"]["status"] == "unavailable"
        assert any(f["code"] == "T_TEST_PROVENANCE_INVALID" for f in trace["import_findings"])
    assert levels["tested_in_this_repository"]["status"] == "not_evaluated_during_import"


def test_cli_roundtrip(produced, tmp_path):
    manifest = tmp_path / "manifest.json"; bundle = tmp_path / "bundle.json"; pack = tmp_path / "pack.json"
    manifest.write_text(json.dumps(produced["manifest"]))
    bundle.write_text(json.dumps(produced["cases"]["restart"]["bundle"]))
    cli = [sys.executable, "-c", "from agent_governance_evidence_pack.cli import main; main()"]
    subprocess.run(cli + ["import", "--manifest", str(manifest), "--reconstruction", str(bundle), "--out", str(pack)], check=True, capture_output=True)
    subprocess.run(cli + ["validate", str(pack)], check=True, capture_output=True)
    text = subprocess.run(cli + ["render", str(pack), "--traceable"], check=True, capture_output=True, text=True).stdout
    assert "applied" in text and "observation_accepted" in text


def test_generated_examples_material_equivalence():
    from agent_governance_evidence_pack.loader import load_evidence_pack
    for path in Path("examples/producer-v2").glob("*.pack.json"):
        pack = load_evidence_pack(path)
        assert validate_evidence_pack(pack).valid
        assert render_traceable_markdown(pack) == path.with_name(path.name.replace(".pack.json", ".md")).read_text()
