# Science Forge adoption pass — 2026-07-19

This report turns the Science Forge handoff into a bounded adoption queue.  It
distinguishes hard reproducibility defects from review signals and avoids
rewriting files currently owned by active science workstreams.

## Completed in this pass

1. The two wrapper/proof `result_id` collisions were separated without
   changing either public claim identity:
   - `LOCAL_BV_MINIMAL_BOOTSTRAP` remains the repository result envelope;
     its detailed proof is now `LOCAL_BV_MINIMAL_BOOTSTRAP_PROOF`.
   - `REDUCED_MODE_SPECTRAL_BOOTSTRAP` remains the repository result envelope;
     its detailed E/A/L ledger is now `REDUCED_MODE_EAL_BRANCH_LEDGER`.
2. The order-six Pais--Uhlenbeck result was imported through a bounded external
   certificate pinning Tango commit
   `ccee11d08de28d3e2681db209264887950666e87` and the three upstream artifact
   hashes.
3. The dirty-toolchain marker in the upstream claims certificate was not
   ignored.  A compiler was built with Go 1.25.8 from a `git archive` of the
   pinned source tree.  It reproduced all 31 exact checks and all three SymPy
   golden comparisons.  The compiler and output hashes are recorded in the
   clean-replay receipt.
4. Paper 05 now reports the exact `5:3` and `7:1` sixth-order obstructions while
   retaining the all-coprime hierarchy as a conjecture.
5. A manual-only GitHub Actions shadow rail reproduces this one clean pinned
   Science Forge import.  It is not a required per-commit check.
6. The handoff's `d_quotient_classical` metric was corrected: `0.13` is recall,
   while the reported precision is `0.33`.

## Hard-defect queue

| Finding | Disposition |
| --- | --- |
| Duplicate result identities | Repaired in this pass |
| Newly landed receipt/subject and fixture identity collisions | Separate follow-up: the broad working-tree scan now sees additional collisions, chiefly recent Einstein tier receipts reusing their subject IDs; repair the receipt generators with the owning team rather than rewriting active outputs |
| Stale committed certificate DAG | Rebuild from the post-repair Git commit; do not include the live dirty working tree |
| Two observer producers fail their own `--check` | Team-owned repair; observer files are actively modified, so no concurrent overwrite here |
| Circumference transport source-manifest drift | Einstein-team review required before refreshing the hash |
| Nine quantum drift findings | Quantum-team review; several target papers and frontier files are actively modified |
| Three classical drift findings | Classical-team review; distinguish stale provenance from changed mathematics before regeneration |
| Stale nonlinear atlas fragment | Rebuild after the current nonlinear product/Taylor work lands |

## Review queues, not automatic defects

### Paper freshness

The four TeX-to-certificate timestamp findings enter review.  A newer
certificate is not by itself proof that the cited sentence is false.  Each
review must record one of:

- `NO_SEMANTIC_CHANGE`;
- `WORDING_REFRESHED`;
- `CLAIM_NARROWED`;
- `THEOREM_REBUILT`.

The queue currently covers the Paper 07--08 supplement/archive citations and
the Paper 09 theorem-freeze citation identified in the handoff.

### Undeclared code dependencies

The 175 code-read but undeclared certificate relationships are proposed edges,
not automatic bulk edits.  Review them in this order:

1. dependencies read by a producer and contributing values or hashes;
2. dependencies read by an independent verifier;
3. source fixtures used only for diagnostics;
4. registries or aggregators whose dependency list is generated dynamically.

Accepted edges must be added to `dependency_refs` with the current source hash
where the family schema supports it.  Rejected edges receive a reason such as
`DIAGNOSTIC_ONLY`, `AGGREGATOR_TRANSITIVE`, or `STATIC_ANALYSIS_FALSE_POSITIVE`.

### Orphan certificates

The 128 apparent orphans must be classified as one of:

- `TERMINAL_RESULT`;
- `SOURCE_FIXTURE`;
- `LEGACY_CERT_ONLY`;
- `SUPERSEDED`;
- `MISSING_LINK`;
- `RETIRE_CANDIDATE`.

No orphan is deleted merely because it has no inbound edge.

### Programmatic dependency corroboration

The low static-analysis recall in programmatic families is a transparency gap,
not proof that their declared graph is wrong.  New generators should emit the
resolved dependency manifest they actually used.  Science Forge can then
compare declared, runtime-resolved and code-inferred edges without trying to
reverse-engineer loops and registries.

## Adoption policy

Science Forge remains an advisory shadow rail until individual families pass a
declared import gate.  Fast identity, schema, hash and DAG checks may become
required.  Expensive verifier fleets remain affected-chain, scheduled or
manual checks so that repository-wide replay does not recreate the previous
OOM and synchronization problems.

The scientific rule is unchanged: an imported computation inherits its exact
theory, background, carrier, lifecycle and `does_not_establish` boundary.  A
new tool cannot promote a result merely by reproducing it faster.
