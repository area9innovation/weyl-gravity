# Compensated nonzero-characteristic snapshot receipt

Date: 2026-07-15

## Established

The 32-dimensional compensated flat minimal BV complex is now exported as
actual canonical sparse matrices over
`Q(c1,alpha,v,v^-1)[p0,p1,p2,p3]`.  The export contains the metric operator,
field transformation, original and invariant Hessians, Gram matrices, gauge
and Noether maps, full differential and pairing, Weyl-doublet contraction,
and reduced operators.

A separate verifier imports neither the operator constructor nor the exporter.
It parses the JSON entries with a closed symbol inventory and independently
checks their canonical hashes, provenance, blocks, nilpotency, formal
cyclicity, chain maps, contraction identities, and pairing nondegeneracy.

The exact characteristic snapshot consumes only that verified export.  At the
declared rational specialization it establishes:

| Fiber | `(rank R, rank H, rank N, rank q)` | `(H^-1,H^0,H^1,H^2)` |
|---|---:|---:|
| generic `p=(2,1,0,0)` | `(5,6,5,16)` | `(0,0,0,0)` |
| null `p=(1,0,0,1)` | `(5,4,5,14)` | `(0,2,2,0)` |
| second root `p=(0,1,0,0)` | `(5,1,5,11)` | `(0,5,5,0)` |
| zero `p=0` | `(1,0,1,2)` | `(4,10,10,4)` |

Each promoted nonzero fiber carries exact sparse inclusions, `pi_cl`
projections, and homotopies.  The induced odd BV pairing is correctly formed
between the `p` and `-p` cohomologies; it has ranks four and ten on the null
and second-root branches respectively.

Verdict:

```text
NONZERO_NULL_2_PLUS_SECOND_ROOT_5_SYMBOL_COHOMOLOGY_WITH_EXACT_CONTRACTIONS
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Interpretation and fail-closed boundary

For a null wave along the `z` direction, the two degree-zero representatives
are equivalent to the real transverse polarizations `h_12` and
`h_22-h_11`.  They are the local symbol precursors of helicity `+/-2` before
the compact residual quotient.  This does not conflict with vanishing
absolute one-particle residual cohomology on the closed cylinder, which is an
additional global residual reduction.

The odd BV pairing is neither a norm nor the physical Cauchy/radiative
symplectic form.  The existing flat TT causal certificate, not this snapshot,
controls the Einstein-Hilbert current and positive-energy helicity phase
space.

The second root contains five extra field classes.  Its representative has
`p_squared=-1` in signature `(+---)` and is only an algebraic characteristic
fixture; no positive-energy particle interpretation is asserted.

The zero fiber is recorded but not promoted.  Global Killing, reducibility,
compact-cylinder, boundary, and physical-state questions depend on the
function space.  Consequently `classical_import_freeze_complete` remains
false.  Covariant characteristic bundles, matter/defect chain maps,
nonminimal gauge fixing, causal Green data, scattering, and quantum claims
also remain open.

## Provenance

Input base commit: `25364fb760ed869f193983eb179ad3b120b52557`.

| Artifact | SHA-256 |
|---|---|
| `compensated_minimal_bv_operator_export.py` | `04d36cdcdb084ae9cf4913651d0d17f2caeb4f92c9db2df8fcfc6a9dfb3ae7b2` |
| `verify_compensated_minimal_bv_operator_export.py` | `4db717c4e9b1cc48d8e723444488847d68e04064d56a557daf551575746f18a2` |
| operator-export schema | `6f13148aafdac6236cf36b074f10758d20923cbb5f6790f7758b351e141f6d6a` |
| operator export | `27f91fb2a2faad75fde497a7fec68ef1e4ec83a92e75d4f2088cca0d69ef3a9d` |
| `compensated_nonzero_characteristic_snapshot.py` | `db58143e7f31587c90fedffb21c8136df22091c229492c00bf4fd552eac2e653` |
| characteristic schema | `2a83b16f27687f5d4ce015c8396dea594dcfdd8eae822278a9f769548cd8ddfa` |
| characteristic certificate | `a690622d5cdd2cb5889aea15b9ca8280b91b345b31bd4a43748fb5e1089fd3dd` |
| operator-export tests | `6e08c11a52b070116a689b8d72e88e0aedae9bbc94446847329fa2825f0365d0` |
| characteristic tests | `12bc7294cdc5f0dc1b786f13f5b87d368054f13cb1104f7f772458f3be84f368` |
| theorem note | `3434cf7778b8970b4116ebf778b73dfec9f80535286d975355c2eb29e63bd30f` |
| imported minimal BV certificate | `bb4cfb76211cb4de913f1df2a405c67a7b0b43ccc7122ee3fe151c490296e002` |
| updated Einstein-sector aggregator | `f77fca9669c6d4e16fdc00818f24e8c7aa1707babacb1c6b55db5efa9ed8fe3e` |
| updated Einstein-sector theorem certificate | `926d566e8a223b278cc89b61ea89fbc02128cf2619fc9ab0cc8deedb8ad4443f` |
| updated aggregator tests | `11d8f2366dbb97d74e6b3c1ceb9e030b978eceda405536bd749a64a1a2cb2ee2` |
| refreshed asymptotically-flat bootstrap certificate | `3fbdc0137e292dc56d799b77251ebf6cc11a36103840b309ca6a0166a53b20e3` |
| refreshed D-quotient asymptotic seed | `4ac34cb9bc6b755c48def9553ed82c0e3be3a05853e89656d252c71cc6b73099` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on three generators/verifiers and two tests | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on both schemas and certificates | under 0.1 s | PASS |
| 0 | `git diff --check` on the working diff | under 0.1 s | PASS |
| 1 | exporter verification followed by independent consumer verification | 31 s | PASS |
| 1 | characteristic snapshot verifier | 11 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 45.15 s | PASS (108 tests) |
| 2 | upstream compensated minimal BV verifier | 22 s | PASS |
| 2 | compensator phase and sourced-defect preflight verifiers | 6 s | PASS |
| 2 | Einstein-sector theorem aggregator verifier and unit tests | under 0.1 s | PASS (5 tests) |
| 2 | regenerated asymptotically-flat bootstrap and D-quotient seed plus scoped tests | 2.6 s | PASS (17 tests) |
| 2 | Berger background and charge-seed tests | 0.78 s | PASS (9 tests) |
| coordination | `python3 d_quotient_classical/verify_classical_status.py --guards` | under 0.1 s | PASS (12/12 guards) |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.04 s | PASS (14/14 guards) |

Tier 3 was not run because the result state explicitly remains
`SCOPED_EXACT_SNAPSHOT_CERTIFIED_GLOBAL_CLASSICAL_FREEZE_OPEN`: it does not
promote a classical freeze/tag, shared core algebra, causal theorem, quantum
lifecycle state, or release.

Unrelated shared-tree edits in the D-quotient programme, paper, and quantum
packages were present during verification and were not included in this work.
