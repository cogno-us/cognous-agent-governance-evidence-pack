# Executive Summary — {{ Agent Name }}

**Prepared for:** {{ CIO / CISO / Board Risk Committee / other }}
**Date:** {{ date }}
**Pack ID:** {{ pack_id }}
**Review Status:** {{ review_status }}

---

## Agent

**{{ Agent Name }}** is a {{ brief role description }} deployed in the **{{ environment }}** environment.

**Business Purpose:** {{ business_purpose }}

**Owner:** {{ owner }} — {{ business_unit }}

---

## Deployment Scope

- **Systems accessed:** {{ systems_touched }}
- **Data domains:** {{ data_domains }}
- **Geographic scope:** {{ geographic_scope }}

---

## Tool and Action Summary

| Item | Count |
|---|---|
| Tools available | {{ tool_count }} |
| Actions available | {{ action_count }} |
| Actions requiring authority | {{ authority_required_count }} |
| Actions requiring human review | {{ review_required_count }} |

---

## Authority and Control Posture

{{ Summary of whether authority is required for privileged actions, whether human review gates are in place, and whether controls are implemented, partial, or planned. }}

---

## Blocked Actions

{{ N }} action(s) were blocked during the review period.

{{ Summary of what was blocked and why. }}

---

## Replay Bundle and Validation Status

- **Replay bundles available:** {{ replay_bundle_count }}
- **Signed bundles:** {{ signed_count }}
- **Validation errors:** {{ error_count }}
- **Validation warnings:** {{ warning_count }}

---

## Open Risks

| Risk ID | Title | Severity | Status |
|---|---|---|---|
| {{ risk_id }} | {{ title }} | {{ severity }} | {{ status }} |

**Critical open risks:** {{ critical_open_risk_count }}

---

## Review Decision

{{ Most recent review decision and reviewer. Include conditions if applicable. }}

---

## Limitations

This summary is derived from available runtime and governance records. It does not certify compliance, guarantee the correctness of model outputs, or substitute for legal or regulatory review.
