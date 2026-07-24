# Common-affine projective Evans panel-0 repair

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The consumer now has an explicit shared panel-local generator and the typed opposite-phase rule
`Delta=q_H-q_out+2*I*omega`.  Endpoint exports are required to subtract centered `q`, `q_tau`, and `q_omega` polynomials before adding independent residuals.

The bounded repair covers panel `0` only.  Adaptive outgoing halving repairs the singleton `AFFINE_Q_REMAINDER_SELF_MAP`; a horizon-distance-relative reciprocal step repairs `RECIPROCAL_REFERENCE_P_MAJORANT_DISCRIMINANT`.  Both endpoint box and singleton transports now reach `r=32`, and both centered polynomial exports are emitted.

The independent post-polynomial residuals remain too wide for the physical mismatch: the certified mismatch-center polynomial has coefficients `['[0.00021238978909115190617240553905276101 +/- 4.76e-39] + [1.939002680709581150075848654523725e-5 +/- 6.41e-39]j', '[0.005034818060965535503614720624909750768 +/- 2.17e-40] + [0.0173375413280897824885862235078093363 +/- 5.47e-38]j']`, while the independent residual radius is `[0.033541234756919145276031921840171197493 +/- 2.88e-40]`.  Its modulus lower bound is `0`, so the panel-0 boundary gate remains `FAIL_CLOSED` with `COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO`.

This is a residual-dependency obstruction, not evidence for a zero of the physical mismatch.  The other 511 panels and the argument-principle count were not run.
