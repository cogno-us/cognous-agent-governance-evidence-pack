# Evidence Pack Format

This document explains the structure and fields of the Agent Governance Evidence Pack JSON format.

---

## Top-Level Structure

An evidence pack is a JSON object conforming to `schemas/evidence_pack.schema.json`.

### Required fields

| Field | Type | Description |
|---|---|---|
| `pack_id` | string | Unique identifier for this evidence pack. |
| `title` | string | Human-readable title. |
| `generated_at` | string | ISO 8601 timestamp when this pack was generated. |
| `agent_overview` | object | Overview of the agent (see below). |
| `deployment_context` | object | Deployment context (see below). |

### Optional fields with defaults

| Field | Type | Default | Description |
|---|---|---|---|
| `pack_version` | string | `"0.1"` | Format version. |
| `review_status` | enum | `"draft"` | Review lifecycle status. |
| `tool_inventory` | array | `[]` | List of tools. |
| `action_inventory` | array | `[]` | List of actions. |
| `authority_model` | object \| null | `null` | Authority model summary. |
| `policy_controls` | array | `[]` | Policy controls. |
| `blocked_actions` | array | `[]` | Blocked-action summaries. |
| `reliance_summary` | array | `[]` | Reliance records. |
| `replay_bundles` | array | `[]` | Replay bundle inventory. |
| `validation_summary` | object \| null | `null` | Validation summary. |
| `redaction_exports` | array | `[]` | Redaction export summaries. |
| `risk_register` | array | `[]` | Risk register items. |
| `review_records` | array | `[]` | Review records. |
| `metadata` | object | `{}` | Free-form metadata. |

---

## agent_overview

| Field | Required | Type | Description |
|---|---|---|---|
| `agent_name` | Yes | string | Name of the agent. |
| `business_purpose` | Yes | string | Why the agent exists. |
| `agent_description` | No | string \| null | Short description. |
| `owner` | No | string \| null | Accountable owner. |
| `business_unit` | No | string \| null | Owning business unit. |
| `user_population` | No | string \| null | Who interacts with the agent. |
| `lifecycle_stage` | No | string \| null | Lifecycle stage. |

---

## deployment_context

| Field | Required | Type | Description |
|---|---|---|---|
| `environment` | Yes | enum | `development`, `staging`, `production`, `sandbox`, `other`. |
| `deployment_name` | No | string \| null | Name for this deployment. |
| `deployment_date` | No | string \| null | ISO 8601 date. |
| `systems_touched` | No | array of strings | Systems the agent can access. |
| `data_domains` | No | array of strings | Data categories. |
| `geographic_scope` | No | string \| null | Regulatory or geographic scope. |
| `notes` | No | string \| null | Additional notes. |

---

## tool_inventory items

| Field | Required | Type | Description |
|---|---|---|---|
| `tool_name` | Yes | string | Unique tool name. |
| `description` | No | string \| null | What the tool does. |
| `external_system` | No | string \| null | External system it connects to. |
| `data_classification` | No | string \| null | Data classification level. |
| `access_mode` | No | string \| null | Access mode (e.g., read-only). |
| `control_status` | No | enum | `implemented`, `partial`, `planned`, `not_applicable`. |

---

## action_inventory items

| Field | Required | Type | Description |
|---|---|---|---|
| `action_name` | Yes | string | Unique action name. |
| `tool_name` | Yes | string | Tool used (must exist in tool_inventory). |
| `action_type` | Yes | enum | `read`, `write`, `external_send`, `delete`, `export`, `purchase`, `approve`, `escalate`, `other`. |
| `description` | No | string \| null | What the action does. |
| `authority_required` | No | boolean | Whether authority is required. Default: false. |
| `review_required` | No | boolean | Whether human review is required. Default: false. |
| `reliance_required` | No | boolean | Whether execution creates a reliance record. Default: false. |
| `default_posture` | No | string \| null | Default posture (e.g., allowed, blocked). |
| `control_status` | No | enum | Control implementation status. |

---

## authority_model

| Field | Required | Type | Description |
|---|---|---|---|
| `summary` | Yes | string | Summary of how authority works. |
| `authority_scopes` | No | array of strings | Scopes of authority. |
| `privileged_action_types` | No | array of enums | Action types requiring authority. |
| `expiration_required` | No | boolean | Whether authority expires. |
| `human_approval_required` | No | boolean | Whether a human approves grants. |
| `notes` | No | string \| null | Notes. |

---

## review_status values

| Value | Meaning |
|---|---|
| `draft` | Evidence pack being assembled. |
| `in_review` | Submitted for review. |
| `approved` | Approved. |
| `approved_with_conditions` | Approved with named conditions. |
| `rejected` | Rejected. |
| `retired` | Agent retired. |

---

## Schema files

All sub-schemas are in `schemas/`. The primary schema is `schemas/evidence_pack.schema.json`.
Each field group has its own schema file (e.g., `schemas/agent_overview.schema.json`).
