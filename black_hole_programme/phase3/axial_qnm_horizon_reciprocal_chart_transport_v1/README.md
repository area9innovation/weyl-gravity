# Axial QNM horizon reciprocal-chart transport v1

This bounded successor repairs the first horizon `q`-chart majorant
obstruction by certifying the full-panel denominator and switching to
`p=1/q`. It transports only to the common checkpoint `r=4`.

The generated certificate records that all 16 reciprocal denominators exclude
zero and that all 16 panels reach `r=4`. The successor uses the scalar
logarithmic norm of the reciprocal equation; an absolute-value Lipschitz bound
would discard its dissipative real part and is intentionally not used.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_qnm_horizon_reciprocal_chart_transport_v1.produce
```

The artifact is fail-closed and makes no QNM, EP2, Evans, outgoing-frame, or
Lorentzian-causal claim.
