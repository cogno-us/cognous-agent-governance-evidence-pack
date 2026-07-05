"""
Loader for Agent Governance Evidence Pack files.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import EvidencePack


def load_evidence_pack(path: str | Path) -> EvidencePack:
    """Load an EvidencePack from a JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid JSON or fails model validation.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Evidence pack file not found: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FileNotFoundError(f"Could not read evidence pack file: {path}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in evidence pack file '{path}': {exc}"
        ) from exc

    return load_evidence_pack_json(payload)


def load_evidence_pack_json(payload: dict) -> EvidencePack:
    """Load an EvidencePack from a parsed JSON dict.

    Raises:
        ValueError: If the payload fails model validation.
    """
    try:
        return EvidencePack.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            f"Evidence pack validation error: {exc}"
        ) from exc


def dump_evidence_pack(pack: EvidencePack, path: str | Path) -> Path:
    """Write an EvidencePack to a JSON file.

    Returns the path written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = pack.model_dump(mode="json")
    path.write_text(
        json.dumps(serialized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
