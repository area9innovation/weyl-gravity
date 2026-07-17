# Full generic (k=0) Einstein--extra moment-map cone

Status: `CLASSIFIED` (`LOCAL-ALGEBRAIC`, `REDUCED-MODE`).

## Result

After exact Gram normalization, the complete generic (k=0) amplitude data
at each (ell\ge2) reduce, for purposes of the five stabilizer charges, to
three positive-semidefinite spin-(ell) density matrices

\[
\rho_{+,ell}\succeq0,
\qquad \rho_{e,ell}\succeq0,
\qquad \rho_{-,ell}\succeq0,
\]

with ranks at most (2,4,2), respectively.  These ranks retain both parities,
both extra cyclic summands in each parity, and both Einstein frequency
branches.

Writing

\[
A_{s,ell}=\operatorname{tr}\rho_{s,ell},
\qquad
j_{s,ell,a}=\operatorname{tr}(\rho_{s,ell}T_{ell,a}),
\]

the full finite-harmonic common-zero cone is exactly the positive-semidefinite
rank locus cut out by

\[
\sum_ell
(\omega_+^2A_{+,ell}+\omega_e^2A_{e,ell}
-\omega_-^2A_{-,ell})=0,
\]

\[
\sum_ell
(\omega_+j_{+,ell,a}+\omega_ej_{e,ell,a}
-\omega_-j_{-,ell,a})=0,
\qquad a=1,2,3.
\]

The circle-momentum charge vanishes identically at (k=0).  Factorization
(ho=C^\dagger C) proves the converse: every point of this rank-constrained
spectrahedral pullback reconstructs linear amplitudes.

## Immediate consequence

For every fixed (ell\ge2), the (m=0) projectors give a two-parameter
rotationally neutral subcone.  If (a_+,a_e\ge0), then

\[
a_-=
\frac{\omega_+^2a_++\omega_e^2a_e}{\omega_-^2}
\]

makes all five moment maps vanish.  The balanced Paper 91 fixture is the
(ell=2), (a_+=0) boundary ray.  It is therefore not isolated at the Taub
level.

## Boundary

This classification does not say that every point of the cone has a
second-order correction.  The next calculation must evaluate the complete
quadratic Weyl--Maxwell source on its strata.  Opposite nonzero momenta and
exceptional/global blocks remain separate gates.

## Verification

```bash
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_k0_moment_map_cone \
  --verify bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_k0_moment_map_cone.py
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_k0_moment_map_cone
```
