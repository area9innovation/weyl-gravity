# Strict cylinder polarized-Bach evaluator prototype v1

**Result:** `STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1`

**State:** `EVALUATOR_PROTOTYPE_EXECUTED_UNIVERSAL_AST_AND_DIFF_IDENTITY_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

An executable, dependency-free exact evaluator now accepts two arbitrary
rational metric four-jets and returns the coefficient of `a*b` in all ten
components of the action-normalized contravariant Euler density. It evaluates
the full metric inverse → connection → curvature → Weyl → Bach → density
pipeline in `Q[a,b]/(a^2,b^2)`, so the polarized coefficient has no hidden
factorial.

This is a prototype evaluator, not yet the universal component AST required
by Gate A. It evaluates any supplied exact jet, but it has not enumerated and
serialized every basis input pair or received an independent coefficient-level
replay.

## Exact checks

| Check | Status |
|---|---|
| `reciprocal_exact_in_square_free_bivariate_quotient` | `PASS` |
| `sqrt_exact_in_square_free_bivariate_quotient` | `PASS` |
| `coordinate_derivative_leibniz_exact` | `PASS` |
| `no_floating_point_scalar_type` | `PASS` |
| `cylinder_background_geometry_exact` | `PASS` |
| `arbitrary_sparse_trial_swap_symmetric` | `PASS` |
| `arbitrary_sparse_trial_nonlinear_nonzero` | `PASS` |
| `twice_polarized_weyl_trace_identity_zero` | `PASS` |
| `three_ppwave_polynomial_trials_zero` | `PASS` |
| `local_conformal_unary_trial_zero` | `PASS` |

The background replay gives `Ric=diag(0,2,2,2)`, scalar curvature `6`, and
zero Weyl and Bach tensors. Three exact polynomial Brinkmann profile pairs
return zero in all ten outputs. A local infinitesimal Weyl direction returns
zero in the unary row. The nonlinear cylinder trial is symmetric under input
exchange and satisfies the twice-polarized identity `coeff_ab(g_mn E^mn)=0`.

## Non-special cylinder smoke result

| Output pair | Exact coefficient |
|---|---:|
| `(0, 0)` | `-119/24` |
| `(0, 1)` | `5/2` |
| `(0, 2)` | `0` |
| `(0, 3)` | `9` |
| `(1, 1)` | `-29/12` |
| `(1, 2)` | `-11/8` |
| `(1, 3)` | `-1/6` |
| `(2, 2)` | `19/3` |
| `(2, 3)` | `31/6` |
| `(3, 3)` | `-7/8` |

Nine of ten components are nonzero, which prevents the zero-slice test from
becoming a vacuous implementation.

## Benchmark progress

| Stage | State | Evidence |
|---|---|---|
| `P0_BIVARIATE_EXACT_JETS` | `PROTOTYPE_EXECUTED` | exact reciprocal, square-root and Leibniz identities over Fraction in Q[a,b]/(a^2,b^2) |
| `P1_CYLINDER_GEOMETRIC_PIPELINE` | `PROTOTYPE_EXECUTED` | inverse, Levi-Civita, curvature, Schouten, Weyl, Cotton/Bach, action normalization, raising and densitization evaluated through jet order four |
| `P2_LOCAL_IDENTITIES` | `PARTIAL` | swap symmetry and the differentiated Weyl trace identity pass; differentiated Diff Noether remains open |
| `P3_PHYSICAL_FIXTURE_ADAPTERS` | `PARTIAL` | three exact Brinkmann polynomial pairs replay the pp-wave zero slice; HT1B cylinder mode adapters remain open |
| `P4_PORTABLE_AST_EXPORT` | `OPEN` | the evaluator accepts concrete exact jets but has not serialized the universal coefficient table |

## Still required

- independent exhaustive comparison with the serialized cylinder linearized Bach operator.
- differentiated Diff Noether identity with connection and density variations.
- HT1B E/A/L mode adapters and exact S3 integrations for both nonzero channels.
- universal 10 x 10 fourth-jet component table and portable tensor-natural AST.
- independent second implementation or coefficient-level receiver replay.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_polarized_bach_evaluator.py --check
python3 quantum-weyl/classical_import/check_strict_cylinder_polarized_bach_evaluator.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_polarized_bach_evaluator.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_cylinder_polarized_bach_evaluator.py -v
```

## Does not establish

- a universal symbolic coefficient table or portable tensor-natural h-star q2 row.
- exhaustive agreement with the independently serialized unary cylinder operator.
- the differentiated diffeomorphism Noether identity for arbitrary fifth test jets.
- the two nonzero HT1B mode-channel densities or their exact S3 projections.
- that three polynomial pp-wave evaluations replace the existing arbitrary-profile theorem.
- a complete six-row support-local q2, local D action, or any interaction receiver identity.
- a passed classical import gate, causal Green homotopy, Hadamard state, QME restoration, or Lorentzian quantum theory.
