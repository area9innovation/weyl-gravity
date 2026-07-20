# Compensated endpoint chain obstruction

The correlated fixed-bundle Maxwell endpoint makes the five-stabilizer Gram
matrix constant, but it does not complete the unary chain map.  Restrict the
chain equation to the translation-invariant `(t,x)` zero mode and the
`P_H_3_t_theta_phi` current component.  Since `lambda_H=0` and the magnetic
field has only `theta-phi` components, the exact target block is

```text
-2 tau u - xi v = -xi
   tau v + 2 xi w = 0.
```

The lowest differential coefficient system has rank
`3` and augmented rank
`4`.  Its two-row left-null witness
evaluates to `-1`.  The
equivalent polynomial elimination leaves the nonzero normal form `xi` modulo
`(tau,xi^2)`.  This is a filtration obstruction, not an extrapolation from
orders one through three, so no finite-order product-equivariant support-local
lift exists on the current carrier.

The missing tensor component is exactly antisymmetric.  Adjoining the
covariant module `Lambda^2(T^*M)` makes the flat block square and
invertible, with the unique normalized solution

```text
u = 0,  v = 1/2,  w = 0,  b = 1/2.
```

This classifies the minimal covariant symbol repair only.  A cyclic dual
completion and the resulting full chain map remain unconstructed, and
`q2/f2` stays inactive.

CLOSE-OUT: OBSTRUCTED — the compensated endpoint removes the pairing defect but the existing symmetric equation carrier has an exact all-finite-order flat-symbol obstruction
EVIDENCE: EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1
