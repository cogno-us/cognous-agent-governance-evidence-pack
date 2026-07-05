# Examples

This repository includes four example evidence packs in `examples/` and their rendered markdown output in `examples/rendered/`.

---

## 1. Customer Service Agent

**File:** `examples/customer_service_agent_evidence_pack.json`

**Scenario:** A customer service agent reads CRM records and drafts outbound customer emails. Email sending requires authority and human review. Three blocked-action instances are recorded where the agent attempted to send without a valid authority grant. A signed and redacted replay bundle exists.

**Review status:** `in_review`

**Key governance points:**
- Outbound email blocked in 3 instances due to missing authority.
- Human review gate implemented.
- Risks include outbound communication without approval and customer data exposure.

---

## 2. Internal Research Assistant

**File:** `examples/internal_research_agent_evidence_pack.json`

**Scenario:** An internal research assistant searches internal document repositories and file systems, summarizes content, and can export research summaries. Document search and file read are read-only; export requires review. No blocked actions in this period. Replay bundle exists but is not signed.

**Review status:** `draft`

**Key governance points:**
- No authority model (no privileged action types in scope).
- Export action requires review (partially implemented).
- Risks include stale source material and overbroad file access.

---

## 3. Procurement Agent

**File:** `examples/procurement_agent_evidence_pack.json`

**Scenario:** A procurement agent compares vendor quotes and drafts purchase recommendations. Purchase order creation and vendor email sends require authority and human approval. Five blocked-action instances where purchase orders were attempted without authority. Production deployment. Approved with conditions.

**Review status:** `approved_with_conditions`

**Key governance points:**
- Full authority model with expiration and human approval.
- Five blocked purchase order attempts.
- Conditions include authority flow defect resolution and EMEA compliance review.
- Signed and redacted replay bundle.

---

## 4. Finance Workflow Agent

**File:** `examples/finance_workflow_agent_evidence_pack.json`

**Scenario:** A finance workflow agent reads invoices and proposes payment approvals. Payment approval requires authority and two-factor human authorization. Two payment approval attempts blocked due to expired authority. Signed replay bundles, audit export, and executive summary export. Production deployment.

**Review status:** `approved_with_conditions`

**Key governance points:**
- Two-factor human authorization for payments.
- Two blocked payment approvals due to expired authority.
- Two signed replay bundles.
- Audit export and executive summary export produced.
- Conditions include authority renewal process documentation.

---

## Rendered examples

Pre-rendered markdown versions of all examples are in `examples/rendered/`. You can regenerate them with:

```bash
agep check-examples
```

Or render a single example:

```bash
agep render examples/finance_workflow_agent_evidence_pack.json --out examples/rendered/finance_workflow_agent_evidence_pack.md
```
