# Berger normalized-readout q3 PBW certificate

`BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW` is the complete
`LOCAL-ALGEBRAIC` two-detector readout source at quartic action order.

An exact second-order jet differentiates the full normalized readout density
over clock value, three rod values, ten metric components, four clock
gradients, and twelve detector-rod gradients.  It preserves the declared
vertical coordinate order and explicitly carries `f''`, `rho_IJ`, and every
entry of the normalized-Jacobian Hessian.  Its first derivative exactly
recovers the certified `q2` input.

The action-derived tensor includes all ordered p-, Maxwell-, metric-, clock-
and rod-cotangent rows.  Independent PBW formal adjunction from the p rows
reproduces the Maxwell and geometry families, including coefficient
derivatives.  Row chunks are deterministic gzip JSON with exact hashes.

This is one `q3` source, not a nonlinear detector solution.  Physical emitter
`q3`, base/zero assembly, arity, equivariance, observer morphism, tangent-cone
response, nonlinear rank, Bridge 3, causal and quantum promotions remain
fail-closed.
