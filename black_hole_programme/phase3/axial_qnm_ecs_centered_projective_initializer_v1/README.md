# Centered phase-factored ECS projective initializer v1

This package Taylor-expands the reduced outgoing amplitude after the exact
phase `exp(-i omega r_star)` has been removed.  An order-16 asymptotic
recurrence supplies the center.  The exact differential residual of that
finite center is then enclosed by the already-certified ECS Volterra
contraction, so only the correction is represented by a ball.

The same panel arithmetic constructs the intrinsic tau sensitivity and the
omega sensitivity, then converts the correlated value/derivative pairs to
the projective variables `q`, `eta=d_tau q`, and `xi=d_omega q`.

The first inward q-chart segment from `r=45` to `r=44.95` passes on all 16
frequency panels.  A q-only continuation reaches approximately `r=39.55`
to `r=40.2` before rectangular Taylor/Cauchy wrapping makes the majorant
fail.  This package is therefore an endpoint and first-segment certificate,
not a complete contour transport.
