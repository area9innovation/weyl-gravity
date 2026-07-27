# Standalone publication-verifier drift repair

Date: 27 July 2026

## Outcome

Three inherited fail-closed publication rails now pass in the standalone
repository:

- `paper/verify_09_relational_clocks_claim_map.py`;
- `paper/verify_13_14_draft_source_maps.py`;
- `planning/paper-coverage/verify_phase1_closure.py`.

No historical commit identifier, theorem statement, certificate payload, or
lifecycle state was rewritten or promoted.

## Repairs

### Paper 09

The current claim map previously imported six append-only planning events
whose serializations had changed and six terminal event files that were not
present in the extracted repository.  Its generator now imports only
materialized, hash-checkable evidence.  The absent event records are replaced
by the existing terminal receipts and closeouts, plus
`OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1`, which independently
replays that three scientific dispositions survive the current receiver
input.

The map contains 22 claims and 43 exact imports.  It remains
`DRAFT_ALLOWED`.  The recursive legacy-ledger hash edge and non-green
Observer Tier-3 boundary remain explicit.

### Papers 13 and 14

Paper 13 retains the historical pre-extraction source-baseline identifier
`aa7f7ff9...`; it is not rewritten.  The standalone repository contains all
60 source blobs named by the Paper 13 map and all 26 named by Paper 14, but
the extraction did not preserve one commit in which every Paper 13 blob
co-occurred.

The verifier therefore authenticates each declared path/Git-blob pair
directly against filtered Git history.  A missing blob, wrong object type,
wrong path, duplicate source, malformed lifecycle state, or mutated blob id
is rejected.

### Phase-1 closure

The closure package is a dated historical snapshot.  Its verifier previously
compared frozen dependency and manuscript hashes with mutable current paths,
so later editorial and claim-map maintenance appeared as scientific drift.
Dependencies that include source commits now replay through the standalone
history crosswalk.  Path-plus-SHA-256 manuscript pins without source commits
are resolved by exact content in filtered path history.  Unknown paths and
hashes fail closed.

## Claim boundary

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`,
`LORENTZIAN-CAUSAL`.

This repair restores standalone verification of already recorded evidence.
It does not establish a new physical result, make Paper 09 theorem-frozen,
green the Observer Tier-3 suite, alter the Paper 13 or Paper 14 lifecycle
states, or update the scientific contents of the Phase-1 closure.

## Verification

The exact commands and outcomes are recorded in
`reports/STANDALONE_PUBLICATION_VERIFIER_DRIFT_REPAIR_2026_07_27_TIER_RECEIPT.json`.
Tier 3 was not run because no mathematical operator, certificate payload,
schema, theorem, or lifecycle state changed.
