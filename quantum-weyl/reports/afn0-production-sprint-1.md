# Antifield-zero production run: Sprint 1

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Scope label: `AFN0_ONLY`

Result state: `IN_PROGRESS`

## Outcome

The four requested Sprint 1 slices now execute in two explicitly separate
modes and emit deterministic receipts:

- `H04_AFN0_EVEN`;
- `H04_AFN0_ODD`;
- `H14_AFN0_EVEN_WITHOUT_EULER`;
- `H14_AFN0_ODD`.

Each slice contains a named `CLOSURE_RESULT` and a separately named
`TRUNCATED_QUOTIENT_RESULT`; all eight are also emitted as independently
schema-validated result files.  They reuse the exhaustive top-level
quadratic-curvature carrier generator.
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
one is likewise incomplete.  The even anomaly slice still excludes
`omega E4`: its frozen-carrier connecting equations now close, but the
epsilon-contracted head and complete lower-form production basis have not yet
passed their independent gates.

Consequently the run emits no nontriviality claim and no dual witness for a
physical representative.  The only permitted provisional witness label is
`TRUNCATED_NONMEMBERSHIP_WITNESS`.  The generic exact engine constructs a dual
functional `lambda` satisfying

```text
lambda(boundary) = 0
lambda(representative) = 1
```

and promotes its label to `COMPLETE_NONTRIVIALITY_WITNESS` only after the
complete boundary space and an exhaustiveness proof are frozen.

An independent multigrading enumerator now preserves the coarse equation

```text
2*n_curvature + n_tensor_derivative + n_ghost_derivative
  + ghost_engineering_offset = 4
```

and then applies tensor-seed, scalar-index, and epsilon-availability
constraints.  The top-form Weyl counts refine from `3` to `2` at ghost number
zero and from `9` to `5` at ghost number one.  A separate Diff top-form ledger
refines from `12` to `7` signatures per parity sector.  The earlier combined
count `21=9+12` remains stored for provenance, but is no longer presented as
the top Weyl-anomaly count.  Generalized-connection degree is tracked as a
separate pending expansion gate.  Raw index-contraction graphs and their
hashes are now emitted for every refined row; their canonical quotient is
still pending.

## Machine receipts

- `quantum-weyl/local_bv/cohomology/H04_AFN0_RESULT.json`;
- `quantum-weyl/local_bv/cohomology/H14_AFN0_RESULT.json`;
- `quantum-weyl/local_bv/cohomology/slices/*.json` (eight mode-specific receipts);
- `quantum-weyl/local_bv/certificates/AFN0_PRODUCTION_RUN_CERTIFICATE.json`;
- `quantum-weyl/local_bv/certificates/BASIS_GAP_REPORT_AFN0.json`;
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
| focused tensor-graph, basis-gap, and AFN0 consumer tests | 12 pass in 5.52 s |
| complete local-BV suite | 171 pass in 33.34 s |
| generic result schemas | 6 pass in 0.001 s |
| classical-import regression | 16 pass in 0.313 s |
| affected certificate builders under hash seeds `1,7,123` | identical |
| changed Python compile rail | pass |

The full classical certificate pipeline was not rerun: no classical input,
freeze state, or published theorem changed.  The complete affected local-BV
suite and the classical-import boundary regression were run because the
relative quotient and filtration interfaces are shared within that package.
