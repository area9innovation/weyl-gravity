# Correlated-functional boundary replay

This bounded experiment replays only the refused shell-4/segment-3 boundary
for the two exact q00 children from
`axial_horizon_h4_plucker_q00_split_v1`.

The first 19 segment computations remain the original raw-coordinate
projective transport.  At the refused boundary only, the replay replaces
the raw coordinate pivot by the real part of the midpoint-Hermitian
functional

```text
L_p(q) = sum_j conjugate(p_j(0)) q_j.
```

Its coefficients are the exact rational Taylor midpoint coefficients.  The
runtime certifies the interval enclosure of `Re L_p(q)` and proceeds only
when that interval excludes zero.  Code 35 is a typed refusal: the
correlated functional enclosure contains zero.

The experiment is intentionally outcome-safe.  A passing replay would show
that a correlated projective chart removes the raw-coordinate shortfall at
this one boundary.  A code-35 replay records the precise algebraic
enclosure obstruction without asserting rank loss.

Run:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_correlated_functional_v1.produce
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_correlated_functional_v1.run_children
PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_horizon_h4_plucker_correlated_functional_v1.test_correlated
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_correlated_functional_v1.verify
```

This package does not transport beyond shell 4 segment 3 and does not
establish the complete horizon transport or a scattering theorem.
