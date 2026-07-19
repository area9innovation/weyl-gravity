# Physical plus ghost-`n=3` third-curvature form factors

## Result

The five-carrier physical-Hessian representative now includes all eleven
integrated generic scalar-flat ghost `n=3` triangle channels. Both inputs
already carry their determinant statistics and multiplicities, so the exact
assembly is channelwise addition in the common basis

```text
J_triangle, log(x2/x1), log(x3/x1), rational_corner,
M14_singlet, M15_standard_u, M16_standard_v.
```

The ghost triangle contributes to the first four coordinates. The three
resolved-boundary Mellin masters and the scale derivative remain the
physical-Hessian values because this integrated ghost `n=3` triangle is
scale-free. All eleven channel recipes are content-addressed, evaluated at
two exact generic holdouts and grouped into the five repository carriers.
The relation

```text
I28_123 + I28_132 + I28_231 = 0
```

continues to hold in every coordinate and the scale row, leaving the exact
ten-dimensional quotient.

## Claim boundary

This is a coefficient-bearing partial-BV result with dependency tags
`LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL`. It is not the complete ghost
determinant or repository effective action. Curved-Endo ghost `n=1/n=2`
insertions, generic finite longitudinal-Schur rows, remaining nonminimal/BV
sectors and the independent finite `C2` normalization remain open. It does
not supply complete `Gamma1/Q1`, residual transfer or any Lorentzian theorem.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_plus_ghost_n3_third_curvature_form_factors --check

PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_plus_ghost_n3_third_curvature_form_factors

PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_plus_ghost_n3_third_curvature_form_factors.py
```

## Next gate

Compute the generic ghost `n=1/n=2` insertion traces and finite Schur rows,
then add the remaining BV sectors. The global finite Schur terms require a
primed Green kernel or complete spectral measure; local symbols alone cannot
fix them.
