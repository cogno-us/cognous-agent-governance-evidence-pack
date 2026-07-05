# Validation

The `validate_evidence_pack` function checks an `EvidencePack` instance and returns a `ValidationReport`.

```python
from agent_governance_evidence_pack import load_evidence_pack, validate_evidence_pack

pack = load_evidence_pack("examples/customer_service_agent_evidence_pack.json")
report = validate_evidence_pack(pack)
print(report.valid)   # True or False
print(report.issues)  # list of ValidationIssue
```

---

## ValidationReport

| Field | Type | Description |
|---|---|---|
| `valid` | bool | True if no error-severity issues exist. Warnings do not affect validity. |
| `pack_id` | str \| None | The pack_id of the pack validated. |
| `issues` | list | List of `ValidationIssue` records. |

## ValidationIssue

| Field | Type | Description |
|---|---|---|
| `severity` | enum | `"error"` or `"warning"`. |
| `code` | str | Stable code string (e.g., `E001`, `W003`). |
| `message` | str | Business-readable description. |
| `path` | str \| None | Field path where the issue was found. |

---

## Error Rules

Errors cause `valid=False`.

| Code | Rule |
|---|---|
| E001 | `pack_id` must be non-empty. |
| E002 | `title` must be non-empty. |
| E003 | `generated_at` must be non-empty. |
| E004 | `agent_overview.agent_name` must be non-empty. |
| E005 | `agent_overview.business_purpose` must be non-empty. |
| E006 | `deployment_context.environment` must be present. |
| E007 | `tool_inventory` tool_name values must be unique. |
| E008 | `action_inventory` action_name values must be unique. |
| E009 | Every `ActionInventoryItem.tool_name` must reference an existing `ToolInventoryItem`. |
| E010 | Blocked action `count` must not be negative. |
| E011 | Reliance `count` must not be negative. |
| E012 | `risk_register` risk_id values must be unique. |
| E013 | `replay_bundles` bundle_id values must be unique. |
| E014 | `redaction_exports` export_id values must be unique. |
| E015 | `review_status` "approved" or "approved_with_conditions" requires at least one `ReviewRecord`. |
| E016 | `ReviewRecord` decision "approved" or "approved_with_conditions" requires `reviewed_at`. |
| E017 | A critical open risk prevents approval: if `review_status` is "approved" and a risk is critical and open, this is an error. |
| E018 | An action with `authority_required=True` requires `authority_model` to be present. |
| E019 | An action with `review_required=True` requires at least one policy control that mentions review or approval. |
| E020 | `review_status` "approved" with an empty `replay_bundles` list is an error. |

---

## Warning Rules

Warnings do not affect validity. They flag gaps that may need attention.

| Code | Rule |
|---|---|
| W001 | `agent_overview.owner` is missing. |
| W002 | `agent_overview.business_unit` is missing. |
| W003 | `deployment_context.systems_touched` is empty. |
| W004 | `deployment_context.data_domains` is empty. |
| W005 | `tool_inventory` is empty. |
| W006 | `action_inventory` is empty. |
| W007 | `policy_controls` is empty. |
| W008 | `blocked_actions` is empty. |
| W009 | `reliance_summary` is empty. |
| W010 | `replay_bundles` is empty. |
| W011 | `validation_summary` is missing. |
| W012 | `redaction_exports` is empty. |
| W013 | `risk_register` is empty. |
| W014 | `review_records` is empty. |
| W015 | Production deployment with `review_status` "draft" or "in_review". |
| W016 | Production deployment with no redaction exports. |
| W017 | Production deployment with no signed replay bundles. |
| W018 | Action of type `external_send`, `delete`, `purchase`, or `approve` without `review_required=True`. |
| W019 | Action of type `external_send`, `delete`, `purchase`, or `approve` without `authority_required=True`. |
| W020 | Tool with `external_system` set but `data_classification` missing. |

---

## CLI

```bash
agep validate examples/customer_service_agent_evidence_pack.json
```

Exit codes:
- `0` — valid.
- `1` — invalid (errors present).
- `2` — usage error, file not found, JSON parse error, or model validation error.
