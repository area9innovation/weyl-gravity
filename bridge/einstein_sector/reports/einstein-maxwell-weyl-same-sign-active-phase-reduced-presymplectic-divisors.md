# Fixed-occupation node-phase-reduced presymplectic divisors

The preceding affine conormal theorem does not yet perform the reduction used
on a fixed-occupation real solution link.  The two parity channels share one
phase for each physical node, and candidate 18 has ten positive
current-orthogonal spectator coordinates.  Treating the parity factors
separately would therefore give the wrong reduced divisor.

Let `J` be the smooth resonance Jacobian, `H` the ambient Hermitian Lee--Wald
current and `C_minus,C_plus` the two Hermitian-orthogonality rows for the
nonzero active nodes.  Then

```text
A = stack(J,C_minus,C_plus)
K_hat = A H^{-1} A^dagger
```

is the exact normal Gram for the fixed-norm horizontal model.  Its determinant
vanishes exactly when the current after both common node-phase quotients is
degenerate.  The determinantal ideals give every corank.  On each smooth
constant-corank stratum, closedness of the Lee--Wald form makes the radical
distribution involutive, so a local simple leaf quotient is symplectic.

For candidates 17 and 20, `A` is `8 x 20`; the reduced horizontal space has
complex dimension 12.  The previously certified bounded point has augmented
normal rank six, hence reduced radical dimension two and local quotient real
dimension 20.  A second exact smooth point has nonzero augmented determinant,
proving that the divisor is proper.  The two total-node rows couple the parity
factors, so this reduced equation is not replaced by the product of the two
affine `3 x 3` determinants.

For candidate 18, the complete regular atlas has 100 product charts.  Each
augmented matrix is `10 x 30` and includes the ten positive spectators.  On
the common central-angular section,

```text
det K_hat =
 -128 (t1^2+t2^2)
 [a^2-a b(t1^2+t2^2)+b^2 t1^2 t2^2-c^2]^4
 / [9 b^7 (a-c)^4 (a+c)^3].
```

The symmetric and antisymmetric branches have augmented normal rank six,
reduced radical dimension four and local quotient real dimension 32.  The
control point `(t1,t2)=(0,1)` is exactly nondegenerate: its internal factor is
strictly negative from the imported exact bounds `w_x>0`, `0<w_y<1` and
`b>2880`.

This closes the regular fixed-occupation node-phase layer.  It does not
perform the lifted `SO(3)` reduction, construct a global Hausdorff leaf space,
resolve singular loci, glue occupation strata, or promote any all-orders,
causal, observational or quantum claim.
