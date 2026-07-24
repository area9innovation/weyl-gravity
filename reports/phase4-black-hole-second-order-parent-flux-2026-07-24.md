# Phase 4 black-hole second-order parent flux

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Result

The quadratic pure-Weyl system on a four-dimensional Ricci-flat background
has an exact auxiliary-tensor parent formulation modulo the Euler
boundary/corner term:

```text
S_par = 4 alpha Integral[
  f^ab deltaG_ab[h] - 1/2 (f_ab f^ab - f^2)
].
```

The auxiliary equation gives `f_ab=q_ab[h]`, the metric equation gives
`deltaG[f]=0`, and eliminating `f` returns the Ricci-factorized quadratic
Weyl action.

With the declared antisymmetric Einstein Green current, the parent current
is

```text
j_par = 4 alpha [j_E(h1,f2) + j_E(f1,h2)].
```

The literal `C^2` current differs by the independently certified Euler
transgression.  This makes the source/target spin-two pairing manifestly
off diagonal and gives a canonical null lift of every nondegenerate
spin-two endpoint block.

The triangular Evans determinant also gives the exact contour count

```text
N_B = 2 N_2 + N_1.
```

The extension changes local Smith structure, not the total algebraic QNM
count.

## Boundary

This result does not identify generic radial nonsplitting with a
time-translation Jordan block.  One physical axial QNM is already certified
as a connection-level EP2, but a Green-resolvent double pole remains
conditional on an analytic Fredholm realization.  No all-frequency
reflection-zero exclusion or complete polar endpoint Gram is claimed.

## Verification

```bash
python3 black_hole_programme/phase4/second_order_parent_flux_v1/produce.py
python3 black_hole_programme/phase4/second_order_parent_flux_v1/verify.py
python3 -m unittest -v \
  black_hole_programme/phase4/second_order_parent_flux_v1/test_parent.py
```

Higher tiers were not required because this package adds an isolated exact
algebraic theorem and imports content-addressed certificates without
changing their operators.

EVIDENCE: black_hole_programme/phase4/second_order_parent_flux_v1/certificate.json
CLOSE-OUT: DONE — objective met; exact certificate and independent verifier published.
