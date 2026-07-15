# AFN0 basis-gap reverse-coverage receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `BASIS_GAPS_PARTIALLY_RESOLVED`

## Outcome

The dimension-four AFN0 enumerator now separates three stages that were
previously conflated:

```text
GRADING_ADMISSIBLE
TENSOR_REALIZABLE
CANONICALLY_NONZERO
```

The coarse top-form Weyl count remains the requested `3` at ghost number zero
and `9` at ghost number one.  Applying only tensor-seed, scalar-index, and
epsilon-availability constraints gives:

| Slice | Coarse | Refined | Tensor-realizable | Known nonzero signatures | Pending |
|---|---:|---:|---:|---:|---:|
| `H04_AFN0_EVEN` | 3 | 2 | 2 | 2 | 0 |
| `H04_AFN0_ODD` | 3 | 2 | 2 | 1 | 0 |
| `H14_AFN0_EVEN_WITHOUT_EULER` | 9 | 5 | 5 | 2 | 2 |
| `H14_AFN0_ODD` | 9 | 5 | 5 | 1 | 3 |

The eliminated signatures attempted to apply covariant tensor derivatives
without any curvature or other tensor seed.  Since the Levi-Civita
connection is metric-compatible, `nabla g = 0`; these rows terminate as
`WRONG_AFTER_REFINED_GRADING` with reproducible proof hashes.

Two further single-factor families terminate as `TOTAL_DERIVATIVE_ONLY`:
the fourth-derivative Weyl-ghost signature and the odd single-curvature
two-derivative signature.  In each raw graph, exposing the outer contracted
derivative gives an explicit current because both metric and epsilon
contractions are covariantly constant.  The mixed curvature/ghost-derivative
signatures remain pending.

The Diff top-form sector is deliberately separate from the Weyl-anomaly
count.  It has 12 coarse signatures and seven refined signatures in each
parity sector.  This ledger is also distinct from the universal lower-form
Diff completion.  No implication between these three spaces is inserted.

## Tensor-graph rail

Every refined signature now instantiates labelled curvature, derivative, and
ghost index slots.  The machine enumerates every raw scalar contraction graph:

- even parity: all perfect metric matchings;
- odd parity: every choice of four epsilon slots followed by all perfect
  metric matchings of the remaining slots.

Each row stores its raw graph count and a content hash of the full graph
manifest.  This is forward raw generation, not yet a canonical tensor basis.
Factor permutations, tensor symmetries, Bianchi identities, integration by
parts, Grassmann relations, and four-dimensional antisymmetrization remain
open gates.

## Claim boundary

Both `H04` parity slices have terminal resolution for every coarse top-form
signature.  Even there, `TOP_FORM_BASIS_EXHAUSTIVE` remains `IN_PROGRESS`
until the canonical forward span is compared with reverse signature coverage.
All lower-form cocycle and boundary bases remain `NOT_COMPUTED`, so
`TOTAL_COMPLEX_EXHAUSTIVE` is also `NOT_COMPUTED`.  The report cannot produce
a `COMPLETE_NONTRIVIALITY_WITNESS`.

Machine receipt:
`quantum-weyl/local_bv/certificates/BASIS_GAP_REPORT_AFN0.json`.

## Next computation

Canonicalize the pending raw contraction graphs under factor permutations,
dummy-index renaming, curvature symmetries, Bianchi identities, Grassmann
relations, integration by parts, and dimension-specific antisymmetrization.
Then repeat the same forward/reverse coverage comparison in every lower-form
bidegree entering the total descent complex.

## Verification receipt

| Rail | Result |
|---|---:|
| focused grading, tensor-graph, gap, AFN0, and consumer tests | 15 pass in 1.28 s |
| complete local-BV suite | 169 pass in 25.51 s |
| generic result schemas | 6 pass in 0.001 s |
| classical-import boundary | 16 pass in 0.315 s |
| three affected certificate builders under hash seeds `1,7,123` | identical in about 10 s |
| changed Python compile rail and scoped `git diff --check` | pass |

The complete classical certificate pipeline was not rerun because no
classical datum, freeze state, or lifecycle theorem changed.  The full
affected local-BV suite and classical-import boundary were run because the
shared grading manifest changed.
