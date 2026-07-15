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
reattached full gauge presentation has an exact scalar-biwave principal
witness. Curved lower-order witness terms, the total causal homotopy,
nonminimal rows, `q2`, and stability remain open. The Einstein-incidence audit
separately classifies this background as a non-Einstein Weyl--matter branch.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
| classical | `D_GAUGE_ON_POSITIVE_BERGER_FIXED_COUPLING_LINEARIZED_SPACE` | The healthy positive Berger background has D_GAUGE on its fixed-coupling linearized phase space. The complete retained minimal q1 is exact and cyclic; its 34-row unary operator and exact clock contraction are frozen portably for downstream consumers. The retained causal endpoints are Green-hyperbolic and reattaching the clock rows gives a full scalar-biwave principal witness. | construct the curved clock-reattached witness and total causal homotopy, then reattach nonminimal rows and export q2 |
| einstein_boundary | `PHASE_SPACE_NOT_CLOSED` | H_ESU, D_M, D_rad, and P_0 cannot be silently identified in the real asymptotic problem. The positive Berger clock is a non-Einstein Weyl--matter branch. A separate positive Einstein--Maxwell/Weyl--Maxwell product background now supplies an exact common base point without yet supplying a tangent phase space. | construct the two minimal metric--Maxwell BV complexes, chain map, cohomology, and presymplectic comparison at the certified product base point; independently complete the asymptotic Bach phase space and charge audit |
| nonlinear | `INPUT_GATE_BLOCKED` | selected residual q2 D-derivation defect vanishes exactly; full support-local verdict remains blocked | complete support-local q2 export and solve for iota_D^(2) or retain its obstruction |
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
| compact_selected_residual_HT1_q2 | `D_compact` | `compact_selected_residual_HT1` | INTERACTING | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |
| compact_interacting | `D_compact` | `compact_interacting` | INTERACTING | `BLOCKED` | `INPUT_GATE_BLOCKED` |
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
6. Berger retained minimal q1 and the reattached scalar-biwave principal witness are complete; curved witness terms, total causal homotopy, nonminimal rows, q2, and arity-two stability remain open
7. the Einstein--Maxwell product common background is certified; its two tangent BV complexes, chain map, cohomology, presymplectic comparison, and all D/charge questions remain open
8. interacting promotion requires a corrected Cartan homotopy
9. quantum promotion requires a restored QME and renormalized Ward identity

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
| nonlinear | `compact_selected_residual_HT1_q2` | `D_compact` | `compact_selected_residual_HT1` | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |
| quantum | `vacuum_cylinder` | `D_compact` | `compact_quantum` | `BLOCKED` | `NO_VERDICT` |

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: certified scalar-clock scope theorem (the single-scalar no-go now qualifies) plus at least one complete boundary or interaction theorem.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`BERGER_CURVED_CLOCK_REATTACHED_WITNESS`: The fixed-coupling D_GAUGE gate, clock SDR, complete retained minimal q1, causal endpoint factors, and reattached scalar-biwave principal witness are complete. Construct the curved lower-order witness and total causal homotopy without weakening the separate nonminimal, q2, arity-two, or Einstein-incidence gates.

## Imported evidence

- `classical`: `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json` at `9278ba7dffa2e8d85292c2a8cc25b03f0ca47847`, SHA-256 `f4f1b07b4a212ab453d9270744691d8554df36ef8bc24d456d6a7a4a5bc77ec6`
- `einstein_boundary`: `bridge/certificates/d_quotient_asymptotic_seed.json` at `7e87281c416f4c4f98edfe61ae05829f4b48593a`, SHA-256 `ce1a6d0ac020eea9ddc95261f6f5003dbce03d8f007e44258b398f05febb2685`
- `nonlinear`: `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json` at `3ff7608b8a8e855f365db6628672301f65d17d81`, SHA-256 `fc7bbe05b5ea7c2c89a55b305677e019a9e7e9b146ae064606128025a2707b12`
- `quantum`: `quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json` at `2aec6ed91793d136c9a6d80a0f74b2b233775d49`, SHA-256 `d4c235dd3b28bc9c2934feff035d358855212fd176d5f7da0dedac3a09ef5d9e`

## Claim boundary

The dossier consolidates sector-indexed results. It does not promote a universal D-gauge verdict, an interacting Cartan theorem, a quantum anomaly result, or an asymptotic charge theorem.

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
