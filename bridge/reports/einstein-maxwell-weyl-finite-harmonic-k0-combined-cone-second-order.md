# Complete finite-harmonic `k=0` second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Every real finite harmonic sum of generic `ell>=2`, `k=0` Einstein and extra
Weyl--Maxwell primaries whose total stabilizer moment maps obey

```text
mu_H=mu_J1=mu_J2=mu_J3=0
```

admits a real smooth, spatially periodic, finite-quasiperiodic second-order
correction.

The proof is a decomposition theorem.  Same-`ell` products are covered by
the fixed-`ell` result: their complete zero-frequency source factors through
`H,J_i`, while every nonzero block is removable.  Distinct-`ell` products
cannot produce `L=0`; they have no zero-frequency collision; and every
generic or exceptional nonzero output misses the target shell.  Their
detailed source coefficients therefore change the correction but cannot
obstruct its existence.  Since the input is a finite harmonic sum, only
finitely many output blocks must be inverted.

This closes the full finite-harmonic cross-`ell` gate at `k=0`.  It does not
claim an infinite-mode Sobolev completion.  The next compact gate is the
relative-phase source for opposite-momentum standing waves, followed by the
exceptional/global homogeneous and twist-velocity mixed cones.

## Verification receipt

Date: 2026-07-18.  Tier 0 scoped parse and diff checks and Tier 1 producer,
independent hash/decomposition verifier, and four tests pass.  Tier 2 imports
the already verified fixed-`ell`, generic cross-`ell`, and exceptional `L=1`
certificates by content hash.  Tier 3 is not run because opposite momenta,
infinite-mode completion, and exceptional/global inputs remain open.
