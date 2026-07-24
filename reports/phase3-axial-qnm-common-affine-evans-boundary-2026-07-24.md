# Common-affine projective Evans boundary attempt

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The consumer now has an explicit shared panel-local generator and the typed opposite-phase rule
`Delta=q_H-q_out+2*I*omega`.  Endpoint exports are required to subtract centered `q`, `q_tau`, and `q_omega` polynomials before adding independent residuals.

The bounded run stopped on panel `0` of `512`.  The outgoing box transport passed, but its singleton-center validation failed with `AFFINE_Q_REMAINDER_SELF_MAP` at `r=45`. The horizon box validation failed with `RECIPROCAL_REFERENCE_P_MAJORANT_DISCRIMINANT` at `r=134217745/67108864`. Accordingly no endpoint polynomial pair was emitted and the boundary gate is `FAIL_CLOSED`.

This is a representation/majorant obstruction, not evidence for a zero of the physical mismatch.  No argument-principle count was run.
