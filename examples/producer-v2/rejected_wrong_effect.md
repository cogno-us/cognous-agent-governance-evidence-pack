# Traceable Agent Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | agep-04756c04be67ce5b |
| Version | 0.2.0 |
| Generated At | 2026-10-06T23:33:40.427847+00:00 |
| Review Status | draft |
| Agent | Synthetic Refund Agent |
| Environment | other |
| Owner | cognous-integration-pilot |
| Business Unit | — |

## 1. Executive Summary

**Synthetic Refund Agent** is represented in this evidence pack for the **other** environment. Business purpose: Imported from Manifest and Reconstruction Bundle; business purpose unavailable.

The pack records **1** tool(s), **2** action(s), **2** privileged/review-sensitive action(s), and **1** replay/reconstruction bundle reference(s).

Validation summary: 1 valid bundle(s), 0 invalid bundle(s), 0 error(s), 1 warning(s).
Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit.

No open risks recorded. Absence of incident records does not prove absence of incidents.

## 2. Agent Overview

**Agent Name:** Synthetic Refund Agent

**Description:** Synthetic bounded integration fixture; not deployed and not an institutional grant.

**Business Purpose:** Imported from Manifest and Reconstruction Bundle; business purpose unavailable.

**Owner:** cognous-integration-pilot

**Business Unit:** —

**User Population:** —

**Lifecycle Stage:** —


## 3. Deployment Context

**Environment:** other

**Deployment Name:** synthetic

**Deployment Date:** —

**Systems Touched:** synthetic-refund-ledger

**Data Domains:** —

**Geographic Scope:** —

**Notes:** Generated from retained producer artifacts; does not establish deployment approval or operational effectiveness.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| refund_adapter | Synthetic refund destination adapter. | synthetic-refund-ledger | synthetic | — | planned |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Default Posture | Control Status |
|---|---|---|---|---|---|---|---|
| refund_issue_routine | refund_adapter | write | Yes | Yes | Yes | escalate | planned |
| refund_issue_high_consequence | refund_adapter | write | Yes | Yes | Yes | escalate | planned |

## 6. Authority Model

**Summary:** Authority evidence imported from retained runtime records. This is not a grant or approval.

**Authority Scopes:** —

**Privileged Action Types:** write

**Expiration Required:** Yes

**Human Approval Required:** Yes

**Notes:** Authority Context profile references remain distinct from context-instance identifiers.


## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Manifest declaration | Actions and requirements imported from Manifest v1.1. Declaration alone does not establish implementation. | planned | metadata.traceable_import.input_artifacts&#91;manifest&#93; |
| Review and approval declaration | Manifest review_requirement and approval-related declarations are preserved for review support; declaration alone does not create human approval. | planned | manifest.actions&#91;*&#93;.review_requirement |
| Replay semantic import validation | The importer executed the accepted Replay semantic validator over retained producer records. This is import-time evidence checking, not evidence that runtime controls were operationally effective. | implemented | metadata.traceable_import.replay_semantic_validation |
| Independent operational verification | No independent real-world effect verification supplied. | planned | metadata.traceable_import.lifecycle_summary.independent_verification |

## 8. Blocked-Action Summary

No blocked actions recorded.

## 9. Reliance Summary

No reliance records recorded.

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| 0fab8d60-ea56-4b4f-81c0-2aa22d368769 | run-1 | reconstruction_complete | 2026-10-06T23:33:40.427847+00:00 | No | No | semantically_valid | metadata.traceable_import.source_record_refs |

## 11. Validation Summary

**Valid Bundles:** 1 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 1

Source artifacts passed supported semantic import checks. This does not establish deployment approval, compliance, operational effectiveness, or independent audit.


## 12. Redaction and Export Summary

No redaction or export records recorded.

## 13. Risk Register

No risks recorded. Missing incident records do not prove that no incidents occurred.

## 14. Review Records

No review records recorded. Default review status remains unreviewed/draft unless supplied by an attributable human reviewer.

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, policy controls are sufficient, compliance obligations are satisfied, deployment is approved, controls are operationally effective, or independent audit has occurred. Schema validity and successful reconstruction are review aids only.

## 16. Traceability and Import Provenance

This section is generated from `metadata.traceable_import`. It is review support only. It does not certify deployment approval, compliance, operational effectiveness, or independent audit.

### Input artifacts

| Role | Artifact ID | Version | Hash | Trusted Revision | Verification Status |
|---|---|---|---|---|---|
| manifest | refund-integration-pilot-v1 | 1.1 | sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac | 46c950bed37fe3812000895430bc0312d29e37ce | digest_and_cross_artifact_binding_checked_when_runtime_proposal_present |
| reconstruction_bundle | 0fab8d60-ea56-4b4f-81c0-2aa22d368769 | 0.2.0 | sha256:76809eca9b90195baba7167c53dbb263b351cf4b881a0dc649cf4243624cdacd | 274543f1cd7171784a923a8e37015017a0d8bc9d | validated_complete |

### Transformation

| Field | Value |
|---|---|
| Transformation Version | agep-manifest-reconstruction-import/0.3.0 |
| Canonicalization Profile | json-sort-keys-compact-utf8-no-nan |

### Derived counts

| Count | Value |
|---|---|
| proposal_count | 1 |
| decision_count | 1 |
| distinct_effect_count | 1 |
| control_plane_attempt_count | 1 |
| executor_attempt_count | 1 |
| attempt_transition_record_count | 4 |
| authorization_granted_count | 1 |
| authorization_held_count | 0 |
| authorization_denied_count | 0 |
| destination_observation.absent | 1 |
| acknowledgement.control_plane_received | 1 |
| acknowledgement.execution_result_received | 1 |

Counting rules:
- Repeated lifecycle records do not inflate attempt counts.
- Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.
- Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.
- Destination effects, effect observations and reconciliations are counted separately.
- Missing observations are unavailable, not success or failure.
- Latest supported state uses Replay producer sequence and exact effect lineage; earlier rejection remains visible. Independent clocks do not establish ordering.

### Lifecycle and effect status

| Dimension | Value |
|---|---|
| authorization | authorized |
| current_permission | not_evaluated_from_historical_records |
| execution_attempted | yes |
| acknowledgement | received |
| destination_observed | unknown |
| destination_observation_scope | latest supplied Control Plane reconciliation per exact effect; not a fresh query |
| reconstruction_status | reconstruction_complete |
| retry_permission | not_established |
| independent_verification | unavailable |

- Historical authorization is retained evidence and does not establish current permission.
- Control Plane transition status is preserved separately from acknowledgement receipt.
- Executor acknowledgement is distinct from independently verified delivery.
- A lost or unknown acknowledgement followed by an applied observation retains both facts.
- Observed local destination state does not establish independently verified institutional outcome.
- Reconstruction completeness does not mean effect completion.
- HMAC/shared-secret integrity is not public issuer identity or independent review.
- A software-generated pack cannot create human approval.

### Control evidence levels

| Level | Status | Evidence | Meaning |
|---|---|---|---|
| semantic_validation_performed_during_import | validated_complete | metadata.traceable_import.replay_semantic_validation | the importer executed the accepted Replay semantic validator; this is not a test-run or runtime-control-effectiveness claim |
| source_asserted_runtime_evidence | unavailable | — | no source runtime or fixture provenance was supplied |
| attributable_test_run_evidence | unavailable | — | no complete attributable test-run provenance was supplied |
| declared | present | manifest | control or requirement is declared only |
| implemented | not_established_by_import | — | implementation requires producer-specific evidence; manifest declarations and import success do not suffice |
| tested | unavailable | — | semantic import validation and source runtime records do not by themselves establish that a test occurred |
| tested_in_this_repository | not_evaluated_during_import | — | this import does not execute or imply execution of the Evidence Pack repository test suite |
| operationally_observed | unavailable | — | no production operational observation supplied |
| independently_audited | unavailable | — | no independent audit or certification supplied |

### Import findings and unresolved limitations

| Code | Severity | Path/Source | Message |
|---|---|---|---|
| REPLAY_M003 | info | moltbot.execution_envelope.operation.institution_id | Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding. |
| REPLAY_M004 | info | moltbot.execution_envelope.operation.authority_context_id | At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID. |
| REPLAY_B020 | info | reconciliations | Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness. |
| REPLAY_SEMANTIC_LIMITATION | info | semantics.notes | Replay reconstructs recorded events only; import never renews permission or creates an effect. |
| R_REDACTION_STATE_UNKNOWN | warning | reconstruction_bundle.derivation\|metadata.redaction | Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility. |

### Unresolved issues

| Code | Severity | Message |
|---|---|---|
| U_INDEPENDENT_VERIFICATION_UNAVAILABLE | warning | Destination observation is producer-retained unless independent verifier evidence is supplied. |
| U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED | warning | Synthetic import success cannot support operational effectiveness or deployment approval. |
| U_HISTORICAL_AUTHORIZATION_NOT_CURRENT_PERMISSION | info | Retained authorization is historical evidence only; current permission must be re-evaluated by the runtime authority/control boundary. |
| U_EXCHANGE_METADATA_SUPPLEMENTARY | info | Accepted GAX/IMX exchange metadata remains supplementary unless represented by a supported Replay mapping; the Evidence Pack does not invent exchange fields. |

### Producer profiles

| Profile | Repository | Revision | Format Version | Revision Check | Independent Provenance Verification |
|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e | cogno-us/cognous-agent-control-plane | 2ea9528eeb87e14ff10f05de06473122b9df540f | — | declared_revision_matches_accepted_pin | not_performed |
| moltbot-safe-executor-producer-2.0.0@177354e9 | cogno-us/moltbot-safe | 177354e959cc78c59c1a776f018cfbfbf28c927b | 2.0.0 | declared_revision_matches_accepted_pin | not_performed |

