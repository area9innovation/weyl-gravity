# Axial Weyl–Maxwell operator-module preflight

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`CLASSIFIED`.

For generic axial `ell>=2`, the ungauged coefficient vector

```text
(h_t,h_x,h_2,q_t,q_x,b)
```

with gauge parameters `(s,r)` contracts exactly to four invariants
`(H_t,H_x,Q_t,Q_x)`. The contraction identities `KG=0`, `KJ=I`,
`I-JK=GH`, and `HG=I` hold over `Q[I,lambda,k][D]`. The only denominator is
the constant `2`; neither `D=partial_t` nor `k` is inverted.

The target operator must be treated as a differential-module presentation
before setting `D=-I*omega`. Its Hessian and independently linearized equation
routes must agree and pass both Noether identities, formal self-adjointness,
the off-shell Green identity, and source-image annihilation. Every pivot factor
must enter a denominator ledger, with `lambda=0`, `lambda=2`, `k=0`, and all
resultant/discriminant loci solved separately.

Before symbolic-`lambda` promotion, a full four-dimensional `Y_20` tensor
replay at symbolic `k` must match all coefficient rows, identities, invariant
factors, denominators, and Lee–Wald pairings without branch substitution.

The target operator and fixture are not yet constructed; no extra dispersion
or mode is certified by this preflight.

Receipt (2026-07-16): Tier 0 Python/JSON and scoped diff checks passed. The
18-test axial/parent affected chain passed in 0.40 s, followed by the axial,
parent extra-branch, and G4 independent verifiers. Tier 3 was not run because
this is a fail-closed reduced-mode preflight with no operator, lifecycle, or
release promotion.
