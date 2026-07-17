# Berger retained rank-46 STF2 prolongation carrier

## Exact construction

The natural local enlargement requested by the retained-36 projector
obstruction is now constructed as a cyclic graph carrier.  Five spatial STF2
coordinates

```text
h12, h13, h23, h11-h22, h11+h22-2h33
```

define `T_STF`, and the new prolongation variable obeys

```text
Y = F h,    F = T_STF Box_2.
```

The cotangent shear gives the extended metric Hessian

```text
[[A10 + F^dagger F, -F^dagger], [-F, I5]],
```

whose Schur complement is exactly `A10`.  Adding the five cyclic-dual rows
gives degree ranks `(4,19,19,4)` and total rank 46.

The exact 46-to-36 graph SDR passes nilpotency, unary cyclicity, both chain
maps, contraction, all three side conditions, homotopy cyclicity and induced
pairing checks.  The exported q1 has 237
nonzero row-pair blocks and maximum differential order
4.

## Boundary

This is the honest carrier construction, not yet the branch theorem.  The
added STF2 complement is contractible, so no new cohomology or physical branch
has been declared.  A rank-46 Einstein-like/extra-Weyl projector or normalized
obstruction remains the next gate.  The nonlinear q2/q3 lift, K_Berger
equivariance, causal support and branch-space ell3 table remain false.
