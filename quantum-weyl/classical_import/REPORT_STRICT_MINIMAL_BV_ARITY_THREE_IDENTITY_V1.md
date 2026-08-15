# Strict minimal-BV arity-three identity v1

**Result:** `STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1`

**State:** `MINIMAL_ARITY_THREE_IDENTITY_CERTIFIED_Q3_CYCLICITY_AND_386_STABILIZATION_OPEN`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The complete arity-three coefficient of the authoritative minimal-BV
identity `Q^2=0` is now certified on arbitrary inputs:

```text
q1 q3 + q3 q1 + sum_(2,1)-unshuffles q2(q2,.) = 0.
```

The typed receiver found **72 nonempty channels**
and **212 composable paths**:
`2` q1-q3,
`204` q2-q2, and
`6` q3-q1 paths.  All six output rows,
all four q1 components that can compose with q3, all 22 ordered q2
components, and every compatible position of the unique q3 component are
covered.  The fifth unary component, `q1_hstar_h`, is type-incompatible with
the only q3 input and output and therefore creates no arity-three path.

## Why the statement is general

The imported q1, q2 and q3 are the first three Taylor coefficients of the
same authoritative natural BV vector field.  Differentiating its certified
nilpotency identity three times gives exactly the enumerated unshuffle
formula.  This is the arbitrary-input proof.

The independent rational five-jet receiver evaluates every channel on a
derivative-sensitive Minkowski fixture.  All 72 defects vanish.  Three
separate multiplier mutations in q1-q3, q3-q1 and q2-q2 paths produce
nonzero defects.  These finite calculations are implementation regressions,
not a replacement for the natural Taylor theorem.

| Natural identity family | Channels | Role |
|---|---:|---|
| `GAUGE_ALGEBRA_AND_REPRESENTATION` | 64 | q2-q2-only Jacobi, semidirect-action and cotangent-lift identities |
| `DIFF_COVARIANCE_OF_BACH_EULER` | 3 | c,h,h permutations in the h_star row |
| `WEYL_COVARIANCE_OF_BACH_EULER` | 3 | omega,h,h permutations in the h_star row |
| `THIRD_DIFF_NOETHER_IDENTITY` | 1 | h,h,h to c_star |
| `THIRD_WEYL_TRACE_IDENTITY` | 1 | h,h,h to omega_star |

## Gate ledger

| Gate | Status |
|---|---|
| `AUTHORITATIVE_MINIMAL_Q3_IMPORT` | `PASS` |
| `MINIMAL_ARITY_THREE_Q_SQUARED` | `PASS` |
| `MINIMAL_Q3_CYCLICITY` | `OPEN` |
| `STRICT_386_CYCLIC_STABILIZATION` | `OPEN` |
| `GENERAL_LAMBDA2_SOURCE_CLOSURE_ON_386` | `OPEN` |

This result does **not** promote the 386-row candidate.  Quartic q3 cyclicity
and an explicit cyclic stabilization map remain separate gates.
Only after both are accepted can the general lambda-squared source be
replayed on the causal graph carrier.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_minimal_bv_arity_three_identity.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_arity_three_identity.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_arity_three_identity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_arity_three_identity.py -v
```

## Does not establish

- quartic cyclicity of q3 under the canonical receiver pairing and suspension signs.
- a source-certified cyclic stabilization or L-infinity morphism from the six-row minimal carrier to all 386 graph rows.
- the complete 386-row arity-three identity or general lambda-squared source closure on that carrier.
- compatibility or estimates for q3 under a retarded or advanced Green homotopy.
- an analytic Moller map or all-order nonlinear fixed point.
- a Hadamard state, renormalized Lorentzian time-ordered products, QME restoration, residual transfer, or a Lorentzian quantum theory.
