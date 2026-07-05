"""Tests for the evidence pack validator."""

import pytest

from agent_governance_evidence_pack.models import (
    ActionInventoryItem,
    ActionType,
    AuthorityModelSummary,
    BlockedActionSummary,
    DeploymentContext,
    DeploymentEnvironment,
    EvidencePack,
    AgentOverview,
    PolicyControlSummary,
    ControlStatus,
    RedactionExportSummary,
    RelianceSummary,
    ReplayBundleInventoryItem,
    ReviewRecord,
    ReviewStatus,
    RiskRegisterItem,
    RiskSeverity,
    RiskStatus,
    ToolInventoryItem,
    ValidationSeverity,
)
from agent_governance_evidence_pack.validator import validate_evidence_pack


def _make_pack(**kwargs) -> EvidencePack:
    """Build a minimal valid pack with optional overrides."""
    defaults = dict(
        pack_id="test-001",
        title="Test Pack",
        generated_at="2026-01-01T00:00:00Z",
        agent_overview=AgentOverview(
            agent_name="TestAgent",
            business_purpose="Test purpose",
        ),
        deployment_context=DeploymentContext(
            environment=DeploymentEnvironment.development,
        ),
    )
    defaults.update(kwargs)
    return EvidencePack(**defaults)


def _error_codes(report) -> set[str]:
    return {i.code for i in report.issues if i.severity == ValidationSeverity.error}


def _warning_codes(report) -> set[str]:
    return {i.code for i in report.issues if i.severity == ValidationSeverity.warning}


class TestErrorRules:
    def test_missing_pack_id_error(self):
        pack = _make_pack(pack_id="")
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E001" in _error_codes(report)

    def test_missing_title_error(self):
        pack = _make_pack(title="")
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E002" in _error_codes(report)

    def test_missing_business_purpose_error(self):
        pack = _make_pack(
            agent_overview=AgentOverview(
                agent_name="TestAgent",
                business_purpose="",
            )
        )
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E005" in _error_codes(report)

    def test_duplicate_tool_names_error(self):
        tools = [
            ToolInventoryItem(tool_name="tool_a"),
            ToolInventoryItem(tool_name="tool_a"),
        ]
        pack = _make_pack(tool_inventory=tools)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E007" in _error_codes(report)

    def test_duplicate_action_names_error(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a", tool_name="tool_a", action_type=ActionType.read
            ),
            ActionInventoryItem(
                action_name="act_a", tool_name="tool_a", action_type=ActionType.write
            ),
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E008" in _error_codes(report)

    def test_action_unknown_tool_error(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="unknown_tool",
                action_type=ActionType.read,
            )
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E009" in _error_codes(report)

    def test_duplicate_risk_ids_error(self):
        risks = [
            RiskRegisterItem(
                risk_id="r1",
                title="R1",
                description="desc",
                severity=RiskSeverity.low,
            ),
            RiskRegisterItem(
                risk_id="r1",
                title="R1 dup",
                description="desc2",
                severity=RiskSeverity.medium,
            ),
        ]
        pack = _make_pack(risk_register=risks)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E012" in _error_codes(report)

    def test_duplicate_replay_bundle_ids_error(self):
        bundles = [
            ReplayBundleInventoryItem(bundle_id="b1"),
            ReplayBundleInventoryItem(bundle_id="b1"),
        ]
        pack = _make_pack(replay_bundles=bundles)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E013" in _error_codes(report)

    def test_approved_status_without_review_record_error(self):
        bundles = [ReplayBundleInventoryItem(bundle_id="b1")]
        pack = _make_pack(review_status=ReviewStatus.approved, replay_bundles=bundles)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E015" in _error_codes(report)

    def test_critical_open_risk_prevents_approval(self):
        risks = [
            RiskRegisterItem(
                risk_id="r1",
                title="Critical Risk",
                description="desc",
                severity=RiskSeverity.critical,
                status=RiskStatus.open,
            )
        ]
        bundles = [ReplayBundleInventoryItem(bundle_id="b1")]
        review_records = [
            ReviewRecord(
                reviewer="Alice",
                reviewed_at="2026-01-02T00:00:00Z",
                decision=ReviewStatus.approved,
            )
        ]
        pack = _make_pack(
            review_status=ReviewStatus.approved,
            risk_register=risks,
            replay_bundles=bundles,
            review_records=review_records,
        )
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E017" in _error_codes(report)

    def test_authority_required_action_without_authority_model_error(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=ActionType.external_send,
                authority_required=True,
            )
        ]
        pack = _make_pack(
            tool_inventory=tools,
            action_inventory=actions,
            authority_model=None,
        )
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E018" in _error_codes(report)

    def test_review_required_action_without_review_control_error(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=ActionType.read,
                review_required=True,
            )
        ]
        # No policy controls mentioning review
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E019" in _error_codes(report)

    def test_review_required_action_with_review_control_no_error(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=ActionType.read,
                review_required=True,
            )
        ]
        controls = [
            PolicyControlSummary(
                control_name="Human Review Gate",
                description="Requires human review before execution.",
                control_status=ControlStatus.implemented,
            )
        ]
        pack = _make_pack(
            tool_inventory=tools,
            action_inventory=actions,
            policy_controls=controls,
        )
        report = validate_evidence_pack(pack)
        assert "E019" not in _error_codes(report)

    def test_approved_with_no_replay_bundles_error(self):
        review_records = [
            ReviewRecord(
                reviewer="Alice",
                reviewed_at="2026-01-02T00:00:00Z",
                decision=ReviewStatus.approved,
            )
        ]
        pack = _make_pack(
            review_status=ReviewStatus.approved,
            review_records=review_records,
            replay_bundles=[],
        )
        report = validate_evidence_pack(pack)
        assert not report.valid
        assert "E020" in _error_codes(report)


