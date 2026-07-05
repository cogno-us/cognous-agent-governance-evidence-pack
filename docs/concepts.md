# Concepts

This document defines the core concepts used in Agent Governance Evidence Packs.

---

## Evidence Pack

An **evidence pack** is a structured document that summarizes AI-agent runtime governance evidence for business-facing review. It answers the questions that governance teams, risk managers, compliance officers, and executives need to evaluate before approving an agent for deployment or continuing its operation.

An evidence pack is not a legal certification, not a compliance guarantee, and not a runtime policy engine. It is a record of what is known.

---

## Agent Overview

The **agent overview** identifies the agent being reviewed. It records:

- **Agent name** — the identifier for the agent.
- **Business purpose** — why the agent exists and what business problem it solves.
- **Owner** — who is accountable for this agent.
- **Business unit** — the part of the organization that operates this agent.
- **User population** — who interacts with the agent.
- **Lifecycle stage** — where the agent is in its development and deployment lifecycle.

---

## Deployment Context

The **deployment context** records where and how the agent is deployed:

- **Environment** — development, staging, production, sandbox, or other.
- **Systems touched** — the external systems, APIs, or data stores the agent can access.
- **Data domains** — the categories of data the agent operates over.
- **Geographic scope** — the regulatory or geographic boundaries of the deployment.

---

## Tool Inventory

The **tool inventory** lists every tool available to the agent. A tool is a capability that connects the agent to an external system, data store, or action endpoint.

Each tool record includes:
- The tool name and description.
- The external system it connects to.
- The data classification of data accessed.
- The access mode (e.g., read-only, read-write).
- The control status (implemented, partial, planned, not applicable).

---

## Action Inventory

The **action inventory** lists every action the agent can propose. An action is a specific operation the agent can request through a tool.

Each action record includes:
- The action name and type (read, write, external_send, delete, export, purchase, approve, escalate, other).
- The tool it uses.
- Whether it requires authority to execute.
- Whether it requires human review before execution.
- Whether it creates a reliance record.
- The default posture (allowed, blocked, requires approval).
- The control status.

---

## Authority Model

The **authority model** describes how privileged actions are governed. When an agent can propose actions that require explicit permission (such as sending an outbound communication, making a purchase, or approving a payment), the authority model records:

- How authority is granted and scoped.
- Which action types are considered privileged.
- Whether authority expires.
- Whether a human must approve authority grants.

---

## Policy Controls

**Policy controls** are the governance mechanisms in place to govern agent behavior. Each control record names the control, describes how it works, records its implementation status, and references evidence.

Examples of policy controls:
- Human review gates for privileged actions.
- Audit logging for data access.
- Authority expiration enforcement.

---

## Blocked-Action Summary

The **blocked-action summary** records actions the agent proposed that were denied by policy controls during the review period. It records the action type, the reason it was blocked, the count, and a reference to the evidence.

---

## Reliance Summary

The **reliance summary** records the sources the agent relied on when generating proposals. This is important for evaluating whether agent outputs were based on current, authoritative, or appropriate sources.

---

## Replay Bundle Inventory

A **replay bundle** is a portable technical record of an agent run. The inventory records which replay bundles exist, whether they are signed (cryptographically verified) or redacted (prepared for export), and their validation status.

---

## Validation Summary

The **validation summary** records the results of validating replay bundles: how many passed, how many failed, and the count of errors and warnings.

---

## Redaction and Export Summary

The **redaction and export summary** records any exports generated from evidence: which fields were redacted, who the intended recipient was, and when the export was produced.

---

## Risk Register

The **risk register** records known risks associated with the agent. Each item has a severity (low, medium, high, critical), a status (open, mitigated, accepted, transferred, closed), a mitigation description, and an owner.

---

## Review Records

**Review records** document formal governance reviews conducted on the evidence pack. Each record names the reviewer, their role, the date, the decision, and any conditions attached.

---

## Review Status

The **review status** of the evidence pack as a whole. Possible values:

- `draft` — the evidence pack is being assembled.
- `in_review` — the pack has been submitted for review.
- `approved` — the pack has been approved.
- `approved_with_conditions` — approved subject to named conditions.
- `rejected` — the review resulted in rejection.
- `retired` — the agent has been retired.
