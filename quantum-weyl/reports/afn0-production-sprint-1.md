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
- `H14_AFN0_EVEN`;
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
one is likewise incomplete.  The even anomaly closure slice now includes
`omega E4` with its completed intrinsic tower.  Its quotient result remains
truncated because the lower-form production and boundary bases are not yet
exhaustive.

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

The current candidate, intrinsic Euler, and explicit exact-boundary
lower-form carriers are now assembled and content-addressed: 64 carriers in
all, 55 below top form degree. The ambient integer solver separately produces
2,480 coarse signatures and 720 refined signatures across total degrees three
through six. The refined set is now realized as 1,224 exact derivative-factor
profiles representing 2,860,932,903 raw graphs without materializing them.
Construct the signed factor actions and quotient these factored graphs, then
assemble exact `Q` and `d_h` matrices and only then solve the full
boundary-membership problem.

Machine receipt:
`quantum-weyl/local_bv/certificates/AFN0_LOWER_FORM_CARRIER_PRECERTIFICATE.json`.

Ambient grading receipt:
`quantum-weyl/local_bv/certificates/AFN0_AMBIENT_LOWER_FORM_SIGNATURE_CERTIFICATE.json`.

Ambient tensor-graph receipt:
`quantum-weyl/local_bv/certificates/AFN0_AMBIENT_TENSOR_GRAPH_REALIZATION_CERTIFICATE.json`.

### Lower-form production receipt

| Rail | Result |
|---|---:|
| lower-form, ambient-signature, basis-gap, and AFN0 consumers | 20 pass in 12.92 s |
| complete local-BV suite | 199 pass, 125 subtests in 54.07 s |
| standalone carrier/signature reproduction checks | pass in under 1 s each |
| changed Python compile, strict schemas, and scoped diff check | pass |

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

### Completed-Euler slice integration

The historical `H14_AFN0_EVEN_WITHOUT_EULER` slice has been replaced by
`H14_AFN0_EVEN`.  Its closure receipt now contains `omega C2`, `omega E4`,
and `omega Box R`; the Euler row points to the completed intrinsic Euler
certificate.  In the truncated quotient, `omega E4` remains `UNDECIDED`,
`omega Box R` remains `EXACT`, and no nonmembership witness is promoted.
Every closure row now binds the bytes and result IDs of its horizontal and
intrinsic certificates and the bytes plus canonical hash of the descent
database.  Emission fails unless those artifacts agree on Diff descent,
intrinsic Weyl descent, and relative status.
Reverse signature coverage records `omega C2` and `omega E4` as two generated
candidates with the same quadratic-curvature signature, without inflating the
number of realizable signatures.

| Rail | Result |
|---|---:|
| AFN0, basis-gap, tensor-graph, and exhaustiveness consumers | 16 pass in 13.11 s |
| complete local-BV suite | 189 pass, 125 subtests in 54.20 s |
| Cartan consumers excluding the intentionally commit-pinned dossier contribution | 28 pass in 0.17 s |
| basis-gap, AFN0, and Cartan artifact reproduction checks | pass |
| AFN0, basis-gap, Cartan-import, certificate, and contribution consumers under hash seeds `1,7,123`, parallel | 29 pass per seed in under 15 s wall |

The Cartan contribution was repinned only after the updated certificate had a
commit hash; its blocked lifecycle and null verdict are unchanged.

### Closure-witness hardening

| Rail | Result |
|---|---:|
| hash-bound AFN0 plus Cartan import/certificate consumers | 20 pass in 14.02 s |
| independent Euler convention and certificate consumers | 12 pass in 24.55 s |
| complete local-BV suite | 189 pass, 125 subtests in 54.20 s |
| all affected certificate reproduction checks | pass |

The dossier contribution remains intentionally pinned to the preceding
certificate commit until this strengthened certificate chain is committed.