### Executor producer contract

| Field | Value |
|---|---|
| interface_profile_id | urn:cognous:profiles:moltbot-safe-executor-producer |
| interface_profile_version | 2.0.0 |
| repository_revision | 177354e959cc78c59c1a776f018cfbfbf28c927b |
| legacy | False |
| source_asserted_repository_revision | 177354e959cc78c59c1a776f018cfbfbf28c927b |
| source_asserted_profile_id | urn:cognous:profiles:moltbot-safe-executor-producer |
| source_asserted_profile_version | 2.0.0 |
| independently_established_count | 0 |

Executor producer metadata and repository revision are source assertions unless separately established. A locally computed commitment or successful semantic import does not authenticate the producer or independently verify the outcome.

### Conversion losses and source findings

| Code | Category | Severity | Path | Value State | Message |
|---|---|---|---|---|---|
| M003 | conversion_warning | info | moltbot.execution_envelope.operation.institution_id | — | Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding. |
| M004 | conversion_warning | info | moltbot.execution_envelope.operation.authority_context_id | — | At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID. |
| B020 | value_state | info | reconciliations | unknown | Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness. |

### Supporting source-record references

| Record ID | Type | Producer Profile | Evidence Class (source assertion) | Producer Revision | Revision Check | Source Path |
|---|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | runtime_proposal | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | proposal |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | runtime_decision | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | decisions&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2 | control_plane_attempt_transition | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | attempts&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3 | control_plane_attempt_transition | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | attempts&#91;1&#93; |
| control-plane-bounded-run@2ea9528e:effect_observation:4 | effect_observation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | observations&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:reconciliation:5 | reconciliation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | reconciliations&#91;0&#93; |
| control-plane-bounded-run@2ea9528e:reconciliation:6 | reconciliation | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | reconciliations&#91;1&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7 | execution_envelope | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.execution_envelope |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:8 | executor_control_plane_evidence | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.control_plane_evidence |
| moltbot-safe-executor-producer-2.0.0@177354e9:rejected_executor_observation:9 | rejected_executor_observation | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.rejected_observations&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10 | execution_result | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.execution_result |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11 | destination_attempt | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempts&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12 | destination_attempt_event | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempt_events&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13 | destination_attempt_event | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.attempt_events&#91;1&#93; |
| control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14 | moltbot_attributed_control_plane_attempt | control-plane-bounded-run@2ea9528e | producer_reported | 2ea9528eeb87e14ff10f05de06473122b9df540f | declared_revision_matches_accepted_pin | moltbot.control_plane_attempts&#91;0&#93; |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | destination_effect | moltbot-safe-executor-producer-2.0.0@177354e9 | producer_reported | 177354e959cc78c59c1a776f018cfbfbf28c927b | declared_revision_matches_accepted_pin | moltbot.effects&#91;0&#93; |

### Source-supplied commitments

| Record ID | Label | Commitment | Algorithm | Canonicalization | Source Verification Status | Source Path |
|---|---|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | proposal.payload_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | effect_id | sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829 | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | decisions&#91;0&#93;.effect_id |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | proposal_commitment | sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.proposal_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | manifest_digest | sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.manifest_digest |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.payload_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | requirement_commitment | sha256:6590406e701b51e637c87953860d1ceb72d8da0af87311048f152e0ee2b8ccb6 | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.requirement_commitment |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | role_mapping_digest | sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d | SHA-256 | json-sort-keys-compact-utf8-no-nan | attributed_claim | decisions&#91;0&#93;.binding.role_mapping_digest |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7 | payload_commitment | sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | moltbot.execution_envelope.operation.payload_commitment |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | operation_digest | sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175 | SHA-256 | json-sort-keys-compact-utf8-no-nan | checked_match | moltbot.effects&#91;0&#93;.operation_digest |

### Locally computed record commitments

| Record ID | Local Commitment | Compatibility Hash Alias | Canonicalization | Verification Status |
|---|---|---|---|---|
| control-plane-bounded-run@2ea9528e:runtime_proposal:0 | sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4 | sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:runtime_decision:1 | sha256:9b744d3ba695c05c94d8e527fe57bd55b9e900d03fef7f67be42bc699d4ea70c | sha256:9b744d3ba695c05c94d8e527fe57bd55b9e900d03fef7f67be42bc699d4ea70c | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2 | sha256:a8568191c8b44e37205afa84ad60be9db6768a6a106ecf7038a7f5a604dc7f68 | sha256:a8568191c8b44e37205afa84ad60be9db6768a6a106ecf7038a7f5a604dc7f68 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3 | sha256:f8abb3d96d3673bc4084d6bf697605357b780361e1e1730faa41d253336a726a | sha256:f8abb3d96d3673bc4084d6bf697605357b780361e1e1730faa41d253336a726a | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:effect_observation:4 | sha256:7a3a403677038b34e5b1d80e64eef174f348e9946b042263289b530a121f44c3 | sha256:7a3a403677038b34e5b1d80e64eef174f348e9946b042263289b530a121f44c3 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:reconciliation:5 | sha256:99534a5a4e036265c8ec00fbcb31afa074c9f0b8dd8bede778b0b524513bae3d | sha256:99534a5a4e036265c8ec00fbcb31afa074c9f0b8dd8bede778b0b524513bae3d | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:reconciliation:6 | sha256:36410b6699e4ca172f0a4d727d52ce30178651f8162c2943433b609aafebbd80 | sha256:36410b6699e4ca172f0a4d727d52ce30178651f8162c2943433b609aafebbd80 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7 | sha256:68c574288ed763e5d2b6f6a05958b9c8dfa1b0906c305910850c9e21c259d2a2 | sha256:68c574288ed763e5d2b6f6a05958b9c8dfa1b0906c305910850c9e21c259d2a2 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:8 | sha256:a84f7be649d8fe9a73212b779f2002707cc7579edc3fc8f3ec712a36a9917ac5 | sha256:a84f7be649d8fe9a73212b779f2002707cc7579edc3fc8f3ec712a36a9917ac5 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:rejected_executor_observation:9 | sha256:3f776f2a991313989663ee39a9b762f31fd4836f0e23d7b2bed89c872c5ba87f | sha256:3f776f2a991313989663ee39a9b762f31fd4836f0e23d7b2bed89c872c5ba87f | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10 | sha256:15d4fa7ebfcd600f2dd74412b2068339e71e4147cd6b61f43a4420ad8e4ba2d0 | sha256:15d4fa7ebfcd600f2dd74412b2068339e71e4147cd6b61f43a4420ad8e4ba2d0 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11 | sha256:ea0b74b4f74f38faa36294a8fb5cf11f4443047b944083a2e615a95dcf61ec6a | sha256:ea0b74b4f74f38faa36294a8fb5cf11f4443047b944083a2e615a95dcf61ec6a | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12 | sha256:ae58aa77a913c27710ad93bddf89597db25aaa246ce2b26fb08e7dbf284d420d | sha256:ae58aa77a913c27710ad93bddf89597db25aaa246ce2b26fb08e7dbf284d420d | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13 | sha256:606e858704f8d21dc09bfd68b9ea0e928e734d9b32fa99dabf742d76c72bbb22 | sha256:606e858704f8d21dc09bfd68b9ea0e928e734d9b32fa99dabf742d76c72bbb22 | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14 | sha256:b063af3a360bf73f97c6a9d125bb910deb06ed9bf3851e1c9bcbb5f0fdcf2e1f | sha256:b063af3a360bf73f97c6a9d125bb910deb06ed9bf3851e1c9bcbb5f0fdcf2e1f | json-sort-keys-compact-utf8-no-nan | computed_during_import |
| moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15 | sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc | sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc | json-sort-keys-compact-utf8-no-nan | computed_during_import |

Source evidence classes and source verification statuses are retained as producer/source assertions. They are not the importer’s independent assurance or verification.

### Complete material trace (escaped JSON)

The following is the complete trace metadata without truncation. Null observations, rejected content, historical states, policy/evaluation metadata and original sources remain distinct. Rejected evidence is not accepted lineage. No retry or current authority is established.

