# Axial QNM common-affine Evans boundary v1

This package attempts the first consumer of
`axial_qnm_common_affine_export_contract_v1`.

Each contour panel receives one named generator
`zeta = omega - omega_center`.  The horizon and outgoing rails are required
to export centered polynomials for `q`, `q_tau`, and `q_omega`, with
independent residuals added only after the polynomials have been subtracted.
The physical mismatch is assembled with the opposite endpoint phases:

```text
Delta = q_H - q_out + 2*I*omega.
```

The run is deliberately bounded.  It stops at the first panel whose endpoint
export or boundary-nonvanishing gate fails.  A failure is not a root count.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
