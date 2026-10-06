"""Traceable Manifest/Reconstruction import with pinned Replay semantic validation."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from .models import (
    ActionInventoryItem,
    ActionType,
    AgentOverview,
    AuthorityModelSummary,
    ControlStatus,
    DeploymentContext,
    DeploymentEnvironment,
    EvidencePack,
    PolicyControlSummary,
    ReplayBundleInventoryItem,
    ReviewStatus,
    ToolInventoryItem,
    ValidationSummary,
)

TRANSFORMATION_VERSION = "agep-manifest-reconstruction-import/0.2.6"
CANONICALIZATION_PROFILE = "json-sort-keys-compact-utf8-no-nan"
MANIFEST_REVISION = "46c950bed37fe3812000895430bc0312d29e37ce"
REPLAY_REVISION = "f12648313cedc2cf06145d397fa56cdea18cc800"
CONTROL_PLANE_REVISION = "283500652d47a692fb0b99a1172a6d5faffbd9a7"
MOLTBOT_SAFE_REVISION = "6b0ba1185bcd390f71df947dda349415e4105f5f"
ODES_REVISION = "b3a2f1e72df88cd24d93d1b7d69963f43139e749"
GAX_IMX_REVISION = "9ad378145d326799e3209136e47e82d66c6f69af"
ALVORADA_REVISION = "fb3d97938969a89e149e8ff8db2756091d1233fc"
SUPPORTED_MANIFEST_VERSION = "1.1"
SUPPORTED_RECONSTRUCTION_VERSION = "0.2.0"

REQUIRED_REPOS = {
    "cogno-us/cognous-agent-action-manifest": MANIFEST_REVISION,
    "cogno-us/cognous-agent-replay-bundle": REPLAY_REVISION,
    "cogno-us/cognous-agent-control-plane": CONTROL_PLANE_REVISION,
    "cogno-us/moltbot-safe": MOLTBOT_SAFE_REVISION,
    "cogno-us/constitutional-governance-for-institutions": ALVORADA_REVISION,
}
EXECUTION_TYPES = {"execution_envelope", "execution_result", "destination_attempt", "destination_attempt_event", "destination_effect"}


class ImportContractError(ValueError):
    """Raised when supplied producer artifacts fail the supported import contract."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _obj(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ImportContractError(f"{path} must be an object")
    return value


def _records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    records = bundle.get("records")
    if not isinstance(records, list) or not records:
        raise ImportContractError("reconstruction bundle must contain a nonempty records array")
    for i, record in enumerate(records):
        _obj(record, f"records[{i}]")
        _obj(record.get("data"), f"records[{i}].data")
        if not record.get("record_id"):
            raise ImportContractError(f"records[{i}].record_id is required")
        if not record.get("record_type"):
            raise ImportContractError(f"records[{i}].record_type is required")
        if not record.get("producer_profile_id"):
            raise ImportContractError(f"records[{i}].producer_profile_id is required")
    return records


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _manifest_version(manifest: dict[str, Any]) -> str | None:
    value = _first(manifest, "manifest_version", "version", "schema_version")
    return str(value) if value is not None else None


def _manifest_id(manifest: dict[str, Any]) -> str | None:
    value = _first(manifest, "manifest_id", "id", "name")
    return str(value) if value is not None else None


def _bundle_version(bundle: dict[str, Any]) -> str | None:
    value = _first(bundle, "reconstruction_bundle_version", "bundle_version", "format_version", "version")
    if value is None and isinstance(bundle.get("metadata"), dict):
        value = _first(bundle["metadata"], "reconstruction_bundle_version", "bundle_version", "format_version")
    return str(value) if value is not None else None


