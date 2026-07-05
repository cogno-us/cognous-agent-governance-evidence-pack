# Integration with Agent Control Plane

This document explains the conceptual relationship between Agent Governance Evidence Pack and the broader AI-agent governance stack.

---

## Conceptual Flow

```
Agent Action Manifest
    ↓ declares what an agent may propose
Agent Control Plane
    ↓ records and governs what an agent actually proposes at runtime
Agent Replay Bundle
    ↓ packages technical run records for audit and replay
Agent Governance Evidence Pack
    ↓ translates runtime records into business-facing governance evidence
        ↓
Risk / Audit / Executive Review
```

---

## What each component does

**Agent Action Manifest** declares what an agent may propose. It defines the actions and tools available to an agent before deployment.

**Agent Control Plane** records and governs what an agent actually proposes at runtime. It applies policy decisions, logs proposals, records blocked actions, and produces replay bundles.

**Agent Replay Bundle** packages technical run records for audit and replay. It provides the raw evidence that can be replayed, verified, and exported.

**Agent Governance Evidence Pack** translates those runtime records into business-facing governance evidence. It summarizes what happened, what was controlled, what risks remain, and who reviewed the evidence.

---

## This repository's scope

This repository implements Agent Governance Evidence Pack only. It:

- Defines the evidence pack schema.
- Validates evidence pack content.
- Renders evidence packs as readable business documents.
- Provides example evidence packs.

It does not implement the Agent Control Plane, Agent Replay Bundle, or Agent Action Manifest. It does not depend on any of those repositories.

---

## Using evidence packs with other components

Evidence packs can be populated from:

- Agent Control Plane export records.
- Replay bundle validation results.
- Agent Action Manifest field definitions.
- Manual or semi-automated evidence collection.

The evidence pack format is a destination format. It is the document a human reviewer, auditor, or executive reads — not the raw technical record used by the runtime system.

---

## Independence

Evidence packs can be authored, validated, and rendered without any other component. The format is public and does not require proprietary tooling.
