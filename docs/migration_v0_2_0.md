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

## 0.2.4 traceability clarification

The importer transformation version advances to `agep-manifest-reconstruction-import/0.2.4` without changing the top-level Evidence Pack schema version.

New trace metadata includes:

- producer-profile revision and provenance status;
- local content commitments and canonicalization profile for retained source records;
- source evidence class without promoting it to independent verification;
- explicit conversion-loss records derived from Replay import findings;
- `current_permission: not_evaluated_from_historical_records`;
- accepted ODES and experimental GAX/IMX pins used by integration validation.

The control-evidence-level summary no longer treats import success as proof of runtime control effectiveness. Bounded synthetic producer evidence can support a tested-path statement only. It does not establish production effectiveness, adoption, certification, compliance or independent audit.

No migration is required for hand-authored 0.1 packs or earlier 0.2.0 imported packs. Consumers that inspect `metadata.traceable_import` should tolerate the added keys.
