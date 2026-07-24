# Centered phase-factored ECS projective initializer

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The previous coarse outgoing initializer put the entire Volterra solution
inside a ball centered at `(v,v_x)=(1,0)`.  Its projective quotient lost the
information needed by the q chart.  This successor instead factors the exact
outgoing phase, computes a finite order-16 `z=1/r` asymptotic center, and
balls only the correction forced by the exact residual.

Across all 16 panels covering the declared QNM contour, the reduced value
balls exclude zero.  The package constructs `q`, the intrinsic deformation
sensitivity `eta`, and the frequency sensitivity `xi` at `r=45`.  Every
panel passes the first inward q-chart segment to `r=44.95`.

The q-only continuation then fails between about `r=39.55` and `r=40.2`.
The terminal condition is uniformly
`NONPOSITIVE_MAJORANT_DISCRIMINANT`: accumulated rectangular wrapping has
again made the scalar majorant too wide.  This is an exact numerical
shortfall, not evidence for a physical projective pole.  A recentered
multi-chart QR/Lohner rail remains necessary.

This certificate does not construct the horizon moving-phase jet, a
two-sided Evans determinant, a root count, a QNM, or an exceptional point.
