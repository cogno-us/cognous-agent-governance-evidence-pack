# Rendering

The `render_markdown` function converts an `EvidencePack` into a business-facing markdown document.

```python
from agent_governance_evidence_pack import load_evidence_pack, render_markdown

pack = load_evidence_pack("examples/customer_service_agent_evidence_pack.json")
md = render_markdown(pack)
print(md)
```

---

## Output structure

The rendered document includes the following sections:

1. **Title and metadata table** — pack ID, version, generated at, review status, agent, environment, owner, business unit.
2. **Executive Summary** — narrative summary of the agent, tools, actions, replay bundles, validation status, and open risks.
3. **Agent Overview** — agent name, description, business purpose, owner, business unit, user population, lifecycle stage.
4. **Deployment Context** — environment, deployment name, date, systems touched, data domains, geographic scope, notes.
5. **Tool Inventory** — markdown table.
6. **Action Inventory** — markdown table with authority/review/reliance flags.
7. **Authority Model** — summary, scopes, privileged types, expiration, human approval.
8. **Policy Controls** — markdown table.
9. **Blocked-Action Summary** — total count and markdown table.
10. **Reliance Summary** — total count and markdown table.
11. **Replay Bundle Inventory** — markdown table with signed/redacted/validation status.
12. **Validation Summary** — counts and narrative.
13. **Redaction and Export Summary** — markdown table.
14. **Risk Register** — markdown table.
15. **Review Records** — markdown table.
16. **Known Limitations** — fixed disclaimer text.

---

## CLI

```bash
agep render examples/customer_service_agent_evidence_pack.json --out /tmp/output.md
```

If `--out` is omitted, the rendered markdown is printed to stdout.

---

## Notes

- Pipe characters (`|`) in field values are escaped as `\|` to avoid breaking markdown tables.
- Output is deterministic: same input produces the same output.
- No external calls are made during rendering.
- Empty sections are rendered with a "No X recorded." placeholder.
