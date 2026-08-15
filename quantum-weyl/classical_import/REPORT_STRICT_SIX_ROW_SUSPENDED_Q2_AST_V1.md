# Portable six-row suspended strict q2 AST v1

**Result:** `STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1`

**State:** `SIX_ROWS_PORTABLE_AND_KOSZUL_REPLAYED_Q1_D_PAIRING_IDENTITIES_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

All six minimal strict pure-Weyl `q2` output rows now have a portable component
ledger in the repository convention
`suspended-graded-symmetric-factorial-v1`.  The twelve diagonal quadratic
terms become twenty-two ordered components. Every mixed term has its exact
Koszul-swapped partner, the metric self-pair uses the symmetric portable Bach
kernel, and the odd Diff-ghost self-pair uses the antisymmetric vector bracket.

This closes two earlier deficits: the metric-antifield row is tensor-natural
on an arbitrary background, and the six-row suspension is explicit. It does
not yet satisfy the complete downstream export contract because `q1q2=0`, the
full local `D` action and BV cyclicity have not been independently executed.

## Row coverage

| Output | Primary terms | Ordered terms | Status |
|---|---:|---:|---|
| `h` | 2 | 4 | `COMPLETE` |
| `c` | 1 | 1 | `COMPLETE` |
| `omega` | 1 | 2 | `COMPLETE` |
| `h_star` | 3 | 5 | `COMPLETE` |
| `c_star` | 3 | 6 | `COMPLETE` |
| `omega_star` | 2 | 4 | `COMPLETE` |

## Twelve primary kernels

| Component | Inputs | Output | Coefficient | Coordinate or natural formula |
|---|---|---|---:|---|
| `q2_c_cc` | `c, c` | `c` | `1` | [c_left,c_right]^mu=c_left^rho partial_rho c_right^mu-c_right^rho partial_rho c_left^mu |
| `q2_omega_comega` | `c, omega` | `omega` | `1` | c^rho partial_rho omega |
| `q2_h_ch` | `c, h` | `h` | `1` | c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho |
| `q2_h_omegah` | `omega, h` | `h` | `2` | omega * h_mu_nu |
| `q2_hstar_hh` | `h, h` | `h_star` | `1` | K_g(h_left,h_right)=[a*b]E_g(gbar+a h_left+b h_right) |
| `q2_hstar_chstar` | `c, h_star` | `h_star` | `1` | c^rho partial_rho h_star^{mu nu} - h_star^{rho nu} partial_rho c^mu - h_star^{mu rho} partial_rho c^nu + (partial_rho c^rho) h_star^{mu nu} |
| `q2_hstar_omegahstar` | `omega, h_star` | `h_star` | `-2` | -2 omega h_star^{mu nu} |
| `q2_cstar_hhstar` | `h, h_star` | `c_star` | `1` | h_star^mu_nu partial_lambda h_mu_nu - 2 partial_mu(h_star^mu_nu h_lambda_nu) |
| `q2_cstar_ccstar` | `c, c_star` | `c_star` | `1` | c^rho partial_rho c_star_lambda + c_star_rho partial_lambda c^rho + (partial_rho c^rho)c_star_lambda |
| `q2_cstar_omegaomegastar` | `omega, omega_star` | `c_star` | `1` | omega_star partial_lambda omega |
| `q2_omegastar_hhstar` | `h, h_star` | `omega_star` | `2` | h_mu_nu h_star^mu_nu |
| `q2_omegastar_comegastar` | `c, omega_star` | `omega_star` | `1` | partial_rho(c^rho omega_star) |

The Taylor relation is

```text
Q(Phi) = q1(Phi) + (1/2) q2(Phi,Phi) + O(Phi^3).
```

For the two self-pairs, `(1/2)[c,c]=c partial c` in the external Grassmann
extension and `(1/2)q2(h,h)=(1/2)K_g(h,h)`. For each mixed species pair, the
Koszul sign of the ordered kernel and the reordering sign of its external
graded coefficients cancel exactly, recovering the displayed diagonal term
once rather than twice. The certificate executes this bookkeeping with two
independent odd generators: the `theta1*theta2` coefficient of `q2(c,c)` is
exactly twice the coefficient of `c partial c`, and all ten mixed half-sums
have multiplier one.

## Proof and gate ledger

| Check | Status | Evidence or missing receiver |
|---|---|---|
| `six_output_rows_complete` | `VERIFIED` | twelve primary and twenty-two ordered components cover every minimal output |
| `cohomological_degree_one` | `VERIFIED` | all ordered components satisfy degree(output)-degree(left)-degree(right)=1 |
| `q2_koszul_symmetry` | `VERIFIED` | every ordered component has an exact swapped partner with sign (-1)^(parity_left parity_right); both self-pairs replay intrinsic signs |
| `diagonal_Taylor_recovery` | `VERIFIED` | an exact two-generator exterior-coefficient fixture replays the odd bracket factor two; the half-Hessian and ten mixed sign products recover every source diagonal term |
| `portable_hstar_row` | `VERIFIED` | the portable Bach root replaces the cylinder table and both source-fixed cotangent lifts remain tensor-natural |
| `q1_q2_arity_two_nilpotency` | `NOT_REPLAYED` | a common executable local q1 receiver is the next gate |
| `D_q2_derivation` | `NOT_REPLAYED` | the full local D action is not serialized |
| `BV_cyclicity_q2` | `NOT_REPLAYED` | the common support-local pairing receiver is not serialized |

The next decisive calculation is the arity-two master identity. It requires a
common executable local `q1`, including the linearized Bach equation and the
two Noether-identity rows. A source-action theorem is useful guidance but will
not be substituted for receiver execution on these bytes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_six_row_suspended_q2_ast.py --check
python3 quantum-weyl/classical_import/check_strict_six_row_suspended_q2_ast.py
python3 quantum-weyl/classical_import/verify_strict_six_row_suspended_q2_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_six_row_suspended_q2_ast.py -v
```

## Does not establish

- q1q2=0 or any higher arity master identity.
- a complete local D action or its derivation identity.
- BV cyclicity on a common support-local pairing.
- the seven-proof complete SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.
- a passed classical import Gate A.
- a causal Green homotopy, Hadamard state, Lorentzian QME, or Lorentzian quantum theory.
