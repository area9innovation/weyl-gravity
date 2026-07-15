# Quantum-Weyl Test Policy

Use claim-directed test tiers so the shared workspace stays responsive while
scientific promotions remain fail-closed.

| Tier | Trigger | Typical quantum bootstrap checks |
|---|---|---|
| 0 | Every edit | Python compile/import, JSON parse, `git diff --check`, source hashes |
| 1 | Changed code/certificate | Changed package's unit tests and deterministic emitter/checker |
| 2 | Upstream mathematical or schema dependency changed | Only the affected classical-to-quantum certificate chain |
| 3 | Freeze, theorem/lifecycle promotion, shared core change, release, scheduled CI | Full repository verification |

The default quantum bootstrap commit runs Tiers 0 and 1.  It does not rerun
the full classical suite when the imported classical files are unchanged;
their byte hashes are the dependency receipts.

## Escalation rule

Escalate to the next tier when any of these is true:

- a changed file is named in an upstream receipt of the claimed result;
- a schema or API used by downstream certificates changes;
- a result moves from `NOT_COMPUTED` or infrastructure status into a
  scientific lifecycle state;
- the scoped test cannot exercise a new mathematical branch;
- a paper statement is strengthened.

If a Tier-1 command takes more than roughly 60 seconds in ordinary use, keep
the exact exhaustive verifier but add a fast deterministic rail covering
parsing, dimensions, hashes, and a representative invariant.  The expensive
rail then runs at Tier 2 or Tier 3.  Do not replace exact arithmetic with
floating point merely to make a certificate faster.

## Receipt format

Each branch report records:

```text
command
elapsed_seconds
status
test_tier
higher_tiers_not_run
escalation_criterion
```

`higher_tiers_not_run` explains why a broader run was unnecessary.  It must
not imply that an unrun suite passed.
