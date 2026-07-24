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

The repair run is deliberately bounded to panel 0.  The outgoing rail uses
adaptive halving when the singleton remainder self-map is too coarse.  The
horizon reciprocal rail caps its near-horizon step by `(r-2)/16`, so its
Taylor disk remains inside the regular domain.  Both endpoint polynomial
exports must complete before the panel-0 physical mismatch is tested.

A failed panel-0 mismatch is not a root count, and success on panel 0 would
not certify the other 511 panels.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