def _actions(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("actions", "tool_actions", "action_inventory", "declared_actions"):
        value = manifest.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    output: list[dict[str, Any]] = []
    for tool in manifest.get("tools", []) if isinstance(manifest.get("tools"), list) else []:
        if not isinstance(tool, dict):
            continue
        for action in tool.get("actions", []) if isinstance(tool.get("actions"), list) else []:
            if isinstance(action, dict):
                copied = dict(action)
                copied.setdefault("tool_name", tool.get("tool_name") or tool.get("name") or tool.get("tool_id"))
                output.append(copied)
    return output


def _requirement(value: Any) -> tuple[bool, str]:
    if value is None:
        return True, "missing_treated_required"
    if isinstance(value, bool):
        return value, "bool"
    if isinstance(value, list):
        if not value:
            return False, "empty_list"
        return any(_requirement(item.get("required", True) if isinstance(item, dict) else item)[0] for item in value), "list"
    if isinstance(value, str):
        normalized = value.lower().strip()
        if normalized in {"required", "require", "true", "yes", "human_review", "approval_required"}:
            return True, "string"
        if normalized in {"not_required", "optional", "false", "no", "none"}:
            return False, "string"
        return True, "unknown_string_treated_required"
    if isinstance(value, dict):
        for key in ("required", "enabled", "applies", "review_required", "reliance_required", "authority_required"):
            if key in value:
                return _requirement(value[key])[0], f"dict.{key}"
        for key in ("mode", "level", "default"):
            if key in value:
                return _requirement(value[key])[0], f"dict.{key}"
        return True, "dict_without_flag_treated_required"
    return True, "unsupported_shape_treated_required"


def _action_type(value: Any) -> ActionType:
    try:
        return ActionType(str(value))
    except Exception:
        return ActionType.other


def _record_type(record: dict[str, Any]) -> str:
    return str(record.get("record_type") or "unknown")


def _data(record: dict[str, Any]) -> dict[str, Any]:
    return _obj(record.get("data"), "record.data")


def _record_id(record: dict[str, Any], index: int) -> str:
    return str(record.get("record_id") or f"records[{index}]")


def _identifier(record: dict[str, Any], data: dict[str, Any], *names: str) -> str | None:
    identifiers = record.get("identifiers") if isinstance(record.get("identifiers"), dict) else {}
    for name in names:
        if data.get(name) not in (None, ""):
            return str(data[name])
        if identifiers.get(name) not in (None, ""):
            return str(identifiers[name])
    return None


def _group(bundle: dict[str, Any]) -> dict[str, list[tuple[int, dict[str, Any], dict[str, Any]]]]:
    grouped: dict[str, list[tuple[int, dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for index, record in enumerate(_records(bundle)):
        grouped[_record_type(record)].append((index, record, _data(record)))
    return grouped


def _normalize_decision(value: Any) -> str:
    normalized = str(value or "").lower().strip()
    if normalized in {"allow", "allowed", "authorized", "grant", "granted", "approved"}:
        return "authorized"
    if normalized in {"hold", "held", "escalate", "pending", "requires_review", "review"}:
        return "hold"
    if normalized in {"deny", "denied", "block", "blocked", "reject", "rejected"}:
        return "deny"
    return normalized or "unknown"


def _decision_result(data: dict[str, Any]) -> str:
    return _normalize_decision(data.get("result") or data.get("decision") or data.get("authorization") or data.get("status"))


def _binding(data: dict[str, Any]) -> dict[str, Any] | None:
    value = data.get("binding") or data.get("authorization_binding") or data.get("effect_binding")
    return value if isinstance(value, dict) else None


def _state_from_value(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("state") or value.get("status") or value.get("result")
    normalized = str(value or "unknown").lower().strip()
    if normalized in {"applied", "present", "delivered", "success", "succeeded", "executed", "reconciled"}:
        return "applied"
    if normalized in {"partial", "partially_applied", "partial_delivery"}:
        return "partial"
    if normalized in {"absent", "not_found", "not_applied", "safe_to_retry"}:
        return "absent"
    if normalized in {"unknown", "timeout", "acknowledgement_lost", "lost"}:
        return "unknown"
    return normalized or "unknown"


def _observation_state(data: dict[str, Any]) -> str:
    return _state_from_value(data.get("state") or data.get("observed_state") or data.get("result") or data.get("destination_state_status"))


def _same(expected: Any, actual: Any, label: str) -> None:
    if expected is not None and actual is not None and expected != actual:
        raise ImportContractError(f"contradictory retained producer evidence: {label} expected {expected!r}, got {actual!r}")


def _validate_manifest(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if _manifest_version(manifest) != SUPPORTED_MANIFEST_VERSION:
        raise ImportContractError(f"unsupported Manifest version {_manifest_version(manifest)!r}; expected {SUPPORTED_MANIFEST_VERSION}")
    if not _manifest_id(manifest):
        raise ImportContractError("manifest identity is required")
    actions = _actions(manifest)
    if not actions:
        raise ImportContractError("manifest must declare at least one action")
    findings: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        if "review_requirement" not in action and "review_required" not in action:
            findings.append({"code": "M_REVIEW_UNKNOWN", "severity": "warning", "path": f"manifest.actions[{index}].review_requirement", "message": "review_requirement absent; treated as required rather than false."})
        if "reliance_requirement" not in action and "reliance_required" not in action:
            findings.append({"code": "M_RELIANCE_UNKNOWN", "severity": "warning", "path": f"manifest.actions[{index}].reliance_requirement", "message": "reliance_requirement absent; treated as required rather than false."})
    return actions, findings


def _validate_headers(manifest: dict[str, Any], bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    actions, findings = _validate_manifest(manifest)
    if _bundle_version(bundle) != SUPPORTED_RECONSTRUCTION_VERSION:
        raise ImportContractError(f"unsupported Reconstruction Bundle version {_bundle_version(bundle)!r}; expected {SUPPORTED_RECONSTRUCTION_VERSION}")
    records = _records(bundle)
    profiles = bundle.get("producer_profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ImportContractError("reconstruction bundle must include producer_profiles")
    profile_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            raise ImportContractError(f"producer_profiles[{index}] must be an object")
        profile_id = profile.get("profile_id")
        if not profile_id:
            raise ImportContractError(f"producer_profiles[{index}].profile_id is required")
        profile_ids.add(str(profile_id))
        repo = profile.get("repository")
        revision = profile.get("revision")
        if repo in REQUIRED_REPOS and revision not in (None, REQUIRED_REPOS[repo]):
            raise ImportContractError(f"producer_profiles[{index}].revision for {repo} conflicts with pinned supported revision")
    for index, record in enumerate(records):
        if str(record["producer_profile_id"]) not in profile_ids:
            raise ImportContractError(f"records[{index}].producer_profile_id references unknown producer profile {record['producer_profile_id']!r}")
    return actions, findings


def _retained_by_type(bundle: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in sorted(_records(bundle), key=lambda item: item.get("source_sequence", 0)):
        by_type[_record_type(record)].append(deepcopy(_data(record)))
    return by_type


def _retained_replay_inputs(bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
    by_type = _retained_by_type(bundle)
    if len(by_type.get("runtime_proposal", [])) > 1:
        raise ImportContractError("importer supports at most one retained runtime_proposal operation")
    if len(by_type.get("runtime_decision", [])) < 1:
        raise ImportContractError("reconstruction bundle must retain at least one runtime_decision")
    for decision in by_type.get("runtime_decision", []):
        if _decision_result(decision) != "authorized" and _binding(decision) is not None:
            raise ImportContractError("held or denied runtime_decision cannot carry an authorization/effect binding")
    has_execution = any(by_type.get(kind) for kind in EXECUTION_TYPES)
    if has_execution:
        if len(by_type.get("execution_envelope", [])) != 1:
            raise ImportContractError("execution evidence requires exactly one execution_envelope")
        if len(by_type.get("execution_result", [])) != 1:
            raise ImportContractError("execution evidence requires exactly one execution_result")
        if not any(_decision_result(item) == "authorized" for item in by_type.get("runtime_decision", [])):
            raise ImportContractError("execution evidence cannot be supplied when no runtime_decision authorized an effect")
    control_plane = {
        "run_id": bundle.get("run_id"),
        "decisions": by_type.get("runtime_decision", []),
        "attempts": by_type.get("control_plane_attempt_transition", []),
        "observations": by_type.get("effect_observation", []),
        "reconciliations": by_type.get("reconciliation", []),
    }
    proposal = by_type.get("runtime_proposal", [None])[0]
    moltbot = None
    if has_execution:
        moltbot = {
            "execution_envelope": by_type["execution_envelope"][0],
            "execution_result": by_type["execution_result"][0],
            "attempts": by_type.get("destination_attempt", []),
            "attempt_events": by_type.get("destination_attempt_event", []),
            "effects": by_type.get("destination_effect", []),
        }
    return control_plane, proposal, moltbot


def _run_pinned_replay_validator(bundle: dict[str, Any]) -> str:
    control_plane, proposal, moltbot = _retained_replay_inputs(bundle)
    try:
        from agent_replay_bundle.importers import ImportContractError as ReplayImportContractError
        from agent_replay_bundle.importers import import_bounded_workflow
    except Exception as exc:
        raise ImportContractError(f"pinned Replay semantic validator unavailable; install cogno-us/cognous-agent-replay-bundle at {REPLAY_REVISION}") from exc
    try:
        reconstructed = import_bounded_workflow(control_plane, proposal=proposal, moltbot_export=moltbot)
    except ReplayImportContractError as exc:
        raise ImportContractError(f"pinned Replay semantic validation failed: {exc}") from exc
    except Exception as exc:
        raise ImportContractError(f"pinned Replay semantic validation failed unexpectedly: {exc}") from exc
    status = getattr(reconstructed, "status", None)
    if status not in {"reconstruction_complete", "reconstruction_partial"}:
        raise ImportContractError(f"pinned Replay semantic validation returned status {status!r}")
    if moltbot is None:
        return "recorded_no_execution"
    return "executed" if status == "reconstruction_complete" else "executed_with_unresolved_evidence"


def _check_commitments(bundle: dict[str, Any], manifest: dict[str, Any]) -> None:
    grouped = _group(bundle)
    proposals = grouped.get("runtime_proposal", [])
    proposal = proposals[0][2] if proposals else None
    if proposal is not None:
        if proposal.get("manifest_id") != _manifest_id(manifest):
            raise ImportContractError("proposal.manifest_id does not match supplied Manifest")
        if str(proposal.get("manifest_version")) != _manifest_version(manifest):
            raise ImportContractError("proposal.manifest_version does not match supplied Manifest")
        if proposal.get("manifest_digest") != sha256(manifest):
            raise ImportContractError("proposal.manifest_digest does not match supplied Manifest digest")
        if proposal.get("payload_commitment") != sha256(proposal.get("payload")):
            raise ImportContractError("proposal.payload_commitment does not match proposal.payload")

    authorized: list[dict[str, Any]] = []
    effects: set[str] = set()
    decisions: set[str] = set()
    for index, record, data in grouped.get("runtime_decision", []):
        decision_id = _identifier(record, data, "decision_id") or f"decision@{index}"
        decisions.add(decision_id)
        result = _decision_result(data)
        bind = _binding(data)
        if result == "authorized":
            if bind is None:
                raise ImportContractError(f"decision {decision_id} is authorized but has no binding")
            authorized.append(data)
            effect_id = _identifier(record, data, "effect_id")
            if effect_id:
                effects.add(effect_id)
        elif bind is not None:
            raise ImportContractError(f"decision {decision_id} result {result!r} cannot carry an authorization/effect binding")

    has_execution = any(grouped.get(kind) for kind in EXECUTION_TYPES)
    if has_execution and not authorized:
        raise ImportContractError("execution evidence supplied without an authorized decision")
    if not has_execution:
        return
    if proposal is None:
        raise ImportContractError("execution evidence requires retained runtime_proposal")
    decision = authorized[0]
    bind = _binding(decision)
    if bind is None:
        raise ImportContractError("authorized runtime_decision must include binding")
    for field in ("proposal_commitment", "manifest_id", "manifest_version", "manifest_digest", "actor", "principal", "action_id", "adapter_id", "target", "payload_commitment", "requested_permissions", "amount", "unit", "effects", "grant_id", "grant_revision"):
        if field not in bind:
            raise ImportContractError(f"runtime_decision.binding.{field} is required")
    if bind["proposal_commitment"] != sha256(proposal):
        raise ImportContractError("runtime_decision.binding.proposal_commitment does not match runtime_proposal")
    if bind["payload_commitment"] != proposal["payload_commitment"]:
        raise ImportContractError("runtime_decision.binding.payload_commitment does not match runtime_proposal")
    if bind["manifest_digest"] != proposal["manifest_digest"]:
        raise ImportContractError("runtime_decision.binding.manifest_digest does not match runtime_proposal")
    operation = grouped["execution_envelope"][0][2].get("operation")
    if not isinstance(operation, dict):
        raise ImportContractError("execution_envelope.operation must be an object")
    if operation.get("proposal_commitment") != bind["proposal_commitment"]:
        raise ImportContractError("execution_envelope.operation.proposal_commitment does not match decision binding")
    if operation.get("payload_commitment") != proposal["payload_commitment"]:
        raise ImportContractError("execution_envelope.operation.payload_commitment does not match proposal")
    for field in ("actor", "principal", "manifest_id", "manifest_version", "manifest_digest", "action_id", "adapter_id", "target", "payload", "payload_commitment", "requested_permissions", "amount", "unit", "effects", "requirement_id"):
        _same(proposal.get(field), operation.get(field), f"execution_envelope.operation.{field}")
    operation_digest = sha256(operation)
    destination_attempts = {item[2].get("attempt_id") for item in grouped.get("destination_attempt", [])}
    destination_attempts |= {_identifier(record, data, "attempt_id") for _, record, data in grouped.get("destination_attempt", [])}
    destination_attempts.discard(None)
    cp_attempts = {_identifier(record, data, "attempt_id") for _, record, data in grouped.get("control_plane_attempt_transition", [])}
    cp_attempts.discard(None)
    result = grouped["execution_result"][0][2]
    result_attempt_id = result.get("attempt_id")
    if result_attempt_id is not None:
        if result_attempt_id not in destination_attempts and result_attempt_id not in cp_attempts:
            raise ImportContractError("execution_result.attempt_id does not reference a retained destination_attempt or Control Plane attempt")
        if result_attempt_id in cp_attempts and result_attempt_id not in destination_attempts:
            if result.get("status") not in {"reconciled", "partial", "unknown"} or result.get("newly_executed") is not False:
                raise ImportContractError("Control Plane attempt namespace is valid only for non-new reconciliation results")
    if result.get("effect_id") not in effects:
        raise ImportContractError("execution_result.effect_id does not match an authorized decision effect_id")
    for _, _, destination in grouped.get("destination_effect", []):
        if destination.get("effect_id") not in effects:
            raise ImportContractError("destination_effect.effect_id does not match an authorized decision effect_id")
        if destination.get("operation_digest") != operation_digest:
            raise ImportContractError("destination_effect.operation_digest does not match execution_envelope.operation")
        if destination.get("target") != operation.get("target"):
            raise ImportContractError("destination_effect.target does not match execution_envelope.operation.target")
        if destination.get("amount") != operation.get("amount"):
            raise ImportContractError("destination_effect.amount does not match execution_envelope.operation.amount")
        if destination.get("unit") != operation.get("unit"):
            raise ImportContractError("destination_effect.unit does not match execution_envelope.operation.unit")
        if isinstance(destination.get("payload_json"), str):
            try:
                payload = json.loads(destination["payload_json"])
            except json.JSONDecodeError as exc:
                raise ImportContractError("destination_effect.payload_json is not valid JSON") from exc
            if payload != operation.get("payload"):
                raise ImportContractError("destination_effect.payload_json does not match execution_envelope.operation.payload")
    checked = {item.get("label") for item in bundle.get("commitments", []) if isinstance(item, dict) and item.get("verification_status") == "checked_match"}
    required_checked = {"payload_commitment"}
    if grouped.get("destination_effect"):
        required_checked |= {"effect_id", "operation_digest"}
    if not required_checked <= checked:
        raise ImportContractError(f"required checked commitments missing: {sorted(required_checked - checked)}")


def _authorization_summary(counter: Counter[str]) -> str:
    meaningful = {key: value for key, value in counter.items() if value and key in {"authorized", "hold", "deny", "unknown"}}
    if not meaningful:
        return "unknown"
    if len(meaningful) == 1:
        key = next(iter(meaningful))
        return "held" if key == "hold" else "denied" if key == "deny" else key
    return "unresolved"


def _semantic(manifest: dict[str, Any], bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter[str], str]:
    actions, findings = _validate_headers(manifest, bundle)
    validator_status = _run_pinned_replay_validator(bundle)
    _check_commitments(bundle, manifest)
    grouped = _group(bundle)
    auth: Counter[str] = Counter()
    effects: set[str] = set()
    decisions: set[str] = set()
    for index, record, data in grouped.get("runtime_decision", []):
        decision_id = _identifier(record, data, "decision_id") or f"decision@{index}"
        decisions.add(decision_id)
        result = _decision_result(data)
        auth[result] += 1
        effect_id = _identifier(record, data, "effect_id")
        if effect_id:
            effects.add(effect_id)
    for record_type in ("execution_envelope", "execution_result", "destination_attempt", "destination_attempt_event", "effect_observation", "destination_effect", "reconciliation", "control_plane_attempt", "control_plane_attempt_transition"):
        for index, record, data in grouped.get(record_type, []):
            effect_id = _identifier(record, data, "effect_id")
            decision_id = _identifier(record, data, "decision_id")
            if effect_id and effects and effect_id not in effects:
                raise ImportContractError(f"{record_type} {index} has dangling effect_id {effect_id}")
            if decision_id and decision_id not in decisions:
                raise ImportContractError(f"{record_type} {index} has dangling decision_id {decision_id}")
    return actions, findings, auth, validator_status


def _make_actions(actions: list[dict[str, Any]], findings: list[dict[str, Any]]) -> list[ActionInventoryItem]:
    output: list[ActionInventoryItem] = []
    for index, action in enumerate(actions):
        authority_required, authority_source = _requirement(action.get("authority_required") if "authority_required" in action else action.get("authority_requirement"))
        review_required, review_source = _requirement(action.get("review_required") if "review_required" in action else action.get("review_requirement"))
        reliance_required, reliance_source = _requirement(action.get("reliance_required") if "reliance_required" in action else action.get("reliance_requirement"))
        for code, source in (("AUTH", authority_source), ("REVIEW", review_source), ("RELIANCE", reliance_source)):
            if "missing" in source or "unknown" in source:
                findings.append({"code": f"M_{code}_UNCERTAIN", "severity": "warning", "path": f"manifest.actions[{index}]", "message": f"{code.lower()} requirement treated as required due to {source}."})
        output.append(ActionInventoryItem(action_name=str(action.get("action_name") or action.get("action_id") or action.get("name") or f"action_{index}"), tool_name=str(action.get("tool_name") or action.get("tool_id") or action.get("adapter_id") or "unknown_tool"), action_type=_action_type(action.get("action_type") or action.get("type")), description=action.get("description"), authority_required=authority_required, review_required=review_required, reliance_required=reliance_required, default_posture=str(action.get("default_action") or action.get("default_posture") or "unknown"), control_status=ControlStatus.planned))
    return output


def _make_tools(manifest: dict[str, Any]) -> list[ToolInventoryItem]:
    tools: list[ToolInventoryItem] = []
    for index, tool in enumerate(manifest.get("tools", []) if isinstance(manifest.get("tools"), list) else []):
        if not isinstance(tool, dict):
            continue
        tools.append(ToolInventoryItem(tool_name=str(tool.get("tool_name") or tool.get("name") or tool.get("tool_id") or f"tool_{index}"), description=tool.get("description"), external_system=tool.get("external_system"), data_classification=tool.get("data_classification"), access_mode=tool.get("access_mode"), control_status=ControlStatus.planned))
    return tools


def _combined_state(counter: Counter[str]) -> str:
    if counter.get("revoked") or counter.get("contradictory") or counter.get("unresolved"):
        return "unresolved"
    if counter.get("partial"):
        return "partial"
    if counter.get("absent"):
        return "absent"
    if counter.get("unknown") and not counter.get("applied"):
        return "unknown"
    if counter.get("applied"):
        return "applied_with_unknown" if counter.get("unknown") else "applied"
    if counter.get("unavailable"):
        return "unavailable"
    return "unknown"


def _ack_transition_state(data: dict[str, Any]) -> str | None:
    status = str(data.get("status") or "unknown").lower()
    ack = data.get("acknowledgement")
    if isinstance(ack, dict) and ack:
        return "received"
    if status == "acknowledged":
        return "unresolved"
    if status in {"unknown", "failed", "lost", "timeout"}:
        return "unknown"
    return None


def _ack_result_state(data: dict[str, Any]) -> str | None:
    if data.get("acknowledged") is True:
        return "received"
    if data.get("acknowledged") is False or str(data.get("status") or "").lower() in {"unknown", "timeout", "lost"}:
        return "unknown"
    return None


def _state_counts(bundle: dict[str, Any], auth: Counter[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    grouped = _group(bundle)
    proposals: set[str] = set(); decisions: set[str] = set(); effects: set[str] = set(); control_attempts: set[str] = set(); executor_attempts: set[str] = set()
    transition_records = 0
    control_statuses: Counter[str] = Counter(); acknowledgement: Counter[str] = Counter(); observations: Counter[str] = Counter(); destination_effect_states: Counter[str] = Counter(); effect_observation_states: Counter[str] = Counter(); reconciliation_states: Counter[str] = Counter(); execution_result_states: Counter[str] = Counter()
    ack_sources: list[dict[str, Any]] = []
    for record_type, entries in grouped.items():
        for index, record, data in entries:
            if record_type == "runtime_proposal":
                proposals.add(_identifier(record, data, "proposal_id", "action_id", "correlation_id") or _record_id(record, index))
            elif record_type == "runtime_decision":
                decisions.add(_identifier(record, data, "decision_id") or _record_id(record, index)); effect_id = _identifier(record, data, "effect_id")
                if effect_id: effects.add(effect_id)
            elif record_type in {"control_plane_attempt", "control_plane_attempt_transition"}:
                attempt_id = _identifier(record, data, "attempt_id") or _record_id(record, index); control_attempts.add("control:" + attempt_id); transition_records += 1
                status = str(data.get("status") or "unknown").lower(); control_statuses[status] += 1
                ack_state = _ack_transition_state(data)
                if ack_state:
                    acknowledgement[f"control_plane_{ack_state}"] += 1; ack_sources.append({"record_id": _record_id(record, index), "source": "control_plane_transition", "state": ack_state, "status": status, "attempt_id": data.get("attempt_id")})
            elif record_type == "destination_attempt":
                attempt_id = _identifier(record, data, "attempt_id", "destination_attempt_id") or _record_id(record, index); executor_attempts.add("destination:" + attempt_id)
            elif record_type == "destination_attempt_event":
                transition_records += 1
            elif record_type == "execution_result":
                state = _state_from_value(data.get("status") or data.get("observed_state")); execution_result_states[state] += 1
                ack_state = _ack_result_state(data)
                if ack_state:
                    acknowledgement[f"execution_result_{ack_state}"] += 1; ack_sources.append({"record_id": _record_id(record, index), "source": "execution_result", "state": ack_state, "status": data.get("status"), "attempt_id": data.get("attempt_id")})
            elif record_type == "effect_observation":
                state = _observation_state(data); effect_observation_states[state] += 1; observations[state] += 1
            elif record_type == "destination_effect":
                state = _observation_state(data); destination_effect_states[state] += 1; observations[state] += 1
            elif record_type == "reconciliation":
                state = _observation_state(data); reconciliation_states[state] += 1; observations[state] += 1
    if not observations: observations["unavailable"] = 1
    ack_summary = "received" if acknowledgement.get("control_plane_received") or acknowledgement.get("execution_result_received") else "unknown"
    if acknowledgement.get("control_plane_unresolved"):
        ack_summary = "unresolved"
    counts = {"proposal_count": len(proposals), "decision_count": len(decisions), "distinct_effect_count": len(effects), "control_plane_attempt_count": len(control_attempts), "executor_attempt_count": len(executor_attempts), "attempt_transition_record_count": transition_records, "destination_effect_count": sum(destination_effect_states.values()), "effect_observation_count": sum(effect_observation_states.values()), "reconciliation_count": sum(reconciliation_states.values()), "destination_observation_counts": dict(sorted(observations.items())), "destination_effect_state_counts": dict(sorted(destination_effect_states.items())), "effect_observation_state_counts": dict(sorted(effect_observation_states.items())), "reconciliation_state_counts": dict(sorted(reconciliation_states.items())), "execution_result_state_counts": dict(sorted(execution_result_states.items())), "acknowledgement_counts": dict(sorted(acknowledgement.items())), "acknowledgement_sources": ack_sources, "coverage_denominators": {"effect_denominator": "distinct authorized effect_id values", "control_plane_attempt_denominator": "unique Control Plane attempt IDs", "executor_attempt_denominator": "unique destination_attempt IDs", "destination_effect_denominator": "destination_effect records", "effect_observation_denominator": "effect_observation records", "reconciliation_denominator": "reconciliation records", "missing_observation": "unavailable, not zero/success/failure"}, "counting_rules": ["Repeated lifecycle records do not inflate attempt counts.", "Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.", "Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.", "Destination effects, effect observations and reconciliations are counted separately.", "Missing observations are unavailable, not success or failure.", "Applied evidence does not override contradictory partial, unresolved, absent or unknown evidence."]}
    lifecycle = {"authorization": _authorization_summary(auth), "current_permission": "not_evaluated_from_historical_records", "execution_attempted": "yes" if control_attempts or executor_attempts else "no", "acknowledgement": ack_summary, "acknowledgement_sources": ack_sources, "control_plane_transition_statuses": dict(sorted(control_statuses.items())), "destination_observed": _combined_state(observations), "independent_verification": "unavailable", "notes": ["Historical authorization is retained evidence and does not establish current permission.", "Control Plane transition status is preserved separately from acknowledgement receipt.", "Executor acknowledgement is distinct from independently verified delivery.", "A lost or unknown acknowledgement followed by an applied observation retains both facts.", "Observed local destination state does not establish independently verified institutional outcome.", "Reconstruction completeness does not mean effect completion.", "HMAC/shared-secret integrity is not public issuer identity or independent review.", "A software-generated pack cannot create human approval."]}
    return counts, lifecycle


def _producer_profile_map(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for profile in bundle.get("producer_profiles", []) if isinstance(bundle.get("producer_profiles"), list) else []:
        if isinstance(profile, dict) and profile.get("profile_id"):
            profiles[str(profile["profile_id"])] = profile
    return profiles


def _producer_profile_status(profile: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(profile, dict):
        return {
            "repository": None,
            "revision": None,
            "format_version": None,
            "revision_check": "producer_profile_unavailable",
            "provenance_status": "unavailable",
            "independent_provenance_verification": "not_performed",
        }
    repository = profile.get("repository")
    revision = profile.get("revision")
    expected = REQUIRED_REPOS.get(repository)
    if expected is None:
        revision_check = "source_asserted_unpinned"
    elif revision is None:
        revision_check = "accepted_repository_revision_not_supplied"
    elif revision == expected:
        revision_check = "declared_revision_matches_accepted_pin"
    else:
        revision_check = "declared_revision_conflicts_with_accepted_pin"
    return {
        "repository": repository,
        "revision": revision,
        "format_version": profile.get("format_version"),
        "revision_check": revision_check,
        "provenance_status": "source_asserted_and_contract_compared",
        "independent_provenance_verification": "not_performed",
    }


def _producer_profile_summaries(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for profile_id, profile in sorted(_producer_profile_map(bundle).items()):
        summaries.append({
            "producer_profile_id": profile_id,
            "producer": profile.get("producer"),
            **_producer_profile_status(profile),
            "format_name": profile.get("format_name"),
            "schema_ref": profile.get("schema_ref"),
            "notes": profile.get("notes"),
        })
    return summaries


def _source_commitments_by_record(bundle: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for commitment in bundle.get("commitments", []) if isinstance(bundle.get("commitments"), list) else []:
        if not isinstance(commitment, dict) or not commitment.get("source_record_id"):
            continue
        by_record[str(commitment["source_record_id"])].append({
            "label": commitment.get("label"),
            "value": commitment.get("value"),
            "algorithm": commitment.get("algorithm"),
            "canonicalization_profile": commitment.get("canonicalization_profile"),
            "verification_status": commitment.get("verification_status"),
            "source_path": commitment.get("source_path"),
            "notes": commitment.get("notes"),
        })
    return by_record


def _source_record_refs(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = _producer_profile_map(bundle)
    commitments = _source_commitments_by_record(bundle)
    refs: list[dict[str, Any]] = []
    for index, record in enumerate(bundle.get("records", [])):
        if not isinstance(record, dict):
            continue
        profile_id = str(record.get("producer_profile_id") or "")
        profile_status = _producer_profile_status(profiles.get(profile_id))
        record_id = _record_id(record, index)
        local_commitment = sha256(record)
        source_commitments = commitments.get(record_id, [])
        primary_source_commitment = source_commitments[0] if source_commitments else {}
        refs.append({
            "record_id": record_id,
            "record_type": _record_type(record),
            "producer_profile_id": record.get("producer_profile_id"),
            "source_path": record.get("source_path") or f"records[{index}]",
            "evidence_class": record.get("evidence_class"),
            "evidence_class_status": "source_assertion",
            "producer_repository": profile_status["repository"],
            "producer_revision": profile_status["revision"],
            "producer_format_version": profile_status["format_version"],
            "producer_revision_check": profile_status["revision_check"],
            "source_asserted_provenance": profile_status["provenance_status"],
            "independent_provenance_verification": profile_status["independent_provenance_verification"],
            "source_commitments": source_commitments,
            "source_content_commitment": primary_source_commitment.get("value"),
            "source_canonicalization_profile": primary_source_commitment.get("canonicalization_profile"),
            "source_commitment_verification_status": primary_source_commitment.get("verification_status"),
            "local_content_commitment": local_commitment,
            "local_canonicalization_profile": CANONICALIZATION_PROFILE,
            "local_commitment_verification_status": "computed_during_import",
            "hash": local_commitment,
        })
    return refs


def _meaningful_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _evidence_levels(bundle: dict[str, Any], replay_validator_status: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    metadata = bundle.get("metadata") if isinstance(bundle.get("metadata"), dict) else {}
    source_runtime: dict[str, Any]
    fixture_provenance = metadata.get("fixture_provenance")
    scenario = metadata.get("scenario")
    if fixture_provenance:
        source_runtime = {
            "status": "source_asserted",
            "evidence": ["reconstruction_bundle.metadata.fixture_provenance"],
            "scope": scenario or "unspecified",
            "assertion": fixture_provenance,
            "meaning": "producer metadata asserts runtime or fixture provenance; importer does not independently establish how the source run was executed",
        }
    else:
        source_runtime = {
            "status": "unavailable",
            "evidence": [],
            "scope": "unavailable",
            "meaning": "no source runtime or fixture provenance was supplied",
        }

    test_provenance = metadata.get("test_provenance")
    attributable_test: dict[str, Any]
    required = ("test_run_id", "producer", "scope", "result")
    invalid_test_fields: list[str] = []
    if test_provenance is not None:
        if not isinstance(test_provenance, dict):
            invalid_test_fields = ["test_provenance"]
        else:
            invalid_test_fields = [key for key in required if not _meaningful_text(test_provenance.get(key))]
            if "revision" in test_provenance and test_provenance.get("revision") is not None and not _meaningful_text(test_provenance.get("revision")):
                invalid_test_fields.append("revision")
    valid_test_provenance = isinstance(test_provenance, dict) and not invalid_test_fields and all(_meaningful_text(test_provenance.get(key)) for key in required)
    if valid_test_provenance:
        attributable_test = {
            "status": "attributable_source_asserted",
            "evidence": ["reconstruction_bundle.metadata.test_provenance"],
            "test_run_id": test_provenance.get("test_run_id"),
            "producer": test_provenance.get("producer"),
            "scope": test_provenance.get("scope"),
            "result": test_provenance.get("result"),
            "revision": test_provenance.get("revision"),
            "meaning": "attributable source-supplied test-run evidence; the importer did not execute or independently verify that test run",
        }
        tested = {
            "status": "attributable_test_evidence_present_scope_bounded",
            "evidence": ["reconstruction_bundle.metadata.test_provenance"],
            "scope": test_provenance.get("scope"),
            "result": test_provenance.get("result"),
            "meaning": "supports only the precise source-attributed test scope; does not establish production effectiveness",
        }
    else:
        if test_provenance is not None:
            findings.append({
                "code": "T_TEST_PROVENANCE_INVALID",
                "severity": "warning",
                "path": "reconstruction_bundle.metadata.test_provenance",
                "message": "Test provenance was supplied but did not contain meaningful string values for required attribution fields.",
                "invalid_fields": sorted(set(invalid_test_fields)),
            })
        attributable_test = {
            "status": "unavailable",
            "evidence": [],
            "scope": "unavailable",
            "meaning": "no complete attributable test-run provenance was supplied",
        }
        tested = {
            "status": "unavailable",
            "evidence": [],
            "scope": "unavailable",
            "meaning": "semantic import validation and source runtime records do not by themselves establish that a test occurred",
        }

    return {
        "semantic_validation_performed_during_import": {
            "status": replay_validator_status,
            "evidence": ["metadata.traceable_import.replay_semantic_validation"],
            "meaning": "the importer executed the accepted Replay semantic validator; this is not a test-run or runtime-control-effectiveness claim",
        },
        "source_asserted_runtime_evidence": source_runtime,
        "attributable_test_run_evidence": attributable_test,
        "declared": {
            "status": "present",
            "evidence": ["manifest"],
            "meaning": "control or requirement is declared only",
        },
        "implemented": {
            "status": "not_established_by_import",
            "evidence": [],
            "meaning": "implementation requires producer-specific evidence; manifest declarations and import success do not suffice",
        },
        "tested": tested,
        "tested_in_this_repository": {
            "status": "not_evaluated_during_import",
            "evidence": [],
            "meaning": "this import does not execute or imply execution of the Evidence Pack repository test suite",
        },
        "operationally_observed": {
            "status": "unavailable",
            "evidence": [],
            "meaning": "no production operational observation supplied",
        },
        "independently_audited": {
            "status": "unavailable",
            "evidence": [],
            "meaning": "no independent audit or certification supplied",
        },
    }


def _conversion_losses(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    losses: list[dict[str, Any]] = []
    for report_index, report in enumerate(bundle.get("import_reports", []) if isinstance(bundle.get("import_reports"), list) else []):
        if not isinstance(report, dict):
            continue
        for finding_index, finding in enumerate(report.get("findings", []) if isinstance(report.get("findings"), list) else []):
            if not isinstance(finding, dict):
                continue
            losses.append({
                "source": "replay_import_report",
                "report_index": report_index,
                "finding_index": finding_index,
                "adapter_profile": report.get("adapter_profile"),
                "code": finding.get("code"),
                "category": finding.get("category"),
                "severity": finding.get("severity"),
                "path": finding.get("path"),
                "value_state": finding.get("value_state"),
                "message": finding.get("message"),
            })
    return losses


def _replay_findings(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for report_index, report in enumerate(bundle.get("import_reports", []) if isinstance(bundle.get("import_reports"), list) else []):
        if not isinstance(report, dict):
            continue
        if report.get("complete") is False:
            findings.append({"code": "REPLAY_REPORT_INCOMPLETE", "severity": "warning", "path": f"import_reports[{report_index}]", "message": f"Replay import report {report.get('adapter_profile', 'unknown')} is incomplete."})
        for item in report.get("findings", []) if isinstance(report.get("findings"), list) else []:
            if isinstance(item, dict):
                findings.append({"code": "REPLAY_" + str(item.get("code", "FINDING")), "severity": item.get("severity", "warning"), "path": item.get("path", f"import_reports[{report_index}].findings"), "message": item.get("message", "Replay import finding."), "category": item.get("category"), "value_state": item.get("value_state")})
    semantics = bundle.get("semantics") if isinstance(bundle.get("semantics"), dict) else {}
    if semantics:
        for key, expected in (("policy_reevaluation", False), ("model_reexecution", False), ("external_effect_execution", False), ("independent_effect_verification", False)):
            if semantics.get(key) is not expected:
                findings.append({"code": "REPLAY_SEMANTIC_UNEXPECTED", "severity": "warning", "path": f"semantics.{key}", "message": f"Replay semantic flag {key} was {semantics.get(key)!r}."})
        notes = semantics.get("notes")
        if notes:
            findings.append({"code": "REPLAY_SEMANTIC_LIMITATION", "severity": "info", "path": "semantics.notes", "message": str(notes)})
    return findings


def _redaction_status(bundle: dict[str, Any], findings: list[dict[str, Any]]) -> tuple[bool, str]:
    if bundle.get("status") == "redacted":
        return True, "source_status_redacted"
    derivation = bundle.get("derivation") if isinstance(bundle.get("derivation"), dict) else None
    if derivation and derivation.get("relationship") == "redacted_derivative":
        return True, "source_derivation_redacted_derivative"
    metadata = bundle.get("metadata") if isinstance(bundle.get("metadata"), dict) else {}
    redaction = bundle.get("redaction") or metadata.get("redaction") or metadata.get("redaction_state")
    if isinstance(redaction, dict):
        if redaction.get("redacted") is True or redaction.get("state") == "redacted": return True, "source_declared_redacted"
        if redaction.get("redacted") is False or redaction.get("state") == "unredacted": return False, "source_declared_unredacted"
    if redaction in (True, "redacted"): return True, "source_declared_redacted"
    if redaction in (False, "unredacted", "not_redacted"): return False, "source_declared_unredacted"
    findings.append({"code": "R_REDACTION_STATE_UNKNOWN", "severity": "warning", "path": "reconstruction_bundle.derivation|metadata.redaction", "message": "Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility."})
    return False, "unknown_schema_default_false"


def import_manifest_reconstruction(manifest: dict[str, Any], reconstruction_bundle: dict[str, Any], *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    manifest = deepcopy(_obj(manifest, "manifest")); bundle = deepcopy(_obj(reconstruction_bundle, "reconstruction_bundle"))
    actions, findings, auth, replay_validator_status = _semantic(manifest, bundle)
    findings.extend(_replay_findings(bundle))
    action_items = _make_actions(actions, findings); tool_items = _make_tools(manifest); counts, lifecycle = _state_counts(bundle, auth)
    generated = bundle.get("generated_at") or (bundle.get("metadata", {}) if isinstance(bundle.get("metadata"), dict) else {}).get("source_generated_at") or generated_at or "unavailable"
    if generated == "unavailable": findings.append({"code": "T_GENERATED_AT_UNAVAILABLE", "severity": "warning", "path": "reconstruction_bundle.generated_at", "message": "No source generation timestamp supplied; importer did not invent one."})
    bundle_id = str(bundle.get("bundle_id") or bundle.get("reconstruction_bundle_id") or bundle.get("run_id") or "unknown_bundle")
    pack_id = "agep-" + sha256({"manifest": sha256(manifest), "bundle": sha256(bundle), "transformation": TRANSFORMATION_VERSION})[7:23]
    redacted, redaction_source = _redaction_status(bundle, findings)
    evidence_levels = _evidence_levels(bundle, replay_validator_status, findings)
    metadata = bundle.get("metadata") if isinstance(bundle.get("metadata"), dict) else {}
    pack = EvidencePack(pack_id=pack_id, pack_version="0.2.0", title=title or "Traceable Agent Governance Evidence Pack", generated_at=str(generated), review_status=ReviewStatus.draft, agent_overview=AgentOverview(agent_name=str(manifest.get("agent_name") or (manifest.get("agent", {}) if isinstance(manifest.get("agent"), dict) else {}).get("name") or "ImportedAgent"), agent_description=manifest.get("agent_description") or (manifest.get("agent", {}) if isinstance(manifest.get("agent"), dict) else {}).get("description"), business_purpose=str(manifest.get("business_purpose") or manifest.get("purpose") or "Imported from Manifest and Reconstruction Bundle; business purpose unavailable."), owner=manifest.get("owner") if isinstance(manifest.get("owner"), str) else None, business_unit=manifest.get("business_unit") if isinstance(manifest.get("business_unit"), str) else None, lifecycle_stage=metadata.get("deployment_status") if isinstance(metadata, dict) else None), deployment_context=DeploymentContext(environment=DeploymentEnvironment.other, deployment_name=str(manifest.get("deployment_name") or manifest.get("environment") or "imported"), systems_touched=[str(tool.get("external_system") or tool.get("tool_name")) for tool in manifest.get("tools", []) if isinstance(tool, dict) and (tool.get("external_system") or tool.get("tool_name"))], data_domains=[], notes="Generated from retained producer artifacts; does not establish deployment approval or operational effectiveness."), tool_inventory=tool_items, action_inventory=action_items, authority_model=AuthorityModelSummary(summary="Authority evidence imported from retained runtime records. This is not a grant or approval.", authority_scopes=[], privileged_action_types=sorted({item.action_type for item in action_items if item.authority_required}, key=lambda value: value.value), expiration_required=True, human_approval_required=any(item.review_required for item in action_items), notes="Authority Context profile references remain distinct from context-instance identifiers."), policy_controls=[PolicyControlSummary(control_name="Manifest declaration", description="Actions and requirements imported from Manifest v1.1. Declaration alone does not establish implementation.", control_status=ControlStatus.planned, evidence_reference="metadata.traceable_import.input_artifacts[manifest]"), PolicyControlSummary(control_name="Review and approval declaration", description="Manifest review_requirement and approval-related declarations are preserved for review support; declaration alone does not create human approval.", control_status=ControlStatus.planned, evidence_reference="manifest.actions[*].review_requirement"), PolicyControlSummary(control_name="Replay semantic import validation", description="The importer executed the accepted Replay semantic validator over retained producer records. This is import-time evidence checking, not evidence that runtime controls were operationally effective.", control_status=ControlStatus.implemented, evidence_reference="metadata.traceable_import.replay_semantic_validation"), PolicyControlSummary(control_name="Independent operational verification", description="No independent real-world effect verification supplied.", control_status=ControlStatus.planned, evidence_reference="metadata.traceable_import.lifecycle_summary.independent_verification")], replay_bundles=[ReplayBundleInventoryItem(bundle_id=bundle_id, run_id=str(bundle.get("run_id") or ""), status=str(bundle.get("status") or "unknown"), generated_at=None if generated == "unavailable" else str(generated), signed=bool(bundle.get("signature") or bundle.get("signatures") or bundle.get("integrity")), redacted=redacted, validation_status="semantically_valid", evidence_reference="metadata.traceable_import.source_record_refs")], validation_summary=ValidationSummary(valid_bundle_count=1, invalid_bundle_count=0, warning_count=len([finding for finding in findings if finding.get("severity") == "warning"]), error_count=0, summary="Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit."), metadata={"traceable_import": {"transformation_version": TRANSFORMATION_VERSION, "canonicalization_profile": CANONICALIZATION_PROFILE, "supported_revisions": {"manifest": MANIFEST_REVISION, "replay": REPLAY_REVISION, "control_plane": CONTROL_PLANE_REVISION, "moltbot_safe": MOLTBOT_SAFE_REVISION, "odes": ODES_REVISION, "gax_imx_experimental_reference": GAX_IMX_REVISION, "alvorada": ALVORADA_REVISION}, "replay_semantic_validation": {"validator": "agent_replay_bundle.importers.import_bounded_workflow", "required_revision": REPLAY_REVISION, "status": replay_validator_status}, "replay_import_reports": bundle.get("import_reports", []), "replay_semantics": bundle.get("semantics", {}), "input_artifacts": [{"artifact_role": "manifest", "artifact_id": _manifest_id(manifest), "version": _manifest_version(manifest), "hash": sha256(manifest), "trusted_revision": MANIFEST_REVISION, "verification_status": "digest_and_cross_artifact_binding_checked_when_runtime_proposal_present", "commitment_source": "locally_computed", "canonicalization_profile": CANONICALIZATION_PROFILE}, {"artifact_role": "reconstruction_bundle", "artifact_id": bundle_id, "version": _bundle_version(bundle), "hash": sha256(bundle), "trusted_revision": REPLAY_REVISION, "verification_status": replay_validator_status, "commitment_source": "locally_computed", "canonicalization_profile": CANONICALIZATION_PROFILE}], "producer_profiles": _producer_profile_summaries(bundle), "source_record_refs": _source_record_refs(bundle), "conversion_losses": _conversion_losses(bundle), "derived_counts": counts | {"authorization_granted_count": auth.get("authorized", 0), "authorization_held_count": auth.get("hold", 0), "authorization_denied_count": auth.get("deny", 0)}, "lifecycle_summary": lifecycle, "control_evidence_levels": evidence_levels, "redaction_state": {"redacted": redacted, "source": redaction_source, "derivation": bundle.get("derivation")}, "import_findings": findings, "manual_assessments": [], "unresolved_issues": [{"code": "U_INDEPENDENT_VERIFICATION_UNAVAILABLE", "severity": "warning", "message": "Destination observation is producer-retained unless independent verifier evidence is supplied."}, {"code": "U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED", "severity": "warning", "message": "Synthetic import success cannot support operational effectiveness or deployment approval."}, {"code": "U_HISTORICAL_AUTHORIZATION_NOT_CURRENT_PERMISSION", "severity": "info", "message": "Retained authorization is historical evidence only; current permission must be re-evaluated by the runtime authority/control boundary."}, {"code": "U_EXCHANGE_METADATA_SUPPLEMENTARY", "severity": "info", "message": "Accepted GAX/IMX exchange metadata remains supplementary unless represented by a supported Replay mapping; the Evidence Pack does not invent exchange fields."}], "outcomes_and_burden": {"unresolved_delivery": "see lifecycle_summary.destination_observed", "incidents": "unavailable_not_zero", "remedies": "unavailable", "measured_latency": "not_measured", "human_review_effort": "not_measured", "error_prevention": "not_measured", "error_correction": "not_measured", "comparison_baseline_reference": "unavailable"}}})
    return pack


def build_evidence_pack_from_artifacts(manifest: dict[str, Any], reconstruction_bundle: dict[str, Any], *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    return import_manifest_reconstruction(manifest, reconstruction_bundle, title=title, generated_at=generated_at)


def build_evidence_pack_from_files(manifest_path: str | Path, reconstruction_path: str | Path, *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with Path(reconstruction_path).open("r", encoding="utf-8") as handle:
        reconstruction_bundle = json.load(handle)
    return build_evidence_pack_from_artifacts(manifest, reconstruction_bundle, title=title, generated_at=generated_at)
