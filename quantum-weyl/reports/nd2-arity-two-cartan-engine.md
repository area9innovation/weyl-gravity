# ND2 exact arity-two Cartan consumer and obstruction engine

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `ENGINE_READY_AWAITING_SUPPORT_LOCAL_CLASSICAL_EXPORT`

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

The quantum-side ND2 consumer rail is ready before the classical support-local
payload arrives.  It parses a versioned canonical local-expression AST,
combines duplicate exact rational terms, enforces component and global jet
bounds, and refuses unknown expression semantics.  The registered executable
evaluator is intentionally limited to scalar-identity fixtures; it does not
guess the meaning of a future conformal-gravity expression language.

The algebra engine constructs the complete exact complex of homogeneous
graded-symmetric bilinear maps and evaluates the distinct tensors

```text
E_D^(2) = [L_D,q2],
A_D^(2) = [q2,iota_D] - L_D^(2).
```

It checks `q1^2=0`, `[q1,q2]=0`, the linear Cartan identity, the `D`
derivation condition, closure of the Cartan source, and the sourced
graded-Jacobi identity

```text
[q1,A_D^(2)] = [L_D,q2] - [q1,L_D^(2)].
```

For a closed source it solves

```text
[q1,iota_D^(2)] = -A_D^(2)
```

over exact rationals.  If no allowed primitive exists, it retains a normalized
dual functional that annihilates every boundary and evaluates to one on the
source.  Linear admissibility constraints are solved as a differential-stable
subcomplex, so a primitive that exists in the ambient space can still yield a
certified obstruction in the allowed space.

The machine certificate exercises four independent branches: a nonzero exact
correction, a deliberately non-equivariant `D` mutation rejected before the
solve, a closed nonboundary with normalized dual witness, and an ambient
primitive excluded by admissibility.

The solver now also admits an exact block decomposition by any declared
additive basis labels preserved by `q1`.  The fixture uses `D` weight and
verifies that block-sparse rational elimination returns the same source and
correction identity as the ambient solve.  A nonconserved label ledger is
rejected before elimination.

Physical executions are no longer coupled to this permanent fixture
certificate.  `ND2_PHYSICAL_RUN.json` defines a separate manifest contract
that pins the support-local tensor, classical contraction, admissibility
policy, expression evaluator, and assembly adapter.  Evaluator implementation
files are content-addressed and rechecked at dispatch.

## Claim boundary

These are engine fixtures, not conformal-gravity coefficients.  The current
classical snapshot still marks the support-local `q2`, local `D` action, and
`iota_cl/pi_cl/s_cl` as `NOT_AVAILABLE`.  The exact retained Berger `q1` now
has a content-addressed, validation-only PBW backend, but it supports arity one
over `Q[alpha_B,u,v] tensor U(e_Berger)`.  It is not a physical expression
evaluator for the finite `Fraction`-valued Cartan engine, and authorizes no
assembly.  Accordingly this result does not compute the conformal-gravity
Cartan source, construct a physical `iota_D^(2)`, or decide cyclic, real,
boundary, or causal admissibility.

It also does not address `q3`, higher transferred brackets, quantum
corrections, or any `LORENTZIAN-CAUSAL` theorem.  A quantum correction remains
downstream of a separate `QME_RESTORED` certificate.

## Next exact gate

The complete 34-row minimal contraction is now an independently verified ND2
prerequisite.  Extend the PBW backend through `q2/D` and either equip ND2 with
the declared PBW-module coefficient domain or import an exact `REDUCED-MODE`
specialization.  Then import the admissibility policy, register the assembly
adapter, recompute the physical identities, and retain either the admissible
`iota_D^(2)` primitive or its normalized obstruction witness.

## Machine receipt

`quantum-weyl/transfer/certificates/ND2_ARITY_TWO_CARTAN_ENGINE.json`

`quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json`

`quantum-weyl/transfer/certificates/BERGER_PBW_OPERATOR_BACKEND.json`

`quantum-weyl/transfer/certificates/BERGER_MINIMAL_34_CONTRACTION_IMPORT.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 -m unittest discover -s quantum-weyl/classical_import/tests -v` | 0.39 | PASS (28 tests) | 1 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -q` | 57.99 | PASS (85 tests after physical-run, sparse, and arity-three hardening) | 2 |
| ND2, ND1, support-local contract, nonlinear aggregate, ND3, and snapshot certificate checks | 6.01 | PASS | 2 |
| Python compile, JSON/YAML parsing, and scoped `git diff --check` | recorded at commit | PASS | 0 |
| Berger PBW backend, ND2, and aggregate focused tests | 11.41 | PASS (14 tests) | 2 |
| Extended ND2 schema under strict AJV Draft-2020-12 | 1.27 | PASS | 0 |
| Backend-era complete transfer suite | 69.45 | FAIL (119 tests pass; pre-existing ND1 reproduction receipt is stale) | 2 |
| Portable contraction, ND2, and aggregate focused tests | 27.93 | PASS (15 tests) | 2 |
| Contraction and extended ND2 schemas under strict AJV Draft-2020-12 | 4.44 | PASS (2 receipts) | 0 |
| Final complete transfer suite after ND1 provenance refresh | 109.19 | PASS (125 tests) | 2 |

The current AJV run validates the extended ND2 receipt.  The complete-suite
failure is not counted as a pass: an unrelated ND1 reproduction receipt has
two hash-only differences after its live classical-status dependency moved.
All other transfer tests, including the seven ND1 semantic and mutation tests,
pass.

After the classical portable-contraction commit stabilized, the ND1
provenance receipt was refreshed with an unchanged analysis payload.  The
final complete transfer suite now passes cleanly.

Tier 3 was not run.  ND2 adds an exact fixture engine and consumer contract,
but changes no imported classical mathematical input, shared core algebra,
lifecycle promotion, paper theorem, or Lorentzian claim.