class TestWarningRules:
    def test_warnings_do_not_make_report_invalid(self):
        # A minimal pack will generate many warnings
        pack = _make_pack()
        report = validate_evidence_pack(pack)
        assert report.valid  # no errors
        assert len(report.issues) > 0  # but there are warnings

    def test_errors_make_report_invalid(self):
        pack = _make_pack(pack_id="")
        report = validate_evidence_pack(pack)
        assert not report.valid

    def test_production_no_redaction_export_warning(self):
        pack = _make_pack(
            deployment_context=DeploymentContext(
                environment=DeploymentEnvironment.production
            )
        )
        report = validate_evidence_pack(pack)
        assert "W016" in _warning_codes(report)

    def test_production_no_signed_replay_bundle_warning(self):
        pack = _make_pack(
            deployment_context=DeploymentContext(
                environment=DeploymentEnvironment.production
            )
        )
        report = validate_evidence_pack(pack)
        assert "W017" in _warning_codes(report)

    def test_privileged_action_without_authority_warning(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=ActionType.external_send,
                authority_required=False,
            )
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert "W019" in _warning_codes(report)

    def test_privileged_action_without_review_warning(self):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=ActionType.delete,
                review_required=False,
            )
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert "W018" in _warning_codes(report)

    @pytest.mark.parametrize("action_type", [ActionType.write, ActionType.export])
    def test_write_and_export_without_review_warning(self, action_type):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=action_type,
                review_required=False,
            )
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert "W018" in _warning_codes(report)

    @pytest.mark.parametrize("action_type", [ActionType.write, ActionType.export])
    def test_write_and_export_without_authority_warning(self, action_type):
        tools = [ToolInventoryItem(tool_name="tool_a")]
        actions = [
            ActionInventoryItem(
                action_name="act_a",
                tool_name="tool_a",
                action_type=action_type,
                authority_required=False,
            )
        ]
        pack = _make_pack(tool_inventory=tools, action_inventory=actions)
        report = validate_evidence_pack(pack)
        assert "W019" in _warning_codes(report)

    def test_empty_pack_has_many_warnings(self):
        pack = _make_pack()
        report = validate_evidence_pack(pack)
        warnings = _warning_codes(report)
        # Should warn about missing owner, business_unit, systems_touched, etc.
        assert "W001" in warnings
        assert "W002" in warnings
        assert "W003" in warnings
        assert "W004" in warnings

    def test_production_draft_status_warning(self):
        pack = _make_pack(
            deployment_context=DeploymentContext(
                environment=DeploymentEnvironment.production
            ),
            review_status=ReviewStatus.draft,
        )
        report = validate_evidence_pack(pack)
        assert "W015" in _warning_codes(report)
