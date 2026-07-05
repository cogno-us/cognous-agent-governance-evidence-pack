# Customer Service Agent — Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | ep-cs-agent-2026-001 |
| Version | 0.1 |
| Generated At | 2026-07-01T09:00:00Z |
| Review Status | in_review |
| Agent | CustomerServiceAgent |
| Environment | staging |
| Owner | Head of Customer Operations |
| Business Unit | Customer Experience |

## 1. Executive Summary

**CustomerServiceAgent** is deployed in the **staging** environment. Business purpose: Automate routine customer query responses by reading CRM records and drafting reply emails for human review and approval before sending.

The agent has access to **2** tool(s) and can propose **2** action(s), of which **1** require authority or human review.

**1** replay bundle(s) are available (1 signed).
Validation summary: 1 valid bundle(s), 0 invalid, 0 error(s), 0 warning(s).

No open risks recorded.

## 2. Agent Overview

**Agent Name:** CustomerServiceAgent

**Description:** Reads CRM records and drafts outbound customer emails. Human review is required before any email is sent.

**Business Purpose:** Automate routine customer query responses by reading CRM records and drafting reply emails for human review and approval before sending.

**Owner:** Head of Customer Operations

**Business Unit:** Customer Experience

**User Population:** Customer service team members and supervisors

**Lifecycle Stage:** pilot


## 3. Deployment Context

**Environment:** staging

**Deployment Name:** cs-agent-staging-v1

**Deployment Date:** 2026-06-15

**Systems Touched:** CRM Platform, Email Gateway

**Data Domains:** customer-data, communication-records

**Geographic Scope:** North America

**Notes:** Staging deployment for pilot evaluation. Production rollout pending governance review.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| crm_read | Read customer records and interaction history from the CRM platform. | CRM Platform | confidential | read-only | implemented |
| email_send | Send outbound email to customers via the Email Gateway. | Email Gateway | confidential | write | implemented |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |
|---|---|---|---|---|---|---|
| read_customer_record | crm_read | read | No | No | Yes | implemented |
| send_customer_email | email_send | external_send | Yes | Yes | No | implemented |

## 6. Authority Model

**Summary:** Outbound communication requires an explicit authority grant from a customer service supervisor. Authority expires after 8 hours and must be renewed per-session.

**Authority Scopes:** outbound_email

**Privileged Action Types:** external_send

**Expiration Required:** Yes

**Human Approval Required:** Yes

**Notes:** Authority grants are logged in the CRM audit trail.


## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Human Review Gate for Email Send | All outbound emails drafted by the agent must be reviewed and approved by a human customer service representative before sending. | implemented | control-log-ep-cs-2026-001 |
| CRM Read Audit Logging | All CRM read operations are logged with agent identity, customer ID, and timestamp. | implemented | crm-audit-log-ep-cs-2026-001 |

## 8. Blocked-Action Summary

A total of **3** blocked action(s) are recorded in this evidence pack.

| Action Name | Action Type | Tool | Count | Reason Summary | Evidence Reference |
|---|---|---|---|---|---|
| send_customer_email | external_send | email_send | 3 | Outbound email send blocked in three instances due to missing authority grant. Agent attempted to send without completing the authority request flow. | blocked-log-ep-cs-2026-001 |

## 9. Reliance Summary

A total of **47** reliance record(s) are recorded in this evidence pack.

| Source Name | Source Type | Count | Scope Summary | Evidence Reference |
|---|---|---|---|---|
| CRM Platform | database | 47 | Customer records retrieved for query response drafting, covering 47 customer interactions during the pilot period. | reliance-log-ep-cs-2026-001 |

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| rb-cs-agent-2026-001-a | run-cs-001 | available | 2026-06-30T18:00:00Z | Yes | Yes | valid | replay-store/rb-cs-agent-2026-001-a |

## 11. Validation Summary

**Valid Bundles:** 1 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 0

One replay bundle validated successfully. No errors or warnings.


## 12. Redaction and Export Summary

| Export ID | Type | Redacted Fields | Generated At | Intended Recipient | Evidence Reference |
|---|---|---|---|---|---|
| export-cs-2026-001-redacted | redacted_evidence_pack | customer_ids, email_content | 2026-07-01T08:00:00Z | Compliance Review Team | exports/export-cs-2026-001-redacted |

## 13. Risk Register

| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |
|---|---|---|---|---|---|---|
| risk-cs-001 | Outbound Communication Without Authority | high | mitigated | Human review gate blocks all sends without authority. Blocked-action logging implemented. | Head of Customer Operations | risk-log-ep-cs-2026-001 |
| risk-cs-002 | Customer Data Exposure in Draft Emails | medium | mitigated | Redacted exports produced for compliance review. Human reviewers check content before send. | Data Protection Officer | risk-log-ep-cs-2026-002 |

## 14. Review Records

No review records recorded.

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, that policies are sufficient, or that external compliance obligations have been satisfied.
