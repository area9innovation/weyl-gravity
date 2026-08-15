# Strict polarized Bach-kernel benchmark v1

**Result:** `STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1`

**State:** `BENCHMARK_CONTRACT_CERTIFIED_GENERAL_KERNEL_ABSENT`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

Five complementary fixture classes constrain normalization, nonzero projections, direct local densities, an infinite-dimensional exact zero slice, and a complete restricted-background Hessian variation. They are a strong falsification suite but do not reconstruct the general cylinder tensor. The missing object is still an exact arbitrary-input, support-local, ten-output symmetric contravariant density K^ab[h1,h2] through metric-jet order four, together with differentiated Diff/Weyl identities.

This distinction matters: a candidate that returns zero passes the pp-wave
slice but fails the two nonzero cylinder channels; a mode-table replay passes
those channels but fails arbitrary-input completeness; and a cylinder-only
program cannot claim the Nariai portability gate. No existing result is being
silently promoted into the missing tensor.

## Target object

The target is the coefficient of `a*b` in the action Euler density

```text
E^ab(gbar + a h1 + b h2),
E^ab = sqrt(-g) g^(a mu) g^(b nu) B_action_munu,
B_action = -2 B_standard.
```

It has ten symmetric contravariant density outputs, accepts two arbitrary
compactly supported symmetric metric perturbations, uses metric jets through
order four, and must obey the support-intersection rule. The coefficient-of-
`a*b` convention contains no hidden factor of `1/2`.

## Existing falsification fixtures

| Fixture | Evidence class | What it can test | What it cannot establish |
|---|---|---|---|
| `CYLINDER_LINEARIZED_ACTION_NORMALIZATION` | `UNARY_FORMULA_AND_EXHAUSTIVE_JET_CONTROL` | fixes the unary convention and fourth-order principal normalization used by the same geometric pipeline | any quadratic coefficient of the arbitrary-input polarized kernel |
| `CYLINDER_HT1B_NONZERO_MODE_CHANNELS` | `NONZERO_MODE_SPECIALIZED_LOCAL_DENSITY_AND_INTEGRATED_PROJECTION` | detects a zero or wrongly normalized nonlinear evaluator on two independent physical channels | the unprojected ten-component tensor or any untested coefficient |
| `CYLINDER_DIRECT_CURVATURE_PROBES` | `DIRECT_EXACT_CURVATURE_PROBES` | independently reevaluates local curvature densities and distinguishes nonzero slice currents from vanishing integrated gauge probes | arbitrary-input completeness or reverse local densities without reverse gauge probes |
| `PPWAVE_ARBITRARY_PROFILE_ZERO_SLICE` | `ARBITRARY_PROFILE_RESTRICTED_NONLINEAR_ZERO` | rejects spurious nonlinear terms on an infinite-dimensional exact slice | any nonaligned interaction coefficient or complete BV q2 |
| `NARIAI_TRANSVERSE_HESSIAN_VARIATION` | `RESTRICTED_BACKGROUND_COMPLETE_HESSIAN_VARIATION` | cross-background method benchmark for direct leading derivation plus differentiated-Noether completion | the cylinder kernel, a rank-310 SDR, or causal transfer |

## Candidate geometric program

1. **`metric_inverse`** → `g^ab`
2. **`levi_civita_connection`** → `Gamma^a_bc`
3. **`curvature`** → `R^a_bcd, Ric_ab, R`
4. **`weyl_tensor`** → `C_abcd`
5. **`bach_standard`** → `B_standard_ab=nabla^c nabla^d C_acbd+(1/2)Ric^cd C_acbd`
6. **`action_normalize`** → `B_action_ab=-2 B_standard_ab`
7. **`raise_and_densitize`** → `E^ab=sqrt(-g) g^(a mu) g^(b nu) B_action_munu`
8. **`polarized_coefficient`** → `K^ab[h1,h2]=coefficient of a*b in E^ab(gbar+a h1+b h2)`

The program is a construction contract, not a claim that these operations
have already been serialized or evaluated for arbitrary inputs.

## Fail-closed acceptance gates

