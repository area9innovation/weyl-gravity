# Paper 15 Phase-1 synthesis and Paper 98 portal refactor

## Disposition

`DONE — PUBLICATION_SYNTHESIS_OF_FROZEN_CLAIMS`

Paper 15, *What Survives the Ghost Test? A Four-Level Phase-1
Classification in Pure-Weyl Gravity*, is a stable 15-page synthesis of
`PURE_WEYL_PROGRAMME_PHASE1_CLASSIFICATION_ENDING_V1`. Paper 98 remains the
live physicist portal. Its first screen now gives the concise Phase-1 verdict
and points to Paper 15; the former expanded opening is preserved inside a
collapsed technical synopsis.

## What was established

- The synthesis states the strict Weyl, Weyl--Maxwell, Einstein--Maxwell,
  compensator, and counterflow theories separately and introduces the typed
  scope tuple before comparing results.
- A ghost taxonomy distinguishes pole residue, Ostrogradsky form, classical
  pairing, nonlinear obstruction, quantum norm, unitarity, and alternative
  prescriptions.
- Five result cards bind the compact linear structure, finite-harmonic
  nonlinear cone, Schwarzschild finite-norm fixture, strict/compensated local
  anomaly, and counterflow causal/physical verdict to their exact scopes and
  non-claims.
- The counterflow endpoint is stated as a persistent physical
  `j=1/2` Hamiltonian--Hopf obstruction in the connected trace-healthy
  same-field stationary family, not as an all-isotype or all-architecture
  theorem.
- The frozen Phase-1 paper-coverage overlay was not rewritten. A new additive
  Paper 15 overlay supplies reverse result-to-paper edges for all eight
  human-classified Phase-1 results.

## What was not established

No new scientific inference was made. The synthesis does not establish a
universal ghost/no-go theorem, a complete bounded nonlinear cone, a general
black-hole boundary theorem, an invariant branch-resolved interaction, a
positive full-BV state, Lorentzian QME, particles, scattering, or unitarity.

## Verification

- `python3 paper/generate_15_phase1_synthesis_claim_map.py`
- `python3 paper/verify_15_phase1_synthesis_claim_map.py`
- `python3 -m pytest -q paper/test_15_phase1_synthesis_claim_map.py planning/paper-coverage/test_phase1_paper_coverage_overlay.py`
  — 5 passed.
- `python3 planning/paper-coverage/verify_phase1_paper_coverage_overlay.py planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json`
  — 5 contradiction mutations rejected.
- Four `pdflatex -halt-on-error` passes produced the 15-page Paper 15 PDF.
- Pandoc/XeLaTeX produced the 12-page Paper 98 PDF after removing only the
  HTML disclosure tags from the PDF input; the expanded synopsis remains in
  the rendered PDF.
- `git diff --check` passed on the scoped text and code paths.

The independently frozen Phase-1 coverage overlay remained byte-identical to
its committed version after the additive overlay was generated.

CLOSE-OUT: DONE — Paper 15 and its PDF, claim map, independent verifier,
additive reverse-coverage overlay, publication receipt, and the concise Paper
98 portal opening are committed and published.
EVIDENCE: reports/PAPER15_PHASE1_SYNTHESIS_V1_TIER_RECEIPT.json
