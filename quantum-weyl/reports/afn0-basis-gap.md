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

| Slice | Coarse | Refined | Raw contraction | Realizable by generated representative | Known nonzero | Pending |
|---|---:|---:|---:|---:|---:|---:|
| `H04_AFN0_EVEN` | 3 | 2 | 2 | 2 | 2 | 0 |
| `H04_AFN0_ODD` | 3 | 2 | 2 | 1 | 1 | 0 |
| `H14_AFN0_EVEN` | 9 | 5 | 5 | 2 | 2 | 2 |
| `H14_AFN0_ODD` | 9 | 5 | 5 | 1 | 1 | 3 |

The eliminated signatures attempted to apply covariant tensor derivatives
without any curvature or other tensor seed.  Since the Levi-Civita
connection is metric-compatible, `nabla g = 0`; these rows terminate as
`WRONG_AFTER_REFINED_GRADING` with reproducible proof hashes.

Two further single-factor families terminate as `TOTAL_DERIVATIVE_ONLY`:
the fourth-derivative Weyl-ghost signature and the odd single-curvature
two-derivative signature.  The derivative ordering is now explicit, with
position zero declared outermost.  For every raw graph the machine stores a
current that replaces that derivative slot by the current's free index and
then verifies that covariant divergence reconstructs the original graph.
The witness count must equal the raw graph count.  Metric and epsilon
covariant constancy are stored inputs.  The mixed curvature/ghost-derivative
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

Each slot now stores factor ownership, index variance, derivative attachment,
and derivative order.  Metric edges distinguish inverse metrics, metrics, and
Kronecker contractions.  Signed Riemann pair antisymmetries, pair exchange,
epsilon reordering, and factor permutation where derivative attachment does
not obstruct it are applied to form symmetry-canonical graph orbits.  An
independent double-factorial/binomial count must agree with the forward raw
enumeration.

Raw contraction is no longer called tensor realizability.  Without an
already generated representative, its status is
`UNDECIDED_PENDING_BIANCHI_AND_DIMENSION_IDENTITIES`.  Algebraic and
differential Bianchi quotients, derivative-distribution factor permutations,
Grassmann relations, integration by parts beyond the certified single-factor
rule, and four-dimensional antisymmetrization remain open gates.

Full slot, orbit, and current payloads are stored separately in the
content-addressed bundle under
`quantum-weyl/local_bv/certificates/basis_graph_manifests/`; the main gap
certificate retains its path and hash.

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
| focused tensor-graph, gap, and AFN0 consumer tests | 12 pass in 5.52 s |
| complete local-BV suite | 171 pass in 33.34 s |
| generic result schemas | 6 pass in 0.001 s |
| classical-import boundary | 16 pass in 0.313 s |
| affected certificate builders under hash seeds `1,7,123` | identical |
| changed Python compile rail and scoped `git diff --check` | pass |

The complete classical certificate pipeline was not rerun because no
classical datum, freeze state, or lifecycle theorem changed.  The full
affected local-BV suite and classical-import boundary were run because the
shared grading manifest changed.
