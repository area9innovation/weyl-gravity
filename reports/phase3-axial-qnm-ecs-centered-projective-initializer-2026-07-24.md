# Phase 3 axial QNM: centered phase-factored ECS initializer

The infinity endpoint failure was traced to expanding or balling the wrong
object.  After retaining the exact phase `exp(-i omega r_star)` and expanding
only the reduced amplitude, an order-16 asymptotic center plus a
residual-only Volterra correction gives certified outgoing value,
derivative, q, tau-sensitivity, and omega-sensitivity balls on all 16 contour
panels.

The reduced value excludes zero on every panel.  The first inward projective
segment, `r=45` to `r=44.95`, is certified everywhere.  The q-only rail then
survives roughly five radial units before rectangular wrapping makes the
majorant discriminant nonpositive (`r` between about `39.55` and `40.2`).

This removes the previous immediate chart obstruction and confirms the
phase-factored endpoint representation.  It does not close the inward
transport, the horizon moving-phase jet, the Evans contour, or any QNM/EP2
claim.

Certificate:
`black_hole_programme/phase3/axial_qnm_ecs_centered_projective_initializer_v1/certificate.json`.
