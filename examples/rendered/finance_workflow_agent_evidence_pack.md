# Finance Workflow Agent — Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | ep-finance-agent-2026-001 |
| Version | 0.1 |
| Generated At | 2026-07-01T12:00:00Z |
| Review Status | approved_with_conditions |
| Agent | FinanceWorkflowAgent |
| Environment | production |
| Owner | Chief Financial Officer |
| Business Unit | Finance |

## 1. Executive Summary

**FinanceWorkflowAgent** is deployed in the **production** environment. Business purpose: Streamline invoice review and payment approval workflows by reading invoice data, validating against purchase orders, and proposing payment approvals for human authorization.

The agent has access to **4** tool(s) and can propose **4** action(s), of which **2** require authority or human review.

**2** replay bundle(s) are available (2 signed).
Validation summary: 2 valid bundle(s), 0 invalid, 0 error(s), 0 warning(s).

No open risks recorded.
This evidence pack is approved with conditions; see Section 14 for review notes.

## 2. Agent Overview

**Agent Name:** FinanceWorkflowAgent

**Description:** Reads invoices and proposes payment approvals. Payment approval execution requires explicit authority and human review. Produces signed audit exports.

**Business Purpose:** Streamline invoice review and payment approval workflows by reading invoice data, validating against purchase orders, and proposing payment approvals for human authorization.

**Owner:** Chief Financial Officer

**Business Unit:** Finance

**User Population:** Finance team members, payment approvers, and internal auditors

**Lifecycle Stage:** production


## 3. Deployment Context

**Environment:** production

**Deployment Name:** finance-agent-prod-v2

**Deployment Date:** 2026-04-01

**Systems Touched:** Invoice Management System, Payment Gateway, ERP System, Audit Export Service

**Data Domains:** financial-data, payment-data, invoice-data, audit-records

**Geographic Scope:** Global

**Notes:** Production deployment. All payment approval actions require two-factor human authorization.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| invoice_read | Read invoice records from the Invoice Management System. | Invoice Management System | confidential | read-only | implemented |
| erp_po_read | Read purchase order records from the ERP system for invoice matching. | ERP System | confidential | read-only | implemented |
| payment_approve | Submit a payment approval to the Payment Gateway. Requires authority and two-factor human authorization. | Payment Gateway | restricted | write | implemented |
| audit_export | Export signed audit records to the Audit Export Service. | Audit Export Service | confidential | write | implemented |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |
|---|---|---|---|---|---|---|
| read_invoice | invoice_read | read | No | No | Yes | implemented |
| match_invoice_to_po | erp_po_read | read | No | No | Yes | implemented |
| propose_payment_approval | payment_approve | approve | Yes | Yes | No | implemented |
| export_audit_record | audit_export | export | No | Yes | No | implemented |

## 6. Authority Model

**Summary:** Payment approval actions require an authority grant from an authorized payment approver. Two-factor human authorization is required. Authority is scoped per payment batch and expires after 4 hours.

**Authority Scopes:** payment_approval

**Privileged Action Types:** approve

**Expiration Required:** Yes

**Human Approval Required:** Yes

**Notes:** All authority grants are logged in the ERP audit trail and require dual-authorization for payments above the materiality threshold.


## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Two-Factor Human Authorization for Payments | All payment approval proposals require two-factor human authorization: initial approver and a secondary reviewer for payments above materiality threshold. | implemented | control-log-ep-finance-001-payment |
| Human Review Gate for Audit Export | Audit exports require review by the finance compliance lead before delivery to the audit service. | implemented | control-log-ep-finance-001-audit |
| Invoice and PO Audit Logging | All invoice reads and PO matches are logged with agent identity, document IDs, and timestamps. | implemented | access-log-ep-finance-001 |

## 8. Blocked-Action Summary

A total of **2** blocked action(s) are recorded in this evidence pack.

| Action Name | Action Type | Tool | Count | Reason Summary | Evidence Reference |
|---|---|---|---|---|---|
| propose_payment_approval | approve | payment_approve | 2 | Two payment approval proposals were blocked due to expired authority grants. Approvals resubmitted with valid authority on the following business day. | blocked-log-ep-finance-001 |

## 9. Reliance Summary

A total of **390** reliance record(s) are recorded in this evidence pack.

| Source Name | Source Type | Count | Scope Summary | Evidence Reference |
|---|---|---|---|---|
| Invoice Management System | database | 204 | 204 invoice records read for payment processing during the review period. | reliance-log-ep-finance-001 |
| ERP System | erp | 186 | 186 purchase order reads for invoice matching. | reliance-log-ep-finance-002 |

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| rb-finance-agent-2026-001-a | run-finance-001 | available | 2026-06-30T20:00:00Z | Yes | No | valid | replay-store/rb-finance-agent-2026-001-a |
| rb-finance-agent-2026-001-b | run-finance-002 | available | 2026-07-01T06:00:00Z | Yes | Yes | valid | replay-store/rb-finance-agent-2026-001-b |

## 11. Validation Summary

**Valid Bundles:** 2 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 0

Two replay bundles validated successfully. No errors or warnings.


## 12. Redaction and Export Summary

| Export ID | Type | Redacted Fields | Generated At | Intended Recipient | Evidence Reference |
|---|---|---|---|---|---|
| export-finance-2026-001-audit | audit_export | payment_amounts, vendor_bank_details | 2026-07-01T08:00:00Z | Internal Audit | exports/export-finance-2026-001-audit |
| export-finance-2026-001-exec | executive_summary | payment_amounts, invoice_details, vendor_bank_details | 2026-07-01T09:00:00Z | CFO and Board Risk Committee | exports/export-finance-2026-001-exec |

## 13. Risk Register

| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |
|---|---|---|---|---|---|---|
| risk-finance-001 | Payment Approval With Expired Authority | high | mitigated | Authority renewal reminder added to agent workflow. Blocked-action alerting implemented. | Chief Financial Officer | risk-log-ep-finance-001 |
| risk-finance-002 | Invoice Data Completeness | medium | mitigated | Incomplete match flag added to proposals. Reviewers required to confirm completeness before authorizing. | Finance Operations Manager | risk-log-ep-finance-002 |

## 14. Review Records

| Reviewer | Role | Reviewed At | Decision | Notes |
|---|---|---|---|---|
| A. Thompson | Chief Financial Officer | 2026-07-01T12:00:00Z | approved_with_conditions | Approved with conditions: (1) Authority renewal process must be formalized and documented within 14 days. (2) Incomplete invoice match handling must be reviewed and tested before the next payment run. (3) Quarterly evidence pack review scheduled. |

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, that policies are sufficient, or that external compliance obligations have been satisfied.
