# Agent Governance Evidence Pack — Template

> **Instructions:** Replace all `{{ placeholder }}` values with content specific to your agent deployment.
> Remove or mark as N/A any sections that do not apply.
> This template is a starting point, not a compliance checklist.

---

# {{ Evidence Pack Title }}

| Field | Value |
|---|---|
| Pack ID | {{ pack_id }} |
| Version | 0.1 |
| Generated At | {{ generated_at }} |
| Review Status | {{ draft / in_review / approved / approved_with_conditions / rejected / retired }} |
| Agent | {{ agent_name }} |
| Environment | {{ development / staging / production / sandbox / other }} |
| Owner | {{ owner or N/A }} |
| Business Unit | {{ business_unit or N/A }} |

---

## 1. Executive Summary

{{ Short summary: what this agent is, why it exists, where it runs, how many tools/actions it has, whether any actions require authority or review, whether replay bundles exist, and what risks are open. }}

---

## 2. Agent Overview

**Agent Name:** {{ agent_name }}

**Description:** {{ agent_description }}

**Business Purpose:** {{ business_purpose }}

**Owner:** {{ owner }}

**Business Unit:** {{ business_unit }}

**User Population:** {{ user_population }}

**Lifecycle Stage:** {{ lifecycle_stage }}

---

## 3. Deployment Context

**Environment:** {{ environment }}

**Deployment Name:** {{ deployment_name }}

**Deployment Date:** {{ deployment_date }}

**Systems Touched:** {{ comma-separated list of systems }}

**Data Domains:** {{ comma-separated list of data domains }}

**Geographic Scope:** {{ geographic_scope }}

**Notes:** {{ notes }}

---

## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| {{ tool_name }} | {{ description }} | {{ external_system }} | {{ data_classification }} | {{ access_mode }} | {{ implemented / partial / planned / not_applicable }} |

---

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |
|---|---|---|---|---|---|---|
| {{ action_name }} | {{ tool_name }} | {{ action_type }} | Yes / No | Yes / No | Yes / No | {{ control_status }} |

---

## 6. Authority Model

**Summary:** {{ summary of how authority is granted and governed }}

**Authority Scopes:** {{ scopes }}

**Privileged Action Types:** {{ action types requiring authority }}

**Expiration Required:** Yes / No

**Human Approval Required:** Yes / No

**Notes:** {{ notes }}

---

## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| {{ control_name }} | {{ description }} | {{ status }} | {{ evidence_reference }} |

---

## 8. Blocked-Action Summary

{{ N }} blocked action(s) recorded.

| Action Name | Action Type | Tool | Count | Reason Summary | Evidence Reference |
|---|---|---|---|---|---|
| {{ action_name }} | {{ action_type }} | {{ tool_name }} | {{ count }} | {{ reason_summary }} | {{ evidence_reference }} |

---

## 9. Reliance Summary

{{ N }} reliance record(s) recorded.

| Source Name | Source Type | Count | Scope Summary | Evidence Reference |
|---|---|---|---|---|
| {{ source_name }} | {{ source_type }} | {{ count }} | {{ scope_summary }} | {{ evidence_reference }} |

---

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| {{ bundle_id }} | {{ run_id }} | {{ status }} | {{ generated_at }} | Yes / No | Yes / No | {{ validation_status }} | {{ evidence_reference }} |

---

## 11. Validation Summary

**Valid Bundles:** {{ n }} | **Invalid Bundles:** {{ n }} | **Errors:** {{ n }} | **Warnings:** {{ n }}

{{ narrative summary }}

---

## 12. Redaction and Export Summary

| Export ID | Type | Redacted Fields | Generated At | Intended Recipient | Evidence Reference |
|---|---|---|---|---|---|
| {{ export_id }} | {{ export_type }} | {{ fields }} | {{ generated_at }} | {{ recipient }} | {{ evidence_reference }} |

---

## 13. Risk Register

| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |
|---|---|---|---|---|---|---|
| {{ risk_id }} | {{ title }} | {{ low/medium/high/critical }} | {{ open/mitigated/accepted/transferred/closed }} | {{ mitigation }} | {{ owner }} | {{ evidence_reference }} |

---

## 14. Review Records

| Reviewer | Role | Reviewed At | Decision | Notes |
|---|---|---|---|---|
| {{ reviewer }} | {{ role }} | {{ reviewed_at }} | {{ decision }} | {{ notes }} |

---

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, that policies are sufficient, or that external compliance obligations have been satisfied.
