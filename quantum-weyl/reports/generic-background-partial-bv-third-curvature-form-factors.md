# Generic partial-BV third-curvature form factors

## Result

Every currently integrated generic scalar-flat parity-even sector is now
assembled in one five-carrier ledger:

```text
same-gauge physical Hessian
+ all ghost n=3 channels
+ ghost N1_VECTOR and N2_VECTOR_VECTOR.
```

The eleven labelled rows remain in the exact ten-dimensional quotient, with
`I28_123 + I28_132 + I28_231 = 0` in all seven function coordinates and the
scale row. Each channel records sector provenance, content digests and two
exact generic holdouts.

## Boundary

This is deliberately named `PARTIAL_BV`. It is not the full ghost determinant
or full BV effective action. Exactly three longitudinal/mixed `D_W` carriers,
their generic finite Schur rows, remaining BV sectors and the finite `C2`
normalization remain open. Complete `Gamma1/Q1`, residual transfer and all
Lorentzian claims remain fail-closed.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_partial_bv_third_curvature_form_factors --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_partial_bv_third_curvature_form_factors
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_partial_bv_third_curvature_form_factors.py
```

Observed scoped receipts: the producer check plus independent exact consumer
`PASS` in 47.4 s; the four-test module `PASS` in 40.24 s. Both stay below the
roughly 60 s Tier-1 split threshold, so the exact reconstruction remains on
the scoped rail. Tier 2 was not triggered because all upstream operators and
certificates are unchanged and content-addressed. Tier 3 was not run because
the artifact remains explicitly partial BV and does not freeze a theorem or
promote a lifecycle state.

## Next gate

Compute the three `D_W` longitudinal/mixed carriers and the generic finite
Schur rows using a primed Green kernel or complete spectral measure, then add
the remaining BV sectors.
