# Hermitian axial-polar ell=2 Taub receipt

Date: 2026-07-17

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact two-amplitude coordinate calculation used the real cosine
representatives of the degenerate axisymmetric axial and polar
Einstein-Maxwell `ell=2,k=0` minus branches. It computed from the same fields:

- the quadratic Chevreton `tt` tensor and normalized spatial average;
- the quadratic Weyl-Maxwell `[epsilon^2](3B_tt-T_tt)` source;
- the axial-polar polarization entry;
- the constant-lapse Taub matrices on cosine amplitudes and on all four real
  cosine/sine quadratures.

The direct mixed entries vanish. Both Taub diagonal entries are strictly
positive, so every nonzero real tangent in this declared four-dimensional
quadrature space is obstructed on the fixed compact U(1) bundle.

Verification receipt:

```text
/usr/bin/time -f 'elapsed=%e' \
  python3 -m bridge.einstein_sector.einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub --write
PASS, exhaustive final generator run, elapsed=501.64 seconds

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub \
  --verify bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub
3 tests, PASS, elapsed below 1 second
```

Tier 0 and Tier 1 were run. The affected Tier 2 inputs are imported by exact
content hash, and the final generator performs the complete new tensor replay.
Tier 3 was not run because this is a scoped compact fixture theorem, not a
freeze, release, causal promotion, or general nonlinear theorem.

Not established: a charge-relaxed correction, generic `ell` or nonzero
momentum, final residual descent, causal boundary preservation, scattering,
or quantum theory.
