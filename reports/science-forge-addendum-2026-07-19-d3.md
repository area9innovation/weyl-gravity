# Science Forge addendum — a new structural observation in the residual complex (2026-07-19)

Status: OBSERVED (a pattern-miner finding with exact evidence — NOT a claim;
see the epistemics note at the end).

## The observation

Automated block-structure mining over the captured residual so(4,2) CE
complexes found that the mode-block decomposition documented for the vacuum
d4 is NOT special to degree 4:

- **vacuum d4 (833x407, rank 291)** — known: splits under row/col permutation
  into six identical 105x50 rank-36 blocks + 97x49 (r33) + 106x58 (r42),
  carried by a proof-carrying decomposition certificate
  (`forge/tools/physics-linalg/certificates/vacuum_residual_H4_d4.decomp-cert.json`).
- **vacuum d3 (48x18, rank 14) — NEW, previously undocumented**: the SAME
  six-identical-block pattern one degree down (blocks equal under
  permutation-invariant signatures: shape, nnz, rank, row/col degree
  sequences).
- **two_particle d4 (385x55, rank 53)**: 8 nontrivial blocks — seven
  near-identical ~40x6 rank-6 + one exceptional 36x12 rank-11.

Exact evidence (indices, ranks, signatures, input sha256s):
`forge/tools/physics-linalg/patterns/observations.json` (repeated_blocks
family), reproducible via `forge/tools/physics-linalg/patterns/run_patterns.sh`
(both compiler backends, sanitizer-clean; the d4 positive control is
rediscovered independently of the existing certificate).

## The conjecture it suggests (recorded, not asserted)

"The energy-grading/mode symmetry pervades EVERY differential of the residual
complexes, not only d4" — filed in our conjecture registry at lifecycle
OBSERVED with full provenance, alternatives considered, and falsifiers:
`forge/tools/science-forge/program/conjectures/mode-block-pervasiveness.json`.

What would test it on your side: whether the energy-completed blocks
(the 727/3084/8532-dim rows your completion proof works with) show the same
finest-block structure — your builders hold those matrices; our capture of
them is currently paused. A mode-mixing entry joining the six blocks would
falsify; the pattern recurring would substantially support.

## Epistemics note

Per our discipline this is an OBSERVATION: a certified fact only for the
vacuum d4 instance (the decomposition certificate above); for d3 and the
two_particle row it is exact-but-uncertified miner output; as a universal
statement about the complexes it is a conjecture with named falsifiers.
"The miner saw a pattern" is not evidence of the general claim — the exact
instances and their reproducibility are what this note transmits.
