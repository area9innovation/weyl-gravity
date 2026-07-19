# Integrated ghost vector `n=1+n=2` functions

## Result

The pure minimal-vector part of the generic ghost `n=1+n=2` determinant is
now integrated exactly. The eleven projected channel integrands are at most
quadratic in the two simplex coordinates. Five exact boundary identities,
together with `Delta/Delta=1`, reduce every required moment to

```text
J_triangle, log(x2/x1), log(x3/x1), rational_corner.
```

Six channels are nonzero: `I10_123`, all three `I24` orientations and two of
the three `I25` orientations. `I25_312`, all three `I28` rows and `I29_123`
vanish. No new transcendental master is required. An independent consumer
solves the moment system through a separate exact matrix inversion and checks
all six nonzero formulas against direct two-dimensional quadrature.

## Boundary

This covers `N1_VECTOR + N2_VECTOR_VECTOR`, with the determinant signs and
multiplicities already included upstream. It does not evaluate
`N1_LONGITUDINAL_SCALAR`, `N2_VECTOR_LONGITUDINAL`, or
`N2_LONGITUDINAL_LONGITUDINAL`. Those contain the anisotropic insertion
`D_W=delta W d` and remain part of the Schur/global-carrier gate.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n1_n2_vector_integrated_functions --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n1_n2_vector_integrated_functions
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_n1_n2_vector_integrated_functions.py
```

Observed scoped receipts: producer check `PASS` in 5.30 s; independent
consumer `PASS` in 3.87 s; four-test module `PASS` in 4.32 s. Tier 2 was not
triggered because every imported operator and upstream certificate is
content-addressed and unchanged. Tier 3 was not run because this is a scoped
`COEFFICIENT_COMPUTED` addition, not a theorem freeze, lifecycle promotion or
release.
