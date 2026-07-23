# Axial horizon Grassmann/Möbius one-shell preflight

This isolated package tests a parameter-correlated Grassmann representation
of the three-complex-dimensional future-horizon-regular axial Bach plane on
Schwarzschild.

Its exact scope is

\[
M=1,\qquad \ell=2,\qquad
M\omega\in[1/2,129/256],\qquad
\rho=r-2\in[2^{-22},2^{-21}].
\]

The frequency interval is divided into four exact subcells.  Within each
subcell, every affine operation retains generator `7315`.  The chart uses

\[
I=(P',Q,H_1),\qquad J=(P,Q',\rho F),
\]

with block-real selectors

```text
I_R = [1,2,8,5,6,10]
J_R = [0,3,9,4,7,11].
```

The producer applies the exact Möbius update

\[
Z_+=(\Phi_{JI}+\Phi_{JJ}Z)
(\Phi_{II}+\Phi_{IJ}Z)^{-1}
\]

through a checked right solve.  A direct full-column rail and a nontrivial
exact rational column-gauge rail provide independent falsification checks.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_horizon_grassmann_mobius_preflight.run_preflight
python3 -m black_hole_programme.phase3.axial_horizon_grassmann_mobius_preflight.verify
python3 -m pytest -q black_hole_programme/phase3/axial_horizon_grassmann_mobius_preflight/tests
```

A pass establishes only the first-shell graph transport.  It does not
establish an \(r=4\) map, a horizon-to-infinity connection, scattering, flux
sign, stability, a physical ghost, positivity, CPT, or unitarity.
