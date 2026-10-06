# Importing executor producer profile 2.0.0

Use the accepted Replay validator and install the Evidence Pack importer from the Batch 4C-D change. The exact mappings, lifecycle examples, commands and boundaries are in the [single qualification checkpoint](workstreams/evidence-pack-producer-v2-checkpoint.md).

New imports use transformation **0.3.0**, while pack schema and Reconstruction Bundle remain **0.2.0**. Consumers must read `reconstruction_completeness` separately from `lifecycle_summary.destination_observed`, `acknowledgement` and `retry_permission`. Do not derive delivery from complete reconstruction, accepted observation from a destination row, or authorization from a package digest.

`retained_sources` binds the original Replay ID and canonical digest. `lifecycle_records` preserves complete attributed records, including rejected observations with intentionally wrong effect IDs. `effect_observation_history` uses accepted Replay sequence semantics; `explicit_links` retains ownership/correlation without merging attempt namespaces. Null observation is unavailable evidence, not absence or retry permission. Public validation reconstructs the material trace; rendering rejects inconsistent generated traces.

The traceable Markdown contains readable lifecycle summaries followed by the complete escaped trace JSON. This preserves equivalent material information when reviewing only Markdown. Local commitments and source assertions are not independently verified evidence. Failed/inconclusive source test reports retain their actual result; import-time semantic validation does not mean those tests were executed by the importer.

Historical producer 1.0.0 and unversioned artifacts remain explicitly revision-mapped with transformation 0.2.6. Do not relabel historical examples. The GAX historical qualification environment is separate; migrate GAX in its own reviewed batch before updating hub dependencies.
