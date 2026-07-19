# Physical triangle six-master coordinates

## Result

All eleven physical three-`H1` triangle numerator rows now have exact reduced
rational coordinates in the six-master relative-simplex-IBP basis

```text
J_triangle, M_x1, M_x2, M14, M15, M16.
```

The proof uses the exact 52-column basis certified by the carrier-completeness
gate.  A 52-row minor factors over `Q[x1,x2,x3]` as

```text
132239526912 * x1^14 * x2^13 * x3^10
  * (2*x1*x2 + x2^2 - 2*x2*x3 + x3^2)^3
  * lambda^5.
```

The monomial and asymmetric quadratic factors are pivot-chart artifacts.  The
fraction-free solve treats each physical channel separately, verifies the
complete 52-row polynomial identity, and then cancels every coordinate by its
own exact gcd.  Individual coordinates therefore do **not** all have
denominator `lambda^5`.  In particular, the three new-master coordinates are
polynomials, whereas the old scalar-triangle derivative coordinates retain
reduced chart/Källén denominators.

The resulting certificate contains 66 rational functions.  Their expected
homogeneity weights are exact, and five unseen generic fixtures replay all
`5 * 11 * 6 = 330` coordinate values.

## Verification

```bash
# Fast producer/schema rail
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_triangle_six_master_coordinates \
  --fast --check

# Independent determinant, denominator and 330-value replay
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_hessian_triangle_six_master_coordinates

PYTHONPATH=quantum-weyl python3 -m pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_hessian_triangle_six_master_coordinates.py

# Exhaustive evidence rail only
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_triangle_six_master_coordinates \
  --emit --jobs 4
```

The exhaustive four-worker solve takes 246.51s and peaks at 105528 KiB in the
parent process.  The independent replay takes 47.65s; four focused tests take
55.38s.

## Claim boundary

Tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This closes the exact master-coordinate gate.  It does not yet compute the
relative-IBP boundary flux, integrate the complete physical triangle, assemble
the five repository third-curvature form factors, supply `Gamma1` or `Q1`,
restore a QME, authorize residual transfer, or certify a Lorentzian or particle
claim.

Tier 0 parse, JSON and diff checks and Tier 1 fast/independent/focused tests are
required for this leaf.  The affected frontier, atlas and Paper 12 claim-map
chain is Tier 2.  Tier 3 is not required because this is a content-addressed
Euclidean/local coefficient leaf, not a theorem freeze, shared-core change,
release, residual transfer or Lorentzian lifecycle promotion.
