# Migration Notes — Evidence Pack 0.2.0

This release adds a deterministic traceable import path without removing the existing 0.1 hand-authored evidence pack shape.

## Backward compatibility

Existing `pack_version: "0.1"` evidence packs remain loadable by the Pydantic model and validator. Existing top-level sections remain unchanged.

The new importer emits `pack_version: "0.2.0"` and stores import provenance under `metadata.traceable_import`. The primary schema already permits metadata extension through `additionalProperties` inside `metadata`.

## New import path

New command:

```bash
agep import --manifest <manifest.json> --reconstruction <bundle.json> --out <pack.json> [--render <pack.md>]
```

Supported inputs:

- Manifest v1.1 from `cogno-us/cognous-agent-action-manifest` at `46c950bed37fe3812000895430bc0312d29e37ce`.
- Reconstruction Bundle 0.2.0 from `cogno-us/cognous-agent-replay-bundle` at `f12648313cedc2cf06145d397fa56cdea18cc800`.

## New rendering path

New option:

```bash
agep render <pack.json> --traceable --out <pack.md>
```

This includes the standard evidence pack report plus a traceability addendum showing input hashes, transformation version, derived counts, lifecycle summary, control-evidence levels, import findings and source-record references.

## Review semantics

Importing a pack does not create a review decision. Generated packs default to `review_status: draft` and include no human review record unless one is supplied as an attributable source artifact in a later version.

Synthetic integration evidence may support a scoped “tested in this synthetic environment” status. It must not be promoted to operational effectiveness, independent audit, deployment approval or compliance certification.

## Integrity semantics

If upstream artifacts contain HMAC or other shared-secret integrity metadata, this repository treats that as producer-profile integrity only. It does not establish public issuer identity, independent review or third-party attestation.

## Remaining dependencies

- Broader multi-operation and fleet-wide import remains outside the current replay importer boundary.
- Production resolver authentication, host confinement, distributed budgets and independent real-world effect verification remain external to this release.
- Generated packs depend on the supplied artifacts; missing source records are surfaced as limitations, not silently filled.

## 0.2.6 traceability clarification

The importer transformation version advances to `agep-manifest-reconstruction-import/0.2.6` without changing the top-level Evidence Pack schema version.

New trace metadata includes:

- producer-profile revision and provenance status;
- source-supplied commitments, canonicalization profiles and source verification statuses;
- local content commitments and canonicalization profile for retained source records;
- the legacy `hash` field as an alias of `local_content_commitment` for additive compatibility;
- source evidence class without promoting it to independent verification;
- explicit conversion-loss records derived from Replay import findings;
- `current_permission: not_evaluated_from_historical_records`;
- accepted ODES and experimental GAX/IMX pins used by integration validation.

The control-evidence-level summary does not treat import success or runtime records as proof that a test occurred. Replay semantic validation performed during import, source-asserted runtime/fixture provenance and attributable test-run evidence are represented separately. `tested` remains unavailable unless complete attributable test provenance is supplied with meaningful string values for test run identity, producer, scope and result. Malformed provenance emits `T_TEST_PROVENANCE_INVALID`. Any resulting tested-evidence claim is limited to that precise scope and preserves source-stated outcomes such as `failed` or `inconclusive`. No such evidence establishes production effectiveness, adoption, certification, compliance or independent audit.

No migration is required for hand-authored 0.1 packs or earlier 0.2.0 imported packs. Consumers that inspect `metadata.traceable_import` should tolerate the added keys.

## 0.3.1 Control Plane persistence compatibility

The Evidence Pack schema remains `0.2.0`. The importer transformation advances to
`agep-manifest-reconstruction-import/0.3.1` only when the selected Control Plane
producer revision is the accepted persistence repair
`248d899634d9db3518e831bc7ab568a48733f825`.

That path uses accepted Replay
`043830b56595cecddfa65c064afd1c0b95e64792` and its explicit revision/profile
mapping. Producer 2.0.0 remains executor
`177354e959cc78c59c1a776f018cfbfbf28c927b` with Execution Envelope 0.2.0 and
Reconstruction Bundle 0.2.0.

The earlier v2 Control Plane revision
`2ea9528eeb87e14ff10f05de06473122b9df540f`, producer 1.0.0 mappings and
unversioned legacy mappings remain supported without relabelling historical
artifacts. New persistence-path trace metadata separates `selected_revisions`
from `supported_revision_sets`; a supported revision is not presented as the
revision that produced a supplied artifact.

No ODES or GAX compatibility conclusion is introduced for the persistence-repair
path. Existing ODES/GAX pins and tests remain historical combinations.
