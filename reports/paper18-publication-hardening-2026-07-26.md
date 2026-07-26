# Paper 18 publication-hardening pass — 26 July 2026

## Outcome

Paper 18 was narrowed and made more reconstructible without broadening its
scientific claim. The title now names the Mannheim–Kazanas family, the
residual-basic normalization theorem states its local regularity hypotheses,
and the simultaneous first law is consistently described as a signed
variational identity rather than a common-equilibrium assertion.

## Mathematical changes

- Added the missing hypotheses \(u\neq0\), \(\mathcal F\neq0\), residual
  orbit rank two, and \(\mathrm dJ\neq0\) to the local uniqueness theorem.
- Distinguished the residual-basic Hamiltonian from a preferred physical
  mass and the signed horizon temperature from a positive Hawking
  temperature.
- Fixed the covariant-phase-space representative explicitly, including the
  \(Q_{\delta\chi}\) subtraction and the Jacobson–Kang–Myers ambiguity
  boundary.
- Printed the two gauge-fixed Bach rows used by the Laurent classification
  and the exact coefficient ideal whose reduced Gröbner basis is
  \(\{c_2,c_3,w^2+3u\gamma-1\}\).
- Replaced the prose-only first-law reduction by the three explicit exact
  quotients:
  \[
  \mathcal E_\beta
    =B(r_h)\frac{2\beta\gamma(3\beta\gamma-2)}{r_h},\qquad
  \mathcal E_\gamma
    =B(r_h)\frac{2\beta^2(3\beta\gamma-2)}{r_h},\qquad
  \mathcal E_k=0.
  \]

## Evidence changes

- Added `paper/verify_18_static_weyl_thermodynamics_stdlib.py`, a
  non-SymPy exact verifier using only `fractions.Fraction` and a separately
  implemented sparse Laurent-polynomial ring.
- Added the deterministic receipt
  `reports/PAPER18_STDLIB_ALGEBRA_RECEIPT.json`.
- Added the append-only successor certificate
  `black_hole_programme/certificates/PAPER18_STATIC_FIRST_LAW_PROMOTION.json`.
  It leaves the historical BH1/BH1A/BH1B `PREFLIGHT` records unchanged and
  promotes only the exact static MK theorem and linear spherical charge
  audit to `CLASSIFIED`.
- Updated the Paper 18 claim map so the successor certificate and independent
  arithmetic rail are visible in the theorem dependency chain.

## Claim boundary

This pass does **not** establish:

- completeness beyond the declared Laurent ansatz;
- a preferred physical mass, clock, or conformal frame;
- a nonlinear physical-process first law;
- a radiative flux law;
- stability, Hawking radiation, or a quantum result;
- expert peer review or journal acceptance.

The exact commands and tier disposition are recorded in
`reports/PAPER18_PUBLICATION_HARDENING_TIER_RECEIPT.json`.
