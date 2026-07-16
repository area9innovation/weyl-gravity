# Consolidated \(D\)-quotient programme status

## Interpretation

There is no universal yes/no verdict for \(D\).  The authoritative claim key is

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

The compact result is sector-dependent: \(D\) is charged on the unrestricted
locally reduced linearized space, and it becomes gauge only after restriction
to the full Taub/moment-map zero fibre and the selected derived quotient.
The one-real-scalar exact-cylinder and complete standard stealth-clock routes
are obstructed. A distinct neutral two-field reference sector supplies a
scoped homogeneous `D_GAUGE` theorem but fails its positive-health audit. The
first healthy background candidate is now exact: a non-conformally-flat Berger
cylinder supports two standard-sign rotating conformal scalars with positive
quartic potential, dominant-energy stress, timelike phase, and full raw clock
incidence. Its fixed-coupling linearized charge gate is also closed: the lapse
constraint fixes \(\delta Q_R=0\), compact averaging excludes an inhomogeneous
escape, and the scoped verdict is `D_GAUGE`. The clock rows contract
support-locally and cyclically, the retained minimal `q1` is complete, and the
selected gauge fermion gives an exact support-local cyclic gauge-fixed
54-to-26 contraction. The complete `q2` has now been transferred exactly to a
retained 26-row operation with 54,236 canonical nonzero coefficients; its
arity-two and odd-Darboux cyclicity defects vanish. This retained operation is
not yet the minimal residual/cohomology `ell2`. The bare local unary D-Cartan
equation is independently obstructed by an exact characteristic-rank mismatch,
so the remaining routes are characteristic cohomology, residual/BFV extension,
and retained causal Green extension. The Einstein-incidence audit separately
classifies this background as a non-Einstein Weyl--matter branch.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
| classical | `D_GAUGE_ON_POSITIVE_BERGER_FIXED_COUPLING_LINEARIZED_SPACE` | The healthy positive Berger background has D_GAUGE on its fixed-coupling linearized phase space. The retained 26-row q1 and portable 34-row minimal contraction extend to an exact cyclic support-local gauge-fixed 54-to-26 contraction. The complete support-local q2 and local D action are exported; the specialized characteristic symbol audit proves that the bare local unary Cartan equation has no solution. | compute the full characteristic symbol-cohomology carrier module and construct a retained causal Green extension without retrying the ruled-out bare local unary ansatz |
| einstein_boundary | `PHASE_SPACE_NOT_CLOSED` | The fixed-bundle standard Einstein--Maxwell harmonic quotient and integrated Lee--Wald form are complete before final residual quotient, and the induced linear tangent quotient map into Weyl--Maxwell is injective. The first exact Weyl--Maxwell restriction is nondegenerate on both axial ell=2 branches but has opposite-sign relative factors 1+3*sqrt(3) and 1-3*sqrt(3), refuting a universal proportional restriction on this scoped block. | derive the arbitrary-lambda axial restriction and compute polar, physical ell=1, homogeneous, and twist blocks, then solve extra fourth-order adjoint classes; independently complete the asymptotic Bach phase space and charge audit |
| nonlinear | `BARE_LOCAL_UNARY_D_CARTAN_OBSTRUCTED_EXTENSION_REQUIRED` | The complete classical 54-row support-local q2 tensor is independently imported and replayed over Q(sqrt(10)), then transferred exactly to a 26-row retained q2 with 54,236 canonical nonzero PBW coefficients. Its retained q1/q2 arity-two and odd-Darboux cyclicity defects vanish coefficientwise. This is not the minimal residual/cohomology ell2. Independently, the bare local unary D-Cartan equation is obstructed by an exact characteristic-rank mismatch. | compute the characteristic symbol-cohomology carrier module, then test residual/BFV and retained causal Green extensions as separate scoped constructions |
| quantum | `ANALYTIC_FRAMEWORK_MISSING` | the current required classical compact-cylinder settings are imported by content hash without quantum promotion; exact Cartan quotient mechanics, complete intrinsic Euler descent, and hash-bound AFN0 closure witnesses are registered | complete the AFN0 lower-form total complex, then instantiate the admissible bulk Cartan-obstruction basis before any QME or residual-transfer promotion |

