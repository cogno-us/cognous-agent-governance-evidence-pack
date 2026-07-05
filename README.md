# Agent Governance Evidence Pack

**Business-facing evidence packages for governed AI-agent deployment.**

Agent Governance Evidence Pack is a lightweight public schema, validator, and markdown renderer for summarizing AI-agent runtime governance evidence. It helps teams document what an agent is deployed to do, which tools and systems it can access, which actions require authority or review, what was blocked, what sources were relied on, what replay bundles exist, what validation results are available, what exports were redacted or signed, and what risks remain open.

It is designed for teams moving from AI-agent demos to governed deployment.

This repository is intentionally narrow. It is not an agent framework, not a model runtime, not a compliance certification product, not a hosted dashboard, and not a complete enterprise governance platform. It is a reference format for business-facing governance evidence.

---

## What it is

An Agent Governance Evidence Pack is a structured JSON document and rendered markdown report that summarizes:

1. What the agent is and why it exists
2. Where it is deployed
3. What tools and systems it can access
4. What actions it can propose
5. What authority model governs privileged actions
6. What policy controls exist
7. What actions were blocked
8. What sources the agent relied on
9. What replay bundles or run records are available
10. What validation results exist
11. What exports were redacted or signed
12. What risks are open
13. Who reviewed the evidence and what was decided

---

## Why it matters

Governance teams need to answer:

- What is this agent deployed to do?
- What systems and tools can it access?
- What actions can it propose?
- Which actions require authority?
- Which actions require human review?
- What was blocked?
- What sources were relied on?
- What replay bundles exist?
- Were exports redacted or signed?
- What validation results are available?
- What risks remain open?
- Who reviewed the evidence?

This repo gives teams a public reference format for business-facing AI-agent governance review.

---

## What an evidence pack contains

| Section | Contents |
|---|---|
| Agent Overview | Name, business purpose, owner, business unit, user population |
| Deployment Context | Environment, systems touched, data domains, geographic scope |
| Tool Inventory | Every tool the agent can access, with data classification and control status |
| Action Inventory | Every action the agent can propose, with authority/review/reliance flags |
| Authority Model | How privileged actions are governed |
| Policy Controls | Controls in place, their implementation status, and evidence references |
| Blocked-Action Summary | What was blocked and why |
| Reliance Summary | What sources the agent relied on |
| Replay Bundle Inventory | Available run records, signed/redacted status |
| Validation Summary | Bundle validation results |
| Redaction and Export Summary | Exports produced for review recipients |
| Risk Register | Known risks with severity, status, and mitigation |
| Review Records | Governance review decisions and conditions |

---

## Quickstart

```bash
pip install -e ".[dev]"
pytest
agep validate examples/customer_service_agent_evidence_pack.json
agep summarize examples/customer_service_agent_evidence_pack.json
agep render examples/customer_service_agent_evidence_pack.json --out /tmp/customer_service_evidence_pack.md
```

---

## Example evidence pack

```json
{
  "pack_id": "ep-cs-agent-2026-001",
  "title": "Customer Service Agent — Governance Evidence Pack",
  "generated_at": "2026-07-01T09:00:00Z",
  "review_status": "in_review",
  "agent_overview": {
    "agent_name": "CustomerServiceAgent",
    "business_purpose": "Automate routine customer query responses by reading CRM records and drafting reply emails for human review.",
    "owner": "Head of Customer Operations",
    "business_unit": "Customer Experience"
  },
  "deployment_context": {
    "environment": "staging",
    "systems_touched": ["CRM Platform", "Email Gateway"],
    "data_domains": ["customer-data", "communication-records"]
  }
}
```

See `examples/` for complete examples.

---

## CLI

```
agep validate <path/to/evidence_pack.json>
  Validate an evidence pack. Returns 0 if valid, 1 if invalid, 2 for load errors.

agep summarize <path/to/evidence_pack.json>
  Print a compact summary of key counts and status.

agep render <path/to/evidence_pack.json> [--out output.md]
  Render an evidence pack as markdown. Prints to stdout if --out is not given.

agep check-examples
  Validate and render all examples/*.json files.
```

---

## Validation

Run validation in Python:

```python
from agent_governance_evidence_pack import load_evidence_pack, validate_evidence_pack

pack = load_evidence_pack("examples/customer_service_agent_evidence_pack.json")
report = validate_evidence_pack(pack)
print(report.valid)   # True or False
for issue in report.issues:
    print(issue.severity.value, issue.code, issue.message)
```

See `docs/validation.md` for all validation rules.

---

## Rendering

```python
from agent_governance_evidence_pack import load_evidence_pack, render_markdown

pack = load_evidence_pack("examples/customer_service_agent_evidence_pack.json")
md = render_markdown(pack)
```

Pre-rendered examples are in `examples/rendered/`. See `docs/rendering.md`.

---

## Relationship to Agent Control Plane and Replay Bundles

Agent Action Manifest declares what an agent may propose.
Agent Control Plane records and governs what an agent actually proposes at runtime.
Agent Replay Bundle packages technical run records for audit and replay.
Agent Governance Evidence Pack translates those runtime records into business-facing governance evidence.

This repository does not depend on any of the above. Evidence packs can be populated from any source, manually or via import helpers.

---

## JSON schemas

Schemas are in `schemas/`. The primary schema is `schemas/evidence_pack.schema.json`. All sub-schemas use JSON Schema Draft 2020-12.

---

## Examples

Four example evidence packs are included:

| Example | Scenario | Review Status |
|---|---|---|
| `customer_service_agent_evidence_pack.json` | CRM read + outbound email draft, email send blocked 3x | `in_review` |
| `internal_research_agent_evidence_pack.json` | Document search and file read, export requires review | `draft` |
| `procurement_agent_evidence_pack.json` | Vendor quote comparison, purchase order blocked 5x | `approved_with_conditions` |
| `finance_workflow_agent_evidence_pack.json` | Invoice processing, payment approval blocked 2x | `approved_with_conditions` |

See `docs/examples.md`.

---

## Security / scope

This is a schema, validator, and markdown renderer. It is not a security boundary. It does not enforce runtime access control. It does not certify compliance. See `SECURITY.md`.

---

## Roadmap

See `docs/roadmap.md`.

---

## License

Apache-2.0. See LICENSE and NOTICE.

Copyright 2026 Cognous.
