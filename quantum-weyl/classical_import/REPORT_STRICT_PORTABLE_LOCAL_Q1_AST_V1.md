# Portable Bach-flat strict local q1 AST v1

**Result:** `STRICT_PORTABLE_LOCAL_Q1_AST_V1`

**State:** `PORTABLE_Q1_AND_Q1_SQUARED_CERTIFIED_ARITY_TWO_IDENTITY_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The strict minimal pure-Weyl unary BV differential is now serialized in the
same suspended convention as the six-row `q2` ledger. It has five nonzero
background-linear components. There are no components whose outputs are the
Diff or Weyl ghost slots, and there are no components taking either ghost-
antifield slot as input. Thus the displayed tangent chain starts with the two
ghost directions and stops after the two ghost-antifield directions.

On the explicitly declared Bach-flat background class, `q1^2=0` is certified
compositionally from naturality and the two Noether identities. An exact
coordinate-jet receiver independently replays every nontrivial composition on
the conformal cylinder, Minkowski space, and flat Brinkmann coordinates. This
is a portable unary theorem, not a claim that the nonlinear arity-two identity
has already been checked.

## Nonzero unary components

| Component | Input | Output | Operator |
|---|---|---|---|
| `q1_h_c` | `c` | `h` | `R_diff` |
| `q1_h_omega` | `omega` | `h` | `R_weyl` |
| `q1_hstar_h` | `h` | `h_star` | `B_linear` |
| `q1_cstar_hstar` | `h_star` | `c_star` | `N_diff_linear` |
| `q1_omegastar_hstar` | `h_star` | `omega_star` | `N_weyl_linear` |

In tangent-complex direction, the formulas are
`q1(c)=L_c gbar`, `q1(omega)=2 omega gbar`, `q1(h)=B_linear(h)`,
`q1(h_star)=N_diff_linear(h_star)+N_weyl_linear(h_star)`, and
`q1(c_star)=q1(omega_star)=0`. Here `B_linear` is the first Frechet derivative
of the already certified action-normalized natural Bach Euler map. This is the
transpose orientation of the BRST vector field acting on coordinate
functions, so the direction is stated explicitly to avoid conflating them.

## Exact square-zero fixtures

| Background | Bach-flat | Diff gauge | Weyl gauge | Diff Noether | Weyl Noether |
|---|---|---|---|---|---|
| `conformal_cylinder` | `True` | `True` | `True` | `True` | `True` |
| `minkowski` | `True` | `True` | `True` | `True` | `True` |
| `flat_brinkmann` | `True` | `True` | `True` | `True` | `True` |

These finite fixtures are regression witnesses. Generality comes from the
typed natural maps and the differentiated covariance/Noether identities, not
from extrapolating three coordinate examples.

## Why Bach-flat matters

At a solution, differentiating Diff and Weyl covariance gives
`B_linear R_diff=0` and `B_linear R_weyl=0`. Away from a solution those
compositions contain transport or Weyl rescaling of `E_g(gbar)`. The present
unary complex therefore does not silently claim an off-shell background
complex.

## Next gate

The exact next calculation is `[q1,q2]=0`. It must differentiate all five unary
components against the twenty-two ordered components in
`STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1`, including the Bach Hessian and both
Noether variations. The certificate keeps that flag false.

## Reproduction

```text
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/build_strict_portable_local_q1_ast.py --check
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/check_strict_portable_local_q1_ast.py
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/verify_strict_portable_local_q1_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_portable_local_q1_ast.py -v
```

## Does not establish

- q1q2=0 or any nonlinear master identity.
- the local D action, D equivariance, or BV cyclicity.
- q1 nilpotency away from a Bach-flat background without the corresponding curved/tadpole terms.
- the complete seven-proof SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.
- a passed classical import Gate A.
- a causal Green homotopy, Hadamard state, Lorentzian QME, positivity, or Lorentzian quantum theory.
