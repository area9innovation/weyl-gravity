# Local algebra scaling foundations receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INFRASTRUCTURE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Improvements made before the mixed quotient

Tensor monomials and expressions now have an explicit tensor-product API.
Right-hand indices are alpha-renamed disjointly unless an `index_map`
declares a contraction.  Unknown maps and contractions that use an abstract
index more than twice fail closed.  The covariant commutator can also act on
one factor inside an existing contraction pattern.  Its exact witness has
four complete scalar terms and mixes two-factor `R nabla^2 R` monomials with
three-factor `R^3` monomials.

The exact quotient reducer now removes dependent zero rows from stored RREFs.
The proof object therefore has one row per relation-rank unit instead of
retaining redundant rows.

## Orbit-first cubic generation

A naïve benchmark canonicalizing the first 100 of 10,395 cubic pairings took
2.51 seconds and projected beyond the 60-second Tier-1 budget.  The new
generator constructs the complete signed action of intrinsic Riemann
symmetries and permutations of the three even factors, then partitions raw
pairings before invoking the general monomial canonicalizer.

```text
raw Riemann^3 perfect matchings             10,395
signed slot/factor group order               3,072
complete signed orbits                          33
orbits vanishing by intrinsic symmetry          20
nonvanishing symmetry orbits                     13
representatives cross-checked                     33
raw canonicalizations avoided                 10,362
canonicalization cache maximum entries        65,536
```

The complete orbit calculation and representative cross-check takes about
two seconds in an isolated run.  Every raw pairing belongs to exactly one
orbit.  The detailed receipt hashes the full 10,395-member signed partition,
while storing only the 33-row orbit ledger and 13 nonzero canonical
representatives.
The cache is explicitly bounded, so later ansatz generation cannot grow it
without limit; eviction affects runtime only, never canonical results.

## Enforced schemas

The differential/Hodge and scaling receipts now use a dependency-free,
recursive validator for the JSON-Schema subset used locally.  Exact counts,
RREF shape, pivot/free columns, signature matrices, hashes, claim-boundary
statuses, cubic orbit counts, and tensor-product witnesses are enforced.
Mutation tests demonstrate that numerical drift is rejected.

## Claim boundary

The 13 nonzero objects are symmetry orbits, not yet independent cubic
curvature invariants.  Algebraic Bianchi identities, dimension-dependent
Schouten identities, and the mixed IBP/commutator quotient with
`(nabla Riemann)^2` remain `NOT_COMPUTED`.  No counterterm class, anomaly
class, coefficient, QME status, residual transfer, or Lorentzian causal claim
is made.

The machine receipts are:

- `quantum-weyl/local_bv/certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS.json`.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile `quantum-weyl/local_bv` | 0.03 s | pass |
| 0 | parse quantum JSON and scoped `git diff --check` | 0.03 s | pass |
| 1 | local-BV unit tests | 10.57 s | 60 pass |
| 1 | four local certificate reproduction checks | 7.42 s | pass |
| 1 | detailed differential/Hodge and scaling schema validation | 0.58 s | pass |
| 1 | four common result-envelope validations | 0.02 s | pass |
| 1 | scaling certificate under hash seeds `1,7,123` | 6.68 s | pass |

Tier 2 is not triggered because no pinned classical dependency or consumed
upstream schema changed.  Tier 3 is not triggered because this remains local
infrastructure, not a freeze, QME result, paper theorem, lifecycle promotion,
or repository shared-core release.  The full repository suite is not
represented as passing.

## Next mathematical gate

Generate algebraic-Bianchi relations on the 13 nonzero cubic orbit
representatives.  Then join that quotient to the four-dimensional isolated
`(nabla Riemann)^2` quotient through exact total-derivative and contracted
commutator relations.
