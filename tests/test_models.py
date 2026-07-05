"""Tests for EvidencePack Pydantic models."""

import pytest
from pydantic import ValidationError

from agent_governance_evidence_pack.models import (
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
    RedactionExportSummary,
    RelianceSummary,
    ReplayBundleInventoryItem,
    ReviewRecord,
    ReviewStatus,
    RiskRegisterItem,
    RiskSeverity,
    RiskStatus,
    ToolInventoryItem,
    ValidationReport,
    ValidationSeverity,
)


def _minimal_pack() -> dict:
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


class TestMinimalPack:
    def test_valid_minimal_pack_loads(self):
        pack = EvidencePack.model_validate(_minimal_pack())
        assert pack.pack_id == "test-001"
        assert pack.title == "Test Pack"
        assert pack.agent_overview.agent_name == "TestAgent"
        assert pack.deployment_context.environment == DeploymentEnvironment.development

    def test_default_values(self):
        pack = EvidencePack.model_validate(_minimal_pack())
        assert pack.pack_version == "0.1"
        assert pack.review_status == ReviewStatus.draft
        assert pack.tool_inventory == []
        assert pack.action_inventory == []
        assert pack.authority_model is None
        assert pack.policy_controls == []
        assert pack.blocked_actions == []
        assert pack.reliance_summary == []
        assert pack.replay_bundles == []
        assert pack.validation_summary is None
        assert pack.redaction_exports == []
        assert pack.risk_register == []
        assert pack.review_records == []
        assert pack.metadata == {}


class TestFullPack:
    def test_full_pack_loads(self):
        data = _minimal_pack()
        data["tool_inventory"] = [
            {
                "tool_name": "crm_read",
                "description": "Read CRM",
                "external_system": "CRM",
                "data_classification": "confidential",
                "access_mode": "read-only",
                "control_status": "implemented",
            }
        ]
        data["action_inventory"] = [
            {
                "action_name": "read_customer",
                "tool_name": "crm_read",
                "action_type": "read",
                "authority_required": False,
                "review_required": False,
                "reliance_required": True,
                "control_status": "implemented",
            }
        ]
        data["authority_model"] = {
            "summary": "Authority required for send actions",
            "authority_scopes": ["email_send"],
            "privileged_action_types": ["external_send"],
            "expiration_required": True,
            "human_approval_required": True,
        }
        data["risk_register"] = [
            {
                "risk_id": "risk-001",
                "title": "Test risk",
                "description": "A test risk",
                "severity": "medium",
                "status": "open",
            }
        ]
        data["review_records"] = [
            {
                "reviewer": "Alice",
                "reviewer_role": "CISO",
                "reviewed_at": "2026-01-02T00:00:00Z",
                "decision": "approved",
            }
        ]
        pack = EvidencePack.model_validate(data)
        assert len(pack.tool_inventory) == 1
        assert pack.tool_inventory[0].tool_name == "crm_read"
        assert pack.tool_inventory[0].control_status == ControlStatus.implemented
        assert len(pack.action_inventory) == 1
        assert pack.action_inventory[0].action_type == ActionType.read
        assert pack.authority_model is not None
        assert pack.authority_model.expiration_required is True
        assert len(pack.risk_register) == 1
        assert pack.risk_register[0].severity == RiskSeverity.medium
        assert len(pack.review_records) == 1
        assert pack.review_records[0].decision == ReviewStatus.approved


class TestEnumValidation:
    def test_invalid_environment_raises(self):
        data = _minimal_pack()
        data["deployment_context"]["environment"] = "invalid_env"
        with pytest.raises(ValidationError):
            EvidencePack.model_validate(data)

    def test_invalid_review_status_raises(self):
        data = _minimal_pack()
        data["review_status"] = "not_a_status"
        with pytest.raises(ValidationError):
            EvidencePack.model_validate(data)

    def test_invalid_action_type_raises(self):
        data = _minimal_pack()
        data["tool_inventory"] = [{"tool_name": "t1"}]
        data["action_inventory"] = [
            {
                "action_name": "act1",
                "tool_name": "t1",
                "action_type": "not_a_type",
            }
        ]
        with pytest.raises(ValidationError):
            EvidencePack.model_validate(data)

    def test_valid_all_environment_values(self):
        for env in ("development", "staging", "production", "sandbox", "other"):
            data = _minimal_pack()
            data["deployment_context"]["environment"] = env
            pack = EvidencePack.model_validate(data)
            assert pack.deployment_context.environment.value == env

    def test_valid_all_review_status_values(self):
        for status in (
            "draft",
            "in_review",
            "approved",
            "approved_with_conditions",
            "rejected",
            "retired",
        ):
            data = _minimal_pack()
            data["review_status"] = status
            pack = EvidencePack.model_validate(data)
            assert pack.review_status.value == status


class TestAgentOverviewDefaults:
    def test_optional_fields_default_none(self):
        ao = AgentOverview(agent_name="Test", business_purpose="Test purpose")
        assert ao.agent_description is None
        assert ao.owner is None
        assert ao.business_unit is None
        assert ao.user_population is None
        assert ao.lifecycle_stage is None


class TestToolInventoryItemDefaults:
    def test_defaults(self):
        tool = ToolInventoryItem(tool_name="my_tool")
        assert tool.description is None
        assert tool.external_system is None
        assert tool.control_status == ControlStatus.planned


class TestActionInventoryItemDefaults:
    def test_defaults(self):
        action = ActionInventoryItem(
            action_name="act", tool_name="tool", action_type=ActionType.read
        )
        assert action.authority_required is False
        assert action.review_required is False
        assert action.reliance_required is False
        assert action.control_status == ControlStatus.planned