## Setting ledger

| Setting | Generator | Phase space | Layer | Status | Verdict |
|---|---|---|---|---|---|
| compact_unrestricted | `D_compact` | `compact_P_lin` | CLASSICAL_CHARGE | `CERTIFIED` | `D_CHARGED` |
| compact_taub_zero | `D_compact` | `compact_P_Taub0` | CLASSICAL_CHARGE | `CERTIFIED` | `D_GAUGE` |
| compact_derived_residual | `D_compact` | `compact_P_der` | CLASSICAL_CARTAN | `CERTIFIED` | `D_GAUGE` |
| compact_scalar_clock | `D_compact` | `compact_scalar_clock` | CLASSICAL_CHARGE | `BLOCKED` | `SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED` |
| compact_neutral_clock_pair | `D_compact` | `compact_neutral_clock_pair_homogeneous` | CLASSICAL_CHARGE | `CERTIFIED` | `D_GAUGE` |
| compact_neutral_clock_pair_local_health | `D_compact` | `compact_neutral_clock_pair_local_extension` | CLASSICAL_CHARGE | `BLOCKED` | `OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED` |
| compact_homogeneous_positive_stealth_clock | `D_compact` | `compact_homogeneous_positive_stealth_scalar` | CLASSICAL_CHARGE | `BLOCKED` | `HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED` |
| compact_standard_conformal_stealth_clock | `D_compact` | `standard_conformal_scalar_stealth_clock_sector` | CLASSICAL_CHARGE | `BLOCKED` | `STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO` |
| compact_positive_berger_clock | `D_compact` | `positive_rotating_scalar_berger_background` | CLASSICAL_CHARGE | `PARTIAL` | `POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS` |
| compact_positive_berger_clock_reduced_charge | `D_compact` | `positive_rotating_scalar_berger_background` | CLASSICAL_CHARGE | `PARTIAL` | `NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN` |
| compact_positive_berger_clock_fixed_coupling_linearized | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | CLASSICAL_CHARGE | `CERTIFIED` | `D_GAUGE` |
| compact_positive_berger_clock_minimal_bv_sdr | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | CLASSICAL_BV | `CERTIFIED` | `MINIMAL_CLOCK_SECTOR_SDR` |
| compact_positive_berger_clock_retained_minimal_layout | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | CLASSICAL_BV | `CERTIFIED` | `RETAINED_MINIMAL_LAYOUT_FROZEN` |
| compact_positive_berger_clock_einstein_incidence | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | CLASSICAL_BV | `CERTIFIED` | `EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND` |
| compact_einstein_maxwell_product_background | `H_product` | `einstein_maxwell_product_background` | CLASSICAL_BV | `CERTIFIED` | `COMMON_EINSTEIN_MAXWELL_WEYL_MAXWELL_BACKGROUND` |
| compact_einstein_maxwell_product_tangent_preflight | `H_product` | `einstein_maxwell_product_principal_tangent_complex` | CLASSICAL_BV | `PARTIAL` | `PRINCIPAL_TANGENT_CHAIN_MAP_WITH_EXTRA_WEYL_CLASSES` |
| compact_einstein_maxwell_product_on_shell_tangent | `H_product` | `einstein_maxwell_product_on_shell_linear_tangents` | CLASSICAL_BV | `CERTIFIED` | `FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON` |
| compact_einstein_maxwell_second_order_fixed_flux | `H_product` | `einstein_maxwell_product_compact_fixed_flux_second_order` | CLASSICAL_BV | `CERTIFIED` | `SECOND_ORDER_FIXED_FLUX_OBSTRUCTION_FOR_RADION_AND_DUALITY` |
| universal_cover_einstein_maxwell_second_order_null_extension | `H_product` | `einstein_maxwell_product_universal_cover_null_second_order` | CLASSICAL_BV | `CERTIFIED` | `NONZERO_CHEVRETON_NULL_TANGENT_EXTENDS_AT_SECOND_ORDER` |
| compact_einstein_maxwell_periodic_photon_second_order | `H_product` | `einstein_maxwell_product_compact_fixed_charge_periodic_photon_second_order` | CLASSICAL_BV | `CERTIFIED` | `PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION` |
| compact_einstein_maxwell_periodic_graviton_second_order | `H_product` | `einstein_maxwell_product_compact_fixed_charge_periodic_graviton_second_order` | CLASSICAL_BV | `CERTIFIED` | `PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION` |
| compact_einstein_maxwell_obstruction_bilinear_g1 | `H_product` | `einstein_maxwell_product_compact_fixture_span_obstruction_bilinear` | CLASSICAL_BV | `CERTIFIED` | `G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN` |
| compact_einstein_maxwell_domain_taub_descent | `H_product` | `einstein_maxwell_product_compact_fixed_u1_harmonic_taub` | CLASSICAL_BV | `CERTIFIED` | `G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT` |
| compact_einstein_maxwell_harmonic_adjoint_block_preflight | `H_product` | `einstein_maxwell_product_compact_harmonic_block_preflight` | CLASSICAL_BV | `CERTIFIED` | `G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT` |
| compact_einstein_maxwell_axial_master_complex | `H_product` | `einstein_maxwell_product_compact_axial_master_complex` | CLASSICAL_BV | `CERTIFIED` | `G1_AXIAL_ALL_MOMENTA_MASTER_COMPLEX` |
| compact_einstein_maxwell_polar_master_preflight | `H_product` | `einstein_maxwell_product_compact_polar_master_preflight` | CLASSICAL_BV | `CERTIFIED` | `G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT` |
| compact_einstein_maxwell_polar_master_complex | `H_product` | `einstein_maxwell_product_compact_polar_master_complex` | CLASSICAL_BV | `CERTIFIED` | `G2_POLAR_ELL_GE2_ARBITRARY_LAMBDA_TENSOR_IDENTITY` |
| compact_einstein_maxwell_polar_exceptional_complex | `H_product` | `einstein_maxwell_product_compact_polar_exceptional_complex` | CLASSICAL_BV | `CERTIFIED` | `G2_POLAR_ALL_ELL_LINEAR_COMPLEX` |
| compact_einstein_maxwell_radiative_symplectic_matching | `H_product` | `einstein_maxwell_product_compact_radiative_symplectic` | CLASSICAL_BV | `CERTIFIED` | `G2_RADIATIVE_COVARIANT_SYMPLECTIC_MATCHING` |
| compact_einstein_maxwell_exceptional_global_symplectic | `H_product` | `einstein_maxwell_product_compact_exceptional_global_symplectic` | CLASSICAL_BV | `CERTIFIED` | `G2_EXCEPTIONAL_GLOBAL_SYMPLECTIC_COMPLETION` |
| compact_einstein_maxwell_weyl_symplectic_preflight | `H_product` | `einstein_maxwell_product_compact_weyl_symplectic_preflight` | CLASSICAL_BV | `CERTIFIED` | `G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE` |
| compact_einstein_maxwell_weyl_axial_ell2_restriction | `H_product` | `einstein_maxwell_product_compact_weyl_axial_ell2_restriction` | CLASSICAL_BV | `CERTIFIED` | `G1_AXIAL_ELL2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION` |
| compact_selected_residual_HT1_q2 | `D_compact` | `compact_selected_residual_HT1` | INTERACTING | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |
| compact_positive_berger_clock_retained_q2_26 | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | INTERACTING | `CERTIFIED` | `RETAINED_Q2_26_COMPLETE_BARE_LOCAL_UNARY_D_CARTAN_OBSTRUCTED` |
| compact_interacting | `D_compact` | `compact_interacting` | INTERACTING | `BLOCKED` | `BARE_LOCAL_UNARY_D_CARTAN_OBSTRUCTED_EXTENSION_REQUIRED` |
| compact_quantum | `D_compact` | `compact_quantum` | QUANTUM | `BLOCKED` | `ANALYTIC_FRAMEWORK_MISSING` |
| asymptotic_real_cylinder_time | `H_ESU` | `asymptotically_flat_full_Bach` | LORENTZIAN_CAUSAL | `OPEN` | `PHASE_SPACE_NOT_CLOSED` |
| asymptotic_dilation | `D_M` | `asymptotically_flat_full_Bach` | LORENTZIAN_CAUSAL | `OPEN` | `OPEN` |
| asymptotic_time_translation | `P_0` | `asymptotically_flat_full_Bach` | LORENTZIAN_CAUSAL | `OPEN` | `OPEN` |
| lorentzian_dS_AdS | `UNSELECTED` | `lorentzian_dS_AdS` | LORENTZIAN_CAUSAL | `NOT_TESTED` | `OPEN` |

