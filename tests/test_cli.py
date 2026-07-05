"""Tests for the CLI."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
VALID_EXAMPLE = EXAMPLES_DIR / "customer_service_agent_evidence_pack.json"
PROCUREMENT_EXAMPLE = EXAMPLES_DIR / "procurement_agent_evidence_pack.json"


def _run_agep(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "agent_governance_evidence_pack.cli"] + list(args),
        capture_output=True,
        text=True,
    )


def _run_agep_cmd(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["agep"] + list(args),
        capture_output=True,
        text=True,
    )


class TestValidateCommand:
    def test_valid_example_returns_0(self):
        result = _run_agep_cmd("validate", str(VALID_EXAMPLE))
        assert result.returncode == 0

    def test_invalid_pack_returns_1(self, tmp_path):
        bad = {"pack_id": "", "title": "", "generated_at": "x"}
        bad["agent_overview"] = {"agent_name": "A", "business_purpose": "p"}
        bad["deployment_context"] = {"environment": "development"}
        f = tmp_path / "bad.json"
        f.write_text(json.dumps(bad), encoding="utf-8")
        result = _run_agep_cmd("validate", str(f))
        assert result.returncode == 1

    def test_output_includes_valid_field(self):
        result = _run_agep_cmd("validate", str(VALID_EXAMPLE))
        assert "Valid" in result.stdout

    def test_file_not_found_returns_2(self):
        result = _run_agep_cmd("validate", "/tmp/nonexistent_file_agep_12345.json")
        assert result.returncode == 2

    def test_invalid_json_returns_2(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        result = _run_agep_cmd("validate", str(f))
        assert result.returncode == 2


class TestSummarizeCommand:
    def test_summarize_returns_0(self):
        result = _run_agep_cmd("summarize", str(VALID_EXAMPLE))
        assert result.returncode == 0

    def test_summarize_output_includes_pack_id(self):
        result = _run_agep_cmd("summarize", str(VALID_EXAMPLE))
        assert "ep-cs-agent-2026-001" in result.stdout

    def test_summarize_output_includes_agent_name(self):
        result = _run_agep_cmd("summarize", str(VALID_EXAMPLE))
        assert "CustomerServiceAgent" in result.stdout

    def test_summarize_file_not_found_returns_2(self):
        result = _run_agep_cmd("summarize", "/tmp/nonexistent_agep.json")
        assert result.returncode == 2


class TestRenderCommand:
    def test_render_returns_0(self, tmp_path):
        out = tmp_path / "output.md"
        result = _run_agep_cmd("render", str(VALID_EXAMPLE), "--out", str(out))
        assert result.returncode == 0

    def test_render_writes_output_file(self, tmp_path):
        out = tmp_path / "output.md"
        _run_agep_cmd("render", str(VALID_EXAMPLE), "--out", str(out))
        assert out.exists()
        content = out.read_text()
        assert "# Customer Service Agent" in content

    def test_render_without_out_prints_to_stdout(self):
        result = _run_agep_cmd("render", str(VALID_EXAMPLE))
        assert result.returncode == 0
        assert "## 1. Executive Summary" in result.stdout

    def test_render_file_not_found_returns_2(self, tmp_path):
        out = tmp_path / "output.md"
        result = _run_agep_cmd("render", "/tmp/nonexistent.json", "--out", str(out))
        assert result.returncode == 2
