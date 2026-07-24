# Panel-77 horizon center self-map repair

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

At `r=2+2^-22`, the panel-center seed radii are approximately `q=8.63e-25`, `eta=1.06e-23`, and `xi=6.53e-24`.  The original subtractive binary64 quadratic formula returns a negative candidate and fails the unchanged self-map inequality.  Raising arithmetic precision to 256 bits or raising the Frobenius/Taylor orders to 24/32 does not repair that cancellation.

Using the algebraically equivalent stable smaller-root formula `2*qc/(-qb+sqrt(discriminant))`, enlarged by the exact rational factor `1000001/1000000`, gives strict first-step margin `[8.6264463207645213556621714448786287493e-31 +/- 7.51e-70]`.  The complete direct-`q` horizon transport then passes for both the box and center without rejection. The reciprocal pivots also exclude zero.  Panel 77 has certified `|Delta|` lower bound `[8.86835506935605363940896836025313349e-6 +/- 5.60e-42]`.  No threshold was lowered and no QNM or EP2 claim is made.
