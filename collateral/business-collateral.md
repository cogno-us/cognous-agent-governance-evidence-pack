# Cognous Governance Evidence Pack — Business Collateral

## 1. Executive Summary

A reference format, validator, traceable importer and Markdown renderer for business-facing review of agent governance records. It preserves the relationship between a declared action surface and reconstructed runtime evidence instead of treating a summary as independent assurance.

## 2. The Business Problem

Enterprise reviewers need to understand authority, review posture, reliance, attempted actions and unresolved outcomes without reading every raw event. A useful summary must remain traceable and must not convert declarations or source assertions into verified operational facts.

## 3. The Component in One View

| Capability | Practical role |
|---|---|
| Evidence structure | Represent the agent, actions, governance context and source records in a review package. |
| Traceable imports | Transform Manifest and Reconstruction Bundle inputs with explicit source references and transformation versions. |
| Assurance separation | Distinguish declared controls, source-asserted runtime facts, executed tests and independent verification. |
| Continuity checks | Validate source identities, commitments and producer compatibility across the selected generation. |
| Business rendering | Validate, summarize and render Markdown for a reviewer while preserving unresolved and missing information. |

## 4. Who Should Evaluate It

Engineers can inspect the reference contracts and examples; enterprise architecture, security and governance reviewers can examine the boundary and evidence. Evaluate this component for its named responsibility rather than as a complete governance platform.

## 5. A Bounded Workflow

The bounded refund produces retained reconstruction evidence. The importer combines it with the Manifest and records the derivation. A reviewer can follow each summarized decision or outcome back to its source and see the difference between historical authorization, current recovery denial and observed destination state.

This is a reference use case. Adopting the format or running the example does not establish a production deployment, institutional acceptance or measured business benefit.

## 6. Relationship to the Stack

This component contributes **turn traceable runtime records into reviewable governance evidence**. The [Cognous Open Control Stack](https://github.com/cogno-us/cognous-open-control-stack) connects declared proposals, independent authority, constrained execution and retained review evidence. Components remain separately owned and versioned; the [selected lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) determines which revisions participate in the supported integration.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## 7. What the Evidence Supports

The hub selects `de6b9e071df49fc3e0c1254d39b5c94cced554f0`. Current persistence-generation transformation is **0.3.1**; previous selected producer-2.0.0 transformation **0.3.0** and historical **0.2.6** remain separately tested. Imported pack schema remains **0.2.0**. See the [persistence checkpoint](../docs/workstreams/evidence-pack-control-plane-store-checkpoint.md); older migration notes describe their original generation.

The [accepted hub evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) supports bounded synthetic integration at its exact pins. Aggregate test totals do not establish deployment benefit, compliance or independent real-world verification. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) distinguishes the standard reference, separate protected-worker campaign and unqualified production work.

## 8. What It Does Not Establish

Import success does not establish that a test ran, that an institution authorized current reliance or that a control is effective in production. This is not certification, legal advice, independent audit or a runtime enforcement layer. Historical transformation outputs remain attributed to their original sources.

## 9. Evaluation Questions

- Which exact input, output and source revision will the receiving system consume?
- Who supplies trusted authority or evidence, and which assumptions remain outside this component?
- Can a reviewer trace the result to retained sources, including rejected or missing information?
- Which documented checks were actually executed in the intended environment?
- What deployment-specific work is required before relying on the result?

## 10. Why Open Reference Material Matters

Public formats, source, examples and evidence allow reviewers to inspect the claimed boundary and reproduce its checks. They also expose what has not been tested. Openness supports review; it does not substitute for independent assurance or operating responsibility.

## 11. Practical Next Step

Follow the [README](../README.md) and select one bounded use case. Inspect its inputs and expected outputs, reproduce the documented checks where prerequisites are available, and record failures and unresolved assumptions alongside passes. Use the [one-page overview](one-page-overview.md) for initial stakeholder orientation.

## 12. Status and Attribution

This collateral summarizes merged public material at repository `de6b9e071df49fc3e0c1254d39b5c94cced554f0` and the accepted hub baseline `5737267d94d2b445735c95e8480a31de73a2abe8`. It does not anticipate pending branches. The protected-worker result applies only to its recorded Linux/bubblewrap fixture; live OpenShell and logical-intent prevention are not hub-supported at this snapshot.

[Cognous](https://cogno.us) · [Source repository](https://github.com/cogno-us/cognous-governance-evidence-pack) · [Stack responsibilities](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/architecture.md). Existing licenses and third-party notices remain controlling.
