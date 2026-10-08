# W0 contract addendum: C8 Evidence Pack compatibility

Status: W0 candidate mapping contract.

Inspected main: `b4baccd823d2a73be276c1de745b19cf7c56a0d6`.
Existing imported schema 0.2.0 and transformation `agep-manifest-reconstruction-import/0.3.2` remain valid only for their exact accepted producer set.

## C8 mapping requirements
A future tenant-aware/profile-aware transformation must preserve:
- exact producer and Replay revisions;
- tenant lineage and explicit missing/unsupported tenant state;
- refusal/failure classification and stage;
- optional profile identity, configuration/policy digest and capability admission;
- flow decision and result-admission identities/outcomes;
- stop request/ack/dispatch-closure/quiescence/reconciliation distinctions;
- observation state, freshness, finality and uncertainty.

A missing lineage field cannot be converted into successful exact-scope evidence. Old artifacts retain their original assurance level. Redacted, unknown, omitted and unsupported are distinct states.

Qualification evidence is bound to exact source revisions, hub lock/configuration, environment and actual case population. Structural validity or successful rendering does not establish authority, delivery, independent verification or production efficacy.

W3 owns the actual consumer implementation/version choice after producer contracts are accepted. W7 owns final composed qualification.
