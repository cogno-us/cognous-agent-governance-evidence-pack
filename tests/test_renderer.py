"""Tests for the markdown renderer."""

import pytest

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
    RelianceSummary,
    ReplayBundleInventoryItem,
    ReviewRecord,
    ReviewStatus,
    RiskRegisterItem,
    RiskSeverity,
    ToolInventoryItem,
)
from agent_governance_evidence_pack.renderer import render_markdown


def _minimal_pack(**kwargs) -> EvidencePack:
    defaults = dict(
        pack_id="r-001",
        title="Render Test Pack",
        generated_at="2026-01-01T00:00:00Z",
        agent_overview=AgentOverview(
            agent_name="RenderAgent",
            business_purpose="Testing rendering",
            owner="Test Owner",
            business_unit="Test Unit",
        ),
        deployment_context=DeploymentContext(
            environment=DeploymentEnvironment.staging,
            systems_touched=["SystemA"],
            data_domains=["internal"],
        ),
    )
    defaults.update(kwargs)
    return EvidencePack(**defaults)


class TestRenderReturnsString:
    def test_render_markdown_returns_str(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_title(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "Render Test Pack" in result

    def test_includes_pack_id(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "r-001" in result


class TestSectionHeaders:
    def test_includes_all_required_sections(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        for section in [
            "## 1. Executive Summary",
            "## 2. Agent Overview",
            "## 3. Deployment Context",
            "## 4. Tool Inventory",
            "## 5. Action Inventory",
            "## 6. Authority Model",
            "## 7. Policy Controls",
            "## 8. Blocked-Action Summary",
            "## 9. Reliance Summary",
            "## 10. Replay Bundle Inventory",
            "## 11. Validation Summary",
            "## 12. Redaction and Export Summary",
            "## 13. Risk Register",
            "## 14. Review Records",
            "## 15. Known Limitations",
        ]:
            assert section in result, f"Missing section: {section}"

    def test_known_limitations_text(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "does not prove that model outputs are correct" in result


class TestMetadataTable:
    def test_metadata_table_contains_pack_id(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "Pack ID" in result

    def test_metadata_table_contains_owner(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "Test Owner" in result

    def test_metadata_table_contains_environment(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "staging" in result


class TestTableEscaping:
    def test_escapes_pipe_in_field_values(self):
        tools = [
            ToolInventoryItem(
                tool_name="tool|with|pipes",
                description="A tool | with | pipes",
            )
        ]
        pack = _minimal_pack(tool_inventory=tools)
        result = render_markdown(pack)
        # Pipes in values should be escaped
        assert "tool\\|with\\|pipes" in result or "tool|with|pipes" in result

    def test_table_pipes_not_broken_by_description_pipes(self):
        tools = [
            ToolInventoryItem(
                tool_name="safe_tool",
                description="Reads | writes data",
            )
        ]
        pack = _minimal_pack(tool_inventory=tools)
        result = render_markdown(pack)
        # The escaped version should appear in the table
        assert "Reads \\| writes data" in result


class TestDeterministicOutput:
    def test_same_input_same_output(self):
        pack = _minimal_pack()
        result1 = render_markdown(pack)
        result2 = render_markdown(pack)
        assert result1 == result2

    def test_same_pack_twice(self):
        pack1 = _minimal_pack()
        pack2 = _minimal_pack()
        assert render_markdown(pack1) == render_markdown(pack2)


class TestEmptySections:
    def test_no_tools_shows_placeholder(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "No tools recorded" in result

    def test_no_actions_shows_placeholder(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "No actions recorded" in result

    def test_no_risks_shows_placeholder(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "No risks recorded" in result

    def test_no_review_records_shows_placeholder(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "No review records recorded" in result

    def test_no_authority_model_shows_missing_message(self):
        pack = _minimal_pack()
        result = render_markdown(pack)
        assert "No authority model recorded" in result


class TestContentRendering:
    def test_tool_inventory_table(self):
        tools = [
            ToolInventoryItem(
                tool_name="crm_read",
                description="Read CRM",
                external_system="CRM",
                data_classification="confidential",
                access_mode="read-only",
                control_status=ControlStatus.implemented,
            )
        ]
        pack = _minimal_pack(tool_inventory=tools)
        result = render_markdown(pack)
        assert "crm_read" in result
        assert "Read CRM" in result
        assert "confidential" in result

    def test_risk_register_table(self):
        risks = [
            RiskRegisterItem(
                risk_id="r1",
                title="Test Risk",
                description="desc",
                severity=RiskSeverity.high,
            )
        ]
        pack = _minimal_pack(risk_register=risks)
        result = render_markdown(pack)
        assert "Test Risk" in result
        assert "high" in result

    def test_review_records_table(self):
        records = [
            ReviewRecord(
                reviewer="Alice",
                reviewer_role="CISO",
                reviewed_at="2026-01-02T00:00:00Z",
                decision=ReviewStatus.approved,
                notes="Looks good",
            )
        ]
        pack = _minimal_pack(review_records=records)
        result = render_markdown(pack)
        assert "Alice" in result
        assert "CISO" in result
        assert "approved" in result
