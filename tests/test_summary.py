"""Tests for the evidence pack summary function."""

import pytest

from agent_governance_evidence_pack.models import (
    ActionInventoryItem,
    ActionType,
    AgentOverview,
    BlockedActionSummary,
    DeploymentContext,
    DeploymentEnvironment,
    EvidencePack,
    RelianceSummary,
    ReplayBundleInventoryItem,
    RiskRegisterItem,
    RiskSeverity,
    RiskStatus,
    ToolInventoryItem,
    ValidationSummary,
)
from agent_governance_evidence_pack.summary import summarize_evidence_pack


def _minimal_pack(**kwargs) -> EvidencePack:
    defaults = dict(
        pack_id="s-001",
        title="Summary Test",
        generated_at="2026-01-01T00:00:00Z",
        agent_overview=AgentOverview(
            agent_name="SummaryAgent", business_purpose="Testing summaries"
        ),
        deployment_context=DeploymentContext(
            environment=DeploymentEnvironment.staging
        ),
    )
    defaults.update(kwargs)
    return EvidencePack(**defaults)


class TestSummaryBasics:
    def test_summary_returns_dict(self):
        pack = _minimal_pack()
        s = summarize_evidence_pack(pack)
        assert isinstance(s, dict)

    def test_summary_pack_id_and_title(self):
        pack = _minimal_pack()
        s = summarize_evidence_pack(pack)
        assert s["pack_id"] == "s-001"
        assert s["title"] == "Summary Test"

    def test_summary_counts_tools(self):
        tools = [
            ToolInventoryItem(tool_name="t1"),
            ToolInventoryItem(tool_name="t2"),
        ]
        pack = _minimal_pack(tool_inventory=tools)
        s = summarize_evidence_pack(pack)
        assert s["tool_count"] == 2

    def test_summary_counts_actions(self):
        tools = [ToolInventoryItem(tool_name="t1")]
        actions = [
            ActionInventoryItem(
                action_name="a1", tool_name="t1", action_type=ActionType.read
            ),
            ActionInventoryItem(
                action_name="a2", tool_name="t1", action_type=ActionType.write
            ),
        ]
        pack = _minimal_pack(tool_inventory=tools, action_inventory=actions)
        s = summarize_evidence_pack(pack)
        assert s["action_count"] == 2


class TestSummaryPrivilegedActions:
    def test_counts_authority_required_actions(self):
        tools = [ToolInventoryItem(tool_name="t1")]
        actions = [
            ActionInventoryItem(
                action_name="a1",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=True,
            ),
            ActionInventoryItem(
                action_name="a2",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=False,
            ),
        ]
        pack = _minimal_pack(tool_inventory=tools, action_inventory=actions)
        s = summarize_evidence_pack(pack)
        assert s["authority_required_action_count"] == 1

    def test_counts_review_required_actions(self):
        tools = [ToolInventoryItem(tool_name="t1")]
        actions = [
            ActionInventoryItem(
                action_name="a1",
                tool_name="t1",
                action_type=ActionType.read,
                review_required=True,
            ),
            ActionInventoryItem(
                action_name="a2",
                tool_name="t1",
                action_type=ActionType.read,
                review_required=False,
            ),
        ]
        pack = _minimal_pack(tool_inventory=tools, action_inventory=actions)
        s = summarize_evidence_pack(pack)
        assert s["review_required_action_count"] == 1

    def test_counts_reliance_required_actions(self):
        tools = [ToolInventoryItem(tool_name="t1")]
        actions = [
            ActionInventoryItem(
                action_name="a1",
                tool_name="t1",
                action_type=ActionType.read,
                reliance_required=True,
            ),
            ActionInventoryItem(
                action_name="a2",
                tool_name="t1",
                action_type=ActionType.read,
                reliance_required=True,
            ),
            ActionInventoryItem(
                action_name="a3",
                tool_name="t1",
                action_type=ActionType.read,
                reliance_required=False,
            ),
        ]
        pack = _minimal_pack(tool_inventory=tools, action_inventory=actions)
        s = summarize_evidence_pack(pack)
        assert s["reliance_required_action_count"] == 2

    def test_privileged_action_count_is_authority_or_review(self):
        tools = [ToolInventoryItem(tool_name="t1")]
        actions = [
            ActionInventoryItem(
                action_name="a1",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=True,
                review_required=False,
            ),
            ActionInventoryItem(
                action_name="a2",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=False,
                review_required=True,
            ),
            ActionInventoryItem(
                action_name="a3",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=True,
                review_required=True,
            ),
            ActionInventoryItem(
                action_name="a4",
                tool_name="t1",
                action_type=ActionType.read,
                authority_required=False,
                review_required=False,
            ),
        ]
        pack = _minimal_pack(tool_inventory=tools, action_inventory=actions)
        s = summarize_evidence_pack(pack)
        assert s["privileged_action_count"] == 3


