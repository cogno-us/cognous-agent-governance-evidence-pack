"""Traceable imports from Manifest and Reconstruction Bundle artifacts.

The importer is deliberately conservative. It derives a business-readable
EvidencePack from supplied artifacts, but it does not treat reconstruction,
HMAC integrity, or a serialized checked_match label as deployment approval,
independent verification, or effect completion.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .models import (
    ActionInventoryItem,
    ActionType,
    AgentOverview,
    AuthorityModelSummary,
    BlockedActionSummary,
    ControlStatus,
    DeploymentContext,
    DeploymentEnvironment,
    EvidencePack,
    PolicyControlSummary,
    RelianceSummary,
    ReplayBundleInventoryItem,
    RiskRegisterItem,
    RiskSeverity,
    RiskStatus,
    ToolInventoryItem,
    ValidationSummary,
)

TRANSFORMATION_VERSION = "agep-manifest-reconstruction-import/0.2.0"
CANONICALIZATION_PROFILE = "canonical-json-sort-keys-no-whitespace-v1"
SUPPORTED_MANIFEST_VERSIONS = {"1.1", "v1.1", "1.1.0", "v1.1.0"}
SUPPORTED_RECONSTRUCTION_BUNDLE_VERSIONS = {"0.2.0", "reconstruction-bundle/0.2.0", None}

PINNED_PRODUCER_REVISIONS = {
    "manifest": "46c950bed37fe3812000895430bc0312d29e37ce",
    "replay_bundle": "f12648313cedc2cf06145d397fa56cdea18cc800",
    "control_plane": "283500652d47a692fb0b99a1172a6d5faffbd9a7",
    "moltbot_safe": "6b0ba1185bcd390f71df947dda349415e4105f5f",
    "alvorada": "fb3d97938969a89e149e8ff8db2756091d1233fc",
}


class ImportErrorDetail(ValueError):
    """Raised when supplied artifacts violate the supported import contract."""


def canonical_bytes(value: Any) -> bytes:
    """Return deterministic JSON bytes for hashing import inputs."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ImportErrorDetail(f"{p} must contain a JSON object")
    return payload


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first(*values: Any, default: Any = None) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return default


def _enum_action_type(value: Any) -> ActionType:
    if isinstance(value, str):
        normalized = value.lower().replace("-", "_")
        if normalized in ActionType.__members__:
            return ActionType[normalized]
        try:
            return ActionType(normalized)
        except ValueError:
            return ActionType.other
    return ActionType.other


def _enum_environment(value: Any) -> DeploymentEnvironment:
    if isinstance(value, str):
        normalized = value.lower()
        try:
            return DeploymentEnvironment(normalized)
        except ValueError:
            return DeploymentEnvironment.other
    return DeploymentEnvironment.other


def _control_status(value: Any) -> ControlStatus:
    if isinstance(value, str):
        normalized = value.lower()
        try:
            return ControlStatus(normalized)
        except ValueError:
            return ControlStatus.partial
    return ControlStatus.partial


def _manifest_version(manifest: dict[str, Any]) -> str | None:
    return _first(
        manifest.get("manifest_version"),
        manifest.get("version"),
        _as_dict(manifest.get("metadata")).get("manifest_version"),
    )


def _manifest_id(manifest: dict[str, Any]) -> str:
    return str(_first(manifest.get("manifest_id"), manifest.get("id"), manifest.get("name"), default="manifest-unknown"))


def _reconstruction_version(bundle: dict[str, Any]) -> str | None:
    return _first(
        bundle.get("bundle_version"),
        bundle.get("schema_version"),
        bundle.get("reconstruction_bundle_version"),
        _as_dict(bundle.get("metadata")).get("reconstruction_bundle_version"),
    )


