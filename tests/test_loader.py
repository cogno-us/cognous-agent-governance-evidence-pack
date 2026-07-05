"""Tests for the evidence pack loader."""

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from agent_governance_evidence_pack.loader import (
    dump_evidence_pack,
    load_evidence_pack,
    load_evidence_pack_json,
)
from agent_governance_evidence_pack.models import EvidencePack


def _minimal_payload() -> dict:
    return {
        "pack_id": "test-001",
        "title": "Test Pack",
        "generated_at": "2026-01-01T00:00:00Z",
        "agent_overview": {
            "agent_name": "TestAgent",
            "business_purpose": "Test purpose",
        },
        "deployment_context": {
            "environment": "development",
        },
    }


class TestLoadValidPack:
    def test_load_from_file(self, tmp_path):
        payload = _minimal_payload()
        f = tmp_path / "pack.json"
        f.write_text(json.dumps(payload), encoding="utf-8")
        pack = load_evidence_pack(str(f))
        assert pack.pack_id == "test-001"
        assert pack.agent_overview.agent_name == "TestAgent"

    def test_load_from_path_object(self, tmp_path):
        payload = _minimal_payload()
        f = tmp_path / "pack.json"
        f.write_text(json.dumps(payload), encoding="utf-8")
        pack = load_evidence_pack(f)
        assert isinstance(pack, EvidencePack)

    def test_load_evidence_pack_json(self):
        pack = load_evidence_pack_json(_minimal_payload())
        assert pack.pack_id == "test-001"


class TestLoadErrors:
    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_evidence_pack("/tmp/nonexistent_evidence_pack_12345.json")

    def test_invalid_json_raises(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("{ not valid json }", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_evidence_pack(str(f))

    def test_model_validation_error_raises(self, tmp_path):
        bad_payload = {"pack_id": "x", "title": "y"}  # missing required fields
        f = tmp_path / "bad.json"
        f.write_text(json.dumps(bad_payload), encoding="utf-8")
        with pytest.raises(ValueError, match="validation error"):
            load_evidence_pack(str(f))

    def test_model_validation_error_from_json_raises(self):
        with pytest.raises(ValueError, match="validation error"):
            load_evidence_pack_json({"pack_id": "x"})  # missing required fields


class TestDumpPack:
    def test_dump_writes_file(self, tmp_path):
        pack = EvidencePack.model_validate(_minimal_payload())
        out = tmp_path / "out.json"
        result = dump_evidence_pack(pack, out)
        assert result == out
        assert out.exists()
        content = json.loads(out.read_text())
        assert content["pack_id"] == "test-001"

    def test_dump_is_formatted_json(self, tmp_path):
        pack = EvidencePack.model_validate(_minimal_payload())
        out = tmp_path / "out.json"
        dump_evidence_pack(pack, out)
        text = out.read_text()
        assert "\n" in text  # formatted with indentation
        assert "  " in text

    def test_dump_creates_parent_dirs(self, tmp_path):
        pack = EvidencePack.model_validate(_minimal_payload())
        out = tmp_path / "deep" / "nested" / "out.json"
        dump_evidence_pack(pack, out)
        assert out.exists()

    def test_roundtrip(self, tmp_path):
        pack = EvidencePack.model_validate(_minimal_payload())
        out = tmp_path / "out.json"
        dump_evidence_pack(pack, out)
        pack2 = load_evidence_pack(out)
        assert pack2.pack_id == pack.pack_id
        assert pack2.title == pack.title
