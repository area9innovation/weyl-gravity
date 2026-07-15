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

## Claim boundary

These are engine fixtures, not conformal-gravity coefficients.  The current
classical snapshot still marks the support-local `q2`, local `D` action, and
`iota_cl/pi_cl/s_cl` as `NOT_AVAILABLE`.  No physical expression evaluator is
registered because the authoritative expression schema has not yet arrived.
Accordingly this result does not compute the conformal-gravity Cartan source,
construct a physical `iota_D^(2)`, or decide cyclic, real, boundary, or causal
admissibility.

It also does not address `q3`, higher transferred brackets, quantum
corrections, or any `LORENTZIAN-CAUSAL` theorem.  A quantum correction remains
downstream of a separate `QME_RESTORED` certificate.

## Next exact gate

Import the pinned classical `q1/q2/D` action and contraction, register the
declared exact expression evaluator, recompute the physical identities, and
then retain either the admissible `iota_D^(2)` primitive or its normalized
obstruction witness.

## Machine receipt

`quantum-weyl/transfer/certificates/ND2_ARITY_TWO_CARTAN_ENGINE.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 -m unittest discover -s quantum-weyl/classical_import/tests -v` | 0.39 | PASS (28 tests) | 1 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -q` | 50.25 | PASS (62 tests) | 2 |
| ND2, ND1, support-local contract, nonlinear aggregate, and snapshot certificate checks | 3.80 | PASS after provenance refresh | 2 |
| Python compile, JSON parsing, and scoped `git diff --check` | 4.00 | PASS | 0 |

Draft-2020-12 schema validation was attempted but was **not run** because the
environment does not provide the `jsonschema` module.  It is not counted as a
pass; deterministic JSON parsing did pass.

Tier 3 was not run.  ND2 adds an exact fixture engine and consumer contract,
but changes no imported classical mathematical input, shared core algebra,
lifecycle promotion, paper theorem, or Lorentzian claim.
