# Phase 3 Riccati chart obstruction

A validated two-chart Riccati rail was attempted on all sixteen QNM contour
panels.  It uses \(q=v_x/v\), \(p=v/v_x\), order-14 `acb` Taylor steps of
length \(1/20\), quadratic self-map tests and Cauchy tails.

All panels stop near \(r=43.2\).  The coarse ECS initializer has a derivative
ball centered at zero; rectangular propagation quickly makes the \(q\) ball
contain zero.  The reciprocal \(p\) chart is then unavailable, while the
current chart loses its self-map discriminant.

This is a certified enclosure obstruction, not a physical Riccati pole.
The next gate is to evaluate a centered finite Picard/Neumann approximation
of the ECS fixed point and bound only its residual.  The intrinsic tangent
can then be carried by differentiating the certified Möbius chart updates.