def _validate_supported_inputs(manifest: dict[str, Any], reconstruction: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    mv = _manifest_version(manifest)
    if mv not in SUPPORTED_MANIFEST_VERSIONS:
        raise ImportErrorDetail(f"unsupported manifest version: {mv!r}; supported={sorted(SUPPORTED_MANIFEST_VERSIONS)}")
    rv = _reconstruction_version(reconstruction)
    if rv not in SUPPORTED_RECONSTRUCTION_BUNDLE_VERSIONS:
        raise ImportErrorDetail(f"unsupported reconstruction bundle version: {rv!r}")
    if not isinstance(reconstruction.get("records"), list):
        raise ImportErrorDetail("reconstruction bundle must contain a records array")
    if reconstruction.get("status") == "reconstruction_complete":
        findings.append({
            "code": "IMPORT_RECONSTRUCTION_NOT_EFFECT_COMPLETION",
            "severity": "notice",
            "message": "reconstruction_complete indicates record reconstruction only; it is not evidence of destination effect completion.",
            "source": "reconstruction.status",
        })
    return findings


@dataclass(frozen=True)
class IndexedRecords:
    records: list[dict[str, Any]]
    by_type: dict[str, list[dict[str, Any]]]


def _index_records(reconstruction: dict[str, Any]) -> IndexedRecords:
    records = [r for r in _as_list(reconstruction.get("records")) if isinstance(r, dict)]
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_type[str(record.get("record_type", "unknown"))].append(record)
    return IndexedRecords(records=records, by_type=dict(by_type))


def _record_ref(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id"),
        "record_type": record.get("record_type"),
        "producer_profile_id": record.get("producer_profile_id"),
        "source_path": record.get("source_path"),
        "hash": sha256_digest(record),
    }


def _record_id(record: dict[str, Any], *keys: str) -> str | None:
    identifiers = _as_dict(record.get("identifiers"))
    data = _as_dict(record.get("data"))
    for key in keys:
        value = identifiers.get(key)
        if value not in (None, ""):
            return str(value)
        value = data.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _data(record: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(record.get("data"))


def derive_counts(index: IndexedRecords) -> dict[str, Any]:
    """Compute deterministic counts without inflating repeated lifecycle records."""
    proposal_records = index.by_type.get("runtime_proposal", []) + index.by_type.get("action_proposal", [])
    decision_records = index.by_type.get("runtime_decision", []) + index.by_type.get("policy_decision", [])
    cp_attempt_records = index.by_type.get("control_plane_attempt_transition", [])
    executor_attempt_records = (
        index.by_type.get("execution_attempt", [])
        + index.by_type.get("executor_attempt", [])
        + index.by_type.get("moltbot_attempt", [])
    )
    observation_records = index.by_type.get("effect_observation", [])

    proposals = {rid for r in proposal_records if (rid := _record_id(r, "action_id", "proposal_id"))}
    decisions = {rid for r in decision_records if (rid := _record_id(r, "decision_id"))}
    effects = {rid for r in decision_records + observation_records + cp_attempt_records if (rid := _record_id(r, "effect_id"))}
    cp_attempts = {rid for r in cp_attempt_records if (rid := _record_id(r, "attempt_id"))}
    executor_attempts = {rid for r in executor_attempt_records if (rid := _record_id(r, "attempt_id"))}

    destination_states: dict[str, int] = {"applied": 0, "absent": 0, "partial": 0, "unknown": 0}
    for record in observation_records:
        state = str(_data(record).get("state", "unknown"))
        if state not in destination_states:
            state = "unknown"
        destination_states[state] += 1

    held = 0
    granted = 0
    for record in decision_records:
        result = str(_first(_data(record).get("result"), _data(record).get("decision"), default="")).lower()
        if result in {"allow", "allowed", "authorize", "authorized", "granted"} or _data(record).get("binding"):
            granted += 1
        elif result in {"block", "blocked", "hold", "held", "escalate", "denied", "reject", "rejected"}:
            held += 1

    return {
        "proposal_count": len(proposals),
        "decision_count": len(decisions),
        "distinct_effect_count": len(effects),
        "control_plane_attempt_count": len(cp_attempts),
        "executor_attempt_count": len(executor_attempts),
        "attempt_transition_record_count": len(cp_attempt_records) + len(executor_attempt_records),
        "authorization_granted_count": granted,
        "authorization_held_count": held,
        "destination_observation_counts": destination_states,
        "coverage_denominators": {
            "effects": len(effects),
            "control_plane_attempts": len(cp_attempts),
            "executor_attempts": len(executor_attempts),
            "destination_observations": len(observation_records),
        },
        "counting_rules": [
            "proposal_count counts distinct action/proposal identifiers, not lifecycle records.",
            "decision_count counts distinct decision_id values.",
            "distinct_effect_count counts distinct effect_id values and is not inflated by duplicate submission or restart records.",
            "control_plane_attempt_count and executor_attempt_count are separate namespaces unless an explicit correlation appears in source records.",
            "missing observations are represented as unavailable and are not counted as zero, failed, or successful effects by default.",
        ],
    }


def derive_lifecycle(index: IndexedRecords, counts: dict[str, Any]) -> dict[str, Any]:
    observation_counts = counts["destination_observation_counts"]
    attempted = counts["control_plane_attempt_count"] > 0 or counts["executor_attempt_count"] > 0
    acknowledgement = "unknown"
    for record in index.by_type.get("control_plane_attempt_transition", []) + index.by_type.get("execution_attempt", []):
        data = _data(record)
        status = str(_first(data.get("acknowledgement"), data.get("ack_status"), data.get("status"), default="")).lower()
        if status in {"acknowledged", "received", "completed", "success"} or data.get("acknowledged") is True:
            acknowledgement = "received"
            break
    destination = "unavailable"
    if observation_counts["partial"]:
        destination = "partial"
    elif observation_counts["applied"]:
        destination = "applied"
    elif observation_counts["absent"]:
        destination = "absent"
    elif observation_counts["unknown"]:
        destination = "unknown"
    return {
        "authorization": "granted" if counts["authorization_granted_count"] else ("held" if counts["authorization_held_count"] else "unavailable"),
        "execution_attempted": attempted,
        "acknowledgement": acknowledgement if attempted else "not_applicable",
        "destination_observed": destination,
        "independent_verification": "unavailable",
        "notes": [
            "A lost acknowledgement followed by an applied observation remains represented as separate facts when both source records exist.",
            "Destination observation is derived from source observation records only; absence of observation is not treated as failure or success.",
        ],
    }


def _manifest_actions(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return _as_list(_first(manifest.get("actions"), manifest.get("tool_actions"), manifest.get("action_inventory"), default=[]))


def _manifest_tools(manifest: dict[str, Any], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tools = _as_list(_first(manifest.get("tools"), manifest.get("tool_inventory"), default=[]))
    if tools:
        return [t for t in tools if isinstance(t, dict)]
    by_name: dict[str, dict[str, Any]] = {}
    for action in actions:
        if not isinstance(action, dict):
            continue
        tool_name = _first(action.get("tool_name"), action.get("tool"), action.get("adapter_id"), default="unknown-tool")
        by_name.setdefault(str(tool_name), {"tool_name": str(tool_name), "description": "Derived from manifest action references."})
    return list(by_name.values())


def _build_tool_inventory(tools: list[dict[str, Any]]) -> list[ToolInventoryItem]:
    out: list[ToolInventoryItem] = []
    for tool in tools:
        out.append(ToolInventoryItem(
            tool_name=str(_first(tool.get("tool_name"), tool.get("name"), tool.get("id"), default="unknown-tool")),
            description=_first(tool.get("description"), tool.get("purpose")),
            external_system=_first(tool.get("external_system"), tool.get("system"), tool.get("adapter_id")),
            data_classification=_first(tool.get("data_classification"), tool.get("classification")),
            access_mode=_first(tool.get("access_mode"), tool.get("mode")),
            control_status=_control_status(tool.get("control_status")),
        ))
    return out


def _build_action_inventory(actions: list[dict[str, Any]]) -> list[ActionInventoryItem]:
    out: list[ActionInventoryItem] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        review = bool(_first(action.get("review_required"), action.get("human_review_required"), default=False))
        authority = bool(_first(action.get("authority_required"), action.get("requires_authority"), action.get("privileged"), default=False))
        out.append(ActionInventoryItem(
            action_name=str(_first(action.get("action_name"), action.get("name"), action.get("action_id"), default="unknown-action")),
            tool_name=str(_first(action.get("tool_name"), action.get("tool"), action.get("adapter_id"), default="unknown-tool")),
            action_type=_enum_action_type(_first(action.get("action_type"), action.get("type"))),
            description=_first(action.get("description"), action.get("purpose")),
            authority_required=authority,
            review_required=review,
            reliance_required=bool(_first(action.get("reliance_required"), default=False)),
            default_posture=_first(action.get("default_posture"), action.get("default")),
            control_status=_control_status(action.get("control_status")),
        ))
    return out


def _blocked_actions(index: IndexedRecords) -> list[BlockedActionSummary]:
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in index.by_type.get("blocked_action", []):
        data = _data(record)
        key = (
            str(_first(data.get("action_name"), data.get("action_id"), default="unknown")),
            str(_first(data.get("action_type"), default="other")),
            str(_first(data.get("tool_name"), default="unknown")),
        )
        item = groups.setdefault(key, {"count": 0, "reasons": set(), "refs": []})
        item["count"] += 1
        if data.get("reason"):
            item["reasons"].add(str(data["reason"]))
        item["refs"].append(record.get("record_id"))
    return [
        BlockedActionSummary(
            action_name=k[0], action_type=_enum_action_type(k[1]), tool_name=k[2], count=v["count"],
            reason_summary="; ".join(sorted(v["reasons"])) or None,
            evidence_reference=", ".join(str(r) for r in v["refs"] if r),
        )
        for k, v in sorted(groups.items())
    ]


def _reliance_summary(index: IndexedRecords) -> list[RelianceSummary]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for record in index.by_type.get("reliance_record", []):
        data = _data(record)
        key = (
            str(_first(data.get("source_name"), default="unknown-source")),
            str(_first(data.get("source_type"), default="other")),
        )
        item = groups.setdefault(key, {"count": 0, "scopes": set(), "refs": []})
        item["count"] += 1
        if data.get("scope"):
            item["scopes"].add(str(data["scope"]))
        item["refs"].append(record.get("record_id"))
    return [
        RelianceSummary(
            source_name=k[0], source_type=k[1], count=v["count"],
            scope_summary="; ".join(sorted(v["scopes"])) or None,
            evidence_reference=", ".join(str(r) for r in v["refs"] if r),
        )
        for k, v in sorted(groups.items())
    ]


def _import_findings(reconstruction: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for report in _as_list(reconstruction.get("import_reports")):
        if not isinstance(report, dict):
            continue
        for finding in _as_list(report.get("findings")):
            if isinstance(finding, dict):
                findings.append(finding)
    return findings


def build_evidence_pack_from_artifacts(
    manifest: dict[str, Any],
    reconstruction: dict[str, Any],
    *,
    pack_id: str | None = None,
    title: str | None = None,
    generated_at: str = "1970-01-01T00:00:00Z",
    manual_assessments: list[dict[str, Any]] | None = None,
) -> EvidencePack:
    """Derive an EvidencePack from actual Manifest and Reconstruction Bundle artifacts."""
    import_findings = _validate_supported_inputs(manifest, reconstruction)
    import_findings.extend(_import_findings(reconstruction))
    index = _index_records(reconstruction)
    counts = derive_counts(index)
    lifecycle = derive_lifecycle(index, counts)
    manifest_actions = _manifest_actions(manifest)
    manifest_tools = _manifest_tools(manifest, manifest_actions)
    manifest_digest = sha256_digest(manifest)
    reconstruction_digest = sha256_digest(reconstruction)

    metadata = _as_dict(reconstruction.get("metadata"))
    frame = next(iter(index.by_type.get("run_frame", [])), {})
    frame_data = _data(frame)
    agent_name = str(_first(
        manifest.get("agent_name"), _as_dict(manifest.get("agent")).get("name"), frame_data.get("actor"), default="ImportedAgent"
    ))
    environment = _enum_environment(_first(
        manifest.get("environment"), _as_dict(manifest.get("deployment_context")).get("environment"), frame_data.get("environment"), default="other"
    ))

    validation_errors = sum(1 for f in import_findings if f.get("severity") == "error")
    validation_warnings = sum(1 for f in import_findings if f.get("severity") in {"warning", "notice"})
    risks: list[RiskRegisterItem] = []
    for n, finding in enumerate(import_findings, start=1):
        severity = RiskSeverity.medium if finding.get("severity") == "warning" else RiskSeverity.low
        risks.append(RiskRegisterItem(
            risk_id=f"import-finding-{n}",
            title=str(finding.get("code", "import_finding")),
            description=str(finding.get("message", "Import finding without message.")),
            severity=severity,
            status=RiskStatus.open,
            mitigation="Resolve source artifact limitation or document review impact before relying on this pack for approval.",
            owner="pack reviewer",
            evidence_reference=str(finding.get("path") or finding.get("source") or "import_reports"),
        ))

    if not index.by_type.get("effect_observation"):
        risks.append(RiskRegisterItem(
            risk_id="missing-destination-observation",
            title="Destination observation unavailable",
            description="No effect_observation records were present. Missing observations are not zero effects, failed effects, or successful effects by default.",
            severity=RiskSeverity.medium,
            status=RiskStatus.open,
            mitigation="Provide destination observation or keep delivery/effect status unresolved.",
            owner="pack reviewer",
            evidence_reference="reconstruction.records[effect_observation]",
        ))

    return EvidencePack(
        pack_id=pack_id or f"agep-{_manifest_id(manifest)}-{str(reconstruction.get('run_id', 'run-unknown'))}",
        pack_version="0.2.0",
        title=title or f"{agent_name} — Traceable Governance Evidence Pack",
        generated_at=generated_at,
        review_status="draft",
        agent_overview=AgentOverview(
            agent_name=agent_name,
            agent_description=_first(manifest.get("description"), _as_dict(manifest.get("agent")).get("description")),
            business_purpose=str(_first(manifest.get("business_purpose"), manifest.get("purpose"), frame_data.get("task"), default="Imported from manifest and reconstruction artifacts.")),
            owner=_first(manifest.get("owner"), _as_dict(manifest.get("agent")).get("owner")),
            business_unit=_first(manifest.get("business_unit"), _as_dict(manifest.get("agent")).get("business_unit")),
            lifecycle_stage=_first(manifest.get("lifecycle_stage"), default="imported_review"),
        ),
        deployment_context=DeploymentContext(
            environment=environment,
            deployment_name=_first(manifest.get("deployment_name"), _as_dict(manifest.get("deployment_context")).get("deployment_name")),
            systems_touched=[str(t) for t in _as_list(_first(manifest.get("systems_touched"), _as_dict(manifest.get("deployment_context")).get("systems_touched"), default=[]))],
            data_domains=[str(t) for t in _as_list(_first(manifest.get("data_domains"), _as_dict(manifest.get("deployment_context")).get("data_domains"), default=[]))],
            notes="Generated from supplied Manifest and Reconstruction Bundle artifacts; no effect is created by import.",
        ),
        tool_inventory=_build_tool_inventory(manifest_tools),
        action_inventory=_build_action_inventory(manifest_actions),
        authority_model=AuthorityModelSummary(
            summary="Imported authority evidence is record-level evidence only. It does not create or renew authority.",
            authority_scopes=[str(s) for s in _as_list(_first(manifest.get("authority_scopes"), default=[]))],
            privileged_action_types=sorted({a.action_type for a in _build_action_inventory(manifest_actions) if a.authority_required}, key=lambda x: x.value),
            expiration_required=True,
            human_approval_required=any(a.review_required for a in _build_action_inventory(manifest_actions)),
            notes="Authority Context profile references remain distinct from authority context instance identifiers.",
        ),
        policy_controls=[
            PolicyControlSummary(
                control_name="Traceable import",
                description="Every derived count and conclusion is tied to canonical input digests, transformation version, and source-record references in metadata.traceable_import.",
                control_status=ControlStatus.implemented,
                evidence_reference="metadata.traceable_import",
            ),
            PolicyControlSummary(
                control_name="Review support boundary",
                description="Synthetic tests, reconstruction, and schema validity do not establish deployment approval, compliance, or operational effectiveness.",
                control_status=ControlStatus.implemented,
                evidence_reference="metadata.traceable_import.control_evidence_levels",
            ),
        ],
        blocked_actions=_blocked_actions(index),
        reliance_summary=_reliance_summary(index),
        replay_bundles=[ReplayBundleInventoryItem(
            bundle_id=str(_first(reconstruction.get("bundle_id"), metadata.get("source_bundle_id"), default="reconstruction-bundle")),
            run_id=str(_first(reconstruction.get("run_id"), default="run-unknown")),
            status=str(_first(reconstruction.get("status"), default="unknown")),
            generated_at=_first(metadata.get("source_generated_at"), reconstruction.get("generated_at")),
            signed=False,
            redacted=bool(metadata.get("redacted", False)),
            validation_status="valid_for_import" if validation_errors == 0 else "import_errors",
            evidence_reference="metadata.traceable_import.input_artifacts[1]",
        )],
        validation_summary=ValidationSummary(
            valid_bundle_count=1 if validation_errors == 0 else 0,
            invalid_bundle_count=0 if validation_errors == 0 else 1,
            warning_count=validation_warnings,
            error_count=validation_errors,
            summary="Import validation checks structure, references visible in the supplied artifacts, and deterministic derivation only. It does not perform public issuer identity verification or independent effect verification.",
        ),
        risk_register=risks,
        review_records=[],
        metadata={
            "traceable_import": {
                "transformation_version": TRANSFORMATION_VERSION,
                "canonicalization_profile": CANONICALIZATION_PROFILE,
                "input_artifacts": [
                    {"artifact_role": "manifest", "artifact_id": _manifest_id(manifest), "version": _manifest_version(manifest), "hash": manifest_digest},
                    {"artifact_role": "reconstruction_bundle", "artifact_id": str(_first(reconstruction.get("bundle_id"), metadata.get("source_bundle_id"), default="reconstruction-bundle")), "version": _reconstruction_version(reconstruction), "hash": reconstruction_digest},
                ],
                "producer_revisions": PINNED_PRODUCER_REVISIONS | _as_dict(reconstruction.get("metadata")),
                "derived_counts": counts,
                "lifecycle_summary": lifecycle,
                "control_evidence_levels": {
                    "declared": {"status": "present_when_manifest_fields_exist", "evidence": ["manifest"]},
                    "implemented": {"status": "reported_not_proven", "evidence": ["manifest.control_status", "policy_controls"]},
                    "tested": {"status": "synthetic_only_when_source_test_records_are_supplied", "evidence": ["reconstruction.import_reports", "validation_summary"]},
                    "operationally_observed": {"status": "unavailable_unless_supplied_by_independent_observation", "evidence": []},
                },
                "source_record_refs": [_record_ref(r) for r in index.records],
                "import_findings": import_findings,
                "manual_assessments": manual_assessments or [],
                "provenance_contract": [
                    "Imported facts, computed summaries, and manual assessments remain separate.",
                    "Manual additions require attributable provenance and do not overwrite generated findings.",
                    "HMAC integrity, where present upstream, is shared-secret integrity and not public issuer identity or independent review.",
                    "Original and redacted derivative identities must remain distinct; original commitments do not verify modified content.",
                ],
            }
        },
    )


def build_evidence_pack_from_files(
    manifest_path: str | Path,
    reconstruction_path: str | Path,
    *,
    pack_id: str | None = None,
    title: str | None = None,
    generated_at: str = "1970-01-01T00:00:00Z",
) -> EvidencePack:
    return build_evidence_pack_from_artifacts(
        load_json(manifest_path),
        load_json(reconstruction_path),
        pack_id=pack_id,
        title=title,
        generated_at=generated_at,
    )
