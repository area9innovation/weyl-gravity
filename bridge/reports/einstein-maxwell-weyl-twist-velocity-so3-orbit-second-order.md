# SO(3) orbit of the balanced twist-velocity fixture

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The Cartesian real `ell=1` harmonics `(Y_x,Y_y,Y_z)` have exact Gram matrix
`(4*pi/3)I`.  The connected background stabilizer contains `SO(3)`, which
acts transitively on each nonzero twist-velocity sphere.

Consequently the direct `Y_z` correction proves second-order extension for
every twist-velocity vector with zero twist position and

```text
3*a^2=4*(B_x^2+B_y^2+B_z^2).
```

Rotate the input to the `z` axis, apply the certified correction, and rotate
the complete correction back.  Naturality of the Weyl--Maxwell equations
preserves every zero remainder.  The construction is independent of the
chosen rotation because the axisymmetric correction is invariant under the
remaining `SO(2)` stabilizer.

Nonzero twist position parallel to the velocity is the next genuinely new
source; it is not covered by this orbit argument.
