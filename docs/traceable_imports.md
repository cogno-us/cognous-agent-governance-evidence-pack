# Traceable Manifest and Reconstruction Bundle Imports

This document defines the Agent Governance Evidence Pack import contract for the pinned Manifest and Reconstruction Bundle producer baselines.

The importer is deterministic and review-support oriented. It converts supplied artifacts into a business-readable evidence pack, but it does not create authority, execute actions, certify deployment approval, or establish compliance.

## Supported producer baselines

| Producer | Supported revision / format |
|---|---|
| Agent Action Manifest | `46c950bed37fe3812000895430bc0312d29e37ce`, Manifest v1.1 |
| Agent Replay Bundle | `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379` (producer-profile migration head), Reconstruction Bundle 0.2.0 |
| Agent Control Plane | `283500652d47a692fb0b99a1172a6d5faffbd9a7` |
| Moltbot Safe | `054e92d12ccb0bc756ca6652f39fc13b51e05d9b` (executor producer profile 1.0.0), Execution Envelope 0.2.0 |
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
- source-record references, source-supplied commitments, and additive `hash`/local commitment aliases;
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
| Tested | Complete attributable test-run evidence supports a test claim only for its stated scope. Semantic import validation or runtime records alone do not establish that a test occurred. |
| Operationally observed | Independent real-world operational observation. Default is unavailable unless supplied. |

Source-asserted runtime or fixture provenance is recorded separately from attributable test-run evidence. Semantic validation performed during import is also separate. Only complete attributable test-run provenance may support a bounded tested status, and only for its precise stated scope. None of these support “operationally effective,” “independently audited,” or “deployment approved.”

## Integrity and redaction limits

HMAC, where present upstream, establishes shared-secret integrity under its producer profile. It does not establish public issuer identity or independent review.

Original and redacted derivative identities remain distinct. Original commitments must not be presented as verification of modified redacted content.

## Review boundary

An evidence pack supports review. Schema validity, successful reconstruction, traceable derivation and passing synthetic tests do not establish deployment approval, compliance or institutional effectiveness. Default review status remains `draft` unless an attributable human review record is supplied.

## Known limits

The replay importer currently supports one supplied proposal/envelope operation. The evidence pack import path preserves that boundary and does not imply fleet-wide or multi-operation coverage.

Control Plane institution/domain fields and producer versions have known gaps. Authority Context profile references remain distinct from context-instance identifiers. Production resolver authentication, host confinement, distributed budgets and independent real-world effect verification remain outside these baselines.

## Worker 10 bounded review completion

Accepted producer pins used by the traceable importer and integration checks:

- Manifest v1.1: `46c950bed37fe3812000895430bc0312d29e37ce`
- Control Plane: `283500652d47a692fb0b99a1172a6d5faffbd9a7`
- Moltbot Safe: `054e92d12ccb0bc756ca6652f39fc13b51e05d9b` (executor producer profile 1.0.0)
- Reconstruction Bundle 0.2.0 / Replay: `710ceb5667762a5e8f3a7b02e14c40eb8e1a9379` (producer-profile migration head)
- ODES: `aa7c53d3ad8c1d0b9c42620e9c8e2b99cd203873`
- accepted experimental GAX/IMX reference: `9ad378145d326799e3209136e47e82d66c6f69af`

The GAX/IMX reference is consumed only through the Reconstruction Bundle it produces. Exchange-specific metadata remains supplementary unless represented by the supported Replay contract. The importer does not consume unfinished transport interfaces or invent fields to make an exchange artifact look compatible.

### Provenance and evidence levels

Trace metadata preserves producer profile identity, repository revision, source evidence class, source-supplied commitments, locally computed record commitments and whether the declared producer revision matches an accepted pin. The legacy `hash` field remains as an additive compatibility alias of `local_content_commitment`. Producer evidence classes and source commitment verification statuses remain source assertions; this is not independent provenance verification.

Evidence levels are deliberately separate:

- **declared** — a manifest or producer record says a control or requirement exists;
- **implemented** — must be established by implementation-specific evidence, not inferred from declarations;
- **semantic validation performed during import** — the accepted Replay validator ran over the supplied records; this is not test-run evidence;
- **source-asserted runtime evidence** — producer metadata may assert fixture/runtime provenance without proving that a test occurred;
- **attributable test-run evidence** — complete source-attributed test provenance requires meaningful string values for run identity, producer, scope and result, and can support only its precise stated scope; malformed supplied provenance remains unavailable and produces an import finding;
- **tested** — unavailable unless valid attributable test-run evidence is supplied; source-stated outcomes such as passed, failed or inconclusive are preserved rather than normalized into assurance;
- **operationally observed** — requires real deployment observation and is unavailable unless supplied;
- **independently audited** — requires independent evidence and is unavailable unless supplied.

Historical authorization is retained as historical evidence. It does not establish current permission. Local destination observation is kept separate from independent institutional verification.

Replay import findings are retained both as findings and as a conversion-loss register. Missing, unknown, unavailable and redacted states remain distinct; they are never normalized to success or zero.


## Executor producer profile migration

New executor evidence is accepted only when Replay preserves the versioned
`urn:cognous:profiles:moltbot-safe-executor-producer` contract at version
`1.0.0` and the supported proposed repository revision. The Evidence Pack
keeps the interface version, repository revision, source-asserted provenance and
independently established provenance distinct.

Legacy unversioned Moltbot evidence at
`6b0ba1185bcd390f71df947dda349415e4105f5f` remains supported through Replay's
explicit legacy compatibility path. Historical artifacts are not relabeled or
upgraded in place.


## Accepted executor / Replay compatibility

The versioned executor path is validated against:

- Moltbot Safe `1d308faf664c504b6e310db3c7a310153ef7b067`
- executor producer profile
  `urn:cognous:profiles:moltbot-safe-executor-producer` / `1.0.0`
- Execution Envelope `0.2.0`
- Replay `f63ce914504dd06813c4ccd199b0570dbd8dd427`
- ODES `cba83a1c06f718a8afd76178f36e5cc15896347d`

Replay-validated executor attempts and explicitly attributed Control Plane attempts
remain separate namespaces. Evidence Pack reconstructs the accepted Replay
semantic-validation input from those records and rejects ambiguous or dangling
attempt lineage.

The executor contract retains interface/profile version, repository revision,
source-asserted provenance and independently established provenance as separate
facts. Source assertions and locally computed commitments are not promoted to
authentication or independent verification.

Historical unversioned Moltbot artifacts remain supported only through the
legacy Replay-managed revision-pinned path at
`6b0ba1185bcd390f71df947dda349415e4105f5f`. Historical artifacts are not
relabeled as producer-profile 1.0.0 evidence.

The Alvorada/GAX experimental checkout at
`9ad378145d326799e3209136e47e82d66c6f69af` remains a provisional
experimental dependency for bounded compatibility tests. Batch 3C does not
promote it to an accepted stack dependency.
