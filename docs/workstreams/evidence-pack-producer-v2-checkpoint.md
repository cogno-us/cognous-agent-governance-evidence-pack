# Batch 4C-D — Evidence Pack producer 2.0.0 compatibility

## Starting point and scope

Starting main: `ee5367b8c16689ef64216e97e2579e87fd81ecba`.
Branch: `worker14b/evidence-pack-producer-v2`. No existing 4C-D branch or PR was found at inspection. Only Evidence Pack implementation, tests, CI, examples and documentation changed. Final submitted head and the one-time CI result are recorded in the PR handoff; this file is part of that tested commit.

## Compatibility and versioning

| Generation | Executor producer / revision | Control Plane | Replay validator | ODES |
|---|---|---|---|---|
| Accepted observation repair | 2.0.0 / `177354e959cc78c59c1a776f018cfbfbf28c927b` | `2ea9528eeb87e14ff10f05de06473122b9df540f` | `274543f1cd7171784a923a8e37015017a0d8bc9d` | `226adb0e3cde5377ac9db6f7e5857bfa7e65e30a`, implementation profile 0.2 |
| Historical producer | 1.0.0 / `1d308faf664c504b6e310db3c7a310153ef7b067` | `283500652d47a692fb0b99a1172a6d5faffbd9a7` | `f63ce914504dd06813c4ccd199b0570dbd8dd427` | `cba83a1c06f718a8afd76178f36e5cc15896347d`, implementation profile 0.1 |
| Historical unversioned evidence | unversioned / `6b0ba1185bcd390f71df947dda349415e4105f5f` | same historical CP | same historical Replay mapping | same historical ODES mapping |

Manifest stays `46c950bed37fe3812000895430bc0312d29e37ce` in both generations. GAX stays `6bcde026a804c7377f5e39f57ca6dd00b3c3292d`, with its historical dependencies installed and executed before the accepted generation in a separate Python process. CI runs both gates on Python 3.11 and 3.12; no historical tests are dropped or skipped.

New inputs select transformation `agep-manifest-reconstruction-import/0.3.0`. Historical inputs retain transformation 0.2.6 and their revisions. Evidence Pack schema/pack version remains 0.2.0: new fields are additive metadata. Reconstruction Bundle stays 0.2.0. The new transformation explicitly changes delivery-summary semantics and introduces retained-source semantic revalidation; consumers must not interpret it using historical count aggregation. Existing historical examples are not relabeled.

## Contract

The importer reconstructs explicit CP revision, executor contract/provenance, nullable observation, separate owning attempts, CP evidence, rejected content and full reconciliations. It invokes accepted Replay, then compares records, links, commitments, profiles, completeness and effect history with Replay's reconstruction. ODES is used through public APIs in qualification, not as a replacement Replay validator.

Completeness describes supplied records. It does not establish delivery, acknowledgement, testing or authority. Latest supported destination state comes from Replay's exact-effect producer sequence. Independent clocks do not establish ordering. Earlier rejection/unavailability survives recovery; unknown acknowledgement stays unknown. Point-in-time `observed_absent` retains `retry_eligible=false`. Historical `safe_to_retry` remains historical evidence; current permission is never established.

New packs retain exact supplied Manifest and Replay sources, original Replay ID and canonical digest, all lifecycle records, explicit links, reports and conversion findings. A fully retained rejected observation is not automatically a conversion loss; source finding categories remain visible. Source assertions, independent provenance, source commitments and local commitments stay separate. Record `hash` remains the compatibility alias for `local_content_commitment`.

Public validation reimports retained sources and compares material trace and generated inventory/control summaries. Traceable rendering refuses inconsistent traces and includes the complete escaped JSON trace after the readable summary, with no truncation of material records. Earlier rejected wrong-effect content is rendered as rejected source evidence. All source-controlled HTML and Markdown table/control characters are escaped. No import, validation or rendering operation performs dispatch or grants authority.

Retained sources can contain sensitive source content; only the supplied source/derivative is retained, with existing redaction declarations and lineage. This is not an unredaction or authentication facility. Digest agreement establishes local content agreement only.

## Executed evidence

[Machine-readable results](evidence-pack-producer-v2-results.json) contain 15 actual-producer scenarios, identities, observation states, destination counts and unchanged-store assertions. [JSON/Markdown lifecycle pairs](../../examples/producer-v2/) provide rejected wrong-effect, restart recovery, lost acknowledgement, partial delivery and prior absence examples. Generated via `scripts/qualify_producer_v2.py`; no digest was hand-edited.

| Scenario family | Actual destination / supported observation |
|---|---|
| Ordinary execution | one applied effect / applied |
| Wrong-effect, stale, malformed, contradictory or unavailable post-dispatch observation | one applied effect / unknown validated observation, null result observation |
| Restart after unavailable or rejected observation | same one applied effect / later applied, earlier rejection retained |
| Lost acknowledgement | one applied effect / applied, acknowledgement unknown |
| Partial delivery | one partial effect / partial, reconstruction complete |
| Prior interruption followed by fresh absence | zero effects / absent; resubmission denied, retry eligibility false |
| Denied, held, historical absence | zero effects; no new execution |
| Historical applied observation | one existing effect; historical local evidence remains separate |

The generator executes Evidence Pack import, validation and rendering inside the accepted Replay generator's snapshots of full logical SQLite contents and CP record bytes. Every before/after comparison is equal. Exact destination target, amount, unit, payload, effect identity and operation commitment are asserted by the accepted generator. The held case separately asserts zero effects and unchanged stores. ODES public export, record validation and recipient inspection also run inside those assertions: original Replay ID/digest agree, package integrity passes, authentication remains unavailable. Synthetic policy/time/status inputs are test-only.

Local Python 3.12.14: **168 historical tests + 43 accepted-generation tests = 211 passed**, zero failures/skips in final runs. The new suite includes 15 lifecycle cases, 15 source adversarial cases, 8 pack-tampering cases, 3 test-provenance cases, CLI roundtrip and generated-example equivalence. Initial local setup lacked the `agep` command on PATH; installation/path correction resolved those environment failures. No safety assertion was weakened.

Commands (dependency checkout environment shown exactly in `.github/workflows/tests.yml`):

```sh
# Original pinned Replay/ODES/executor/CP and GAX environment
pytest tests --ignore=tests/test_producer_v2.py
agep check-examples
# Fresh process with accepted Replay/ODES installed; explicit accepted checkout env
pytest tests/test_producer_v2.py
python scripts/qualify_producer_v2.py /tmp/agep-producer-v2
agep import --manifest MANIFEST.json --reconstruction REPLAY.json --out PACK.json
agep validate PACK.json
agep render PACK.json --traceable
```

CI is checked once after submission. A queued run is a checkpoint, not a green claim. The PR carries exact head/run status.

## Remaining work

Governor review; no self-merge. GAX has not migrated. Evidence Pack compatibility does not authorize a hub lock update or qualification rerun. Hub PR #4, Batch 4C cases 3–5 and research extensions remain pending separately. Destination-population reconciliation, deployment applicability and human-oversight studies are not implemented here. Authentication, live confinement, distributed delivery/cross-host guarantees, independent real-world verification and operational effectiveness remain unestablished.