| Gate | Current state | Required evidence |
|---|---|---|
| `TYPE_AND_EXACTNESS` | `NOT_RUN_NO_GENERAL_EVALUATOR` | ten symmetric contravariant density outputs with exact rational/algebraic coefficients and no floats |
| `ARBITRARY_INPUT_COMPLETENESS` | `NOT_RUN_NO_GENERAL_EVALUATOR` | all 10 x 10 unordered metric-component input pairs and all coefficient jets through total differential order four are addressable |
| `POLARIZATION_SYMMETRY` | `NOT_RUN_NO_GENERAL_EVALUATOR` | K[h1,h2]=K[h2,h1] under the declared coefficient-of-a*b convention |
| `SUPPORT_INTERSECTION` | `NOT_RUN_NO_GENERAL_EVALUATOR` | the local bidifferential AST contains no inverse differential operator and obeys supp K(u,v) subset supp(u) intersection supp(v) |
| `DIFFERENTIATED_WEYL_IDENTITY` | `NOT_RUN_NO_GENERAL_EVALUATOR` | the twice-polarized identity derived from g_ab E^ab(g)=0 vanishes, including the two unary cross terms |
| `DIFFERENTIATED_DIFF_NOETHER_IDENTITY` | `NOT_RUN_NO_GENERAL_EVALUATOR` | the twice-polarized covariant-divergence identity vanishes with connection and density variations retained |
| `CYLINDER_UNARY_NORMALIZATION` | `NOT_RUN_NO_GENERAL_EVALUATOR` | the shared pipeline reproduces the exhaustive action-normalized linearized cylinder operator |
| `PPWAVE_ZERO_SLICE` | `NOT_RUN_NO_GENERAL_EVALUATOR` | the evaluator returns zero for arbitrary aligned pp-wave profile pairs before projection |
| `HT1B_NONZERO_CHANNELS` | `NOT_RUN_NO_GENERAL_EVALUATOR` | mode adapters and exact S3 integration reproduce both nonzero local-density/Taub channels |
| `NARIAI_PORTABILITY` | `NOT_RUN_NO_GENERAL_EVALUATOR` | a background-generic implementation reproduces the restricted Nariai Hessian-variation hash; cylinder-only implementations must mark this NOT_APPLICABLE, never PASS |

In particular, the nonlinear Weyl identity is not a naive trace-free test.
Twice differentiating `g_ab E^ab(g)=0` also produces two cross terms involving
the unary Bach operator. The Diff identity likewise retains variations of the
connection and density. Both must be replayed in their differentiated form.

## Construction sequence

| Stage | State | Deliverable |
|---|---|---|
| `P0_BIVARIATE_EXACT_JETS` | `OPEN` | exact a,b coefficient algebra with coordinate derivatives through order four |
| `P1_CYLINDER_GEOMETRIC_PIPELINE` | `OPEN` | executable inverse/connection/curvature/Weyl/Bach/raise-density pipeline at a homogeneous cylinder chart |
| `P2_LOCAL_IDENTITIES` | `OPEN` | independent polarization, differentiated Weyl and Diff Noether replays |
| `P3_PHYSICAL_FIXTURE_ADAPTERS` | `OPEN` | pp-wave restriction and HT1B mode/integration adapters |
| `P4_PORTABLE_AST_EXPORT` | `OPEN` | content-addressed tensor-natural component payload consumable by the strict q2 receiver |

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_polarized_bach_benchmark.py --check
python3 quantum-weyl/classical_import/check_strict_polarized_bach_benchmark.py
python3 quantum-weyl/classical_import/verify_strict_polarized_bach_benchmark.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_polarized_bach_benchmark.py -v
```

## Does not establish

- the arbitrary-input polarized second Bach tensor on the conformal cylinder.
- a portable h-star q2 component row or complete six-row support-local q2.
- polarization symmetry or differentiated Diff/Weyl identities for a candidate evaluator.
- that the reduced-mode HT1B channels determine unprojected local coefficients.
- that the pp-wave zero slice constrains nonaligned nonlinear interactions.
- that the Nariai transverse variation is a cylinder or open-background theorem.
- a passed classical import gate, causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory.
