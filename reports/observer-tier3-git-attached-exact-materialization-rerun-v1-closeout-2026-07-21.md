# Observer Tier-3 Git-attached exact-materialization rerun v1

Decision: `OBSTRUCTED`. The Git-attached materialization gate itself passes.
At repair commit `d3b46e000875e06c97f4afd701c662e0ccb1bc1b`, the detached worktree was
clean, resolved committed snapshots through Git, retained committed LFS pointer
blobs, and matched all 11,191 regular-file/symlink blobs in the declared
`physics/symplectic-reconstruction` scope. The independent census found 11,189
regular files, two symlinks, and zero missing, content-mismatched or
mode-mismatched objects. Resource preflight also passed.

Exactly one fresh fail-fast full Observer traversal was run. It passed 826
tests, then stopped at
`test_comparison_ledger_is_fail_closed` after 1175.10 pytest seconds
(1183.15 wall seconds, 904656 KiB maximum RSS). There was no retry, no patch
inside the run, no skipped test before the failure, and no prior partial pass
was credited.

The first failure is a stale bridge-artifact entry in
`closed_universe_observers/ledgers/comparison_ledger.json`. Its entry for
`BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW` pins artifact SHA-256
`eaed93a3...`, while the exact artifact at the selected commit has SHA-256
`1adce4fe...`. The claim boundary also changed materially: the ledger says the
two-form Diff--BV q2 orbit remains to be scalarized and leaves every q3 block
unavailable; the current artifact says that Diff--BV q2 orbit is separately
certified and narrows the remaining complete-arity-two obstruction to the
relational temporal emitter-Diff orbit. This is not a scientific
contradiction, test-harness defect, or recurrence of the archive-without-Git
failure.

The smallest successor must semantically relock that ledger entry to the exact
current artifact hash, claim boundary and scope. A blind hash-only repin is not
sufficient. The relock needs an independent verifier plus mutations that
detect artifact, claim-boundary and scope drift; only after that scoped gate
passes should a new owner run one fresh fail-fast full Observer Tier-3 suite.

The disposition verifier and its 15 fail-closed mutations pass (16 tests
total). No Paper 9 PDF was rebuilt because the evidence gate is not green.
Paper 9 therefore remains `DRAFT_ALLOWED`; no observer, redshift, nonlinear,
particle or quantum claim is promoted.

EVIDENCE:
`closed_universe_observers/receipts/OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1_MANIFEST.json`;
`closed_universe_observers/receipts/OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1_OBSTRUCTION.json`;
`closed_universe_observers/receipts/OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1_TIER_RECEIPT.json`.

CLOSE-OUT: OBSTRUCTED — exact Git-attached materialization repaired; stale
comparison-ledger semantic pin is the next first frontier.