## Shared dependency gate

1. the selected generator preserves the declared phase space and boundary data
2. the generator is Hamiltonian with an integrable normalized charge
3. the charge vanishes on the exact sector proposed for quotienting
4. the zero-charge transformations close as a Lie algebra or declared algebroid
5. the classical Cartan and causal homotopies exist in the declared support category
6. Berger retained minimal q1, portable 34-row contraction, curved five-direction companion, support-local cyclic gauge-fixed 54-to-26 contraction, complete q2, local D action, and exact retained q2_26 transfer are complete; the bare local unary Cartan equation is obstructed, while characteristic cohomology, residual/BFV extension, and retained causal Green extension remain open
7. the Einstein--Maxwell product common background is certified; its two tangent BV complexes, chain map, cohomology, presymplectic comparison, and all D/charge questions remain open
8. the product principal tangent chain map is certified with two additional simple-symbol Weyl metric classes; the complete Einstein--Maxwell solution tangent also injects on shell by the Chevreton factorization, while off-shell BV rows, prolonged modes, cyclicity, presymplectic comparison, nonlinear closure, and all D/charge questions remain open
9. the compact radion, duality, l=1 photon, and l=2 gravitational-plus fixtures assemble into a certified constant-lapse obstruction bilinear on their declared span, with exact charge-fibre cokernel behavior and relative Taub interpretation; the full harmonic domain and full cokernel remain open
10. interacting promotion requires a scoped Cartan extension beyond the certified bare local unary no-go
11. quantum promotion requires a restored QME and renormalized Ward identity

