# AFN0 ambient tensor-graph realization

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`AMBIENT_TENSOR_GRAPH_REALIZATION_COMPLETE_QUOTIENT_OPEN`.

The 720 refined integer signatures now have a complete factored tensor-slot
realization.  Distributing the declared derivatives among indistinguishable
curvature, Weyl-ghost, and Diff-ghost factors gives 1,224 derivative profiles.
Every profile reproduces the signature's index count and admits an exact
epsilon/metric contraction graph.

Materializing all raw graphs would be counterproductive.  The exact count is

```text
2,860,932,903
```

and one parity-odd dimension-six signature already contains 413,513,100 raw
graphs.  The certificate therefore stores factor inventories, derivative
distributions, identical-factor groups, exact matching formulas, and hashes.
It labels 167 signatures `FACTORED_COUNT_ONLY`; it does not claim those graphs
were individually generated.

The realization closes the index-balance and derivative-distribution layer.
The following quotients remain open:

- signed factor-permutation and Grassmann actions;
- algebraic and differential Bianchi identities;
- covariant-jet commutator relations;
- integration by parts;
- four-dimensional antisymmetrization.

Consequently, this result does not give a canonical basis dimension or promote
any truncated dual witness to complete cohomological nontriviality.  Its next
use is orbit-first reduction of the 1,224 profiles, without expanding the
billions of raw pairings.
