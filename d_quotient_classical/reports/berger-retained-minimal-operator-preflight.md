# Retained Berger minimal-operator preflight

The retained 26-component layout has three (q_1) blocks.  Two are now
complete: the full first-order spatial diffeomorphism generator and its exact
formal-adjoint identity row.  The complete matter contribution to the metric
Hessian is also derived from the conformally coupled two-scalar action.

The fourth-order Bach principal matrix is reconstructed independently from
(deltaGamma), (delta Riem), (delta P), and
(zeta^czeta^ddelta C_{acbd}).  It is symmetric, has generic rank five,
and annihilates the complete rank-three spatial gauge symbol.  The
second-order matter symbol is symmetric and obeys the same principal gauge
identity.

The parent gate remains false.  The Berger background has nonzero Weyl and
Bach curvature, so the lower-order linearized Bach operator contains
connection-variation terms absent on the conformally flat round cylinder.
Importing the round-cylinder Hessian would therefore be wrong.

The remaining exact calculation is

```text
BERGER_LINEARIZED_BACH_PBW_EXPANSION
```

It must emit all order-three-and-lower Bach coefficients in the declared
invariant covariant PBW normal form.  Only then can the complete retained
(q_1^2=0), cyclicity, and action-adjoint identities promote
`BERGER_RETAINED_MINIMAL_OPERATOR`.
