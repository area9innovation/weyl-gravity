# Paper 15 referee self-containment revision

## Disposition

`DONE — TECHNICALLY_SELF_CONTAINED_REFEREE_REVISION`

Paper 15 now addresses the five substantive issues in the second external
editorial review. The author line was deliberately left unchanged under the
coordinator's explicit instruction.

## What changed

- The paper no longer assigns an inertia to the antisymmetric Lee--Wald form.
  It defines the real form, its rank and radical, and separately defines the
  positive-frequency Hermitian form whose inertia is reported, including its
  frequency, reality, normalization, and exceptional-mode conventions.
- The changed counterflow theory is defined by its complete displayed action,
  fields, gauge transformations, Berger background, stationary parameter
  family, selected point, invariant free BV complex, and differential orders.
  The 70-row representation is identified only as a harmonic-component
  implementation. An exact discriminant/no-crossing lemma proves persistence
  of the Hamiltonian--Hopf quartet on the declared connected family.
- The Schwarzschild result now fixes units, defines the truncated radial
  Lee--Wald slice pairing and its improper limit, prints representative metric
  asymptotics and current-density powers, and expressly distinguishes this
  condition from a Cauchy, scattering, wave-packet, or Hilbert norm.
- The strict one-loop anomaly is reported with
  `c_W = 199/30`, `a_W = 87/20`, and the chosen `b_W = 0` convention. A
  four-row determinant/heat-kernel ledger and the residue-to-BV-cohomology map
  make the promotion from effective-action Weyl anomaly to gauge obstruction
  explicit.
- Mathematical scope is separated from evidence state. The missing
  foundational and adjacent literature was added, implementation terminology
  was reduced, the machine-facing frozen claim index was removed from the
  narrative, and permanent public repository links were supplied without
  inventing an archival DOI.

## Claim boundary

This is a self-containment and exposition revision of frozen Phase-1 results.
It establishes no new source theorem. In particular it does not establish a
signature for an antisymmetric symplectic form, an all-frequency or scattering
black-hole theorem, a full-PDE counterflow stability theorem, anomaly freedom
beyond the declared local Euclidean calculation, or viability outside the
printed counterflow family.

## Verification

- `python3 paper/generate_15_phase1_synthesis_claim_map.py`
- `python3 paper/verify_15_phase1_synthesis_claim_map.py`
- `python3 -m pytest -q paper/test_15_phase1_synthesis_claim_map.py planning/paper-coverage/test_phase1_paper_coverage_overlay.py`
- `python3 planning/paper-coverage/verify_phase1_paper_coverage_overlay.py planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json`
- two warning-free `pdflatex -interaction=nonstopmode -halt-on-error` passes
- scoped whitespace/diff checks against the committed Paper 15 sources

The generated paper is an 18-page PDF. The machine-readable receipt records
the exact artifact hashes and tier disposition.

CLOSE-OUT: DONE — Paper 15 is technically self-contained enough for external
expert refereeing of the underlying derivations, with all frozen scopes and
non-claims preserved.

EVIDENCE: reports/PAPER15_REFEREE_SELF_CONTAINMENT_REVISION_V2_TIER_RECEIPT.json