## Registered scoped contributions

| Team | Setting | Generator | Phase space | Status | Verdict |
|---|---|---|---|---|---|
| classical | `compact_scalar_clock` | `D_compact` | `compact_scalar_clock` | `CERTIFIED` | `SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED` |
| classical | `compact_neutral_clock_pair` | `D_compact` | `compact_neutral_clock_pair_homogeneous` | `CERTIFIED` | `D_GAUGE` |
| classical | `compact_neutral_clock_pair_local_health` | `D_compact` | `compact_neutral_clock_pair_local_extension` | `CERTIFIED` | `OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED` |
| classical | `compact_homogeneous_positive_stealth_clock` | `D_compact` | `compact_homogeneous_positive_stealth_scalar` | `CERTIFIED` | `HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED` |
| classical | `compact_standard_conformal_stealth_clock` | `D_compact` | `standard_conformal_scalar_stealth_clock_sector` | `CERTIFIED` | `STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO` |
| classical | `compact_positive_berger_clock` | `D_compact` | `positive_rotating_scalar_berger_background` | `CERTIFIED` | `POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS` |
| classical | `compact_positive_berger_clock_reduced_charge` | `D_compact` | `positive_rotating_scalar_berger_background` | `CERTIFIED` | `NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN` |
| classical | `compact_positive_berger_clock_fixed_coupling_linearized` | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | `CERTIFIED` | `D_GAUGE` |
| classical | `compact_positive_berger_clock_minimal_bv_sdr` | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | `CERTIFIED` | `MINIMAL_CLOCK_SECTOR_SDR` |
| classical | `compact_positive_berger_clock_retained_minimal_layout` | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | `CERTIFIED` | `RETAINED_MINIMAL_LAYOUT_FROZEN` |
| einstein_boundary | `asymptotic_real_cylinder_time` | `H_ESU` | `asymptotically_flat_full_Bach` | `PARTIAL` | `PHASE_SPACE_NOT_CLOSED` |
| einstein_boundary | `compact_positive_berger_clock_einstein_incidence` | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | `CERTIFIED` | `EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND` |
| einstein_boundary | `compact_einstein_maxwell_product_background` | `H_product` | `einstein_maxwell_product_background` | `CERTIFIED` | `COMMON_EINSTEIN_MAXWELL_WEYL_MAXWELL_BACKGROUND` |
| einstein_boundary | `compact_einstein_maxwell_product_tangent_preflight` | `H_product` | `einstein_maxwell_product_principal_tangent_complex` | `PARTIAL` | `PRINCIPAL_TANGENT_CHAIN_MAP_WITH_EXTRA_WEYL_CLASSES` |
| einstein_boundary | `compact_einstein_maxwell_product_on_shell_tangent` | `H_product` | `einstein_maxwell_product_on_shell_linear_tangents` | `CERTIFIED` | `FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON` |
| einstein_boundary | `compact_einstein_maxwell_second_order_fixed_flux` | `H_product` | `einstein_maxwell_product_compact_fixed_flux_second_order` | `CERTIFIED` | `SECOND_ORDER_FIXED_FLUX_OBSTRUCTION_FOR_RADION_AND_DUALITY` |
| einstein_boundary | `universal_cover_einstein_maxwell_second_order_null_extension` | `H_product` | `einstein_maxwell_product_universal_cover_null_second_order` | `CERTIFIED` | `NONZERO_CHEVRETON_NULL_TANGENT_EXTENDS_AT_SECOND_ORDER` |
| einstein_boundary | `compact_einstein_maxwell_periodic_photon_second_order` | `H_product` | `einstein_maxwell_product_compact_fixed_charge_periodic_photon_second_order` | `CERTIFIED` | `PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION` |
| einstein_boundary | `compact_einstein_maxwell_periodic_graviton_second_order` | `H_product` | `einstein_maxwell_product_compact_fixed_charge_periodic_graviton_second_order` | `CERTIFIED` | `PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION` |
| einstein_boundary | `compact_einstein_maxwell_obstruction_bilinear_g1` | `H_product` | `einstein_maxwell_product_compact_fixture_span_obstruction_bilinear` | `CERTIFIED` | `G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN` |
| einstein_boundary | `compact_einstein_maxwell_domain_taub_descent` | `H_product` | `einstein_maxwell_product_compact_fixed_u1_harmonic_taub` | `CERTIFIED` | `G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT` |
| einstein_boundary | `compact_einstein_maxwell_harmonic_adjoint_block_preflight` | `H_product` | `einstein_maxwell_product_compact_harmonic_block_preflight` | `CERTIFIED` | `G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT` |
| einstein_boundary | `compact_einstein_maxwell_axial_master_complex` | `H_product` | `einstein_maxwell_product_compact_axial_master_complex` | `CERTIFIED` | `G1_AXIAL_ALL_MOMENTA_MASTER_COMPLEX` |
| einstein_boundary | `compact_einstein_maxwell_polar_master_preflight` | `H_product` | `einstein_maxwell_product_compact_polar_master_preflight` | `CERTIFIED` | `G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT` |
| einstein_boundary | `compact_einstein_maxwell_polar_master_complex` | `H_product` | `einstein_maxwell_product_compact_polar_master_complex` | `CERTIFIED` | `G2_POLAR_ELL_GE2_ARBITRARY_LAMBDA_TENSOR_IDENTITY` |
| einstein_boundary | `compact_einstein_maxwell_polar_exceptional_complex` | `H_product` | `einstein_maxwell_product_compact_polar_exceptional_complex` | `CERTIFIED` | `G2_POLAR_ALL_ELL_LINEAR_COMPLEX` |
| einstein_boundary | `compact_einstein_maxwell_radiative_symplectic_matching` | `H_product` | `einstein_maxwell_product_compact_radiative_symplectic` | `CERTIFIED` | `G2_RADIATIVE_COVARIANT_SYMPLECTIC_MATCHING` |
| einstein_boundary | `compact_einstein_maxwell_exceptional_global_symplectic` | `H_product` | `einstein_maxwell_product_compact_exceptional_global_symplectic` | `CERTIFIED` | `G2_EXCEPTIONAL_GLOBAL_SYMPLECTIC_COMPLETION` |
| einstein_boundary | `compact_einstein_maxwell_weyl_symplectic_preflight` | `H_product` | `einstein_maxwell_product_compact_weyl_symplectic_preflight` | `CERTIFIED` | `G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE` |
| einstein_boundary | `compact_einstein_maxwell_weyl_axial_ell2_restriction` | `H_product` | `einstein_maxwell_product_compact_weyl_axial_ell2_restriction` | `CERTIFIED` | `G1_AXIAL_ELL2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION` |
| nonlinear | `compact_selected_residual_HT1_q2` | `D_compact` | `compact_selected_residual_HT1` | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |
| nonlinear | `compact_positive_berger_clock_retained_q2_26` | `D_compact` | `positive_berger_fixed_coupling_linearized_solutions` | `CERTIFIED` | `RETAINED_Q2_26_COMPLETE_BARE_LOCAL_UNARY_D_CARTAN_OBSTRUCTED` |
| quantum | `vacuum_cylinder` | `D_compact` | `compact_quantum` | `BLOCKED` | `NO_VERDICT` |

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: certified scalar-clock scope theorem (the single-scalar no-go now qualifies) plus at least one complete boundary or interaction theorem.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`BERGER_CHARACTERISTIC_COHOMOLOGY_AND_RETAINED_CAUSAL_EXTENSION`: The exact retained q2_26 transfer is complete and the bare local unary D-Cartan ansatz is ruled out. Compute the full characteristic symbol-cohomology carrier module, then pursue residual/BFV and retained causal Green extensions independently without weakening the separate QME, Einstein-incidence, or Einstein--Maxwell tangent gates.

## Imported evidence

- `classical`: `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json` at `7b352307eb2adb0dfb8e76b7d24f0bb94a37cc8d`, SHA-256 `35d75f22d9cb6703b2cd4283c5e1ccde296045dc42fcc3bf177308c9ce76f5b3`
- `einstein_boundary`: `bridge/certificates/d_quotient_asymptotic_seed.json` at `7e87281c416f4c4f98edfe61ae05829f4b48593a`, SHA-256 `ce1a6d0ac020eea9ddc95261f6f5003dbce03d8f007e44258b398f05febb2685`
- `nonlinear`: `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json` at `29fb5db6a70932ca68810cfcdc3c1187441de3fb`, SHA-256 `a544aceaea2618ba5a2a7d5b03e7f69b87c6ef3df156da3b7b0a16c04a37ae8d`
- `quantum`: `quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json` at `a7cdaad7d34fad49ee284f6b7dbb3d67408a31d6`, SHA-256 `9f450477532a24edbd02282f29593876a13ea886808a6c9ba06b41004653f8da`

## Claim boundary

The dossier consolidates sector-indexed results. It does not promote a universal D-gauge verdict, an interacting Cartan theorem, a quantum anomaly result, or an asymptotic charge theorem.

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
