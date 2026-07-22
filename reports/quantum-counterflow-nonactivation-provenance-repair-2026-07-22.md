# Counterflow nonactivation provenance repair

## Result

The scientific dispositions are unchanged:

- `TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1` remains
  `NOT_ACTIVATED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK`;
- `TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1` remains
  `NOT_ACTIVATED_MISSING_SUCCESSFUL_FULL_BV_HADAMARD_INPUT`.

This repair addresses provenance only. The Hadamard tier receipt now pins the
scientific result commit
`0966eebe5147e1458e419073940ae1dbedc17159` and records the SHA-256 digest of
each of its nine final Git blobs. An independent verifier reads those blobs
directly with `git show`, checks all nine receipt entries, and rejects a
mutated certificate hash.

The downstream positivity generator was rerun after the receipt repair. Its
certificate and atlas now pin the repaired Hadamard receipt, its provenance
names the independent verifier, and the positivity verifier replays every
source pin and every output hash. A separate output-hash mutation is rejected.

## Defect and cause

The original Hadamard receipt captured seven hashes before the final output
serialization; only the team brief and closeout hashes described the committed
blobs. The downstream positivity result consequently pinned an obsolete
Hadamard receipt hash. The scientific JSON payload and its fail-closed claim
boundary were not contradicted, but the provenance chain was not replayable.

## Verification

- Python compilation: PASS (`0.03s`).
- Hadamard committed-blob receipt replay: PASS, nine hashes checked and one
  mutation rejected (`0.07s`).
- Hadamard producer and independent scientific verifier: PASS (`0.03s` and
  `0.14s`; ten scientific mutations rejected).
- Positivity producer and independent verifier: PASS (`0.02s` and `0.07s`;
  five scientific mutations and one receipt mutation rejected).
- Scoped tests: PASS, `10 passed in 0.56s` (`1.00s` wall clock).
- Both residual-atlas fragments: PASS (`0.13s` each).
- JSON parsing and scoped `git diff --check`: PASS.

The first combined atlas invocation used two positional paths although the
validator accepts one and therefore exited with usage status 2. Both fragments
were then rerun separately and passed; the rejected invocation is not counted
as a pass.

Tier 2 was not run because the underlying mathematical inputs and scientific
payload are unchanged and content-addressed. Tier 3 was not run because this
is not a theorem freeze, release, shared-core change, or lifecycle promotion.

## Claim boundary

Dependency tags remain `LORENTZIAN-CAUSAL`, `REDUCED-MODE`, and where already
declared `LOCAL-ALGEBRAIC`. This repair constructs no covariance, wavefront-set
proof, Ward identity, QME restoration, positive state, particle space,
scattering theory, or unitarity theorem.

## Coordination shortfall

The three predecessor items have landed `WORK_COMMITTED` and terminal `DONE`
events but no `WORK_REPORTED` checkpoints. A post-hoc `work report` was
attempted for the local-anomaly item and correctly refused because its lease
was already released. Science Forge also refuses to reacquire a terminal
`DONE` item, so the missing predecessor checkpoints cannot be backfilled
without a coordinator-authored lifecycle-repair facility. This does not affect
the committed certificates or the repaired hash chain; the present successor
report is the append-only provenance handoff.

EVIDENCE: `quantum-weyl/lorentzian/receipts/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1_TIER_RECEIPT.json`, `quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_receipt.py`, `quantum-weyl/transfer/certificates/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1.json`, and `quantum-weyl/transfer/receipts/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1_TIER_RECEIPT.json`.

CLOSE-OUT: SHORTFALL — the scientific provenance repair is complete, but terminal predecessor items cannot receive retroactive checkpoints through the current lifecycle API.
