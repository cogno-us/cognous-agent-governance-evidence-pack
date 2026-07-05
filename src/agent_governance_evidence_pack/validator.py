"""
Validator for Agent Governance Evidence Pack.

Implements all error and warning checks described in the specification.
"""

from __future__ import annotations

from .models import (
    ActionType,
    EvidencePack,
    ReviewStatus,
    RiskSeverity,
    RiskStatus,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)


def _error(code: str, message: str, path: str | None = None) -> ValidationIssue:
    return ValidationIssue(
        severity=ValidationSeverity.error,
        code=code,
        message=message,
        path=path,
    )


def _warning(code: str, message: str, path: str | None = None) -> ValidationIssue:
    return ValidationIssue(
        severity=ValidationSeverity.warning,
        code=code,
        message=message,
        path=path,
    )


_PRIVILEGED_TYPES = {
    ActionType.external_send,
    ActionType.delete,
    ActionType.purchase,
    ActionType.approve,
}


def validate_evidence_pack(pack: EvidencePack) -> ValidationReport:
    """Validate an EvidencePack and return a ValidationReport.

    Returns a report with valid=True only when there are no error-severity issues.
    Warnings do not affect validity.
    """
    issues: list[ValidationIssue] = []

    # ------------------------------------------------------------------ #
    # Errors
    # ------------------------------------------------------------------ #

    # 1. pack_id must be non-empty
    if not pack.pack_id or not pack.pack_id.strip():
        issues.append(_error("E001", "pack_id must be non-empty.", "pack_id"))

    # 2. title must be non-empty
    if not pack.title or not pack.title.strip():
        issues.append(_error("E002", "title must be non-empty.", "title"))

    # 3. generated_at must be non-empty
    if not pack.generated_at or not pack.generated_at.strip():
        issues.append(
            _error("E003", "generated_at must be non-empty.", "generated_at")
        )

    # 4. agent_overview.agent_name must be non-empty
    if not pack.agent_overview.agent_name or not pack.agent_overview.agent_name.strip():
        issues.append(
            _error(
                "E004",
                "agent_overview.agent_name must be non-empty.",
                "agent_overview.agent_name",
            )
        )

    # 5. agent_overview.business_purpose must be non-empty
    if (
        not pack.agent_overview.business_purpose
        or not pack.agent_overview.business_purpose.strip()
    ):
        issues.append(
            _error(
                "E005",
                "agent_overview.business_purpose must be non-empty.",
                "agent_overview.business_purpose",
            )
        )

    # 6. deployment_context.environment must be present (enforced by Pydantic, but belt-and-suspenders)
    if pack.deployment_context.environment is None:
        issues.append(
            _error(
                "E006",
                "deployment_context.environment must be present.",
                "deployment_context.environment",
            )
        )

    # 7. tool_inventory tool_name values must be unique
    tool_names = [item.tool_name for item in pack.tool_inventory]
    seen_tool_names: set[str] = set()
    for name in tool_names:
        if name in seen_tool_names:
            issues.append(
                _error(
                    "E007",
                    f"Duplicate tool_name '{name}' in tool_inventory.",
                    "tool_inventory",
                )
            )
        seen_tool_names.add(name)

    # 8. action_inventory action_name values must be unique
    action_names = [item.action_name for item in pack.action_inventory]
    seen_action_names: set[str] = set()
    for name in action_names:
        if name in seen_action_names:
            issues.append(
                _error(
                    "E008",
                    f"Duplicate action_name '{name}' in action_inventory.",
                    "action_inventory",
                )
            )
        seen_action_names.add(name)

    # 9. every ActionInventoryItem.tool_name must reference an existing ToolInventoryItem
    valid_tool_names = {item.tool_name for item in pack.tool_inventory}
    for action in pack.action_inventory:
        if action.tool_name not in valid_tool_names:
            issues.append(
                _error(
                    "E009",
                    f"Action '{action.action_name}' references unknown tool '{action.tool_name}'.",
                    "action_inventory",
                )
            )

    # 10. blocked action count must not be negative
    for i, blocked in enumerate(pack.blocked_actions):
        if blocked.count < 0:
            issues.append(
                _error(
                    "E010",
                    f"blocked_actions[{i}].count must not be negative.",
                    f"blocked_actions[{i}].count",
                )
            )

    # 11. reliance count must not be negative
    for i, reliance in enumerate(pack.reliance_summary):
        if reliance.count < 0:
            issues.append(
                _error(
                    "E011",
                    f"reliance_summary[{i}].count must not be negative.",
                    f"reliance_summary[{i}].count",
                )
            )

    # 12. risk_register risk_id values must be unique
    seen_risk_ids: set[str] = set()
    for risk in pack.risk_register:
        if risk.risk_id in seen_risk_ids:
            issues.append(
                _error(
                    "E012",
                    f"Duplicate risk_id '{risk.risk_id}' in risk_register.",
                    "risk_register",
                )
            )
        seen_risk_ids.add(risk.risk_id)

    # 13. replay_bundles bundle_id values must be unique
    seen_bundle_ids: set[str] = set()
    for bundle in pack.replay_bundles:
        if bundle.bundle_id in seen_bundle_ids:
            issues.append(
                _error(
                    "E013",
                    f"Duplicate bundle_id '{bundle.bundle_id}' in replay_bundles.",
                    "replay_bundles",
                )
            )
        seen_bundle_ids.add(bundle.bundle_id)

    # 14. redaction_exports export_id values must be unique
    seen_export_ids: set[str] = set()
    for export in pack.redaction_exports:
        if export.export_id in seen_export_ids:
            issues.append(
                _error(
                    "E014",
                    f"Duplicate export_id '{export.export_id}' in redaction_exports.",
                    "redaction_exports",
                )
            )
        seen_export_ids.add(export.export_id)

    # 15. approved status requires at least one ReviewRecord
    if pack.review_status in (
        ReviewStatus.approved,
        ReviewStatus.approved_with_conditions,
    ):
        if not pack.review_records:
            issues.append(
                _error(
                    "E015",
                    "review_status 'approved' or 'approved_with_conditions' requires at least one ReviewRecord.",
                    "review_records",
                )
            )

    # 16. ReviewRecord decision "approved" or "approved_with_conditions" requires reviewed_at
    for i, record in enumerate(pack.review_records):
        if record.decision in (
            ReviewStatus.approved,
            ReviewStatus.approved_with_conditions,
        ):
            if not record.reviewed_at or not record.reviewed_at.strip():
                issues.append(
                    _error(
                        "E016",
                        f"review_records[{i}] has decision '{record.decision.value}' but reviewed_at is missing.",
                        f"review_records[{i}].reviewed_at",
                    )
                )

    # 17. Critical open risk prevents approval
    if pack.review_status == ReviewStatus.approved:
        for risk in pack.risk_register:
            if risk.severity == RiskSeverity.critical and risk.status == RiskStatus.open:
                issues.append(
                    _error(
                        "E017",
                        f"Risk '{risk.risk_id}' is critical and open; cannot approve.",
                        "risk_register",
                    )
                )

    # 18. authority_required action without authority_model
    if any(action.authority_required for action in pack.action_inventory):
        if pack.authority_model is None:
            issues.append(
                _error(
                    "E018",
                    "One or more actions have authority_required=True but authority_model is missing.",
                    "authority_model",
                )
            )

    # 19. review_required action without matching policy control
    review_control_keywords = {"review", "approval", "human", "approve"}
    has_review_control = any(
        any(kw in pc.control_name.lower() or kw in pc.description.lower() for kw in review_control_keywords)
        for pc in pack.policy_controls
    )
    for action in pack.action_inventory:
        if action.review_required and not has_review_control:
            issues.append(
                _error(
                    "E019",
                    f"Action '{action.action_name}' has review_required=True but no policy control mentions review or approval.",
                    "policy_controls",
                )
            )
            break  # one error per pack is sufficient

    # 20. approved with no replay bundles
    if (
        pack.review_status == ReviewStatus.approved
        and not pack.replay_bundles
    ):
        issues.append(
            _error(
                "E020",
                "review_status is 'approved' but replay_bundles is empty.",
                "replay_bundles",
            )
        )

    # ------------------------------------------------------------------ #
    # Warnings
    # ------------------------------------------------------------------ #

    # W001. owner is missing
    if not pack.agent_overview.owner:
        issues.append(
            _warning(
                "W001",
                "agent_overview.owner is missing.",
                "agent_overview.owner",
            )
        )

    # W002. business_unit is missing
    if not pack.agent_overview.business_unit:
        issues.append(
            _warning(
                "W002",
                "agent_overview.business_unit is missing.",
                "agent_overview.business_unit",
            )
        )

    # W003. systems_touched is empty
    if not pack.deployment_context.systems_touched:
        issues.append(
            _warning(
                "W003",
                "deployment_context.systems_touched is empty.",
                "deployment_context.systems_touched",
            )
        )

    # W004. data_domains is empty
    if not pack.deployment_context.data_domains:
        issues.append(
            _warning(
                "W004",
                "deployment_context.data_domains is empty.",
                "deployment_context.data_domains",
            )
        )

    # W005. tool_inventory is empty
    if not pack.tool_inventory:
        issues.append(
            _warning("W005", "tool_inventory is empty.", "tool_inventory")
        )

    # W006. action_inventory is empty
    if not pack.action_inventory:
        issues.append(
            _warning("W006", "action_inventory is empty.", "action_inventory")
        )

    # W007. policy_controls is empty
    if not pack.policy_controls:
        issues.append(
            _warning("W007", "policy_controls is empty.", "policy_controls")
        )

    # W008. blocked_actions is empty
    if not pack.blocked_actions:
        issues.append(
            _warning("W008", "blocked_actions is empty.", "blocked_actions")
        )

    # W009. reliance_summary is empty
    if not pack.reliance_summary:
        issues.append(
            _warning("W009", "reliance_summary is empty.", "reliance_summary")
        )

    # W010. replay_bundles is empty
    if not pack.replay_bundles:
        issues.append(
            _warning("W010", "replay_bundles is empty.", "replay_bundles")
        )

    # W011. validation_summary is missing
    if pack.validation_summary is None:
        issues.append(
            _warning(
                "W011",
                "validation_summary is missing.",
                "validation_summary",
            )
        )

    # W012. redaction_exports is empty
    if not pack.redaction_exports:
        issues.append(
            _warning("W012", "redaction_exports is empty.", "redaction_exports")
        )

    # W013. risk_register is empty
    if not pack.risk_register:
        issues.append(
            _warning("W013", "risk_register is empty.", "risk_register")
        )

    # W014. review_records is empty
    if not pack.review_records:
        issues.append(
            _warning("W014", "review_records is empty.", "review_records")
        )

    # W015. production deployment with review_status draft or in_review
    from .models import DeploymentEnvironment
    if pack.deployment_context.environment == DeploymentEnvironment.production:
        if pack.review_status in (ReviewStatus.draft, ReviewStatus.in_review):
            issues.append(
                _warning(
                    "W015",
                    "Production deployment has review_status 'draft' or 'in_review'.",
                    "review_status",
                )
            )

    # W016. production deployment with no redaction exports
    if (
        pack.deployment_context.environment == DeploymentEnvironment.production
        and not pack.redaction_exports
    ):
        issues.append(
            _warning(
                "W016",
                "Production deployment has no redaction exports.",
                "redaction_exports",
            )
        )

    # W017. production deployment with no signed replay bundles
    if pack.deployment_context.environment == DeploymentEnvironment.production:
        if not any(b.signed for b in pack.replay_bundles):
            issues.append(
                _warning(
                    "W017",
                    "Production deployment has no signed replay bundles.",
                    "replay_bundles",
                )
            )

    # W018. privileged action types without review_required
    for action in pack.action_inventory:
        if action.action_type in _PRIVILEGED_TYPES and not action.review_required:
            issues.append(
                _warning(
                    "W018",
                    f"Action '{action.action_name}' is type '{action.action_type.value}' but review_required is False.",
                    "action_inventory",
                )
            )

    # W019. privileged action types without authority_required
    for action in pack.action_inventory:
        if action.action_type in _PRIVILEGED_TYPES and not action.authority_required:
            issues.append(
                _warning(
                    "W019",
                    f"Action '{action.action_name}' is type '{action.action_type.value}' but authority_required is False.",
                    "action_inventory",
                )
            )

    # W020. tool with external_system but missing data_classification
    for tool in pack.tool_inventory:
        if tool.external_system and not tool.data_classification:
            issues.append(
                _warning(
                    "W020",
                    f"Tool '{tool.tool_name}' has external_system set but data_classification is missing.",
                    "tool_inventory",
                )
            )

    has_errors = any(
        issue.severity == ValidationSeverity.error for issue in issues
    )
    return ValidationReport(
        valid=not has_errors,
        pack_id=pack.pack_id or None,
        issues=issues,
    )
