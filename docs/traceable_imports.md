# Traceable Manifest and Reconstruction Bundle Imports

This document defines the Agent Governance Evidence Pack import contract for the pinned Manifest and Reconstruction Bundle producer baselines.

The importer is deterministic and review-support oriented. It converts supplied artifacts into a business-readable evidence pack, but it does not create authority, execute actions, certify deployment approval, or establish compliance.

## Supported producer baselines

| Producer | Supported revision / format |
|---|---|
| Agent Action Manifest | `46c950bed37fe3812000895430bc0312d29e37ce`, Manifest v1.1 |
| Agent Replay Bundle | `f12648313cedc2cf06145d397fa56cdea18cc800`, Reconstruction Bundle 0.2.0 |
| Agent Control Plane | `283500652d47a692fb0b99a1172a6d5faffbd9a7` |
| Moltbot Safe | `6b0ba1185bcd390f71df947dda349415e4105f5f`, Execution Envelope 0.2.0 |
| Alvorada | `fb3d97938969a89e149e8ff8db2756091d1233fc`, Authority Context 0.1.0 |

The import path currently consumes a Manifest artifact and a Reconstruction Bundle artifact. It does not fetch arbitrary external references. It treats source text as data.

## CLI

```bash
agep import \
  --manifest examples/import_inputs/traceable_manifest.json \
  --reconstruction examples/import_inputs/traceable_reconstruction_bundle.json \
  --out /tmp/traceable_imported_evidence_pack.json \
  --render /tmp/traceable_imported_evidence_pack.md \
  --generated-at 2026-10-05T00:00:00Z
```

Use `agep render --traceable` to render a pack with the traceability addendum:

```bash
agep render /tmp/traceable_imported_evidence_pack.json --traceable --out /tmp/traceable.md
```

## Provenance contract

Every generated pack includes `metadata.traceable_import` with:

- transformation version;
- canonicalization profile;
- input artifact IDs, versions and SHA-256 hashes;
- pinned producer revisions;
- derived counts;
- lifecycle summary;
- control-evidence levels;
- source-record references and hashes;
- import findings;
- manual assessments, if supplied.

Imported facts, computed summaries and manual assessments remain separate. Manual additions require attributable provenance and do not overwrite generated findings.

## Counting rules

The importer uses explicit counting rules:

- `proposal_count` counts distinct action/proposal identifiers, not lifecycle records.
- `decision_count` counts distinct `decision_id` values.
- `distinct_effect_count` counts distinct `effect_id` values and is not inflated by duplicate submission or restart records.
- `control_plane_attempt_count` and `executor_attempt_count` are separate namespaces unless explicit correlation exists.
- repeated lifecycle transition records do not inflate attempt counts.
- missing observations are represented as unavailable and are not counted as zero, failed or successful effects by default.

Coverage denominators are recorded explicitly in `metadata.traceable_import.derived_counts.coverage_denominators`.

## Lifecycle distinctions

The generated lifecycle summary distinguishes:

- authorization granted or held;
- execution attempted;
- acknowledgement received, unknown or not applicable;
- destination observed as absent, applied, partial, unknown or unavailable;
- independent verification performed or unavailable.

A lost acknowledgement followed by an applied observation must retain both facts. The importer therefore does not collapse acknowledgement and destination state into a single success/failure field.

## Control evidence levels

Control evidence is represented at four separate levels:

| Level | Meaning |
|---|---|
| Declared | The Manifest or other source declares the control or requirement. |
| Implemented | Source artifacts report implemented status; this is reported, not independently proven. |
| Tested | Synthetic or supplied test records support a test claim within that environment only. |
| Operationally observed | Independent real-world operational observation. Default is unavailable unless supplied. |

Synthetic integration results may support “tested in this synthetic environment.” They cannot support “operationally effective,” “independently audited,” or “deployment approved.”

## Integrity and redaction limits

HMAC, where present upstream, establishes shared-secret integrity under its producer profile. It does not establish public issuer identity or independent review.

Original and redacted derivative identities remain distinct. Original commitments must not be presented as verification of modified redacted content.

## Review boundary

An evidence pack supports review. Schema validity, successful reconstruction, traceable derivation and passing synthetic tests do not establish deployment approval, compliance or institutional effectiveness. Default review status remains `draft` unless an attributable human review record is supplied.

## Known limits

The replay importer currently supports one supplied proposal/envelope operation. The evidence pack import path preserves that boundary and does not imply fleet-wide or multi-operation coverage.

Control Plane institution/domain fields and producer versions have known gaps. Authority Context profile references remain distinct from context-instance identifiers. Production resolver authentication, host confinement, distributed budgets and independent real-world effect verification remain outside these baselines.
