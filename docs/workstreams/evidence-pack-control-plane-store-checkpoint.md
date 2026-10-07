# Evidence Pack — Control Plane Store Compatibility Checkpoint

## Workstream

Worker 10 — Governance Evidence Pack compatibility for the accepted Control Plane persistence repair.

- Repository: `cogno-us/cognous-agent-governance-evidence-pack`
- Starting accepted Evidence Pack revision: `812194b9a89a5fa21e675200fcb4e0089666f1b6`
- Branch: `worker10/evidence-pack-control-plane-store-compatibility`
- Pack schema: `0.2.0` (unchanged)
- Persistence-path transformation: `agep-manifest-reconstruction-import/0.3.1`

## Accepted dependency combinations

### New repaired-Control-Plane qualification

This workstream qualifies only this accepted combination:

- Manifest: `46c950bed37fe3812000895430bc0312d29e37ce`
- Replay: `043830b56595cecddfa65c064afd1c0b95e64792`
- Control Plane: `248d899634d9db3518e831bc7ab568a48733f825`
- executor: `177354e959cc78c59c1a776f018cfbfbf28c927b`
- executor producer profile: `2.0.0`
- Execution Envelope: `0.2.0`
- Reconstruction Bundle: `0.2.0`

Accepted Replay explicitly maps the repaired Control Plane revision to
`control-plane-bounded-run@248d8996` and preserves
`2ea9528eeb87e14ff10f05de06473122b9df540f` as the previously accepted v2
revision/profile `control-plane-bounded-run@2ea9528e`.

### Historical combinations preserved

Historical mappings are not relabelled:

- unversioned executor / historical Control Plane mappings retain their existing
  accepted revisions;
- executor producer 1.0.0 retains its existing accepted mapping;
- the earlier producer-2.0.0 Evidence Pack path retains Replay
  `274543f1cd7171784a923a8e37015017a0d8bc9d` with Control Plane
  `2ea9528eeb87e14ff10f05de06473122b9df540f`;
- existing ODES and GAX pins remain the historical integration combinations
  already present on accepted main.

The existing ODES/GAX tests do **not** establish compatibility with Control Plane
`248d8996...`. Worker 8 is updating ODES independently. Any future
ODES/GAX-dependent qualification of the repaired Control Plane remains pending a
separately accepted compatibility update.

## Compatibility behavior

For the repaired-Control-Plane path, trace metadata now keeps:

- `selected_revisions`: revisions attributed to the supplied artifact and
  accepted Replay validator used for this import;
- `supported_revision_sets`: revisions the Evidence Pack can accept.

The selected revision is never inferred by replacing a historical revision
string. Control Plane producer revision/profile attribution is checked against
accepted Replay's explicit mapping. Unsupported or contradictory mappings fail
closed.

The import preserves:

- distinct Control Plane and executor attempt namespaces;
- historical rejected observations followed by later accepted recovery;
- acknowledgement separately from destination observation;
- reconstruction completeness separately from delivery state;
- historical authorization separately from current permission;
- `observed_absent` separately from retry permission;
- `retry_eligible: false` without creating retry authority;
- source-asserted provenance separately from independent verification;
- source commitments separately from locally computed commitments;
- `hash` as the compatibility alias of `local_content_commitment`;
- findings, warning counts and redaction/derivative lineage.

## Qualification method

The dedicated qualification helper executes accepted Replay's actual
producer-v2 generator against Control Plane `248d8996...` and executor
`177354e9...`.

Replay's generator snapshots the Control Plane record bytes and the logical
SQLite destination contents before invoking the wrapped Replay import. The
wrapper then executes the public Evidence Pack path:

1. import the generated Reconstruction Bundle;
2. validate the Evidence Pack;
3. render traceable Markdown.

Only after those operations return does the producer generator compare the
Control Plane and destination snapshots. This establishes that the exercised
Evidence Pack import/validation/render path is non-effecting with respect to
those bounded synthetic producer stores. It does not establish production
confinement or independent real-world verification.

The qualification covers success, lost acknowledgement, restart recovery,
rejected-observation then applied recovery, partial delivery, prior observed
absence without retry permission, denied and held no-effect cases, separate
attempt namespaces, unsupported/contradictory revision-profile attribution,
operation/attempt lineage tampering, malformed/missing test provenance and
failed source-attributed test results.

## Assurance boundary

Semantic validation means the accepted Replay validator accepted the retained
records. It does not establish operational effectiveness.

Source assertions are not independent provenance verification. Imported test
provenance does not mean this repository executed the source test. Failed or
inconclusive source results remain visible. Historical authorization does not
establish current permission.

## Validation record

The workflow runs focused repaired-path tests first, then the full applicable
suite under accepted Replay `043830b...`, existing examples and CLI
import/validate/traceable-render checks. Exact final-head CI status and actual
test totals are reported in the PR handoff; this checkpoint does not convert a
queued or unexecuted check into a passing claim.

## Remaining dependency

No upstream interface change is proposed by this workstream.

New-path ODES/GAX qualification is explicitly pending separately accepted
component compatibility; the existing historical ODES/GAX integration is not
evidence for the repaired Control Plane combination.