<pre>{
  "transformation_version": "agep-manifest-reconstruction-import/0.3.0",
  "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
  "supported_revisions": {
    "manifest": "46c950bed37fe3812000895430bc0312d29e37ce",
    "replay": "274543f1cd7171784a923a8e37015017a0d8bc9d",
    "control_plane": "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "moltbot_safe": "177354e959cc78c59c1a776f018cfbfbf28c927b",
    "odes": "226adb0e3cde5377ac9db6f7e5857bfa7e65e30a",
    "gax_imx_experimental_reference": "6bcde026a804c7377f5e39f57ca6dd00b3c3292d",
    "gax_imx_acceptance_status": "provisional_experimental_dependency",
    "alvorada": "fb3d97938969a89e149e8ff8db2756091d1233fc"
  },
  "replay_semantic_validation": {
    "validator": "agent_replay_bundle.importers.import_bounded_workflow",
    "required_revision": "274543f1cd7171784a923a8e37015017a0d8bc9d",
    "status": "validated_complete"
  },
  "replay_import_reports": [
    {
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "source_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "complete": true,
      "field_mappings": {
        "decisions": "records[runtime_decision]",
        "attempts": "records[control_plane_attempt_transition]",
        "observations": "records[effect_observation]",
        "reconciliations": "records[reconciliation]"
      },
      "findings": [
        {
          "code": "M003",
          "category": "conversion_warning",
          "severity": "info",
          "path": "moltbot.execution_envelope.operation.institution_id",
          "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
          "value_state": null
        },
        {
          "code": "M004",
          "category": "conversion_warning",
          "severity": "info",
          "path": "moltbot.execution_envelope.operation.authority_context_id",
          "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
          "value_state": null
        },
        {
          "code": "B020",
          "category": "value_state",
          "severity": "info",
          "path": "reconciliations",
          "message": "Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness.",
          "value_state": "unknown"
        }
      ]
    }
  ],
  "replay_semantics": {
    "record_reconstruction": true,
    "policy_reevaluation": false,
    "model_reexecution": false,
    "external_effect_execution": false,
    "destination_observation": "producer_reported",
    "independent_effect_verification": false,
    "notes": "Replay reconstructs recorded events only; import never renews permission or creates an effect."
  },
  "input_artifacts": [
    {
      "artifact_role": "manifest",
      "artifact_id": "refund-integration-pilot-v1",
      "version": "1.1",
      "hash": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
      "trusted_revision": "46c950bed37fe3812000895430bc0312d29e37ce",
      "verification_status": "digest_and_cross_artifact_binding_checked_when_runtime_proposal_present",
      "commitment_source": "locally_computed",
      "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan"
    },
    {
      "artifact_role": "reconstruction_bundle",
      "artifact_id": "0fab8d60-ea56-4b4f-81c0-2aa22d368769",
      "version": "0.2.0",
      "hash": "sha256:76809eca9b90195baba7167c53dbb263b351cf4b881a0dc649cf4243624cdacd",
      "trusted_revision": "274543f1cd7171784a923a8e37015017a0d8bc9d",
      "verification_status": "validated_complete",
      "commitment_source": "locally_computed",
      "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan"
    }
  ],
  "producer_profiles": [
    {
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "producer": "Cognous Agent Control Plane",
      "repository": "cogno-us/cognous-agent-control-plane",
      "revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "format_version": null,
      "revision_check": "declared_revision_matches_accepted_pin",
      "provenance_status": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "format_name": "BoundedRunRecord",
      "schema_ref": null,
      "notes": "No embedded format version; adapter is revision-pinned."
    },
    {
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "producer": "Moltbot Safe",
      "repository": "cogno-us/moltbot-safe",
      "revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "format_version": "2.0.0",
      "revision_check": "declared_revision_matches_accepted_pin",
      "provenance_status": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "format_name": "Executor producer export",
      "schema_ref": null,
      "notes": "Versioned producer profile; repository provenance remains source-asserted unless separately established."
    }
  ],
  "executor_producer_contract": {
    "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
    "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
    "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
    "interface_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
    "interface_profile_version": "2.0.0",
    "provenance": {
      "mode": "versioned_profile",
      "source_asserted": {
        "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
        "producer_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
        "producer_profile_version": "2.0.0"
      },
      "independently_established": []
    },
    "legacy": false
  },
  "source_record_refs": [
    {
      "record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
      "record_type": "runtime_proposal",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "proposal",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "proposal.payload_commitment",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:e72961e2b5814723f665fcb1335516c1541c158862087867def4116864893ba4"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
      "record_type": "runtime_decision",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "decisions[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "effect_id",
          "value": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "decisions[0].effect_id",
          "notes": "Checked under pinned Control Plane effect-id contract."
        },
        {
          "label": "proposal_commitment",
          "value": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.proposal_commitment",
          "notes": null
        },
        {
          "label": "manifest_digest",
          "value": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.manifest_digest",
          "notes": null
        },
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.payload_commitment",
          "notes": null
        },
        {
          "label": "requirement_commitment",
          "value": "sha256:6590406e701b51e637c87953860d1ceb72d8da0af87311048f152e0ee2b8ccb6",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.requirement_commitment",
          "notes": null
        },
        {
          "label": "role_mapping_digest",
          "value": "sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "attributed_claim",
          "source_path": "decisions[0].binding.role_mapping_digest",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:9b744d3ba695c05c94d8e527fe57bd55b9e900d03fef7f67be42bc699d4ea70c",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:9b744d3ba695c05c94d8e527fe57bd55b9e900d03fef7f67be42bc699d4ea70c"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2",
      "record_type": "control_plane_attempt_transition",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:a8568191c8b44e37205afa84ad60be9db6768a6a106ecf7038a7f5a604dc7f68",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:a8568191c8b44e37205afa84ad60be9db6768a6a106ecf7038a7f5a604dc7f68"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
      "record_type": "control_plane_attempt_transition",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "attempts[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:f8abb3d96d3673bc4084d6bf697605357b780361e1e1730faa41d253336a726a",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:f8abb3d96d3673bc4084d6bf697605357b780361e1e1730faa41d253336a726a"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:4",
      "record_type": "effect_observation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "observations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:7a3a403677038b34e5b1d80e64eef174f348e9946b042263289b530a121f44c3",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:7a3a403677038b34e5b1d80e64eef174f348e9946b042263289b530a121f44c3"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:5",
      "record_type": "reconciliation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "reconciliations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:99534a5a4e036265c8ec00fbcb31afa074c9f0b8dd8bede778b0b524513bae3d",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:99534a5a4e036265c8ec00fbcb31afa074c9f0b8dd8bede778b0b524513bae3d"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:6",
      "record_type": "reconciliation",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "reconciliations[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:36410b6699e4ca172f0a4d727d52ce30178651f8162c2943433b609aafebbd80",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:36410b6699e4ca172f0a4d727d52ce30178651f8162c2943433b609aafebbd80"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7",
      "record_type": "execution_envelope",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.execution_envelope",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "moltbot.execution_envelope.operation.payload_commitment",
          "notes": null
        }
      ],
      "source_content_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:68c574288ed763e5d2b6f6a05958b9c8dfa1b0906c305910850c9e21c259d2a2",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:68c574288ed763e5d2b6f6a05958b9c8dfa1b0906c305910850c9e21c259d2a2"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:8",
      "record_type": "executor_control_plane_evidence",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.control_plane_evidence",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:a84f7be649d8fe9a73212b779f2002707cc7579edc3fc8f3ec712a36a9917ac5",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:a84f7be649d8fe9a73212b779f2002707cc7579edc3fc8f3ec712a36a9917ac5"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:rejected_executor_observation:9",
      "record_type": "rejected_executor_observation",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.rejected_observations[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:3f776f2a991313989663ee39a9b762f31fd4836f0e23d7b2bed89c872c5ba87f",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:3f776f2a991313989663ee39a9b762f31fd4836f0e23d7b2bed89c872c5ba87f"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
      "record_type": "execution_result",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.execution_result",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:15d4fa7ebfcd600f2dd74412b2068339e71e4147cd6b61f43a4420ad8e4ba2d0",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:15d4fa7ebfcd600f2dd74412b2068339e71e4147cd6b61f43a4420ad8e4ba2d0"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
      "record_type": "destination_attempt",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:ea0b74b4f74f38faa36294a8fb5cf11f4443047b944083a2e615a95dcf61ec6a",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:ea0b74b4f74f38faa36294a8fb5cf11f4443047b944083a2e615a95dcf61ec6a"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12",
      "record_type": "destination_attempt_event",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempt_events[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:ae58aa77a913c27710ad93bddf89597db25aaa246ce2b26fb08e7dbf284d420d",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:ae58aa77a913c27710ad93bddf89597db25aaa246ce2b26fb08e7dbf284d420d"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13",
      "record_type": "destination_attempt_event",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.attempt_events[1]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:606e858704f8d21dc09bfd68b9ea0e928e734d9b32fa99dabf742d76c72bbb22",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:606e858704f8d21dc09bfd68b9ea0e928e734d9b32fa99dabf742d76c72bbb22"
    },
    {
      "record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
      "record_type": "moltbot_attributed_control_plane_attempt",
      "producer_profile_id": "control-plane-bounded-run@2ea9528e",
      "source_path": "moltbot.control_plane_attempts[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/cognous-agent-control-plane",
      "producer_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
      "producer_format_version": null,
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [],
      "source_content_commitment": null,
      "source_canonicalization_profile": null,
      "source_commitment_verification_status": null,
      "local_content_commitment": "sha256:b063af3a360bf73f97c6a9d125bb910deb06ed9bf3851e1c9bcbb5f0fdcf2e1f",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:b063af3a360bf73f97c6a9d125bb910deb06ed9bf3851e1c9bcbb5f0fdcf2e1f"
    },
    {
      "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
      "record_type": "destination_effect",
      "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
      "source_path": "moltbot.effects[0]",
      "evidence_class": "producer_reported",
      "evidence_class_status": "source_assertion",
      "producer_repository": "cogno-us/moltbot-safe",
      "producer_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
      "producer_format_version": "2.0.0",
      "producer_revision_check": "declared_revision_matches_accepted_pin",
      "source_asserted_provenance": "source_asserted_and_contract_compared",
      "independent_provenance_verification": "not_performed",
      "source_commitments": [
        {
          "label": "operation_digest",
          "value": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "verification_status": "checked_match",
          "source_path": "moltbot.effects[0].operation_digest",
          "notes": "Checked against the exact retained Execution Envelope operation under the pinned canonicalization profile."
        }
      ],
      "source_content_commitment": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
      "source_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "source_commitment_verification_status": "checked_match",
      "local_content_commitment": "sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc",
      "local_canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
      "local_commitment_verification_status": "computed_during_import",
      "hash": "sha256:edcff53d4d8a61c48841d9256e7f7bca01d45dc62466b4bfef1c3544b1880ebc"
    }
  ],
  "conversion_losses": [
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 0,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "M003",
      "category": "conversion_warning",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.institution_id",
      "value_state": null,
      "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding."
    },
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 1,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "M004",
      "category": "conversion_warning",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.authority_context_id",
      "value_state": null,
      "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID."
    },
    {
      "source": "replay_import_report",
      "report_index": 0,
      "finding_index": 2,
      "adapter_profile": "control-plane-bounded-run@2ea9528e",
      "code": "B020",
      "category": "value_state",
      "severity": "info",
      "path": "reconciliations",
      "value_state": "unknown",
      "message": "Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness."
    }
  ],
  "derived_counts": {
    "proposal_count": 1,
    "decision_count": 1,
    "distinct_effect_count": 1,
    "control_plane_attempt_count": 1,
    "executor_attempt_count": 1,
    "attempt_transition_record_count": 4,
    "destination_effect_count": 1,
    "effect_observation_count": 1,
    "reconciliation_count": 2,
    "destination_observation_counts": {
      "absent": 1
    },
    "destination_effect_state_counts": {
      "applied": 1
    },
    "effect_observation_state_counts": {
      "absent": 1
    },
    "reconciliation_state_counts": {
      "hold": 1,
      "observed_absent": 1
    },
    "execution_result_state_counts": {
      "unknown": 1
    },
    "acknowledgement_counts": {
      "control_plane_received": 1,
      "execution_result_received": 1
    },
    "acknowledgement_sources": [
      {
        "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
        "source": "control_plane_transition",
        "state": "received",
        "status": "acknowledged",
        "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81"
      },
      {
        "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
        "source": "execution_result",
        "state": "received",
        "status": "unknown",
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499"
      }
    ],
    "coverage_denominators": {
      "effect_denominator": "distinct authorized effect_id values",
      "control_plane_attempt_denominator": "unique Control Plane attempt IDs",
      "executor_attempt_denominator": "unique destination_attempt IDs",
      "destination_effect_denominator": "destination_effect records",
      "effect_observation_denominator": "effect_observation records",
      "reconciliation_denominator": "reconciliation records",
      "missing_observation": "unavailable, not zero/success/failure",
      "destination_observation_denominator": "accepted Control Plane effect_observation records only; destination rows and reconciliations counted separately"
    },
    "counting_rules": [
      "Repeated lifecycle records do not inflate attempt counts.",
      "Duplicate submissions do not inflate distinct effect counts when effect_id is unchanged.",
      "Control Plane and executor attempt IDs are separate namespaces unless explicit correlation exists.",
      "Destination effects, effect observations and reconciliations are counted separately.",
      "Missing observations are unavailable, not success or failure.",
      "Latest supported state uses Replay producer sequence and exact effect lineage; earlier rejection remains visible. Independent clocks do not establish ordering."
    ],
    "authorization_granted_count": 1,
    "authorization_held_count": 0,
    "authorization_denied_count": 0
  },
  "lifecycle_summary": {
    "authorization": "authorized",
    "current_permission": "not_evaluated_from_historical_records",
    "execution_attempted": "yes",
    "acknowledgement": "received",
    "acknowledgement_sources": [
      {
        "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
        "source": "control_plane_transition",
        "state": "received",
        "status": "acknowledged",
        "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81"
      },
      {
        "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
        "source": "execution_result",
        "state": "received",
        "status": "unknown",
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499"
      }
    ],
    "control_plane_transition_statuses": {
      "acknowledged": 1,
      "attempted": 1
    },
    "destination_observed": "unknown",
    "independent_verification": "unavailable",
    "notes": [
      "Historical authorization is retained evidence and does not establish current permission.",
      "Control Plane transition status is preserved separately from acknowledgement receipt.",
      "Executor acknowledgement is distinct from independently verified delivery.",
      "A lost or unknown acknowledgement followed by an applied observation retains both facts.",
      "Observed local destination state does not establish independently verified institutional outcome.",
      "Reconstruction completeness does not mean effect completion.",
      "HMAC/shared-secret integrity is not public issuer identity or independent review.",
      "A software-generated pack cannot create human approval."
    ],
    "reconstruction_status": "reconstruction_complete",
    "effect_observation_history": {
      "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829": {
        "basis": "Control Plane reconciliation array order, filtered by exact effect_id",
        "rejected_reconciliation_indices": [
          1
        ],
        "latest_reconciliation": {
          "source_index": 1,
          "result": "hold",
          "observation_accepted": false
        },
        "latest_accepted_observation": {
          "source_index": 0,
          "observation": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-10-05T19:00:00+00:00",
            "state": "absent",
            "destination_state": {}
          }
        },
        "latest_supported_destination_state": "unknown",
        "retry_eligible": false,
        "acknowledgement_history": [
          {
            "source_index": 0,
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "status": "attempted",
            "acknowledgement": {}
          },
          {
            "source_index": 1,
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "status": "acknowledged",
            "acknowledgement": {
              "moltbot_safe_status": "executed",
              "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
              "newly_executed": true,
              "observation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "destination_state": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "amount": 50.0,
                  "unit": "USD",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                }
              }
            }
          }
        ],
        "cross_sequence_order": "not_established",
        "freshness_at_import": "not_evaluated"
      }
    },
    "destination_observation_scope": "latest supplied Control Plane reconciliation per exact effect; not a fresh query",
    "retry_permission": "not_established",
    "historical_local_observation": false
  },
  "control_evidence_levels": {
    "semantic_validation_performed_during_import": {
      "status": "validated_complete",
      "evidence": [
        "metadata.traceable_import.replay_semantic_validation"
      ],
      "meaning": "the importer executed the accepted Replay semantic validator; this is not a test-run or runtime-control-effectiveness claim"
    },
    "source_asserted_runtime_evidence": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "no source runtime or fixture provenance was supplied"
    },
    "attributable_test_run_evidence": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "no complete attributable test-run provenance was supplied"
    },
    "declared": {
      "status": "present",
      "evidence": [
        "manifest"
      ],
      "meaning": "control or requirement is declared only"
    },
    "implemented": {
      "status": "not_established_by_import",
      "evidence": [],
      "meaning": "implementation requires producer-specific evidence; manifest declarations and import success do not suffice"
    },
    "tested": {
      "status": "unavailable",
      "evidence": [],
      "scope": "unavailable",
      "meaning": "semantic import validation and source runtime records do not by themselves establish that a test occurred"
    },
    "tested_in_this_repository": {
      "status": "not_evaluated_during_import",
      "evidence": [],
      "meaning": "this import does not execute or imply execution of the Evidence Pack repository test suite"
    },
    "operationally_observed": {
      "status": "unavailable",
      "evidence": [],
      "meaning": "no production operational observation supplied"
    },
    "independently_audited": {
      "status": "unavailable",
      "evidence": [],
      "meaning": "no independent audit or certification supplied"
    }
  },
  "redaction_state": {
    "redacted": false,
    "source": "unknown_schema_default_false",
    "derivation": null
  },
  "import_findings": [
    {
      "code": "REPLAY_M003",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.institution_id",
      "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
      "category": "conversion_warning",
      "value_state": null
    },
    {
      "code": "REPLAY_M004",
      "severity": "info",
      "path": "moltbot.execution_envelope.operation.authority_context_id",
      "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
      "category": "conversion_warning",
      "value_state": null
    },
    {
      "code": "REPLAY_B020",
      "severity": "info",
      "path": "reconciliations",
      "message": "Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness.",
      "category": "value_state",
      "value_state": "unknown"
    },
    {
      "code": "REPLAY_SEMANTIC_LIMITATION",
      "severity": "info",
      "path": "semantics.notes",
      "message": "Replay reconstructs recorded events only; import never renews permission or creates an effect."
    },
    {
      "code": "R_REDACTION_STATE_UNKNOWN",
      "severity": "warning",
      "path": "reconstruction_bundle.derivation|metadata.redaction",
      "message": "Source did not declare redaction state; EvidencePack boolean defaults to false for schema compatibility."
    }
  ],
  "manual_assessments": [],
  "unresolved_issues": [
    {
      "code": "U_INDEPENDENT_VERIFICATION_UNAVAILABLE",
      "severity": "warning",
      "message": "Destination observation is producer-retained unless independent verifier evidence is supplied."
    },
    {
      "code": "U_OPERATIONAL_EFFECTIVENESS_NOT_MEASURED",
      "severity": "warning",
      "message": "Synthetic import success cannot support operational effectiveness or deployment approval."
    },
    {
      "code": "U_HISTORICAL_AUTHORIZATION_NOT_CURRENT_PERMISSION",
      "severity": "info",
      "message": "Retained authorization is historical evidence only; current permission must be re-evaluated by the runtime authority/control boundary."
    },
    {
      "code": "U_EXCHANGE_METADATA_SUPPLEMENTARY",
      "severity": "info",
      "message": "Accepted GAX/IMX exchange metadata remains supplementary unless represented by a supported Replay mapping; the Evidence Pack does not invent exchange fields."
    }
  ],
  "outcomes_and_burden": {
    "unresolved_delivery": "see lifecycle_summary.destination_observed",
    "incidents": "unavailable_not_zero",
    "remedies": "unavailable",
    "measured_latency": "not_measured",
    "human_review_effort": "not_measured",
    "error_prevention": "not_measured",
    "error_correction": "not_measured",
    "comparison_baseline_reference": "unavailable"
  },
  "retained_sources": {
    "manifest": {
      "manifest_version": "1.1",
      "manifest_id": "refund-integration-pilot-v1",
      "agent_name": "Synthetic Refund Agent",
      "agent_description": "Synthetic bounded integration fixture; not deployed and not an institutional grant.",
      "owner": "cognous-integration-pilot",
      "environment": "synthetic",
      "default_action": "escalate",
      "tools": [
        {
          "tool_name": "refund_adapter",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "description": "Synthetic refund destination adapter.",
          "allowed": true,
          "external_system": "synthetic-refund-ledger",
          "data_classification": "synthetic"
        }
      ],
      "actions": [
        {
          "action_name": "refund_issue_routine",
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "tool_name": "refund_adapter",
          "action_type": "write",
          "description": "Issue one bounded routine synthetic refund.",
          "default_action": "escalate",
          "authority_required": [
            {
              "scope": "refund.issue.routine",
              "description": "Declaration only; downstream resolver must establish a current institutional grant.",
              "required": true,
              "source": "alvorada-authority-context-0.1.0"
            }
          ],
          "review_requirement": {
            "mode": "human_review",
            "reviewer_role": "customer-service-supervisor",
            "reason": "Synthetic routine case retains human review for the integration pilot."
          },
          "reliance_requirement": {
            "required": true,
            "allowed_source_types": [
              "database",
              "user_input"
            ],
            "description": "Record entitlement and customer request evidence."
          },
          "payload_policy": {
            "required_fields": [
              "customer_id",
              "refund_reason"
            ],
            "optional_fields": [],
            "sensitive_fields": [
              "customer_id"
            ],
            "forbidden_fields": []
          },
          "target_policy": {
            "allowed_targets": [
              "urn:cognous:synthetic-account:customer-001"
            ],
            "allow_any_target": false
          },
          "effect_limits": {
            "max_amount": 100.0,
            "unit": "USD",
            "max_effects": 1
          },
          "authority_context": {
            "schema_version": "0.1.0",
            "profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "authority_domain": "customer-refunds",
            "consequence_tier": "T1",
            "evidence_obligation_ids": [
              "urn:cognous:evidence:refund-entitlement"
            ]
          },
          "redaction_hints": [
            {
              "field_path": "customer_id",
              "reason": "Synthetic identifier is treated as sensitive in exported evidence.",
              "replacement": "[REDACTED]"
            }
          ],
          "tags": [
            "synthetic",
            "refund",
            "routine"
          ],
          "metadata": {}
        },
        {
          "action_name": "refund_issue_high_consequence",
          "action_id": "urn:cognous:action:refund-issue-high-v1",
          "tool_name": "refund_adapter",
          "action_type": "write",
          "description": "Issue one higher-consequence synthetic refund requiring explicit approval downstream.",
          "default_action": "escalate",
          "authority_required": [
            {
              "scope": "refund.issue.high",
              "description": "Declaration only; downstream resolver must establish a current institutional grant.",
              "required": true,
              "source": "alvorada-authority-context-0.1.0"
            }
          ],
          "review_requirement": {
            "mode": "approval_required",
            "reviewer_role": "refund-authorizer",
            "reason": "Higher-consequence synthetic case requires explicit approval."
          },
          "reliance_requirement": {
            "required": true,
            "allowed_source_types": [
              "database",
              "user_input"
            ],
            "description": "Record entitlement, amount basis and approval evidence."
          },
          "payload_policy": {
            "required_fields": [
              "customer_id",
              "refund_reason",
              "case_reference"
            ],
            "optional_fields": [],
            "sensitive_fields": [
              "customer_id"
            ],
            "forbidden_fields": []
          },
          "target_policy": {
            "allowed_targets": [
              "urn:cognous:synthetic-account:customer-002"
            ],
            "allow_any_target": false
          },
          "effect_limits": {
            "max_amount": 1000.0,
            "unit": "USD",
            "max_effects": 1
          },
          "authority_context": {
            "schema_version": "0.1.0",
            "profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-high-v1",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "authority_domain": "customer-refunds",
            "consequence_tier": "T2",
            "evidence_obligation_ids": [
              "urn:cognous:evidence:refund-entitlement",
              "urn:cognous:evidence:refund-approval"
            ]
          },
          "redaction_hints": [
            {
              "field_path": "customer_id",
              "reason": "Synthetic identifier is treated as sensitive in exported evidence.",
              "replacement": "[REDACTED]"
            }
          ],
          "tags": [
            "synthetic",
            "refund",
            "higher-consequence"
          ],
          "metadata": {}
        }
      ],
      "metadata": {
        "upstream_alvorada_commit": "fb3d97938969a89e149e8ff8db2756091d1233fc",
        "authority_context_version": "0.1.0",
        "deployment_status": "not_deployed"
      }
    },
    "reconstruction_bundle": {
      "bundle_id": "0fab8d60-ea56-4b4f-81c0-2aa22d368769",
      "bundle_version": "0.2.0",
      "run_id": "run-1",
      "status": "reconstruction_complete",
      "generated_at": "2026-10-06T23:33:40.427847+00:00",
      "producer_profiles": [
        {
          "profile_id": "control-plane-bounded-run@2ea9528e",
          "producer": "Cognous Agent Control Plane",
          "repository": "cogno-us/cognous-agent-control-plane",
          "revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
          "format_name": "BoundedRunRecord",
          "format_version": null,
          "schema_ref": null,
          "notes": "No embedded format version; adapter is revision-pinned."
        },
        {
          "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "producer": "Moltbot Safe",
          "repository": "cogno-us/moltbot-safe",
          "revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
          "format_name": "Executor producer export",
          "format_version": "2.0.0",
          "schema_ref": null,
          "notes": "Versioned producer profile; repository provenance remains source-asserted unless separately established."
        }
      ],
      "records": [
        {
          "record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "runtime_proposal",
          "source_sequence": 0,
          "source_path": "proposal",
          "recorded_at": null,
          "identifiers": {
            "run_id": "run-1",
            "correlation_id": "case-1",
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "manifest_id": "refund-integration-pilot-v1",
            "authority_context_profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1"
          },
          "evidence_class": "producer_reported",
          "data": {
            "manifest_id": "refund-integration-pilot-v1",
            "manifest_version": "1.1",
            "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
            "actor": "urn:cognous:identity:refund-agent-1",
            "principal": "urn:cognous:principal:refund-service",
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
            "target": "urn:cognous:synthetic-account:customer-001",
            "payload": {
              "customer_id": "customer-001",
              "refund_reason": "duplicate"
            },
            "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
            "requested_permissions": [
              "refund.issue.routine"
            ],
            "amount": 50.0,
            "unit": "USD",
            "effects": 1,
            "authority_context_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
            "risk_metadata": {},
            "not_before": null,
            "expires_at": null,
            "correlation_id": "case-1",
            "run_id": "run-1",
            "expected_side_effects": [],
            "evidence_refs": [
              "urn:cognous:evidence:refund-entitlement"
            ]
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "runtime_decision",
          "source_sequence": 1,
          "source_path": "decisions[0]",
          "recorded_at": "2026-10-05T19:00:00+00:00",
          "identifiers": {
            "run_id": "run-1",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "manifest_id": "refund-integration-pilot-v1",
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "grant_id": "urn:cognous:grant:routine-1",
            "grant_revision": "1",
            "authority_context_instance_id": "urn:cognous:authority-context:pilot-1",
            "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1"
          },
          "evidence_class": "producer_reported",
          "data": {
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "result": "authorized",
            "reasons": [],
            "decided_at": "2026-10-05T19:00:00+00:00",
            "binding": {
              "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
              "manifest_id": "refund-integration-pilot-v1",
              "manifest_version": "1.1",
              "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
              "actor": "urn:cognous:identity:refund-agent-1",
              "principal": "urn:cognous:principal:refund-service",
              "action_id": "urn:cognous:action:refund-issue-routine-v1",
              "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
              "requested_permissions": [
                "refund.issue.routine"
              ],
              "amount": 50.0,
              "unit": "USD",
              "effects": 1,
              "authority_context_id": "urn:cognous:authority-context:pilot-1",
              "authority_context_version": "0.1.0",
              "authority_context_status": "proposed_pending_governor_review",
              "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
              "requirement_commitment": "sha256:6590406e701b51e637c87953860d1ceb72d8da0af87311048f152e0ee2b8ccb6",
              "grant_id": "urn:cognous:grant:routine-1",
              "grant_revision": "1",
              "policy_versions": [
                {
                  "ref": "urn:cognous:policy:refund-policy",
                  "version": "1.0"
                }
              ],
              "role_mapping_version": "roles-v1",
              "role_mapping_digest": "sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d",
              "effective_max_effects": 1
            }
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:2",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "control_plane_attempt_transition",
          "source_sequence": 2,
          "source_path": "attempts[0]",
          "recorded_at": "2026-10-05T19:00:00+00:00",
          "identifiers": {
            "run_id": "run-1",
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e"
          },
          "evidence_class": "producer_reported",
          "data": {
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "started_at": "2026-10-05T19:00:00+00:00",
            "status": "attempted",
            "acknowledgement": {},
            "error": null
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "control_plane_attempt_transition",
          "source_sequence": 3,
          "source_path": "attempts[1]",
          "recorded_at": "2026-10-05T19:00:00+00:00",
          "identifiers": {
            "run_id": "run-1",
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e"
          },
          "evidence_class": "producer_reported",
          "data": {
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "started_at": "2026-10-05T19:00:00+00:00",
            "status": "acknowledged",
            "acknowledgement": {
              "moltbot_safe_status": "executed",
              "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
              "newly_executed": true,
              "observation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "destination_state": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "amount": 50.0,
                  "unit": "USD",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                }
              }
            },
            "error": null
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:effect_observation:4",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "effect_observation",
          "source_sequence": 4,
          "source_path": "observations[0]",
          "recorded_at": "2026-10-05T19:00:00+00:00",
          "identifiers": {
            "run_id": "run-1",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "evidence_class": "producer_reported",
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "observed_at": "2026-10-05T19:00:00+00:00",
            "state": "absent",
            "destination_state": {}
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:5",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "reconciliation",
          "source_sequence": 5,
          "source_path": "reconciliations[0]",
          "recorded_at": "2026-10-06T23:33:40.424115+00:00",
          "identifiers": {
            "run_id": "run-1",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "evidence_class": "producer_reported",
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "reconciled_at": "2026-10-06T23:33:40.424115+00:00",
            "result": "observed_absent",
            "observation": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "observed_at": "2026-10-05T19:00:00+00:00",
              "state": "absent",
              "destination_state": {}
            },
            "observation_accepted": true,
            "retry_eligible": false,
            "reasons": [],
            "evaluation_time": "2026-10-05T19:00:00+00:00",
            "observation_max_age_seconds": 60,
            "observation_clock_tolerance_seconds": 5
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:reconciliation:6",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "reconciliation",
          "source_sequence": 6,
          "source_path": "reconciliations[1]",
          "recorded_at": "2026-10-06T23:33:40.425695+00:00",
          "identifiers": {
            "run_id": "run-1",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "evidence_class": "producer_reported",
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
            "result": "hold",
            "observation": {
              "effect_id": "rejected-unrelated-effect",
              "observed_at": "2026-10-05T19:00:00+00:00",
              "state": "applied",
              "destination_state": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "grant_id": "urn:cognous:grant:routine-1",
                "target": "urn:cognous:synthetic-account:customer-001",
                "amount": 50.0,
                "unit": "USD",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
              }
            },
            "observation_accepted": false,
            "retry_eligible": false,
            "reasons": [
              "observation_effect_id_mismatch"
            ],
            "evaluation_time": "2026-10-05T19:00:00+00:00",
            "observation_max_age_seconds": 60,
            "observation_clock_tolerance_seconds": 5
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "execution_envelope",
          "source_sequence": 7,
          "source_path": "moltbot.execution_envelope",
          "recorded_at": null,
          "identifiers": {
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "manifest_id": "refund-integration-pilot-v1",
            "action_id": "urn:cognous:action:refund-issue-routine-v1",
            "grant_id": "urn:cognous:grant:routine-1",
            "grant_revision": "1",
            "authority_context_profile_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
            "institution_id": "urn:cognous:institution:synthetic-customer-service",
            "authority_domain": "customer-refunds"
          },
          "evidence_class": "producer_reported",
          "data": {
            "version": "0.2.0",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "operation": {
              "actor": "urn:cognous:identity:refund-agent-1",
              "principal": "urn:cognous:principal:refund-service",
              "institution_id": "urn:cognous:institution:synthetic-customer-service",
              "authority_domain": "customer-refunds",
              "manifest_id": "refund-integration-pilot-v1",
              "manifest_version": "1.1",
              "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
              "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
              "action_id": "urn:cognous:action:refund-issue-routine-v1",
              "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
              "requested_permissions": [
                "refund.issue.routine"
              ],
              "amount": 50.0,
              "unit": "USD",
              "effects": 1,
              "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
              "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
              "grant_id": "urn:cognous:grant:routine-1",
              "grant_revision": "1",
              "effective_max_effects": 1
            },
            "attempt_id": null
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:executor_control_plane_evidence:8",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "executor_control_plane_evidence",
          "source_sequence": 8,
          "source_path": "moltbot.control_plane_evidence",
          "recorded_at": null,
          "identifiers": {},
          "evidence_class": "producer_reported",
          "data": {
            "attempt": {
              "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
              "started_at": "2026-10-05T19:00:00+00:00",
              "status": "acknowledged",
              "acknowledgement": {
                "moltbot_safe_status": "executed",
                "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
                "newly_executed": true,
                "observation": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "destination_state": {
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied",
                    "grant_id": "urn:cognous:grant:routine-1",
                    "target": "urn:cognous:synthetic-account:customer-001",
                    "amount": 50.0,
                    "unit": "USD",
                    "payload": {
                      "customer_id": "customer-001",
                      "refund_reason": "duplicate"
                    },
                    "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                  }
                }
              },
              "error": null
            },
            "reconciliation": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
              "result": "hold",
              "observation": {
                "effect_id": "rejected-unrelated-effect",
                "observed_at": "2026-10-05T19:00:00+00:00",
                "state": "applied",
                "destination_state": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "amount": 50.0,
                  "unit": "USD",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                }
              },
              "observation_accepted": false,
              "retry_eligible": false,
              "reasons": [
                "observation_effect_id_mismatch"
              ],
              "evaluation_time": "2026-10-05T19:00:00+00:00",
              "observation_max_age_seconds": 60,
              "observation_clock_tolerance_seconds": 5
            }
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:rejected_executor_observation:9",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "rejected_executor_observation",
          "source_sequence": 9,
          "source_path": "moltbot.rejected_observations[0]",
          "recorded_at": null,
          "identifiers": {},
          "evidence_class": "producer_reported",
          "data": {
            "effect_id": "rejected-unrelated-effect",
            "observed_at": "2026-10-05T19:00:00+00:00",
            "state": "applied",
            "destination_state": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied",
              "grant_id": "urn:cognous:grant:routine-1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "amount": 50.0,
              "unit": "USD",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
            }
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_result:10",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "execution_result",
          "source_sequence": 10,
          "source_path": "moltbot.execution_result",
          "recorded_at": null,
          "identifiers": {
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499"
          },
          "evidence_class": "producer_reported",
          "data": {
            "status": "unknown",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "attempted": true,
            "acknowledged": true,
            "observed_state": "unknown",
            "newly_executed": true,
            "observation": null,
            "error": "observation_effect_id_mismatch",
            "control_plane_evidence": {
              "attempt": {
                "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
                "started_at": "2026-10-05T19:00:00+00:00",
                "status": "acknowledged",
                "acknowledgement": {
                  "moltbot_safe_status": "executed",
                  "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
                  "newly_executed": true,
                  "observation": {
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied",
                    "destination_state": {
                      "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                      "state": "applied",
                      "grant_id": "urn:cognous:grant:routine-1",
                      "target": "urn:cognous:synthetic-account:customer-001",
                      "amount": 50.0,
                      "unit": "USD",
                      "payload": {
                        "customer_id": "customer-001",
                        "refund_reason": "duplicate"
                      },
                      "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                    }
                  }
                },
                "error": null
              },
              "reconciliation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
                "result": "hold",
                "observation": {
                  "effect_id": "rejected-unrelated-effect",
                  "observed_at": "2026-10-05T19:00:00+00:00",
                  "state": "applied",
                  "destination_state": {
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied",
                    "grant_id": "urn:cognous:grant:routine-1",
                    "target": "urn:cognous:synthetic-account:customer-001",
                    "amount": 50.0,
                    "unit": "USD",
                    "payload": {
                      "customer_id": "customer-001",
                      "refund_reason": "duplicate"
                    },
                    "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                  }
                },
                "observation_accepted": false,
                "retry_eligible": false,
                "reasons": [
                  "observation_effect_id_mismatch"
                ],
                "evaluation_time": "2026-10-05T19:00:00+00:00",
                "observation_max_age_seconds": 60,
                "observation_clock_tolerance_seconds": 5
              }
            }
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "destination_attempt",
          "source_sequence": 11,
          "source_path": "moltbot.attempts[0]",
          "recorded_at": null,
          "identifiers": {
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e"
          },
          "evidence_class": "producer_reported",
          "data": {
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
            "created_at": 1791329620.424714
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:12",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "destination_attempt_event",
          "source_sequence": 12,
          "source_path": "moltbot.attempt_events[0]",
          "recorded_at": null,
          "identifiers": {
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "event_id": "1",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e"
          },
          "evidence_class": "producer_reported",
          "data": {
            "event_id": 1,
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "status": "attempted",
            "error": null,
            "created_at": 1791329620.424817
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt_event:13",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "destination_attempt_event",
          "source_sequence": 13,
          "source_path": "moltbot.attempt_events[1]",
          "recorded_at": null,
          "identifiers": {
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "event_id": "2",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e"
          },
          "evidence_class": "producer_reported",
          "data": {
            "event_id": 2,
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "status": "executed",
            "error": null,
            "created_at": 1791329620.4252424
          }
        },
        {
          "record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
          "producer_profile_id": "control-plane-bounded-run@2ea9528e",
          "record_type": "moltbot_attributed_control_plane_attempt",
          "source_sequence": 14,
          "source_path": "moltbot.control_plane_attempts[0]",
          "recorded_at": null,
          "identifiers": {
            "run_id": "run-1",
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829"
          },
          "evidence_class": "producer_reported",
          "data": {
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "started_at": "2026-10-05T19:00:00+00:00",
            "status": "acknowledged",
            "acknowledgement": {
              "moltbot_safe_status": "executed",
              "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
              "newly_executed": true,
              "observation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "destination_state": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "amount": 50.0,
                  "unit": "USD",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                }
              }
            },
            "error": null
          }
        },
        {
          "record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
          "producer_profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "record_type": "destination_effect",
          "source_sequence": 15,
          "source_path": "moltbot.effects[0]",
          "recorded_at": null,
          "identifiers": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "grant_id": "urn:cognous:grant:routine-1"
          },
          "evidence_class": "producer_reported",
          "data": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
            "grant_id": "urn:cognous:grant:routine-1",
            "target": "urn:cognous:synthetic-account:customer-001",
            "amount": 50.0,
            "unit": "USD",
            "payload_json": "{\"customer_id\":\"customer-001\",\"refund_reason\":\"duplicate\"}",
            "state": "applied"
          }
        }
      ],
      "links": [
        {
          "link_type": "explicit",
          "from_record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
          "to_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
          "basis": "Producer-supplied Control Plane attempt evidence exactly matches the retained Control Plane run record.",
          "establishes_identity_equivalence": true
        },
        {
          "link_type": "explicit",
          "from_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
          "to_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
          "basis": "Control Plane acknowledgement explicitly supplied executor attempt_id.",
          "establishes_identity_equivalence": false
        }
      ],
      "commitments": [
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_proposal:0",
          "source_path": "proposal.payload_commitment",
          "verification_status": "checked_match",
          "notes": null
        },
        {
          "label": "effect_id",
          "value": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].effect_id",
          "verification_status": "checked_match",
          "notes": "Checked under pinned Control Plane effect-id contract."
        },
        {
          "label": "proposal_commitment",
          "value": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].binding.proposal_commitment",
          "verification_status": "attributed_claim",
          "notes": null
        },
        {
          "label": "manifest_digest",
          "value": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].binding.manifest_digest",
          "verification_status": "attributed_claim",
          "notes": null
        },
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].binding.payload_commitment",
          "verification_status": "attributed_claim",
          "notes": null
        },
        {
          "label": "requirement_commitment",
          "value": "sha256:6590406e701b51e637c87953860d1ceb72d8da0af87311048f152e0ee2b8ccb6",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].binding.requirement_commitment",
          "verification_status": "attributed_claim",
          "notes": null
        },
        {
          "label": "role_mapping_digest",
          "value": "sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "control-plane-bounded-run@2ea9528e:runtime_decision:1",
          "source_path": "decisions[0].binding.role_mapping_digest",
          "verification_status": "attributed_claim",
          "notes": null
        },
        {
          "label": "payload_commitment",
          "value": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:execution_envelope:7",
          "source_path": "moltbot.execution_envelope.operation.payload_commitment",
          "verification_status": "checked_match",
          "notes": null
        },
        {
          "label": "operation_digest",
          "value": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
          "algorithm": "SHA-256",
          "canonicalization_profile": "json-sort-keys-compact-utf8-no-nan",
          "source_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_effect:15",
          "source_path": "moltbot.effects[0].operation_digest",
          "verification_status": "checked_match",
          "notes": "Checked against the exact retained Execution Envelope operation under the pinned canonicalization profile."
        }
      ],
      "import_reports": [
        {
          "adapter_profile": "control-plane-bounded-run@2ea9528e",
          "source_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
          "complete": true,
          "field_mappings": {
            "decisions": "records[runtime_decision]",
            "attempts": "records[control_plane_attempt_transition]",
            "observations": "records[effect_observation]",
            "reconciliations": "records[reconciliation]"
          },
          "findings": [
            {
              "code": "M003",
              "category": "conversion_warning",
              "severity": "info",
              "path": "moltbot.execution_envelope.operation.institution_id",
              "message": "Institution/domain provenance is the trusted Moltbot integration context, not Control Plane AuthorizationBinding.",
              "value_state": null
            },
            {
              "code": "M004",
              "category": "conversion_warning",
              "severity": "info",
              "path": "moltbot.execution_envelope.operation.authority_context_id",
              "message": "At the pinned adapter this field carries the proposal profile reference; it is distinct from the Control Plane binding context-instance ID.",
              "value_state": null
            },
            {
              "code": "B020",
              "category": "value_state",
              "severity": "info",
              "path": "reconciliations",
              "message": "Historical rejected/unavailable observations are fully retained. This finding does not determine latest delivery state or reconstruction completeness.",
              "value_state": "unknown"
            }
          ]
        }
      ],
      "semantics": {
        "record_reconstruction": true,
        "policy_reevaluation": false,
        "model_reexecution": false,
        "external_effect_execution": false,
        "destination_observation": "producer_reported",
        "independent_effect_verification": false,
        "notes": "Replay reconstructs recorded events only; import never renews permission or creates an effect."
      },
      "derivation": null,
      "integrity": [],
      "metadata": {
        "effect_observation_history": {
          "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829": {
            "basis": "Control Plane reconciliation array order, filtered by exact effect_id",
            "rejected_reconciliation_indices": [
              1
            ],
            "latest_reconciliation": {
              "source_index": 1,
              "result": "hold",
              "observation_accepted": false
            },
            "latest_accepted_observation": {
              "source_index": 0,
              "observation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "observed_at": "2026-10-05T19:00:00+00:00",
                "state": "absent",
                "destination_state": {}
              }
            },
            "latest_supported_destination_state": "unknown",
            "retry_eligible": false,
            "acknowledgement_history": [
              {
                "source_index": 0,
                "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
                "status": "attempted",
                "acknowledgement": {}
              },
              {
                "source_index": 1,
                "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
                "status": "acknowledged",
                "acknowledgement": {
                  "moltbot_safe_status": "executed",
                  "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
                  "newly_executed": true,
                  "observation": {
                    "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                    "state": "applied",
                    "destination_state": {
                      "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                      "state": "applied",
                      "grant_id": "urn:cognous:grant:routine-1",
                      "target": "urn:cognous:synthetic-account:customer-001",
                      "amount": 50.0,
                      "unit": "USD",
                      "payload": {
                        "customer_id": "customer-001",
                        "refund_reason": "duplicate"
                      },
                      "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                    }
                  }
                }
              }
            ],
            "cross_sequence_order": "not_established",
            "freshness_at_import": "not_evaluated"
          }
        },
        "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
        "moltbot_safe_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
        "moltbot_producer_contract": {
          "profile_id": "moltbot-safe-executor-producer-2.0.0@177354e9",
          "control_plane_revision": "2ea9528eeb87e14ff10f05de06473122b9df540f",
          "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
          "interface_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
          "interface_profile_version": "2.0.0",
          "provenance": {
            "mode": "versioned_profile",
            "source_asserted": {
              "repository_revision": "177354e959cc78c59c1a776f018cfbfbf28c927b",
              "producer_profile_id": "urn:cognous:profiles:moltbot-safe-executor-producer",
              "producer_profile_version": "2.0.0"
            },
            "independently_established": []
          },
          "legacy": false
        },
        "manifest_revision": "46c950bed37fe3812000895430bc0312d29e37ce",
        "alvorada_revision": "fb3d97938969a89e149e8ff8db2756091d1233fc",
        "freshness": "current"
      }
    }
  },
  "retained_source_scope": "exact supplied sources, including declared redaction/derivative lineage; no unredaction",
  "lifecycle_records": {
    "runtime_proposal": [
      {
        "manifest_id": "refund-integration-pilot-v1",
        "manifest_version": "1.1",
        "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
        "actor": "urn:cognous:identity:refund-agent-1",
        "principal": "urn:cognous:principal:refund-service",
        "action_id": "urn:cognous:action:refund-issue-routine-v1",
        "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
        "target": "urn:cognous:synthetic-account:customer-001",
        "payload": {
          "customer_id": "customer-001",
          "refund_reason": "duplicate"
        },
        "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
        "requested_permissions": [
          "refund.issue.routine"
        ],
        "amount": 50.0,
        "unit": "USD",
        "effects": 1,
        "authority_context_ref": "urn:cognous:alvorada:public-stack-profile:0.1.0",
        "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
        "risk_metadata": {},
        "not_before": null,
        "expires_at": null,
        "correlation_id": "case-1",
        "run_id": "run-1",
        "expected_side_effects": [],
        "evidence_refs": [
          "urn:cognous:evidence:refund-entitlement"
        ]
      }
    ],
    "runtime_decision": [
      {
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "result": "authorized",
        "reasons": [],
        "decided_at": "2026-10-05T19:00:00+00:00",
        "binding": {
          "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "manifest_id": "refund-integration-pilot-v1",
          "manifest_version": "1.1",
          "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "actor": "urn:cognous:identity:refund-agent-1",
          "principal": "urn:cognous:principal:refund-service",
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "target": "urn:cognous:synthetic-account:customer-001",
          "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "requested_permissions": [
            "refund.issue.routine"
          ],
          "amount": 50.0,
          "unit": "USD",
          "effects": 1,
          "authority_context_id": "urn:cognous:authority-context:pilot-1",
          "authority_context_version": "0.1.0",
          "authority_context_status": "proposed_pending_governor_review",
          "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
          "requirement_commitment": "sha256:6590406e701b51e637c87953860d1ceb72d8da0af87311048f152e0ee2b8ccb6",
          "grant_id": "urn:cognous:grant:routine-1",
          "grant_revision": "1",
          "policy_versions": [
            {
              "ref": "urn:cognous:policy:refund-policy",
              "version": "1.0"
            }
          ],
          "role_mapping_version": "roles-v1",
          "role_mapping_digest": "sha256:f8a8db156df7087ddf34be1ed77fc86fa20ba7668deb87a9b3a5bd0a6ace496d",
          "effective_max_effects": 1
        }
      }
    ],
    "control_plane_attempt_transition": [
      {
        "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "started_at": "2026-10-05T19:00:00+00:00",
        "status": "attempted",
        "acknowledgement": {},
        "error": null
      },
      {
        "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "started_at": "2026-10-05T19:00:00+00:00",
        "status": "acknowledged",
        "acknowledgement": {
          "moltbot_safe_status": "executed",
          "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
          "newly_executed": true,
          "observation": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "state": "applied",
            "destination_state": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied",
              "grant_id": "urn:cognous:grant:routine-1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "amount": 50.0,
              "unit": "USD",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
            }
          }
        },
        "error": null
      }
    ],
    "effect_observation": [
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "observed_at": "2026-10-05T19:00:00+00:00",
        "state": "absent",
        "destination_state": {}
      }
    ],
    "reconciliation": [
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "reconciled_at": "2026-10-06T23:33:40.424115+00:00",
        "result": "observed_absent",
        "observation": {
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "observed_at": "2026-10-05T19:00:00+00:00",
          "state": "absent",
          "destination_state": {}
        },
        "observation_accepted": true,
        "retry_eligible": false,
        "reasons": [],
        "evaluation_time": "2026-10-05T19:00:00+00:00",
        "observation_max_age_seconds": 60,
        "observation_clock_tolerance_seconds": 5
      },
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
        "result": "hold",
        "observation": {
          "effect_id": "rejected-unrelated-effect",
          "observed_at": "2026-10-05T19:00:00+00:00",
          "state": "applied",
          "destination_state": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "state": "applied",
            "grant_id": "urn:cognous:grant:routine-1",
            "target": "urn:cognous:synthetic-account:customer-001",
            "amount": 50.0,
            "unit": "USD",
            "payload": {
              "customer_id": "customer-001",
              "refund_reason": "duplicate"
            },
            "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
          }
        },
        "observation_accepted": false,
        "retry_eligible": false,
        "reasons": [
          "observation_effect_id_mismatch"
        ],
        "evaluation_time": "2026-10-05T19:00:00+00:00",
        "observation_max_age_seconds": 60,
        "observation_clock_tolerance_seconds": 5
      }
    ],
    "execution_envelope": [
      {
        "version": "0.2.0",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "operation": {
          "actor": "urn:cognous:identity:refund-agent-1",
          "principal": "urn:cognous:principal:refund-service",
          "institution_id": "urn:cognous:institution:synthetic-customer-service",
          "authority_domain": "customer-refunds",
          "manifest_id": "refund-integration-pilot-v1",
          "manifest_version": "1.1",
          "manifest_digest": "sha256:4d1ad6c96bc242c63998231b4df3ad7c86dc2e5e59cdae63afe7bff86e60f6ac",
          "proposal_commitment": "sha256:133c4baa21d85e41ae7f75af45a96810aa1a175ee3e693913585568630aea96b",
          "action_id": "urn:cognous:action:refund-issue-routine-v1",
          "adapter_id": "urn:cognous:adapter:synthetic-refund-v1",
          "target": "urn:cognous:synthetic-account:customer-001",
          "payload": {
            "customer_id": "customer-001",
            "refund_reason": "duplicate"
          },
          "payload_commitment": "sha256:6b782ebbcc034edeca4069b31aa4d8cbc9d3eeaf3b2034ab989bb430de962c0e",
          "requested_permissions": [
            "refund.issue.routine"
          ],
          "amount": 50.0,
          "unit": "USD",
          "effects": 1,
          "authority_context_id": "urn:cognous:alvorada:public-stack-profile:0.1.0",
          "requirement_id": "urn:cognous:authority-requirement:refund-routine-v1",
          "grant_id": "urn:cognous:grant:routine-1",
          "grant_revision": "1",
          "effective_max_effects": 1
        },
        "attempt_id": null
      }
    ],
    "executor_control_plane_evidence": [
      {
        "attempt": {
          "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
          "started_at": "2026-10-05T19:00:00+00:00",
          "status": "acknowledged",
          "acknowledgement": {
            "moltbot_safe_status": "executed",
            "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
            "newly_executed": true,
            "observation": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied",
              "destination_state": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "grant_id": "urn:cognous:grant:routine-1",
                "target": "urn:cognous:synthetic-account:customer-001",
                "amount": 50.0,
                "unit": "USD",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
              }
            }
          },
          "error": null
        },
        "reconciliation": {
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
          "result": "hold",
          "observation": {
            "effect_id": "rejected-unrelated-effect",
            "observed_at": "2026-10-05T19:00:00+00:00",
            "state": "applied",
            "destination_state": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied",
              "grant_id": "urn:cognous:grant:routine-1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "amount": 50.0,
              "unit": "USD",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
            }
          },
          "observation_accepted": false,
          "retry_eligible": false,
          "reasons": [
            "observation_effect_id_mismatch"
          ],
          "evaluation_time": "2026-10-05T19:00:00+00:00",
          "observation_max_age_seconds": 60,
          "observation_clock_tolerance_seconds": 5
        }
      }
    ],
    "rejected_executor_observation": [
      {
        "effect_id": "rejected-unrelated-effect",
        "observed_at": "2026-10-05T19:00:00+00:00",
        "state": "applied",
        "destination_state": {
          "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
          "state": "applied",
          "grant_id": "urn:cognous:grant:routine-1",
          "target": "urn:cognous:synthetic-account:customer-001",
          "amount": 50.0,
          "unit": "USD",
          "payload": {
            "customer_id": "customer-001",
            "refund_reason": "duplicate"
          },
          "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
        }
      }
    ],
    "execution_result": [
      {
        "status": "unknown",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
        "attempted": true,
        "acknowledged": true,
        "observed_state": "unknown",
        "newly_executed": true,
        "observation": null,
        "error": "observation_effect_id_mismatch",
        "control_plane_evidence": {
          "attempt": {
            "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
            "started_at": "2026-10-05T19:00:00+00:00",
            "status": "acknowledged",
            "acknowledgement": {
              "moltbot_safe_status": "executed",
              "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
              "newly_executed": true,
              "observation": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "destination_state": {
                  "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                  "state": "applied",
                  "grant_id": "urn:cognous:grant:routine-1",
                  "target": "urn:cognous:synthetic-account:customer-001",
                  "amount": 50.0,
                  "unit": "USD",
                  "payload": {
                    "customer_id": "customer-001",
                    "refund_reason": "duplicate"
                  },
                  "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
                }
              }
            },
            "error": null
          },
          "reconciliation": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "reconciled_at": "2026-10-06T23:33:40.425695+00:00",
            "result": "hold",
            "observation": {
              "effect_id": "rejected-unrelated-effect",
              "observed_at": "2026-10-05T19:00:00+00:00",
              "state": "applied",
              "destination_state": {
                "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
                "state": "applied",
                "grant_id": "urn:cognous:grant:routine-1",
                "target": "urn:cognous:synthetic-account:customer-001",
                "amount": 50.0,
                "unit": "USD",
                "payload": {
                  "customer_id": "customer-001",
                  "refund_reason": "duplicate"
                },
                "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
              }
            },
            "observation_accepted": false,
            "retry_eligible": false,
            "reasons": [
              "observation_effect_id_mismatch"
            ],
            "evaluation_time": "2026-10-05T19:00:00+00:00",
            "observation_max_age_seconds": 60,
            "observation_clock_tolerance_seconds": 5
          }
        }
      }
    ],
    "destination_attempt": [
      {
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
        "created_at": 1791329620.424714
      }
    ],
    "destination_attempt_event": [
      {
        "event_id": 1,
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
        "status": "attempted",
        "error": null,
        "created_at": 1791329620.424817
      },
      {
        "event_id": 2,
        "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
        "status": "executed",
        "error": null,
        "created_at": 1791329620.4252424
      }
    ],
    "moltbot_attributed_control_plane_attempt": [
      {
        "attempt_id": "41148d13-c156-4dd2-bf5a-362afa71ee81",
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "decision_id": "a72290fe-2af5-4de9-aeb4-8b31db3eb35e",
        "started_at": "2026-10-05T19:00:00+00:00",
        "status": "acknowledged",
        "acknowledgement": {
          "moltbot_safe_status": "executed",
          "attempt_id": "7d4a0e96-1e16-4d37-895b-63f8e999f499",
          "newly_executed": true,
          "observation": {
            "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
            "state": "applied",
            "destination_state": {
              "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
              "state": "applied",
              "grant_id": "urn:cognous:grant:routine-1",
              "target": "urn:cognous:synthetic-account:customer-001",
              "amount": 50.0,
              "unit": "USD",
              "payload": {
                "customer_id": "customer-001",
                "refund_reason": "duplicate"
              },
              "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175"
            }
          }
        },
        "error": null
      }
    ],
    "destination_effect": [
      {
        "effect_id": "sha256:d19d83b15e0ec164f3da356fe7a1ecef64734724d7fd65265e91e95f2ffe2829",
        "operation_digest": "sha256:ffcad4c587ea3a81df49e9b2c5d3ee817a929d07356d8704db82c1b9c70af175",
        "grant_id": "urn:cognous:grant:routine-1",
        "target": "urn:cognous:synthetic-account:customer-001",
        "amount": 50.0,
        "unit": "USD",
        "payload_json": "{\"customer_id\":\"customer-001\",\"refund_reason\":\"duplicate\"}",
        "state": "applied"
      }
    ]
  },
  "explicit_links": [
    {
      "link_type": "explicit",
      "from_record_id": "control-plane-bounded-run@2ea9528e:moltbot_attributed_control_plane_attempt:14",
      "to_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
      "basis": "Producer-supplied Control Plane attempt evidence exactly matches the retained Control Plane run record.",
      "establishes_identity_equivalence": true
    },
    {
      "link_type": "explicit",
      "from_record_id": "control-plane-bounded-run@2ea9528e:control_plane_attempt_transition:3",
      "to_record_id": "moltbot-safe-executor-producer-2.0.0@177354e9:destination_attempt:11",
      "basis": "Control Plane acknowledgement explicitly supplied executor attempt_id.",
      "establishes_identity_equivalence": false
    }
  ],
  "reconstruction_completeness": "reconstruction_complete"
}</pre>
