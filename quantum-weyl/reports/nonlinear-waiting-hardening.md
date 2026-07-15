# Nonlinear waiting-time hardening: physical-run contract through arity three

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

Five payload-independent improvements are now executable, and the first
healthy-clock candidate is imported without crossing its claim boundary.

First, the permanent ND2 fixture engine is separated from a physical-run
receipt.  The versioned physical manifest pins exactly four artifacts: the
total-`D` disposition certificate, support-local `q1/q2/D` export, classical
contraction, and admissibility policy.  A run additionally names the
expression evaluator and contraction assembly adapter.  Missing artifacts, hash drift, unknown
evaluators, expression-schema mismatches, changed evaluator implementations,
and unregistered adapters stop before a physical classification.

The disposition certificate is a semantic gate, not just another hash.  Its
setting, phase space, generator, boundary conditions, classical commit,
dependency tags, and source hashes must agree with the manifest.  Only
`D_GAUGE` dispatches the assembly adapter and Cartan solver.  `OPEN`, canonical
`D_CHARGED`, `SECTOR_DEPENDENT`, and `NOT_HAMILTONIAN` return distinct
receipts without contracting `D`.  Execution requires an opaque verified-
manifest token.

Second, evaluator dispatch is content-addressed.  Each evaluator declares its
accepted expression schema, allowed local operators, complete implementation
manifest, and canonical manifest hash.  The only registered implementation is
the scalar-identity fixture evaluator; this remains deliberately incapable of
interpreting a physical conformal-gravity expression.

Third, the exact arity-two solve can be decomposed by conserved additive
labels.  If `q1` preserves labels such as `D` weight, momentum, representation
charge, or jet filtration, the bilinear-map differential preserves

```text
label(output) - label(left input) - label(right input).
```

Sparse rational elimination is performed only in occupied blocks.  The
fixture reproduces the ambient correction exactly, retains the same normalized
obstruction witness, and rejects a label ledger not conserved by `q1`.

Fourth, the Cartan recurrence now extends through arity three:

```text
[q1,iota_D^(3)] = -[q3,iota_D] - [q2,iota_D^(2)] + L_D^(3).
```

The engine checks the arity-two and arity-three `Q^2=0` identities, the Cartan
identities through arity two, `D` equivariance through arity three, and closure
of the arity-three source.  Direct `q3` and exchange `[q2,iota_D^(2)]`
contributions are retained as distinct tensors.  Nonzero fixtures establish
the exact-correction, normalized-obstruction, exchange, and broken-`D`
rejection branches.

Fifth, the exact positive Berger background, reduced O(2) clock momentum, and
fixed-coupling tangent theorem are imported content-addressedly from the
classical and programme ledgers.  The exact lapse row and compact averaging
give `delta Q_R=0` for every allowed smooth tangent, so the scoped disposition
is `D_GAUGE`.  The subsequently registered minimal theorem contracts exactly
8 of 34 clock-sector rows.  That evidence is imported without using it as the
complete physical contraction: portable entries, the retained/nonminimal
maps, and `D`-equivariance remain absent.

## Claim boundary

No fixture carries a conformal-gravity interaction coefficient.  The Berger
import is `LOCAL-ALGEBRAIC` plus `REDUCED-MODE`; it is not a
`LORENTZIAN-CAUSAL` result.  No physical
expression evaluator, contraction assembly adapter, support-local `q2`, `q3`,
or physical `iota_D^(2)` is available.  Consequently these changes do not
establish an interacting Cartan homotopy, dynamical/topological closure,
quartic stability, a relational-clock result, a quantum correction, or a
`LORENTZIAN-CAUSAL` theorem.

## Machine receipts

- `quantum-weyl/transfer/certificates/ND2_ARITY_TWO_CARTAN_ENGINE.json`
- `quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json`
- `quantum-weyl/transfer/certificates/ND3_ARITY_THREE_CARTAN_ENGINE.json`
- `quantum-weyl/transfer/certificates/BERGER_CLOCK_NONLINEAR_IMPORT.json`
- `quantum-weyl/transfer/certificates/BERGER_TOTAL_D_DISPOSITION.json`
- `quantum-weyl/transfer/certificates/BERGER_CLOCK_PARTIAL_SDR_IMPORT.json`

## Next gate

Complete `FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT` and the separate
`CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT`.  Then verify the remaining physical
manifest, dispatch its pinned evaluator and assembly adapter, classify the
arity-two source, and feed the retained physical `iota_D^(2)` together with
`q3` into the arity-three recurrence.

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Python compile, JSON parsing, and workflow YAML parsing | 0.30 | PASS | 0 |
| ND1, ND2 engine, ND2 physical-run, ND3, nonlinear aggregate, support-local contract, and snapshot checks | 6.01 | PASS | 2 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -q` | 57.99 | PASS (85 tests) | 2 |
| `python3 -m unittest discover -s quantum-weyl/classical_import/tests -q` | 0.36 | PASS (28 tests) | 1 |
| Berger background and charge source checks | 2.00 | PASS (19/19 mutation guards) | 1 |
| Classical and programme status guards | 0.26 | PASS (25/25 mutation guards) | 2 |
| Berger/ND2/aggregate focused tests | 1.58 | PASS (14 tests) | 2 |
| Updated complete transfer suite | 66.03 | PASS (90 tests) | 2 |
| Scoped Berger `D_GAUGE` producer, independent audit, and unit tests | 2.47 | PASS | 2 |
| Hardened total-`D` certificate chain | 5.24 | PASS | 2 |
| Hardened complete transfer suite | 66.69 | PASS (98 tests) | 2 |
| Scoped `git diff --check` and staged-diff inspection | recorded at commit | PASS | 0 |

An initial full-suite run exposed an import-order dependency in two new test
modules and failed.  The modules were made independently importable, their
certificates were regenerated, and the complete 85-test suite above then
passed.  The failed run is not counted as a pass.

Tier 3 was not run.  These changes add fixture engines, execution contracts,
and exact solver infrastructure; they change no imported classical
mathematical input, shared classical operator, lifecycle promotion, paper
theorem, or Lorentzian claim.
