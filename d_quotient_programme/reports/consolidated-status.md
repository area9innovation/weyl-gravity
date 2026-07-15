# Consolidated \(D\)-quotient programme status

## Interpretation

There is no universal yes/no verdict for \(D\).  The authoritative claim key is

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

The compact result is sector-dependent: \(D\) is charged on the unrestricted
locally reduced linearized space, and it becomes gauge only after restriction
to the full Taub/moment-map zero fibre and the selected derived quotient.
The first one-real-scalar exact-cylinder clock candidate is obstructed before
a coupled phase space exists.  A distinct neutral two-field reference sector
now supplies an exact homogeneous clock and a scoped `D_GAUGE` reduction, but
its inhomogeneous BV and health questions remain open. Boundary, nonlinear,
and quantum questions are separate gates.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
| classical | `SECTOR_DEPENDENT_WITH_SCOPED_NEUTRAL_CLOCK_D_GAUGE` | D_compact is charged on compact_P_lin, gauge on compact_P_Taub0/compact_P_der, and gauge on the exact homogeneous neutral two-field clock sector; the one-real-scalar candidate remains obstructed. | support-local inhomogeneous neutral-clock BV completion and health audit of its opposite-sign reference sector |
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
| einstein_boundary | `asymptotic_real_cylinder_time` | `H_ESU` | `asymptotically_flat_full_Bach` | `PARTIAL` | `PHASE_SPACE_NOT_CLOSED` |
| nonlinear | `compact_selected_residual_HT1_q2` | `D_compact` | `compact_selected_residual_HT1` | `PARTIAL` | `SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO` |

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: certified scalar-clock scope theorem (the single-scalar no-go now qualifies) plus at least one complete boundary or interaction theorem.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION`: Import the certified neutral two-field homogeneous sector by hash, construct its support-local inhomogeneous BV complex, and determine whether the opposite-sign reference direction is entirely gauge or contractible.

## Imported evidence

- `classical`: `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json` at `a558ecf6eae7259ebd9dfef048602b83f9ccf9e4`, SHA-256 `592ec58f7604fda6a7702f6e9898b0044da657aeb28e5253a408096c2c5cb4d9`
- `einstein_boundary`: `bridge/certificates/d_quotient_asymptotic_seed.json` at `89acca36479ebaea069c21eb23517dc6b1b49389`, SHA-256 `359914fbb0122ee49e8351b5b87d62c536adbfeb4d754a3deebf87ac3ecb6663`
- `nonlinear`: `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json` at `b49e055fcba87540343c97f9736887b5321f6062`, SHA-256 `87ab515cf19a29077af086d3d0c3d32f204ae31f77c42a75ae72fa6473162592`
- `quantum`: `quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json` at `04e9d20c2c5dd7b2d3fa62492fdc7e12e2fe1f61`, SHA-256 `aa7edc21c7250349531559657d4ec69eee2dd9100de3eedf242a8e29829e874c`

## Claim boundary

The dossier consolidates sector-indexed results. It does not promote a universal D-gauge verdict, an interacting Cartan theorem, a quantum anomaly result, or an asymptotic charge theorem.

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
