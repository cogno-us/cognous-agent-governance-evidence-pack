# Audit and Risk Review — {{ Agent Name }}

**Review Type:** Audit / Risk / Compliance
**Pack ID:** {{ pack_id }}
**Reviewed By:** {{ reviewer }}
**Reviewer Role:** {{ reviewer_role }}
**Review Date:** {{ reviewed_at }}
**Review Status:** {{ review_status }}

---

## 1. Agent Identification

| Field | Value |
|---|---|
| Agent Name | {{ agent_name }} |
| Business Purpose | {{ business_purpose }} |
| Owner | {{ owner }} |
| Business Unit | {{ business_unit }} |
| Environment | {{ environment }} |
| Deployment Date | {{ deployment_date }} |

---

## 2. Evidence Availability

| Evidence Type | Available | Reference |
|---|---|---|
| Tool inventory | Yes / No | — |
| Action inventory | Yes / No | — |
| Authority model | Yes / No | — |
| Policy controls | Yes / No | — |
| Blocked-action log | Yes / No | {{ evidence_reference }} |
| Reliance records | Yes / No | {{ evidence_reference }} |
| Replay bundles | Yes / No | {{ evidence_reference }} |
| Validation report | Yes / No | {{ evidence_reference }} |
| Redacted export | Yes / No | {{ evidence_reference }} |
| Signed export | Yes / No | {{ evidence_reference }} |

---

## 3. Validation Results

| Metric | Value |
|---|---|
| Valid bundles | {{ valid_bundle_count }} |
| Invalid bundles | {{ invalid_bundle_count }} |
| Validation errors | {{ error_count }} |
| Validation warnings | {{ warning_count }} |

**Narrative:** {{ validation_summary }}

---

## 4. Authority and Control Assessment

**Authority model present:** Yes / No

{{ Summary of authority model: who can grant authority, scope, expiration, human approval requirements. }}

**Policy controls implemented:** {{ n of m controls fully implemented }}

| Control Name | Status | Evidence |
|---|---|---|
| {{ control_name }} | {{ status }} | {{ evidence_reference }} |

---

## 5. Blocked-Action Review

| Action | Type | Count | Reason | Evidence |
|---|---|---|---|---|
| {{ action_name }} | {{ type }} | {{ count }} | {{ reason }} | {{ reference }} |

**Audit finding:** {{ any findings or observations regarding blocked actions }}

---

## 6. Reliance Record Review

| Source | Type | Count | Evidence |
|---|---|---|---|
| {{ source_name }} | {{ source_type }} | {{ count }} | {{ reference }} |

**Audit finding:** {{ any findings or observations regarding reliance records }}

---

## 7. Redaction and Export Review

| Export ID | Type | Recipient | Generated At | Evidence |
|---|---|---|---|---|
| {{ export_id }} | {{ type }} | {{ recipient }} | {{ generated_at }} | {{ reference }} |

---

## 8. Risk Assessment

| Risk ID | Title | Severity | Status | Mitigation | Owner |
|---|---|---|---|---|---|
| {{ risk_id }} | {{ title }} | {{ severity }} | {{ status }} | {{ mitigation }} | {{ owner }} |

**Critical open risks:** {{ n }}
**High open risks:** {{ n }}

---

## 9. Review Decision

**Decision:** {{ approved / approved_with_conditions / rejected / in_review }}

**Conditions:** {{ conditions if approved_with_conditions }}

**Notes:** {{ reviewer notes }}

---

## 10. Limitations

This audit review record is based on available evidence summarized in this evidence pack. It does not constitute a legal opinion, a regulatory compliance certification, or a guarantee that the agent will behave correctly in all future conditions.
