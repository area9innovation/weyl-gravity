# Common affine endpoint export shortfall

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The serialized horizon and outgoing artifacts do not export a common omega-generator identity, centered omega-polynomial coefficients, or residual radii after subtracting those polynomials. Consequently the cross-endpoint cancellation required by `Delta=q_H-q_out+2*I*omega` cannot be reconstructed safely.

A bounded singleton-centered horizon attempt passed its first Taylor reference step but failed the existing remainder self-map at the first seed step. No long rerun was started. Boundary nonvanishing and all downstream gates remain not run.
