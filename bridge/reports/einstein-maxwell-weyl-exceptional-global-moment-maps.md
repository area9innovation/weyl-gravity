# Exceptional/global moment maps

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The certified real Weyl--Maxwell symplectic forms determine the stabilizer
moment maps on all standard exceptional blocks.

* The physical `ell=1` oscillators have definite nonzero `mu_H`, hence only
  the origin is common-zero in that block alone.
* For the homogeneous coordinates `(a,b,c,d,Q_e,W_x)`, after removing the
  common positive factor `2*pi*L`,

  ```text
  mu_H = -a^2-b^2+b*d-Q_e^2.
  ```

  The common-zero locus is this quadric, with circumference `c` and flat
  holonomy `W_x` free.
* For the three twist pairs `(A,B)`, `mu_H=2|B|^2` and
  `mu_J=-4 A cross B`.  Thus the isolated common-zero locus is the constant
  twist family `B=0`; it is tangent to the exact lifted-rotation mapping
  tori.

Electric charge variation contributes `-Q_e^2`.  It therefore cannot rescue
a pure-extra obstruction, which has the same moment-map sign.  It can enter
larger balances with Einstein-minus or twist-velocity directions.  Such a
cancellation must occur in the first-order tangent; adding charge only at
second order cannot change an adjoint-cokernel pairing.

Exceptional fourth-order target modes and the full quadratic source on the
combined cone remain separate gates.
