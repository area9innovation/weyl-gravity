# Observer Berger84 apparatus handoff provenance relock

Decision: `SHORTFALL`. The scoped `BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF`
provenance repair is complete, but `OBSERVER_STREAM_TIER3_GREEN` is not yet
established because the uninterrupted suite found the next unrelated stale
certificate.

## Scoped repair

The original failure was reproduced. Exactly two imported hashes were stale:

- `global_rods`: `03c70e99...` to `38f3c390...`;
- `rod_q1_solvability`: `36153ad6...` to `dbabf49b...`.

The declared producer regenerated the certificate. Its diff is exactly those
two hash substitutions. All other top-level fields agree with the current
producer, every scientific flag is unchanged, and no apparatus result was
promoted. Producer check, independent verifier, all seven fail-closed input
mutations and all five scoped tests pass.

## Tier 3 disposition

The complete observer suite was restarted from the beginning with `-x`, which
does not reduce coverage on a green run and implements the work package's
instruction to stop at the first unrelated failure. It passed 151 tests before
failing at:

```text
test_berger_84_row_mixed_r_kappa_unary_gate.py::
test_fail_closed_boundary_and_independent_verifier
```

`BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE` imports stale hashes for both the
newly relocked handoff and `BERGER_84_ROW_ROD_GRAVITY_UNARY`. Its generated
`q10_memory_transport` also changes canonical hash and all three frequency
sectors. Its scientific flags and mutations remain unchanged, but that
certificate cannot be manually repinned because the content change requires
its own producer replay and independent verification.

Typed request
`sf:program/request/observer-berger84-apparatus-handoff-provenance-relock-to-observer-4be912d627c270d1`
asks the observer stream to perform that relock and restart the uninterrupted
suite. No broad regeneration was attempted.

This report does not establish a new apparatus, receiver, detector, memory,
redshift, counterflow result or Paper 9 freeze. It establishes only the exact
two-hash handoff repair and the first subsequent Tier 3 obstruction.

EVIDENCE: closed_universe_observers/certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json;
closed_universe_observers/receipts/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF_PROVENANCE_RELOCK_V1_TIER_RECEIPT.json

CLOSE-OUT: SHORTFALL — the handoff is relocked; the mixed-r-kappa certificate
requires its own provenance relock before `OBSERVER_STREAM_TIER3_GREEN` can be
retested.
