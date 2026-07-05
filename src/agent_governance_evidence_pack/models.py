"""
Pydantic models for the Agent Governance Evidence Pack format.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeploymentEnvironment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"
    sandbox = "sandbox"
    other = "other"


class ReviewStatus(str, Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"
    approved_with_conditions = "approved_with_conditions"
    rejected = "rejected"
    retired = "retired"


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskStatus(str, Enum):
    open = "open"
    mitigated = "mitigated"
    accepted = "accepted"
    transferred = "transferred"
    closed = "closed"


class ActionType(str, Enum):
    read = "read"
    write = "write"
    external_send = "external_send"
    delete = "delete"
    export = "export"
    purchase = "purchase"
    approve = "approve"
    escalate = "escalate"
    other = "other"


class ControlStatus(str, Enum):
    implemented = "implemented"
    partial = "partial"
    planned = "planned"
    not_applicable = "not_applicable"


class ValidationSeverity(str, Enum):
    error = "error"
    warning = "warning"


class AgentOverview(BaseModel):
    agent_name: str = Field(description="The name of the agent being reviewed.")
    agent_description: str | None = Field(
        default=None, description="A short description of what this agent does."
    )
    business_purpose: str = Field(
        description="The business purpose this agent serves. Why does it exist?"
    )
    owner: str | None = Field(
        default=None,
        description="The business or technical owner responsible for this agent.",
    )
    business_unit: str | None = Field(
        default=None, description="The business unit that owns or operates this agent."
    )
    user_population: str | None = Field(
        default=None,
        description="Description of the users or systems that interact with this agent.",
    )
    lifecycle_stage: str | None = Field(
        default=None,
        description="The lifecycle stage of this agent (e.g., pilot, production, deprecated).",
    )


class DeploymentContext(BaseModel):
    environment: DeploymentEnvironment = Field(
        description="The deployment environment (development, staging, production, sandbox, other)."
    )
    deployment_name: str | None = Field(
        default=None, description="A human-readable name for this deployment."
    )
    deployment_date: str | None = Field(
        default=None, description="The date this agent was deployed (ISO 8601)."
    )
    systems_touched: list[str] = Field(
        default_factory=list,
        description="Systems, APIs, or data stores this agent can access.",
    )
    data_domains: list[str] = Field(
        default_factory=list,
        description="Data domains or classifications this agent operates over.",
    )
    geographic_scope: str | None = Field(
        default=None,
        description="Geographic or regulatory scope of this deployment.",
    )
    notes: str | None = Field(
        default=None, description="Additional deployment context notes."
    )


class ToolInventoryItem(BaseModel):
    tool_name: str = Field(description="Unique name of the tool available to this agent.")
    description: str | None = Field(
        default=None, description="What this tool does."
    )
    external_system: str | None = Field(
        default=None,
        description="The external system or API this tool connects to, if any.",
    )
    data_classification: str | None = Field(
        default=None,
        description="The data classification level for data accessed via this tool.",
    )
    access_mode: str | None = Field(
        default=None,
        description="The access mode for this tool (e.g., read-only, read-write).",
    )
    control_status: ControlStatus = Field(
        default=ControlStatus.planned,
        description="Whether controls for this tool are implemented, partial, planned, or not applicable.",
    )


class ActionInventoryItem(BaseModel):
    action_name: str = Field(
        description="Unique name of the action this agent can propose."
    )
    tool_name: str = Field(
        description="The tool through which this action is executed. Must match a tool in tool_inventory."
    )
    action_type: ActionType = Field(
        description="The type of action (read, write, external_send, delete, export, purchase, approve, escalate, other)."
    )
    description: str | None = Field(
        default=None, description="What this action does."
    )
    authority_required: bool = Field(
        default=False,
        description="Whether this action requires explicit authority to be granted before execution.",
    )
    review_required: bool = Field(
        default=False,
        description="Whether this action requires human review before execution.",
    )
    reliance_required: bool = Field(
        default=False,
        description="Whether execution of this action creates a reliance record.",
    )
    default_posture: str | None = Field(
        default=None,
        description="The default posture for this action (e.g., allowed, blocked, requires_approval).",
    )
    control_status: ControlStatus = Field(
        default=ControlStatus.planned,
        description="Whether controls for this action are implemented, partial, planned, or not applicable.",
    )


class AuthorityModelSummary(BaseModel):
    summary: str = Field(
        description="A short summary of how authority is granted and governed for privileged actions."
    )
    authority_scopes: list[str] = Field(
        default_factory=list,
        description="The scopes of authority that can be granted to this agent.",
    )
    privileged_action_types: list[ActionType] = Field(
        default_factory=list,
        description="Action types that are considered privileged and require authority.",
    )
    expiration_required: bool = Field(
        default=False,
        description="Whether authority grants must expire.",
    )
    human_approval_required: bool = Field(
        default=False,
        description="Whether a human must approve authority grants.",
    )
    notes: str | None = Field(
        default=None, description="Additional notes on the authority model."
    )


class PolicyControlSummary(BaseModel):
    control_name: str = Field(description="The name of this policy control.")
    description: str = Field(description="What this control does and how it works.")
    control_status: ControlStatus = Field(
        description="Whether this control is implemented, partial, planned, or not applicable."
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to evidence records for this control.",
    )
    notes: str | None = Field(
        default=None, description="Additional notes on this control."
    )


class BlockedActionSummary(BaseModel):
    action_name: str | None = Field(
        default=None, description="The name of the blocked action, if known."
    )
    action_type: ActionType | None = Field(
        default=None, description="The type of the blocked action, if known."
    )
    tool_name: str | None = Field(
        default=None, description="The tool through which the action was attempted, if known."
    )
    count: int = Field(
        default=0, description="The number of times this action was blocked."
    )
    reason_summary: str | None = Field(
        default=None, description="A summary of why this action was blocked."
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to the evidence records for these blocked actions.",
    )


class RelianceSummary(BaseModel):
    source_name: str = Field(
        description="The name of the source the agent relied on."
    )
    source_type: str = Field(
        description="The type of source (e.g., document, database, API, file)."
    )
    count: int = Field(
        default=0, description="The number of times this source was relied on."
    )
    scope_summary: str | None = Field(
        default=None, description="A summary of the scope of reliance on this source."
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to the reliance records for this source.",
    )


class ReplayBundleInventoryItem(BaseModel):
    bundle_id: str = Field(description="A unique identifier for this replay bundle.")
    run_id: str | None = Field(
        default=None, description="The run identifier associated with this replay bundle."
    )
    status: str | None = Field(
        default=None, description="The status of this replay bundle (e.g., available, archived)."
    )
    generated_at: str | None = Field(
        default=None, description="When this replay bundle was generated (ISO 8601)."
    )
    signed: bool = Field(
        default=False, description="Whether this replay bundle has been cryptographically signed."
    )
    redacted: bool = Field(
        default=False,
        description="Whether this replay bundle has been redacted for export.",
    )
    validation_status: str | None = Field(
        default=None,
        description="The validation status of this replay bundle.",
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to this replay bundle in the evidence store.",
    )


class ValidationSummary(BaseModel):
    valid_bundle_count: int = Field(
        default=0, description="Number of replay bundles that passed validation."
    )
    invalid_bundle_count: int = Field(
        default=0, description="Number of replay bundles that failed validation."
    )
    warning_count: int = Field(
        default=0, description="Total number of validation warnings across all bundles."
    )
    error_count: int = Field(
        default=0, description="Total number of validation errors across all bundles."
    )
    summary: str | None = Field(
        default=None, description="A short narrative summary of the validation results."
    )


class RedactionExportSummary(BaseModel):
    export_id: str = Field(description="A unique identifier for this redacted export.")
    export_type: str = Field(
        description="The type of export (e.g., redacted_evidence_pack, executive_summary, audit_export)."
    )
    redacted_fields: list[str] = Field(
        default_factory=list,
        description="Fields that were redacted in this export.",
    )
    generated_at: str | None = Field(
        default=None, description="When this export was generated (ISO 8601)."
    )
    intended_recipient: str | None = Field(
        default=None, description="The intended recipient or audience for this export."
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to this export in the evidence store.",
    )


class RiskRegisterItem(BaseModel):
    risk_id: str = Field(description="A unique identifier for this risk.")
    title: str = Field(description="A short title for this risk.")
    description: str = Field(description="A description of the risk and its potential impact.")
    severity: RiskSeverity = Field(
        description="The severity of this risk (low, medium, high, critical)."
    )
    status: RiskStatus = Field(
        default=RiskStatus.open,
        description="The current status of this risk (open, mitigated, accepted, transferred, closed).",
    )
    mitigation: str | None = Field(
        default=None, description="Description of the mitigation applied or planned for this risk."
    )
    owner: str | None = Field(
        default=None, description="The person or team responsible for managing this risk."
    )
    evidence_reference: str | None = Field(
        default=None,
        description="A reference to evidence records related to this risk.",
    )


class ReviewRecord(BaseModel):
    reviewer: str = Field(description="The name or identifier of the reviewer.")
    reviewer_role: str | None = Field(
        default=None, description="The role of the reviewer (e.g., CISO, Risk Manager, Compliance Lead)."
    )
    reviewed_at: str | None = Field(
        default=None, description="When the review was completed (ISO 8601)."
    )
    decision: ReviewStatus = Field(
        description="The review decision (draft, in_review, approved, approved_with_conditions, rejected, retired)."
    )
    notes: str | None = Field(
        default=None, description="Notes from the reviewer, including any conditions."
    )


class EvidencePack(BaseModel):
    pack_id: str = Field(description="A unique identifier for this evidence pack.")
    pack_version: str = Field(
        default="0.1", description="The version of the evidence pack format."
    )
    title: str = Field(description="A human-readable title for this evidence pack.")
    generated_at: str = Field(
        description="When this evidence pack was generated (ISO 8601)."
    )
    review_status: ReviewStatus = Field(
        default=ReviewStatus.draft,
        description="The current review status of this evidence pack.",
    )
    agent_overview: AgentOverview = Field(
        description="Overview of the agent being reviewed."
    )
    deployment_context: DeploymentContext = Field(
        description="The deployment context for this agent."
    )
    tool_inventory: list[ToolInventoryItem] = Field(
        default_factory=list,
        description="Inventory of tools available to this agent.",
    )
    action_inventory: list[ActionInventoryItem] = Field(
        default_factory=list,
        description="Inventory of actions this agent can propose.",
    )
    authority_model: AuthorityModelSummary | None = Field(
        default=None,
        description="Summary of the authority model governing privileged actions.",
    )
    policy_controls: list[PolicyControlSummary] = Field(
        default_factory=list,
        description="Policy controls in place for this agent.",
    )
    blocked_actions: list[BlockedActionSummary] = Field(
        default_factory=list,
        description="Summary of actions that were blocked during the review period.",
    )
    reliance_summary: list[RelianceSummary] = Field(
        default_factory=list,
        description="Summary of sources this agent relied on.",
    )
    replay_bundles: list[ReplayBundleInventoryItem] = Field(
        default_factory=list,
        description="Inventory of replay bundles associated with this evidence pack.",
    )
    validation_summary: ValidationSummary | None = Field(
        default=None,
        description="Summary of validation results for replay bundles.",
    )
    redaction_exports: list[RedactionExportSummary] = Field(
        default_factory=list,
        description="Summary of redacted or signed exports generated from this evidence.",
    )
    risk_register: list[RiskRegisterItem] = Field(
        default_factory=list,
        description="Register of known risks associated with this agent.",
    )
    review_records: list[ReviewRecord] = Field(
        default_factory=list,
        description="Records of governance reviews conducted on this evidence pack.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for extensibility.",
    )


class ValidationIssue(BaseModel):
    severity: ValidationSeverity = Field(
        description="Severity of this validation issue (error or warning)."
    )
    code: str = Field(description="A stable code string identifying the type of issue.")
    message: str = Field(description="A business-readable description of the issue.")
    path: str | None = Field(
        default=None,
        description="The field path within the evidence pack where this issue was found.",
    )


class ValidationReport(BaseModel):
    valid: bool = Field(
        description="True if there are no error-severity issues; warnings do not affect validity."
    )
    pack_id: str | None = Field(
        default=None, description="The pack_id of the evidence pack that was validated."
    )
    issues: list[ValidationIssue] = Field(
        default_factory=list,
        description="List of validation issues found.",
    )
