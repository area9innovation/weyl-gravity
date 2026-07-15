# Antifield-zero production run: Sprint 1

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Scope label: `AFN0_ONLY`

Result state: `IN_PROGRESS`

## Outcome

The four requested Sprint 1 slices now execute and emit deterministic
receipts:

- `H04_AFN0_EVEN`;
- `H04_AFN0_ODD`;
- `H14_AFN0_EVEN_WITHOUT_EULER`;
- `H14_AFN0_ODD`.

They reuse the exhaustive top-level quadratic-curvature carrier generator.
That generator starts from 105 pairings, reduces to four symmetry-canonical
monomials, applies the rank-one algebraic-Bianchi quotient, and recovers the
three-dimensional quadratic curvature quotient.  Even and odd Weyl carrier
spaces are generated and reduced independently.  Every slice records its
rules, bounds, raw and canonical counts, identity ranks, and manifest hash.

The run also imports the exact primitives for `Box R` and `omega Box R`.
Those two entries are `EXACT`; all other relative class statuses remain
`UNDECIDED`.

## Deliberate fail-closed boundary

This is not yet the antifield-independent obstruction classification.  The
top curvature-density carrier basis is complete under its declared rules,
but the lower-form ghost/generalized-connection bases required by the total
complex are still `IN_PROGRESS`.  The pure-Diff ghost basis at ghost number
one is likewise incomplete, and the even anomaly slice excludes `omega E4`
until its intrinsic tower closes.

Consequently the run emits no nontriviality claim and no dual witness for a
physical representative.  The generic exact engine now constructs a dual
functional `lambda` satisfying

```text
lambda(boundary) = 0
lambda(representative) = 1
```

but production witnesses will be attached only after the complete boundary
space and its basis-manifest hash are frozen.

## Machine receipts

- `quantum-weyl/local_bv/cohomology/H04_AFN0_RESULT.json`;
- `quantum-weyl/local_bv/cohomology/H14_AFN0_RESULT.json`;
- `quantum-weyl/local_bv/certificates/AFN0_PRODUCTION_RUN_CERTIFICATE.json`;
- `quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.

## Next computation

Generate all lower-form spaces at total engineering dimension four, including
Weyl-ghost derivatives and the certified generalized-connection carriers.
Assemble exact `Q` and `d_h` matrices, complete the intrinsic `omega E4`
tower, rerun the even anomaly slice, and only then solve the full boundary
membership problem.

## Verification receipt

| Rail | Result |
|---|---:|
| focused AFN0, descent, Euler, and quotient tests | pass |
| complete local-BV suite | 153 pass in 21.91 s |
| generic result schemas | 6 pass |
| classical-import regression | 16 pass |
| five affected certificate builders under hash seeds `1,7,123` | identical |
