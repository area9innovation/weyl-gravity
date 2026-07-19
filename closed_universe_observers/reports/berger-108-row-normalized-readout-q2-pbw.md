# Berger 108-row normalized-readout q2 PBW block

The complete two-channel detector-readout contribution to the binary bracket is
now exported as an exact sparse PBW tensor.  It is the first variation of

`-kappa p_a sqrt(-g) f_a rho_a J_a C_g(dA,dTheta wedge dR_aI)`

in the metric, clock and all six detector-indexed rods.  The serializer retains
the volume, clock-bump, rod-bump, normalized Gram-Jacobian, inverse-metric and
polarization channels separately before canonical combination.  The 26
vertical coordinates of each `J_a` jet are ordered explicitly by ten metric,
four clock-gradient and twelve detector-rod-gradient components.  Formal
adjunction uses the exact noncommuting Berger-frame coefficient algebra, so the
Maxwell, metric, clock and rod cotangent outputs include every derivative of
the compact profiles.

Direct symbolic differentiation of the full density and form contraction has
zero first-jet defect.  Deleting the normalized-Jacobian variation is detected,
and all three raised cyclic orbits come from the same cubic action vertex.

This closes apparatus q2 when combined with the scalar-BV, six-rod metric and
memory-transport blocks.  It does not close the complete 108-row q2 tensor:
the dynamical-emitter q2 block is next.  No q3 or arity identity, tangent-cone
observer response, physical-branch bridge, finite-parameter causal theorem or
quantum claim follows yet.
