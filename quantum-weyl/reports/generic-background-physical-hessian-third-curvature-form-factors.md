# Physical-Hessian third-curvature form factors

## Result

The same-gauge rank-nine traceless physical Hessian now has five exact
carrier-labelled parity-even third-curvature form-factor functions in the
declared common Mellin minimal-subtraction representative.  The eleven raw
orientation channels are grouped as

```text
I10: 1   I24: 3   I25: 3   I28: 3   I29: 1,
```

and the symmetric `I28` component vanishes coefficientwise, leaving the
certified ten-dimensional four-dimensional quotient.

Each channel is an exact recipe combining:

```text
integrated three-H1 seven-function decomposition
+ sum of the three finite H1-H2 contact rows
+ log(mu^2) times the combined triangle/contact scale row.
```

The finite contact sum is absorbed into the rational coordinate of the
triangle basis.  Content digests bind every imported triangle, contact and
scale row, while two exact generic holdouts record all seven triangle
coordinates, the contact sum, the assembled rational coordinate and the
scale derivative.

## Scheme boundary

This closes the physical-Hessian assembly gate, not the full-BV determinant.
The representative uses the common resolved-boundary Mellin subtraction and
excludes the common `(4*pi)^-2` loop factor.  An independent mu-independent
finite local `C^2` counterterm can shift the cubic expansion, so its absolute
normalization remains explicit and unfixed.  Ghost and remaining BV rows,
complete `Gamma1/Q1`, residual transfer and Lorentzian claims remain open.

## Exact checks

The producer verifies the five carrier groups, all eleven orientations, all
three contact incidences per orientation, exact combined scale rows and the
four-dimensional `I28` relation in every triangle-basis coordinate, the
finite contact sum, the assembled rational coordinate and the scale row.
The independent consumer reconstructs the sums directly from the hashed
dependencies and repeats the exact relation without importing the producer.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_third_curvature_form_factors --check

PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_hessian_third_curvature_form_factors

PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_hessian_third_curvature_form_factors.py
```

## Next gate

Add the generic ghost and remaining BV rows, provide the missing global
primed Green/spectral carrier for their finite pieces, and either fix or
parameterize the independent finite `C^2` normalization.  Only then can the
programme claim complete repository form factors or a complete renormalized
`Gamma1/Q1`.
