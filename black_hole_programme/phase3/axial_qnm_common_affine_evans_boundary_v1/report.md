# Common-affine projective Evans panel-0 repair

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The consumer now has an explicit shared panel-local generator and the typed opposite-phase rule
`Delta=q_H-q_out+2*I*omega`.  Endpoint exports are required to subtract centered `q`, `q_tau`, and `q_omega` polynomials before adding independent residuals.

The bounded repair covers panel `0` only.  The earlier adaptive halving repairs are followed by order-26 direct-`q` transport with radial recentering at both endpoints.  Both endpoint box and singleton transports reach `r=32`, and both centered polynomial exports are emitted.

The mismatch polynomial coefficients are `['[0.00021238978909147629946241320197941604 +/- 4.23e-39] + [1.939002680716433307805957042546651e-5 +/- 8.07e-39]j', '[0.0050348180609611258365387875812757556559 +/- 9.05e-41] + [0.0173375413280913541480554584950368735 +/- 3.97e-38]j']`.  The tightened physical mismatch is certified nonzero on panel 0.  Its independent residual radius is `[3.2532117244264900720884872285147054397e-5 +/- 3.92e-43]`, and its modulus lower bound is `[0.00017797152290985444570195903794139806072 +/- 6.90e-42]`.  This is a panel-local boundary result only.

The other 511 panels and the argument-principle count were not run; no QNM or EP2 claim follows from this single-panel gate.
