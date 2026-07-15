# Nonlinear waiting-time hardening: physical-run contract through arity three

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

Four payload-independent improvements are now executable while the classical
team investigates physical clocks.

First, the permanent ND2 fixture engine is separated from a physical-run
receipt.  The versioned physical manifest pins exactly three artifacts: the
support-local `q1/q2/D` export, the classical contraction, and the
admissibility policy.  A run additionally names the expression evaluator and
contraction assembly adapter.  Missing artifacts, hash drift, unknown
evaluators, expression-schema mismatches, changed evaluator implementations,
and unregistered adapters stop before a physical classification.

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

## Claim boundary

No fixture carries a conformal-gravity interaction coefficient.  No physical
expression evaluator, contraction assembly adapter, support-local `q2`, `q3`,
or physical `iota_D^(2)` is available.  Consequently these changes do not
establish an interacting Cartan homotopy, dynamical/topological closure,
quartic stability, a relational-clock result, a quantum correction, or a
`LORENTZIAN-CAUSAL` theorem.

## Machine receipts

- `quantum-weyl/transfer/certificates/ND2_ARITY_TWO_CARTAN_ENGINE.json`
- `quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json`
- `quantum-weyl/transfer/certificates/ND3_ARITY_THREE_CARTAN_ENGINE.json`

## Next gate

When the classical payload arrives, verify the physical manifest, dispatch its
pinned evaluator and assembly adapter, classify the arity-two source, and only
then feed the retained physical `iota_D^(2)` together with `q3` into the
arity-three recurrence.

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Python compile, JSON parsing, and workflow YAML parsing | 0.30 | PASS | 0 |
| ND1, ND2 engine, ND2 physical-run, ND3, nonlinear aggregate, support-local contract, and snapshot checks | 6.01 | PASS | 2 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -q` | 57.99 | PASS (85 tests) | 2 |
| `python3 -m unittest discover -s quantum-weyl/classical_import/tests -q` | 0.36 | PASS (28 tests) | 1 |
| Scoped `git diff --check` and staged-diff inspection | recorded at commit | PASS | 0 |

An initial full-suite run exposed an import-order dependency in two new test
modules and failed.  The modules were made independently importable, their
certificates were regenerated, and the complete 85-test suite above then
passed.  The failed run is not counted as a pass.

Tier 3 was not run.  These changes add fixture engines, execution contracts,
and exact solver infrastructure; they change no imported classical
mathematical input, shared classical operator, lifecycle promotion, paper
theorem, or Lorentzian claim.