class TestSummaryBlockedAndReliance:
    def test_counts_blocked_action_total(self):
        pack = _minimal_pack(
            blocked_actions=[
                BlockedActionSummary(action_name="a1", count=5),
                BlockedActionSummary(action_name="a2", count=3),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["blocked_action_total"] == 8

    def test_counts_reliance_total(self):
        pack = _minimal_pack(
            reliance_summary=[
                RelianceSummary(source_name="s1", source_type="db", count=10),
                RelianceSummary(source_name="s2", source_type="file", count=7),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["reliance_total"] == 17


class TestSummaryReplayBundles:
    def test_counts_replay_bundles(self):
        pack = _minimal_pack(
            replay_bundles=[
                ReplayBundleInventoryItem(bundle_id="b1"),
                ReplayBundleInventoryItem(bundle_id="b2"),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["replay_bundle_count"] == 2

    def test_counts_signed_bundles(self):
        pack = _minimal_pack(
            replay_bundles=[
                ReplayBundleInventoryItem(bundle_id="b1", signed=True),
                ReplayBundleInventoryItem(bundle_id="b2", signed=False),
                ReplayBundleInventoryItem(bundle_id="b3", signed=True),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["signed_replay_bundle_count"] == 2

    def test_counts_redacted_bundles(self):
        pack = _minimal_pack(
            replay_bundles=[
                ReplayBundleInventoryItem(bundle_id="b1", redacted=True),
                ReplayBundleInventoryItem(bundle_id="b2", redacted=False),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["redacted_replay_bundle_count"] == 1


class TestSummaryRisks:
    def test_counts_open_risks(self):
        pack = _minimal_pack(
            risk_register=[
                RiskRegisterItem(
                    risk_id="r1",
                    title="R1",
                    description="d",
                    severity=RiskSeverity.high,
                    status=RiskStatus.open,
                ),
                RiskRegisterItem(
                    risk_id="r2",
                    title="R2",
                    description="d",
                    severity=RiskSeverity.medium,
                    status=RiskStatus.mitigated,
                ),
                RiskRegisterItem(
                    risk_id="r3",
                    title="R3",
                    description="d",
                    severity=RiskSeverity.low,
                    status=RiskStatus.open,
                ),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["open_risk_count"] == 2

    def test_counts_critical_open_risks(self):
        pack = _minimal_pack(
            risk_register=[
                RiskRegisterItem(
                    risk_id="r1",
                    title="C1",
                    description="d",
                    severity=RiskSeverity.critical,
                    status=RiskStatus.open,
                ),
                RiskRegisterItem(
                    risk_id="r2",
                    title="C2",
                    description="d",
                    severity=RiskSeverity.critical,
                    status=RiskStatus.mitigated,
                ),
                RiskRegisterItem(
                    risk_id="r3",
                    title="H1",
                    description="d",
                    severity=RiskSeverity.high,
                    status=RiskStatus.open,
                ),
            ]
        )
        s = summarize_evidence_pack(pack)
        assert s["critical_open_risk_count"] == 1


class TestSummaryValidation:
    def test_validation_counts_from_summary(self):
        pack = _minimal_pack(
            validation_summary=ValidationSummary(
                valid_bundle_count=2,
                invalid_bundle_count=1,
                warning_count=3,
                error_count=1,
            )
        )
        s = summarize_evidence_pack(pack)
        assert s["validation_error_count"] == 1
        assert s["validation_warning_count"] == 3

    def test_validation_counts_zero_when_no_summary(self):
        pack = _minimal_pack()
        s = summarize_evidence_pack(pack)
        assert s["validation_error_count"] == 0
        assert s["validation_warning_count"] == 0
