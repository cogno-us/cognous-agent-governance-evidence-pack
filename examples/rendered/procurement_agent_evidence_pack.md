# Procurement Agent — Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | ep-procurement-agent-2026-001 |
| Version | 0.1 |
| Generated At | 2026-07-01T11:00:00Z |
| Review Status | approved_with_conditions |
| Agent | ProcurementAgent |
| Environment | production |
| Owner | Head of Procurement |
| Business Unit | Finance and Operations |

## 1. Executive Summary

**ProcurementAgent** is deployed in the **production** environment. Business purpose: Automate vendor quote comparison and purchase recommendation drafting for the procurement team, with human approval required before any purchase order is created or vendor is contacted.

The agent has access to **4** tool(s) and can propose **4** action(s), of which **2** require authority or human review.

**1** replay bundle(s) are available (1 signed).
Validation summary: 1 valid bundle(s), 0 invalid, 0 error(s), 0 warning(s).

**1** open risk(s) (0 critical).

## 2. Agent Overview

**Agent Name:** ProcurementAgent

**Description:** Compares vendor quotes and drafts purchase recommendations. Purchase order creation and vendor email sends require authority and human approval.

**Business Purpose:** Automate vendor quote comparison and purchase recommendation drafting for the procurement team, with human approval required before any purchase order is created or vendor is contacted.

**Owner:** Head of Procurement

**Business Unit:** Finance and Operations

**User Population:** Procurement team members and finance approvers

**Lifecycle Stage:** production


## 3. Deployment Context

**Environment:** production

**Deployment Name:** procurement-agent-prod-v1

**Deployment Date:** 2026-05-01

**Systems Touched:** Procurement Platform, Vendor Database, Email Gateway, ERP System

**Data Domains:** procurement-data, vendor-data, financial-data, communication-records

**Geographic Scope:** North America, EMEA

**Notes:** Production deployment with conditions. Agent operates under human approval requirements for all transactional actions.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| vendor_db_read | Read vendor quotes, profiles, and historical procurement data. | Vendor Database | confidential | read-only | implemented |
| erp_read | Read purchase order history and budget data from the ERP system. | ERP System | confidential | read-only | implemented |
| purchase_order_create | Create a purchase order in the procurement platform. | Procurement Platform | confidential | write | implemented |
| vendor_email_send | Send outbound email to a vendor via the Email Gateway. | Email Gateway | confidential | write | implemented |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |
|---|---|---|---|---|---|---|
| read_vendor_quotes | vendor_db_read | read | No | No | Yes | implemented |
| read_erp_budget | erp_read | read | No | No | Yes | implemented |
| create_purchase_order | purchase_order_create | purchase | Yes | Yes | No | implemented |
| send_vendor_email | vendor_email_send | external_send | Yes | Yes | No | implemented |

## 6. Authority Model

**Summary:** Purchase order creation and vendor email sends require an explicit authority grant from a finance approver. Authority is scoped per transaction and expires after 24 hours.

**Authority Scopes:** purchase_order, vendor_outbound_email

**Privileged Action Types:** purchase, external_send

**Expiration Required:** Yes

**Human Approval Required:** Yes

**Notes:** All authority grants and approvals are logged in the ERP audit trail.


## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Human Approval Gate for Purchase Orders | All purchase order proposals require explicit approval from an authorized finance approver before creation. | implemented | control-log-ep-procurement-001-po |
| Human Review Gate for Vendor Email | All vendor emails drafted by the agent require review and approval before sending. | implemented | control-log-ep-procurement-001-email |
| Vendor Data Access Logging | All vendor database reads are logged with agent identity, vendor ID, and timestamp. | implemented | access-log-ep-procurement-001 |

## 8. Blocked-Action Summary

A total of **5** blocked action(s) are recorded in this evidence pack.

| Action Name | Action Type | Tool | Count | Reason Summary | Evidence Reference |
|---|---|---|---|---|---|
| create_purchase_order | purchase | purchase_order_create | 5 | Five purchase order attempts were blocked due to missing authority grant. Agent initiated purchase flow without a valid authority token. | blocked-log-ep-procurement-001 |

## 9. Reliance Summary

A total of **111** reliance record(s) are recorded in this evidence pack.

| Source Name | Source Type | Count | Scope Summary | Evidence Reference |
|---|---|---|---|---|
| Vendor Database | database | 89 | 89 vendor quote retrievals used for procurement comparison during the review period. | reliance-log-ep-procurement-001 |
| ERP System | erp | 22 | 22 budget and purchase order history reads for decision context. | reliance-log-ep-procurement-002 |

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| rb-procurement-agent-2026-001-a | run-procurement-001 | available | 2026-06-30T16:00:00Z | Yes | Yes | valid | replay-store/rb-procurement-agent-2026-001-a |

## 11. Validation Summary

**Valid Bundles:** 1 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 0

One replay bundle validated successfully. No errors or warnings.


## 12. Redaction and Export Summary

| Export ID | Type | Redacted Fields | Generated At | Intended Recipient | Evidence Reference |
|---|---|---|---|---|---|
| export-procurement-2026-001-redacted | redacted_evidence_pack | vendor_pricing, internal_budget_figures | 2026-07-01T07:00:00Z | External Audit Team | exports/export-procurement-2026-001-redacted |

## 13. Risk Register

| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |
|---|---|---|---|---|---|---|
| risk-procurement-001 | Purchase Order Without Authority | high | mitigated | Authority gate enforced. Blocked-action logging active. Developer notified to fix authority flow. | Head of Procurement | risk-log-ep-procurement-001 |
| risk-procurement-002 | Vendor Data Handling in Multi-Region Deployment | medium | open | Legal and compliance review scheduled for Q3 2026. | General Counsel | — |

## 14. Review Records

| Reviewer | Role | Reviewed At | Decision | Notes |
|---|---|---|---|---|
| J. Martinez | Chief Risk Officer | 2026-07-01T11:00:00Z | approved_with_conditions | Approved with conditions: (1) Authority flow defect must be resolved within 30 days. (2) EMEA vendor data handling compliance review must be completed before EMEA rollout expansion. (3) Monthly blocked-action report required. |

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, that policies are sufficient, or that external compliance obligations have been satisfied.
