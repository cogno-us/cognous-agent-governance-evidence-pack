"""Tests verifying that all example evidence packs load, validate, and render correctly."""

import json
from pathlib import Path

import pytest

from agent_governance_evidence_pack.loader import load_evidence_pack
from agent_governance_evidence_pack.renderer import render_markdown
from agent_governance_evidence_pack.validator import validate_evidence_pack


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
RENDERED_DIR = EXAMPLES_DIR / "rendered"

EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.json"))


class TestExamplesLoad:
    @pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.name)
    def test_example_loads(self, example_file):
        pack = load_evidence_pack(example_file)
        assert pack is not None
        assert pack.pack_id


class TestExamplesValidate:
    @pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.name)
    def test_example_validates_with_no_errors(self, example_file):
        pack = load_evidence_pack(example_file)
        report = validate_evidence_pack(pack)
        errors = [i for i in report.issues if i.severity.value == "error"]
        assert report.valid, (
            f"{example_file.name} has validation errors: "
            + ", ".join(f"{e.code}: {e.message}" for e in errors)
        )


class TestRenderedExamples:
    @pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.name)
    def test_example_renders(self, example_file):
        pack = load_evidence_pack(example_file)
        md = render_markdown(pack)
        assert isinstance(md, str)
        assert len(md) > 100

    @pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.name)
    def test_rendered_example_includes_required_sections(self, example_file):
        pack = load_evidence_pack(example_file)
        md = render_markdown(pack)
        for section in [
            "## 1. Executive Summary",
            "## 2. Agent Overview",
            "## 3. Deployment Context",
            "## 15. Known Limitations",
        ]:
            assert section in md, f"{example_file.name}: missing section '{section}'"

    @pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=lambda p: p.name)
    def test_rendered_file_exists_or_can_be_generated(self, example_file):
        stem = example_file.stem
        rendered_path = RENDERED_DIR / f"{stem}.md"
        if not rendered_path.exists():
            pack = load_evidence_pack(example_file)
            md = render_markdown(pack)
            RENDERED_DIR.mkdir(parents=True, exist_ok=True)
            rendered_path.write_text(md, encoding="utf-8")
        assert rendered_path.exists()
        content = rendered_path.read_text()
        assert len(content) > 100
