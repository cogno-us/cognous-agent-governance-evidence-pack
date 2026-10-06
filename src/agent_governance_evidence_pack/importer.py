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
    ValidationSummary,
)

TRANSFORMATION_VERSION = "agep-manifest-reconstruction-import/0.2.2"
CANONICALIZATION_PROFILE = "json-sort-keys-compact-utf8-no-nan"
MANIFEST_REVISION = "46c950bed37fe3812000895430bc0312d29e37ce"
REPLAY_REVISION = "f12648313cedc2cf06145d397fa56cdea18cc800"
CONTROL_PLANE_REVISION = "283500652d47a692fb0b99a1172a6d5faffbd9a7"
MOLTBOT_SAFE_REVISION = "6b0ba1185bcd390f71df947dda349415e4105f5f"
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
    if normalized in {"applied", "present", "delivered", "success", "succeeded", "executed"}:
        return "applied"
    if normalized in {"partial", "partially_applied", "partial_delivery"}:
        return "partial"
    if normalized in {"absent", "not_found", "not_applied"}:
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


def _retained_replay_inputs(bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in sorted(_records(bundle), key=lambda item: item.get("source_sequence", 0)):
        by_type[_record_type(record)].append(deepcopy(_data(record)))
    if len(by_type.get("runtime_proposal", [])) != 1:
        raise ImportContractError("importer supports exactly one retained runtime_proposal operation")
    if len(by_type.get("runtime_decision", [])) < 1:
        raise ImportContractError("reconstruction bundle must retain at least one runtime_decision")
    if len(by_type.get("execution_envelope", [])) != 1:
        raise ImportContractError("reconstruction bundle must retain exactly one execution_envelope")
    if len(by_type.get("execution_result", [])) != 1:
        raise ImportContractError("reconstruction bundle must retain exactly one execution_result")
    control_plane = {
        "run_id": bundle.get("run_id"),
        "decisions": by_type.get("runtime_decision", []),
        "attempts": by_type.get("control_plane_attempt_transition", []),
        "observations": by_type.get("effect_observation", []),
        "reconciliations": by_type.get("reconciliation", []),
    }
    proposal = by_type["runtime_proposal"][0]
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
    if status != "reconstruction_complete":
        raise ImportContractError(f"pinned Replay semantic validation returned status {status!r}")
    return "executed"


def _check_commitments(bundle: dict[str, Any], manifest: dict[str, Any]) -> None:
    grouped = _group(bundle)
    proposal = grouped["runtime_proposal"][0][2]
    decision = grouped["runtime_decision"][0][2]
    bind = _binding(decision)
    if bind is None:
        raise ImportContractError("authorized runtime_decision must include binding")
    if proposal.get("manifest_id") != _manifest_id(manifest):
        raise ImportContractError("proposal.manifest_id does not match supplied Manifest")
    if str(proposal.get("manifest_version")) != _manifest_version(manifest):
        raise ImportContractError("proposal.manifest_version does not match supplied Manifest")
    if proposal.get("manifest_digest") != sha256(manifest):
        raise ImportContractError("proposal.manifest_digest does not match supplied Manifest digest")
    if proposal.get("payload_commitment") != sha256(proposal.get("payload")):
        raise ImportContractError("proposal.payload_commitment does not match proposal.payload")
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
    attempts = {item[2].get("attempt_id") for item in grouped.get("destination_attempt", [])}
    attempts |= {_identifier(record, data, "attempt_id") for _, record, data in grouped.get("destination_attempt", [])}
    attempts.discard(None)
    result = grouped["execution_result"][0][2]
    if result.get("attempt_id") not in attempts:
        raise ImportContractError("execution_result.attempt_id does not reference a retained destination_attempt")
    if result.get("effect_id") != decision.get("effect_id"):
        raise ImportContractError("execution_result.effect_id does not match decision effect_id")
    effects = grouped.get("destination_effect", [])
    if not effects:
        raise ImportContractError("reconstruction bundle must retain at least one destination_effect")
    for _, _, destination in effects:
        if destination.get("effect_id") != decision.get("effect_id"):
            raise ImportContractError("destination_effect.effect_id does not match decision effect_id")
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
    required_checked = {"payload_commitment", "effect_id", "operation_digest"}
    if not required_checked <= checked:
        raise ImportContractError(f"required checked commitments missing: {sorted(required_checked - checked)}")


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
        bind = _binding(data)
        if result != "authorized" and bind:
            raise ImportContractError(f"decision {decision_id} result {result!r} cannot carry an authorization/effect binding")
        if result == "authorized" and not bind:
            raise ImportContractError(f"decision {decision_id} is authorized but has no binding")
        effect_id = _identifier(record, data, "effect_id")
        if effect_id:
            effects.add(effect_id)
    for record_type in ("execution_envelope", "execution_result", "destination_attempt", "destination_attempt_event", "effect_observation", "destination_effect", "reconciliation", "control_plane_attempt", "control_plane_attempt_transition"):
        for index, record, data in grouped.get(record_type, []):
            effect_id = _identifier(record, data, "effect_id")
            decision_id = _identifier(record, data, "decision_id")
            if effect_id and effect_id not in effects:
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


def _combined_state(counter: Counter[str]) -> str:
    if counter.get("revoked") or counter.get("contradictory") or counter.get("unresolved"):
        return "unresolved"
    if counter.get("partial"):
        return "partial"
    if counter.get("absent"):
        return "absent"
    if counter.get("unknown") or counter.get("unavailable"):
        return "unknown"
    if counter.get("applied"):
        return "applied"
    return "unknown"


def _state_counts(bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    grouped = _group(bundle)
    proposals: set[str] = set(); decisions: set[str] = set(); effects: set[str] = set(); control_attempts: set[str] = set(); executor_attempts: set[str] = set()
    transition_records = 0
    control_statuses: Counter[str] = Counter(); acknowledgement: Counter[str] = Counter(); observations: Counter[str] = Counter(); destination_effect_states: Counter[str] = Counter(); effect_observation_states: Counter[str] = Counter(); reconciliation_states: Counter[str] = Counter(); execution_result_states: Counter[str] = Counter()
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
                acknowledgement["unknown"] += 1
            elif record_type == "destination_attempt":
                attempt_id = _identifier(record, data, "attempt_id", "destination_attempt_id") or _record_id(record, index); executor_attempts.add("destination:" + attempt_id)
            elif record_type == "destination_attempt_event":
                transition_records += 1
            elif record_type == "execution_result":
                execution_result_states[_state_from_value(data.get("status") or data.get("observed_state"))] += 1
            elif record_type == "effect_observation":
                state = _observation_state(data); effect_observation_states[state] += 1; observations[state] += 1
            elif record_type == "destination_effect":
                state = _observation_state(data); destination_effect_states[state] += 1; observations[state] += 1
            elif record_type == "reconciliation":
                state = _observation_state(data); reconciliation_states[state] += 1; observations[state] += 1
    if not observations: observations["unavailable"] = 1
    if not acknowledgement: acknowledgement["unknown"] = 1
    counts = {"proposal_count": len(proposals), "decision_count": len(decisions), "distinct_effect_count": len(effects), "control_plane_attempt_count": len(control_attempts), "executor_attempt_count": len(executor_attempts), "attempt_transition_record_count": transition_records, "destination_effect_count": sum(destination_effect_states.values()), "effect_observation_count": sum(effect_observation_states.values()), "reconciliation_count": sum(reconciliation_states.values()), "destination_observation_counts": dict(sorted(observations.items())), "destination_effect_state_counts": dict(sorted(destination_effect_states.items())), "effect_observation_state_counts": dict(sorted(effect_observation_states.items())), "reconciliation_state_counts": dict(sorted(reconciliation_states.items())), "execution_result_state_counts": dict(sorted(execution_result_states.items())), "acknowledgement_counts": dict(sorted(acknowledgement.items())), "coverage_denominators": {"effect_denominator": "distinct authorized effect_id values", "control_plane_attempt_denominator": "unique Control Plane attempt IDs", "executor_attempt_denominator": "unique destination_attempt IDs", "destination_effect_denominator": "destination_effect records", "effect_observation_denominator": "effect_observation records", "reconciliation_denominator": "reconciliation records", "missing_observation": "unavailable, not zero/success/failure"}, "counting_rules": ["Repeated lifecycle records do not inflate attempt counts.", "Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.", "Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.", "Destination effects, effect observations and reconciliations are counted separately.", "Missing observations are unavailable, not success or failure.", "Applied evidence does not override contradictory partial, unresolved, absent or unknown evidence."]}
    lifecycle = {"authorization": "authorized", "execution_attempted": "yes" if control_attempts or executor_attempts else "no", "acknowledgement": "unknown" if acknowledgement.get("unknown") else "received", "control_plane_transition_statuses": dict(sorted(control_statuses.items())), "destination_observed": _combined_state(observations), "independent_verification": "unavailable", "notes": ["Control Plane transition status is preserved separately from acknowledgement receipt.", "A lost or unknown acknowledgement followed by an applied observation retains both facts.", "Reconstruction completeness does not mean effect completion.", "HMAC/shared-secret integrity is not public issuer identity or independent review.", "A software-generated pack cannot create human approval."]}
    return counts, lifecycle


def _source_record_refs(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"record_id": _record_id(record, index), "record_type": _record_type(record), "producer_profile_id": record.get("producer_profile_id"), "source_path": record.get("source_path") or f"records[{index}]", "hash": sha256(record)} for index, record in enumerate(bundle.get("records", [])) if isinstance(record, dict)]


def _redaction_status(bundle: dict[str, Any], findings: list[dict[str, Any]]) -> tuple[bool, str]:
    metadata = bundle.get("metadata") if isinstance(bundle.get("metadata"), dict) else {}
    redaction = bundle.get("redaction") or metadata.get("redaction") or metadata.get("redaction_state")
    if isinstance(redaction, dict):
        if redaction.get("redacted") is True or redaction.get("state") == "redacted": return True, "source_declared_redacted"
        if redaction.get("redacted") is False or redaction.get("state") == "unredacted": return False, "source_declared_unredacted"
    if redaction in (True, "redacted"): return True, "source_declared_redacted"
    if redaction in (False, "unredacted", "not_redacted"): return False, "source_declared_unredacted"
    findings.append({"code": "R_REDACTION_STATE_UNKNOWN", "severity": "warning", "path": "reconstruction_bundle.metadata.redaction", "message": "Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility."})
    return False, "unknown_schema_default_false"


def import_manifest_reconstruction(manifest: dict[str, Any], reconstruction_bundle: dict[str, Any], *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    manifest = deepcopy(_obj(manifest, "manifest")); bundle = deepcopy(_obj(reconstruction_bundle, "reconstruction_bundle"))
    actions, findings, auth, replay_validator_status = _semantic(manifest, bundle)
    action_items = _make_actions(actions, findings); counts, lifecycle = _state_counts(bundle)
    generated = bundle.get("generated_at") or (bundle.get("metadata", {}) if isinstance(bundle.get("metadata"), dict) else {}).get("source_generated_at") or generated_at or "unavailable"
    if generated == "unavailable": findings.append({"code": "T_GENERATED_AT_UNAVAILABLE", "severity": "warning", "path": "reconstruction_bundle.generated_at", "message": "No source generation timestamp supplied; importer did not invent one."})
    bundle_id = str(bundle.get("bundle_id") or bundle.get("reconstruction_bundle_id") or bundle.get("run_id") or "unknown_bundle")
    pack_id = "agep-" + sha256({"manifest": sha256(manifest), "bundle": sha256(bundle), "transformation": TRANSFORMATION_VERSION})[7:23]
    redacted, redaction_source = _redaction_status(bundle, findings)
    metadata = bundle.get("metadata") if isinstance(bundle.get("metadata"), dict) else {}
    pack = EvidencePack(pack_id=pack_id, pack_version="0.2.0", title=title or "Traceable Agent Governance Evidence Pack", generated_at=str(generated), review_status=ReviewStatus.draft, agent_overview=AgentOverview(agent_name=str(manifest.get("agent_name") or (manifest.get("agent", {}) if isinstance(manifest.get("agent"), dict) else {}).get("name") or "ImportedAgent"), agent_description=manifest.get("agent_description") or (manifest.get("agent", {}) if isinstance(manifest.get("agent"), dict) else {}).get("description"), business_purpose=str(manifest.get("business_purpose") or manifest.get("purpose") or "Imported from Manifest and Reconstruction Bundle; business purpose unavailable."), owner=manifest.get("owner") if isinstance(manifest.get("owner"), str) else None, business_unit=manifest.get("business_unit") if isinstance(manifest.get("business_unit"), str) else None, lifecycle_stage=metadata.get("deployment_status") if isinstance(metadata, dict) else None), deployment_context=DeploymentContext(environment=DeploymentEnvironment.other, deployment_name=str(manifest.get("deployment_name") or manifest.get("environment") or "imported"), systems_touched=[str(tool.get("external_system") or tool.get("tool_name")) for tool in manifest.get("tools", []) if isinstance(tool, dict) and (tool.get("external_system") or tool.get("tool_name"))], data_domains=[], notes="Generated from retained producer artifacts; does not establish deployment approval or operational effectiveness."), action_inventory=action_items, authority_model=AuthorityModelSummary(summary="Authority evidence imported from retained runtime records. This is not a grant or approval.", authority_scopes=[], privileged_action_types=sorted({item.action_type for item in action_items if item.authority_required}, key=lambda value: value.value), expiration_required=True, human_approval_required=any(item.review_required for item in action_items), notes="Authority Context profile references remain distinct from context-instance identifiers."), policy_controls=[PolicyControlSummary(control_name="Manifest declaration", description="Actions and requirements imported from Manifest v1.1. Declaration alone does not establish implementation.", control_status=ControlStatus.planned, evidence_reference="metadata.traceable_import.input_artifacts[manifest]"), PolicyControlSummary(control_name="Pinned Replay semantic validation", description="Retained producer records were validated through the pinned Replay semantic validator.", control_status=ControlStatus.implemented, evidence_reference="metadata.traceable_import.replay_semantic_validation"), PolicyControlSummary(control_name="Independent operational verification", description="No independent real-world effect verification supplied.", control_status=ControlStatus.planned, evidence_reference="metadata.traceable_import.lifecycle_summary.independent_verification")], replay_bundles=[ReplayBundleInventoryItem(bundle_id=bundle_id, run_id=str(bundle.get("run_id") or ""), status=str(bundle.get("status") or "unknown"), generated_at=None if generated == "unavailable" else str(generated), signed=bool(bundle.get("signature") or bundle.get("signatures")), redacted=redacted, validation_status="semantically_valid", evidence_reference="metadata.traceable_import.source_record_refs")], validation_summary=ValidationSummary(valid_bundle_count=1, invalid_bundle_count=0, warning_count=len([finding for finding in findings if finding.get("severity") == "warning"]), error_count=0, summary="Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit."), metadata={"traceable_import": {"transformation_version": TRANSFORMATION_VERSION, "canonicalization_profile": CANONICALIZATION_PROFILE, "supported_revisions": {"manifest": MANIFEST_REVISION, "replay": REPLAY_REVISION, "control_plane": CONTROL_PLANE_REVISION, "moltbot_safe": MOLTBOT_SAFE_REVISION, "alvorada": ALVORADA_REVISION}, "replay_semantic_validation": {"validator": "agent_replay_bundle.importers.import_bounded_workflow", "required_revision": REPLAY_REVISION, "status": replay_validator_status}, "input_artifacts": [{"artifact_role": "manifest", "artifact_id": _manifest_id(manifest), "version": _manifest_version(manifest), "hash": sha256(manifest), "trusted_revision": MANIFEST_REVISION}, {"artifact_role": "reconstruction_bundle", "artifact_id": bundle_id, "version": _bundle_version(bundle), "hash": sha256(bundle), "trusted_revision": REPLAY_REVISION}], "source_record_refs": _source_record_refs(bundle), "derived_counts": counts | {"authorization_granted_count": auth.get("authorized", 0), "authorization_held_count": auth.get("hold", 0), "authorization_denied_count": auth.get("deny", 0)}, "lifecycle_summary": lifecycle, "control_evidence_levels": {"declared": {"status": "present", "evidence": ["manifest"]}, "implemented": {"status": "not_inferred_from_manifest", "evidence": []}, "tested": {"status": "unavailable", "evidence": []}, "tested_in_this_repository": {"status": "importer_tests_only", "evidence": ["tests/test_importer.py"]}, "operationally_observed": {"status": "unavailable", "evidence": []}, "independently_audited": {"status": "unavailable", "evidence": []}}, "redaction_state": {"redacted": redacted, "source": redaction_source}, "import_findings": findings, "manual_assessments": [], "unresolved_issues": [{"code": "U_INDEPENDENT_VERIFICATION_UNAVAILABLE", "severity": "warning", "message": "Destination observation is producer-retained unless independent verifier evidence is supplied."}, {"code": "U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED", "severity": "warning", "message": "Synthetic import success cannot support operational effectiveness or deployment approval."}], "outcomes_and_burden": {"unresolved_delivery": "see lifecycle_summary.destination_observed", "incidents": "unavailable_not_zero", "remedies": "unavailable", "measured_latency": "not_measured", "human_review_effort": "not_measured", "error_prevention": "not_measured", "error_correction": "not_measured", "comparison_baseline_reference": "unavailable"}}})
    return pack


def build_evidence_pack_from_artifacts(manifest: dict[str, Any], reconstruction_bundle: dict[str, Any], *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    return import_manifest_reconstruction(manifest, reconstruction_bundle, title=title, generated_at=generated_at)


def build_evidence_pack_from_files(manifest_path: str | Path, reconstruction_path: str | Path, *, title: str | None = None, generated_at: str | None = None) -> EvidencePack:
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with Path(reconstruction_path).open("r", encoding="utf-8") as handle:
        reconstruction_bundle = json.load(handle)
    return build_evidence_pack_from_artifacts(manifest, reconstruction_bundle, title=title, generated_at=generated_at)
