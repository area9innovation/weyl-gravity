# ECS Riccati transport preflight v1

This package attempts a two-chart projective transport of the spin-two Jost
line using \(q=v_x/v\) and \(p=v/v_x\).  Every Taylor step has an `acb`
enclosure, a quadratic self-map majorant and a Cauchy tail.

All contour panels stop near \(r=43.2\): the coarse norm-only ECS initializer
expands until its \(q\) enclosure contains zero, preventing a certified
reciprocal chart, while the current-chart majorant ceases to contract.
This is an enclosure obstruction, not a physical Jost zero.
