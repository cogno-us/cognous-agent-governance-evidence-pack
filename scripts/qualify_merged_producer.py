#!/usr/bin/env python3
"""Qualify accepted Replay against the Control Plane persistence repair.

The producer workflow and Evidence Pack import/validation/render all execute
inside the producer's unchanged-store assertions. No ODES or GAX dependency is
used on this path.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

from agent_governance_evidence_pack import (
    import_manifest_reconstruction,
    render_traceable_markdown,
    validate_evidence_pack,
)

REPLAY_REVISION = "459e4ba62fca49364aebb0050cd5fb2dd5a71bfa"
CONTROL_PLANE_REVISION = "d3dadee70bd319812b207389ab1e0f6efe511916"
EXECUTOR_REVISION = "c3c3ee7188b9367cf70b08074b9c40a5c70c94ac"
MANIFEST_REVISION = "46c950bed37fe3812000895430bc0312d29e37ce"


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def main(output: Path) -> None:
    replay_root = Path(os.environ["AGEP_ACCEPTED_REPLAY_ROOT"]).resolve()
    cp_root = Path(os.environ["AGEP_PERSISTENCE_CONTROL_PLANE_ROOT"]).resolve()
    executor_root = Path(os.environ["AGEP_ACCEPTED_EXECUTOR_ROOT"]).resolve()
    manifest_path = Path(os.environ["AGEP_MANIFEST_FIXTURE"]).resolve()

    assert git_head(replay_root) == REPLAY_REVISION
    assert git_head(cp_root) == CONTROL_PLANE_REVISION
    assert git_head(executor_root) == EXECUTOR_REVISION
    assert git_head(manifest_path.parents[1]) == MANIFEST_REVISION

    sys.path.insert(0, str(replay_root / "src"))
    from agent_replay_bundle import import_bounded_workflow

    spec = importlib.util.spec_from_file_location(
        "agep_store_generator",
        replay_root / "scripts" / "generate_producer_v2_examples.py",
    )
    generator = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(generator)

    manifest = json.loads(manifest_path.read_text())
    captured: list[dict] = []

    def inspect(*args, **kwargs):
        bundle = import_bounded_workflow(*args, **kwargs)
        source = bundle.model_dump(mode="json")
        source_before = copy.deepcopy(source)
        pack = import_manifest_reconstruction(manifest, source)
        report = validate_evidence_pack(pack)
        assert report.valid, report
        markdown = render_traceable_markdown(pack)
        assert source == source_before
        captured.append({
            "bundle": source,
            "pack": pack.model_dump(mode="json"),
            "markdown": markdown,
        })
        return bundle

    generator.import_bounded_workflow = inspect
    output.mkdir(parents=True, exist_ok=True)

    old_env = os.environ.copy()
    os.environ["ARB_V2_CONTROL_PLANE_ROOT"] = str(cp_root)
    os.environ["ARB_V2_MOLTBOT_ROOT"] = str(executor_root)
    os.environ["ARB_PINNED_MANIFEST_FIXTURE"] = str(manifest_path)
    try:
        with tempfile.TemporaryDirectory() as temporary:
            generated = Path(temporary)
            generator.main(generated)
            sources = json.loads((generated / "producer_v2_sources.json").read_text())
            results = json.loads((generated / "producer_v2_results.json").read_text())
    finally:
        os.environ.clear()
        os.environ.update(old_env)

    cases = dict(zip(sources, captured, strict=True))

    # Genuine held/no-effect case. The Evidence Pack path remains inside
    # explicit Control Plane-file and destination-SQLite unchanged assertions.
    sys.path[:0] = [str(cp_root / "src"), str(executor_root)]
    os.environ["MOLTBOT_SAFE_CONTROL_PLANE_ROOT"] = str(cp_root)
    os.environ["MOLTBOT_SAFE_MANIFEST_FIXTURE"] = str(manifest_path)
    fixture_spec = importlib.util.spec_from_file_location(
        "agep_store_held_fixture",
        executor_root / "tests" / "test_safe_executor.py",
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
        held = import_bounded_workflow(
            workflow.records.load().model_dump(mode="json"),
            proposal=proposal.model_dump(mode="json", exclude_none=False),
            control_plane_revision=CONTROL_PLANE_REVISION,
        )
        held_source = held.model_dump(mode="json")
        held_before = copy.deepcopy(held_source)
        held_pack = import_manifest_reconstruction(manifest, held_source)
        assert validate_evidence_pack(held_pack).valid
        held_markdown = render_traceable_markdown(held_pack)
        assert held_source == held_before
        assert workflow.records.path.read_bytes() == cp_before
        assert rows() == destination_before
        assert destination.effect_count(request.operation.grant_id) == 0
        cases["held"] = {
            "bundle": held_source,
            "pack": held_pack.model_dump(mode="json"),
            "markdown": held_markdown,
        }
        results["scenarios"]["held"] = {
            "decision_id": decision.decision_id,
            "effect_count_before_import": 0,
            "effect_count_after_import": 0,
            "records_unchanged": True,
            "classification": "required_safety_invariant_pass",
        }

    results["evidence_pack_qualification"] = {
        "starting_evidence_pack_revision": "dad2a187f2556950d125b0798500a347b46f017d",
        "replay_revision": REPLAY_REVISION,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "executor_revision": EXECUTOR_REVISION,
        "producer_profile": "2.0.0",
        "execution_envelope": "0.2.0",
        "reconstruction_bundle": "0.2.0",
        "scope": "synthetic same-host producer qualification; Evidence Pack import, validation and traceable rendering occur inside unchanged producer-store assertions; no independent verification",
        "odes_gax": "not exercised on this repaired-Control-Plane path",
    }

    (output / "cases.json").write_text(
        json.dumps({"manifest": manifest, "cases": cases}, indent=2) + "\n"
    )
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(
        f"{len(cases)} repaired-Control-Plane Evidence Pack scenarios passed "
        "with producer stores unchanged"
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
