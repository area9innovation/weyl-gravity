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
incidence. This is a background theorem only; its perturbative covariant
charge, all-row BV reduction, causal propagation, and stability remain open.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
| classical | `POSITIVE_CLOCK_BACKGROUND_EXISTS_CHARGE_OPEN` | The standard one-field stealth route is ruled out, while an exact non-conformally-flat Berger-cylinder family carries a healthy rotating two-scalar phase clock. The action and SU(2) volume are frozen, Q_R is nonzero, and Omega_total(delta,L_D)=omega delta Q_R. Fixed couplings force delta q=0 in the stationary family. | construct or exclude an allowed fixed-coupling linearized delta-Q_R tangent, then complete the all-row BV audit |
| einstein_boundary | `PHASE_SPACE_NOT_CLOSED` | H_ESU, D_M, D_rad, and P_0 cannot be silently identified in the real asymptotic problem. | complete a boundary-preserving full Bach phase space and calculate charge and flux |
| nonlinear | `INPUT_GATE_BLOCKED` | selected residual q2 D-derivation defect vanishes exactly; full support-local verdict remains blocked | complete support-local q2 export and solve for iota_D^(2) or retain its obstruction |
| quantum | `ANALYTIC_FRAMEWORK_MISSING` | the pre-scalar classical compact split is imported by content hash without quantum promotion; the new scalar no-go is not yet imported | import the scalar-clock obstruction hash, then construct the renormalized observable algebra and classify the first D-Ward obstruction |

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
6. interacting promotion requires a corrected Cartan homotopy
7. quantum promotion requires a restored QME and renormalized Ward identity

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
| einstein_boundary | `asymptotic_real_cylinder_time` | `H_ESU` | `asymptotically_flat_full_Bach` | `PARTIAL` | `PHASE_SPACE_NOT_CLOSED` |
| nonlinear | `compact_selected_residual_HT1_q2` | `D_compact` | `compact_selected_residual_HT1` | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: certified scalar-clock scope theorem (the single-scalar no-go now qualifies) plus at least one complete boundary or interaction theorem.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT`: Use the exact identity Omega_total(delta,L_D)=omega delta Q_R. Construct or exclude an allowed fixed-coupling linearized tangent with delta Q_R nonzero; only then classify D and proceed to the support-local all-row BV clock contraction, causal theory, and stability audit.

## Imported evidence

- `classical`: `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json` at `958f51a700a839baf4d526c6a207c893048dfe62`, SHA-256 `ca4a6f632aaf6d5cc903fcf1dee9a0c69d1d935b1b174df590ffcc430b59c776`
- `einstein_boundary`: `bridge/certificates/d_quotient_asymptotic_seed.json` at `89acca36479ebaea069c21eb23517dc6b1b49389`, SHA-256 `359914fbb0122ee49e8351b5b87d62c536adbfeb4d754a3deebf87ac3ecb6663`
- `nonlinear`: `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json` at `84dd459381bc4bc6219c5012594b018992b636c8`, SHA-256 `466db529891e3d306b704f2ceb119598386f74893274b051a56babba409a2cd8`
- `quantum`: `quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json` at `04e9d20c2c5dd7b2d3fa62492fdc7e12e2fe1f61`, SHA-256 `aa7edc21c7250349531559657d4ec69eee2dd9100de3eedf242a8e29829e874c`

## Claim boundary

The dossier consolidates sector-indexed results. It does not promote a universal D-gauge verdict, an interacting Cartan theorem, a quantum anomaly result, or an asymptotic charge theorem.

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
