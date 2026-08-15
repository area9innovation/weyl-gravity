# Strict pure-Weyl minimal-BV q3 import v1

**Result:** `STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1`

**State:** `ARBITRARY_INPUT_MINIMAL_BV_Q3_IMPORTED_ARITY_THREE_AND_386_STABILIZATION_OPEN`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The arbitrary-input cubic bracket is now imported from the authoritative classical minimal master action rather than inferred from the single diagonal
witness.  On the six-generator carrier its complete support is

```text
q3(h1,h2,h3) -> h_star = D^3[-2 sqrt(abs(g)) B(g)^sharp](h1,h2,h3),
all other q3 output rows = 0.
```

The independent receiver evaluates the classical AST over the exact
square-free algebra `Q[a,b,c]/(a^2,b^2,c^2)`.  The `[a*b*c]` coefficient is
the polarized third Frechet derivative directly, with no numerical finite
difference and no hidden factorial.

## Exact checks

| Background | Input seeds | Nonzero outputs | Digest |
|---|---:|---:|---|
| `conformal_cylinder` | 1, 2, 3 | 10 | `2570776c56ff789d...` |
| `minkowski` | 2, 3, 4 | 10 | `edf47a11248bc201...` |
| `flat_brinkmann` | 3, 4, 5 | 10 | `37226366f5c029bd...` |

All six input permutations agree.  A separate seven-diagonal polarization
using the earlier one-parameter cubic evaluator agrees exactly.  The pinned
pure-diffeomorphism witness reproduces all 41 stored terms and its
`q1(q3)_omega_star=-75760/9` value.  Three pp-wave profile directions give
zero, and a signed coordinate permutation transforms the output as a
contravariant absolute weight-one density.

The general coordinate claim comes from composition of natural operations
and three formal derivatives; the finite coordinate fixtures are
implementation regressions, not the proof of general naturality.

## Gate ledger

| Gate | Status | Evidence or remaining work |
|---|---|---|
| `AUTHORITATIVE_MINIMAL_Q3_IMPORT` | `PASS` | all six source rows imported without carrier or convention change |
| `ARBITRARY_INPUT_COMPONENT_EXECUTION` | `PASS` | exact trivariate receiver, three backgrounds, S3, polarization, covariance, pp-wave and pinned witness checks |
| `MINIMAL_ARITY_THREE_Q_SQUARED` | `OPEN` | the complete q1 q3 plus q2 q2 plus q3 q1 channel replay is the next independent gate |
| `MINIMAL_Q3_CYCLICITY` | `OPEN` | quartic BV vertex cyclicity has not yet been replayed in receiver signs |
| `STRICT_386_CYCLIC_STABILIZATION` | `OPEN` | no content-addressed extension or L-infinity morphism to all 386 rows is yet accepted |

The import does **not** yet claim the arity-three identity merely because the
parent full vector field is nilpotent.  The next rail must enumerate and
independently replay every typed `q1 q3 + q2 q2 + q3 q1` channel.  Quartic
cyclicity and the 386-row stabilization are separate open gates.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_pure_weyl_minimal_bv_q3_import.py --check
python3 quantum-weyl/classical_import/check_strict_pure_weyl_minimal_bv_q3_import.py
python3 quantum-weyl/classical_import/verify_strict_pure_weyl_minimal_bv_q3_import.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_pure_weyl_minimal_bv_q3_import.py -v
```

## Does not establish

- the complete minimal-BV arity-three nilpotency identity on all typed input channels.
- quartic cyclicity of q3 under the receiver BV pairing and suspension signs.
- a source-certified cyclic stabilization or L-infinity morphism to the 386-row carrier.
- all-order nonlinear source closure or an analytic Moller map.
- compatibility estimates between q3 and any causal Green homotopy.
- a Hadamard state, renormalized Lorentzian time-ordered products, QME restoration, residual transfer, or a Lorentzian quantum theory.
