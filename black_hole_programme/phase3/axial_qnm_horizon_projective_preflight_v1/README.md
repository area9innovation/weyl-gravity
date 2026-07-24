# QNM-band horizon moving-phase projective preflight v1

This package evaluates the regular spin-two horizon germ after factoring
`exp(i omega r_star)`.  The imported certificate gives
`dot(lambda_H)=0`, so the intrinsic tau jet adds no logarithm.

The scalar Frobenius recurrence is evaluated on all 16 QNM contour panels
at `rho=2^-22`, including tau and omega derivatives.  A geometric affine
projective rail then attempts to reach `r=32`.

The rail refuses before `r=32` on every panel because the absolute Cauchy
majorant for the singleton reference trajectory loses a positive Riccati
discriminant.  This is recorded fail-closed; no endpoint mismatch or root
claim is formed.
