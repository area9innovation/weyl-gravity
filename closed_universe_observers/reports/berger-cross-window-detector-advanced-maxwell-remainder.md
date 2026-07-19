# Berger D1-to-h0 advanced-Maxwell remainder

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The six mismatched recoil channels require one detector-profile bandwidth not
covered by the corresponding-window certificate: `I_100` evaluates the D1
advanced detector image on the earlier `h0` feedback slab.  Exact supports give

```text
source_time - t in [7/24, 3/8],
T = t_D1 - t in [5/16, 17/48].
```

The exact order-five polynomial coefficients are unchanged.  This certificate
recomputes the uniform cosine, sine and differentiated-cosine tails at the
larger `tau_max=3/8` for every `two_j=0,...,4`.  The previous D1/h1
`tau_max=3/16` is rejected as insufficient for this cross window.

This closes a finite profile-bandwidth input only.  It does not evaluate
`I_100`, extend above `two_j=4`, select physical masses, descend through the
apparatus quotient, restrict to the tangent cone, activate Bridge 3 or make a
quantum claim.
