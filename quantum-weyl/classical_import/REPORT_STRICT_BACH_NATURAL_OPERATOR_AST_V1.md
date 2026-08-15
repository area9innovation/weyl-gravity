# Portable tensor-natural Bach-Hessian AST v1

**Result:** `STRICT_BACH_NATURAL_OPERATOR_AST_V1`

**State:** `PORTABLE_NATURAL_BACH_HESSIAN_CERTIFIED_HSTAR_INTEGRATION_AND_SUSPENSION_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The polarized action-normalized Bach kernel is no longer defined only by a
large table at one conformal-cylinder frame.  This result supplies a typed,
content-addressed and executable natural-operator DAG for

```text
K_g(h1,h2) = [a*b] (-2 sqrt(abs(g+a h1+b h2)) B(g+a h1+b h2)^sharp).
```

The general coordinate-independence claim comes from composition: metric
inverse, Levi-Civita curvature, the Schouten/Weyl/Cotton/Bach construction,
contraction, absolute densitization, and mixed Frechet differentiation are
all pullback-natural.  The exact signed-coordinate replay is deliberately an
implementation regression only; it is not the proof of the general statement.

## Executable DAG

| Node | Operation | Output type | Metric-jet order |
|---|---|---|---:|
| `g_ab` | `metric_two_parameter_family` | `symmetric_covariant_2` | 0 |
| `g_inverse` | `inverse_metric` | `symmetric_contravariant_2` | 0 |
| `geometry` | `levi_civita_geometry` | `levi_civita_geometry_bundle` | 2 |
| `P_and_C` | `schouten_and_weyl_4d` | `schouten_cov2_and_weyl_cov4_bundle` | 2 |
| `Cotton` | `cotton_4d` | `cotton_covariant_3` | 3 |
| `B_lower` | `bach_4d` | `symmetric_covariant_2` | 4 |
| `B_upper` | `raise_symmetric_two_tensor` | `symmetric_contravariant_2` | 4 |
| `volume` | `absolute_metric_volume_density` | `absolute_metric_density_weight_plus_1` | 0 |
| `E_g` | `densitize_and_scale` | `symmetric_contravariant_density_weight_plus_1` | 4 |
| `K_hh` | `mixed_frechet_coefficient` | `symmetric_bilinear_metric_jet_operator_to_symmetric_contravariant_density_weight_plus_1` | 4 |

The root has fourth metric-jet order, exact rational coefficients and the
support-intersection property.  Its output is the same symmetric
contravariant weight-one density used by the authoritative metric antifield.

## Independent exact checks

| Background | Seeds | Nonzero outputs | Output digest |
|---|---:|---:|---|
| `conformal_cylinder` | 1, 2 | 9 | `0b7b62aaefa891d6...` |
| `minkowski` | 2, 3 | 9 | `caaf8401c6e60adb...` |
| `flat_brinkmann` | 3, 4 | 3 | `7492e7e35d1a876d...` |

The AST receiver agrees coefficientwise with the earlier point evaluator on
the conformal cylinder, Minkowski space and a flat Brinkmann chart.  Three
polynomial pp-wave pairs give all ten outputs zero.  A nontrivial signed
coordinate permutation also transforms all ten outputs exactly as a
contravariant absolute density.

The independent Nariai action-Hessian calculation is pinned as
cross-background evidence for the same covariant Bach construction and
normalization.  This result does **not** claim a direct component adapter to
that separate moving-frame PBW table.

## Gate ledger

| Gate | Status | Evidence or remaining work |
|---|---|---|
| `P4_PORTABLE_AST_EXPORT` | `PASS` | content-addressed typed DAG, exact evaluator, compositional naturality theorem and multi-background regressions |
| `HSTAR_PORTABLE_INTEGRATION` | `OPEN` | replace the cylinder K reference in the h-star row by this AST and combine with its already certified cotangent terms |
| `SUSPENDED_GRADED_POLARIZATION` | `OPEN` | the repository suspension and odd diagonal convention have not yet been replayed across all six rows |
| `SIX_ROW_INTERACTION_IDENTITIES` | `OPEN` | q1q2, D derivation and BV cyclicity require the integrated six-row receiver |

The immediate next step is mechanical but scientifically consequential:
replace the basepoint-only `K` reference in the metric-antifield row with this
portable root, then perform the repository suspended polarization across all
six minimal rows.  Only after that can Koszul symmetry and the arity-two
master identity be replayed honestly.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_bach_natural_operator_ast.py --check
python3 quantum-weyl/classical_import/check_strict_bach_natural_operator_ast.py
python3 quantum-weyl/classical_import/verify_strict_bach_natural_operator_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_bach_natural_operator_ast.py -v
```

## Does not establish

- the integrated metric-antifield row including its cotangent terms.
- the repository suspended graded bilinear q2 or its Koszul symmetry.
- q1q2=0, a complete local D action, D derivation, or BV cyclicity.
- a passed classical import Gate A.
- a causal Green homotopy, Hadamard state, Lorentzian QME, or Lorentzian quantum theory.
- a direct component equality with the separately normalized Nariai PBW action-Hessian table.
