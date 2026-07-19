# Renormalized physical triangle master values

## Result

The three new rank-52 physical triangle masters are evaluated in the common
dominant-sector Mellin minimal-subtraction scheme:

```text
M14 = FP_MS integral_simplex e3/Delta^4
M15 = FP_MS integral_simplex e3*(alpha1-alpha2)/Delta^4
M16 = FP_MS integral_simplex e3*(alpha2-alpha0)/Delta^4.
```

The exact output is sector decomposed.  On one generic dominant sector, six
half-sector kernels suffice: `K0` carries the Mellin finite part, while `Kp`
and `Kq` are finite first moments.  The other dominant sectors follow by
cyclic box substitution.  Exact chart reconstruction supplies the singlet
and standard-`S3` coefficient triples without a second integration pass.

Every stored value is an explicit rational/logarithmic function of
`(x1,x2,x3,z)`, where `z=mu^2/Q^2`, and includes its exact derivative with
respect to `log z`.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_triangle_renormalized_master_values \
  --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_hessian_triangle_renormalized_master_values
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_physical_hessian_triangle_renormalized_master_values
```

The cold producer takes 44.24s (25.39s warm), the independent verifier 12.54s,
and four tests take 21.97s.  The verifier directly quadratures all six defining
radial finite parts and two positive-Euclidean fixtures independently replay
both standard generators of the `S3` action to better than `1e-60`.

Test-tier disposition: Tier 0 parse, JSON and diff checks; Tier 1 producer,
independent verifier and four focused tests; and the Tier 2 active-frontier,
atlas, common-atlas and Paper 12 claim-map consumers all pass.  Tier 3 was not
run because this adds one content-addressed Euclidean master-value leaf and
does not freeze a theorem, change shared core algebra or prepare a release.

## Claim boundary

Tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This computes the three renormalized master values.  It does not yet compute
the six-master coordinate functions of the eleven physical channels,
integrate the complete physical triangle, assemble the five repository
third-curvature form factors, supply `Gamma1` or `Q1`, restore a QME,
authorize residual transfer, or certify any Lorentzian or particle claim.
