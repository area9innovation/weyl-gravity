# Paper-suite update: BT torus theorem and successor boundaries

Date: 2026-08-17

## Established

- Paper 22 now presents the certified Bateman--Turok Euclidean torus
  Green-tail counterfamily as a standalone theorem.  It imports RF-83 through
  RF-96 and preserves the exact `LOCAL-ALGEBRAIC` / `EUCLIDEAN-SPECTRAL`
  boundary.
- Paper 21 now carries a compact programme-level synthesis of RF-83--RF-96;
  the former detailed narrative remains in the TeX source as an uncompiled
  audit trail.  The compiled paper is 79 pages rather than 87.
- Paper 19 now reports the bounded NGC 3198 common-protocol comparison.  The
  Mannheim curve has the smaller unweighted RMS; GR+NFW has the smaller
  weighted chi-squared and AICc and alone passes the declared random-error
  gate.  The text excludes population-level or complete-theory promotion.
- Paper 08 now distinguishes the later full-complex BRST--Hadamard
  pseudo-state pair from a positive quasifree state.
- Paper 12 now imports the immutable Gate-A snapshot, the independent Gate-A
  decision, typed q2/q3 Green compatibility and the full-complex Hadamard
  pseudo-state pair as successor provenance.  Its local anomaly coefficients
  and theorem dispositions are unchanged.
- The Papers 07--08 computational supplement now records the post-freeze
  classical-import chain and reiterates that the centered Weyl-square classes
  are deformation/vertex classes, not one-particle states.

## Does not establish

This paper pass adds no new scientific certificate beyond the already
certified RF-96 result.  In particular it does not decide the full BT Witten
quotient, Gibbs typicality, the interacting H-minus-one moment, continuum or
Osterwalder--Schrader reconstruction, a positive Hadamard state, renormalized
Lorentzian products, a Lorentzian QME, residual quantum transfer, particles,
scattering or unitarity.

## Machine-readable receipts

- `paper/22-bateman-turok-euclidean-torus-collapse-claim-map.json`
- `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`
- `paper/21-reverse-foundations-of-physics-claim-map.json`
- `paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`

## Verification

Tier 0:

- `python3 -m py_compile` on the four changed claim-map scripts: PASS.
- JSON parse of the Paper 12 and Paper 22 claim maps: PASS.
- Two `pdflatex -interaction=nonstopmode -halt-on-error` passes for each
  changed PDF entrypoint: PASS.  Paper 22 is 5 pages; Paper 21 is 79 pages.
- `git diff --check`: PASS.

Tier 1 and affected certificate chain:

- `python3 -m unittest discover -s reverse_physics/tests -p
  'test_bt_euclidean_torus_*.py'`: PASS, 143 tests in 3.240 s.
- Paper 12 generator freshness and independent claim-map verifier: PASS.
- Paper 21 appendix freshness, claim-map freshness and independent verifier:
  PASS.
- Paper 22 claim-map freshness and independent verifier: PASS.
- Science Forge Paper 12 coverage audit in advisory mode: 11/11 results
  classified, nine paper claims OK, zero blocking findings.

Tier 3 was not run.  No mathematical input, shared operator, schema,
certificate, lifecycle promotion or release/freeze changed; the affected
143-test torus chain was nevertheless replayed.  The previously recorded
repository-wide reverse-physics rail remains non-green and is not represented
as a pass here.
