# Strict local q1/q2 arity-two identity v1

**Result:** `STRICT_LOCAL_Q1_Q2_IDENTITY_V1`

**State:** `Q1_Q2_ARITY_TWO_IDENTITY_CERTIFIED_D_AND_PAIRING_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The first nonlinear master identity for the strict minimal pure-Weyl BV
complex is now certified in the common portable suspension convention:

```text
[q1,q2](x,y)
  = q1(q2(x,y)) + q2(q1(x),y) + (-1)^|x| q2(x,q1(y))
  = 0.
```

The typed expansion contains **18 channels** and **51 composable paths**. It
uses all five nonzero `q1` components and all twenty-two ordered `q2`
components. No uncomposed row is hidden outside the verdict.

## Four identity families

| Family | Output | Channels | General identity |
|---|---|---:|---|
| `DIFF_X_WEYL_GAUGE_ACTION_CLOSURE` | `h` | 4 | closure of the semidirect Diff action on metrics and Weyl scalars |
| `BACH_EULER_DIFF_X_WEYL_EQUIVARIANCE` | `h_star` | 4 | second Frechet derivative of Diff/Weyl covariance of the natural Bach Euler density |
| `DIFFERENTIATED_DIFF_NOETHER_AND_COTANGENT_COVARIANCE` | `c_star` | 5 | first and second Frechet derivatives of the Diff Noether identity, including cotangent transport |
| `DIFFERENTIATED_WEYL_NOETHER_AND_DENSITY_COVARIANCE` | `omega_star` | 5 | first and second Frechet derivatives of the Weyl trace identity, including density transport |

The general theorem comes from differentiating the natural Diff/Weyl action,
the Bach Euler covariance laws, and the two Noether identities at a Bach-flat
base point. The exact coordinate fixtures below are regression witnesses for
the serialized operator bytes and signs; three examples are not treated as a
proof by induction or extrapolation.

## Exact local receiver

| Bach-flat background | Channels | Paths | All defects zero |
|---|---:|---:|---|
| `conformal_cylinder` | 18 | 51 | `True` |
| `minkowski` | 18 | 51 | `True` |
| `flat_brinkmann` | 18 | 51 | `True` |

Each run uses rational normalized metric five-jets and independently generated
field, ghost, and antifield jets. One sign is then flipped in a representative
channel from each output family; all four mutations produce nonzero exact
defects. The receiver does not use the legacy finite-dimensional Cartan matrix
helper because this calculation must propagate coordinate jets and Leibniz
rules through the natural differential operators.

## Gate ledger

| Check | Status | Evidence or remaining input |
|---|---|---|
| `q1_q2_channel_exhaustion` | `VERIFIED` | 18 typed channels and 51 composable paths use all five q1 and all twenty-two ordered q2 components |
| `q1_q2_arity_two_nilpotency` | `VERIFIED` | all four natural identity families vanish; three exact five-jet background fixtures replay every channel |
| `receiver_mutation_sensitivity` | `VERIFIED` | one sign flip in each of the four output families produces a nonzero exact defect |
| `D_q1_commutator_zero` | `NOT_REPLAYED` | the full local D action is not serialized |
| `D_q2_derivation` | `NOT_REPLAYED` | the full local D action is not serialized |
| `BV_cyclicity_q2` | `NOT_REPLAYED` | the common support-local BV pairing receiver is not serialized |

This closes `q1q2=0`, but it does not complete the downstream export contract.
The next algebraic goal is a common support-local BV pairing and full local
`D` action, followed by `[D,q1]=0`, the `D` derivation identity for `q2`, and
BV cyclicity. Gate A remains fail closed until those independent bytes and
receivers exist.

## Reproduction

```text
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/build_strict_local_q1_q2_identity.py --check
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/check_strict_local_q1_q2_identity.py
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/verify_strict_local_q1_q2_identity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_local_q1_q2_identity.py -v
```

## Does not establish

- a complete local D action, D/q1 commutation, or D/q2 derivation identity.
- BV cyclicity for q1 or q2 on a common support-local pairing.
- the complete seven-proof SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.
- a passed classical import Gate A.
- a gauge-fixed normally or strongly hyperbolic Lorentzian BV operator.
- a causal Green homotopy, Hadamard state, renormalized products, restored QME, positivity, or Lorentzian quantum theory.
