# Strict q2 kinematic/cotangent AST v1

**Result:** `STRICT_Q2_KINEMATIC_COTANGENT_AST_V1`

**State:** `FIVE_OF_SIX_MINIMAL_ROWS_SERIALIZED_POLARIZATION_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The exact, receiver-replayed minimal-BV `Q` export fixes the signs and rational
coefficients of five non-Bach quadratic rows. This result turns those rows into
a portable tensor-natural diagonal Taylor polynomial with nine named local
operators and explicit coordinate formulas. The sixth, metric-antifield row is
kept open because it contains the polarized second Bach variation through
fourth metric-jet order.

This is intentionally not presented as a complete `q2`. The expressions are
the quadratic diagonal polynomial in `Q(epsilon Phi)`. The repository's
suspended graded polarization—especially the odd ghost diagonal—must be
implemented and replayed before Koszul symmetry or any arity-two identity can
be claimed.

## Row coverage

| Output | Status | Components |
|---|---|---:|
| `h` | `DIAGONAL_POLYNOMIAL_SERIALIZED` | 2 |
| `c` | `DIAGONAL_POLYNOMIAL_SERIALIZED` | 1 |
| `omega` | `DIAGONAL_POLYNOMIAL_SERIALIZED` | 1 |
| `h_star` | `OPEN_HARD_BACH_AND_COTANGENT_ROW` | 0 |
| `c_star` | `DIAGONAL_POLYNOMIAL_SERIALIZED` | 3 |
| `omega_star` | `DIAGONAL_POLYNOMIAL_SERIALIZED` | 2 |

## Portable operator dictionary

| Operator | Inputs | Output | Coordinate representative |
|---|---|---|---|
| `odd_vector_half_bracket` | `c, c` | `c^mu` | c^rho partial_rho c^mu = (1/2)[c,c]^mu |
| `scalar_lie_transport` | `c, omega` | `omega` | c^rho partial_rho omega |
| `metric_lie_transport` | `c, h` | `h_mu_nu` | c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho |
| `weyl_metric_product` | `omega, h` | `h_mu_nu` | omega * h_mu_nu |
| `metric_antifield_diff_noether` | `h, h_star` | `c_star_lambda` | h_star^mu_nu partial_lambda h_mu_nu - 2 partial_mu(h_star^mu_nu h_lambda_nu) |
| `covector_density_lie_transport` | `c, c_star` | `c_star_lambda` | c^rho partial_rho c_star_lambda + c_star_rho partial_lambda c^rho + (partial_rho c^rho)c_star_lambda |
| `weyl_antifield_gradient` | `omega, omega_star` | `c_star_lambda` | omega_star partial_lambda omega |
| `metric_antifield_trace_pair` | `h, h_star` | `omega_star` | h_mu_nu h_star^mu_nu |
| `scalar_density_lie_transport` | `c, omega_star` | `omega_star` | partial_rho(c^rho omega_star) |

All coefficients are integers, all serialized operators have input jet order
at most one, and every binary term obeys the support-intersection rule.

## Receiver checks and open gates

| Check | Status | Scope or boundary |
|---|---|---|
| `source_sign_and_coefficient_crosswalk` | `RECEIVER_REPLAYED` | five source Q rows in the executable antifield export |
| `operator_inventory_and_tensor_types` | `RECEIVER_REPLAYED` | nine declared tensor-natural primitives |
| `exact_coefficients_and_jet_bounds` | `RECEIVER_REPLAYED` | nine serialized components, maximum total input jet order two |
| `five_row_diagonal_completeness` | `RECEIVER_REPLAYED` | c, omega, h, c_star and omega_star only |
| `q2_koszul_symmetry` | `NOT_REPLAYED` | suspended polarization and odd diagonal convention remain to be implemented |
| `q1_q2_arity_two_nilpotency` | `NOT_REPLAYED` | requires the polarized six-row q2 including the Bach row |
| `D_q2_derivation` | `NOT_REPLAYED` | full local D is not serialized |
| `BV_cyclicity_q2` | `NOT_REPLAYED` | requires polarized components and the common support-local pairing |

## Next construction

Derive the `h_star` row as two separately auditable pieces: the polarized
`D^2 Bach[h,h]` kernel through metric-jet order four, and the Diff/Weyl
cotangent terms. Then implement the suspended polarization and replay all seven
checks required by `SUPPORT_LOCAL_Q2_EXPORT_CONTRACT` on the six-row payload.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_q2_kinematic_cotangent_ast.py --check
python3 quantum-weyl/classical_import/check_strict_q2_kinematic_cotangent_ast.py
python3 quantum-weyl/classical_import/verify_strict_q2_kinematic_cotangent_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_q2_kinematic_cotangent_ast.py
```

## Does not establish

- a complete six-row support-local q2.
- the polarized second Bach variation.
- Koszul symmetry under the repository suspension convention.
- the arity-two master identity.
- a full local D action or its derivation identity.
- BV cyclicity on a common local pairing.
- Gate A, a causal Green homotopy, a Hadamard state, QME restoration or a Lorentzian quantum theory.
