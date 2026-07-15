# Consolidated \(D\)-quotient programme status

## Interpretation

There is no universal yes/no verdict for \(D\).  The authoritative claim key is

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

The compact result is sector-dependent: \(D\) is charged on the unrestricted
locally reduced linearized space, and it becomes gauge only after restriction
to the full Taub/moment-map zero fibre and the selected derived quotient.
Boundary, nonlinear, and quantum questions are separate gates.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
| classical | `SECTOR_DEPENDENT` | D_compact is charged on compact_P_lin and gauge on compact_P_Taub0/compact_P_der. | canonical conformal-scalar clock model and total improved D charge |
| einstein_boundary | `PHASE_SPACE_NOT_CLOSED` | H_ESU, D_M, D_rad, and P_0 cannot be silently identified in the real asymptotic problem. | complete a boundary-preserving full Bach phase space and calculate charge and flux |
| nonlinear | `INPUT_GATE_BLOCKED` | selected residual q2 D-derivation defect vanishes exactly; full support-local verdict remains blocked | complete support-local q2 export and solve for iota_D^(2) or retain its obstruction |
| quantum | `ANALYTIC_FRAMEWORK_MISSING` | classical sector split imported by content hash without quantum promotion | construct the renormalized observable algebra and classify the first D-Ward obstruction |

## Setting ledger

| Setting | Generator | Phase space | Layer | Status | Verdict |
|---|---|---|---|---|---|
| compact_unrestricted | `D_compact` | `compact_P_lin` | CLASSICAL_CHARGE | `CERTIFIED` | `D_CHARGED` |
| compact_taub_zero | `D_compact` | `compact_P_Taub0` | CLASSICAL_CHARGE | `CERTIFIED` | `D_GAUGE` |
| compact_derived_residual | `D_compact` | `compact_P_der` | CLASSICAL_CARTAN | `CERTIFIED` | `D_GAUGE` |
| compact_scalar_clock | `D_compact` | `compact_scalar_clock` | CLASSICAL_CHARGE | `OPEN` | `OPEN` |
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

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: scalar-clock theorem plus at least one boundary or interaction theorem.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`SCALAR_CLOCK_VERTICAL_SLICE`: define one canonical conformal-scalar
BV/clock model, then make every downstream team import it by content hash.

## Imported evidence

- `classical`: `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json` at `926e03ce07b3bff437cd942587837504a44fc8fb`, SHA-256 `495de6865c8aa7bceb32a55769cd4f912da6d67035e899b8571843ab504457af`
- `einstein_boundary`: `bridge/certificates/d_quotient_asymptotic_seed.json` at `89acca36479ebaea069c21eb23517dc6b1b49389`, SHA-256 `359914fbb0122ee49e8351b5b87d62c536adbfeb4d754a3deebf87ac3ecb6663`
- `nonlinear`: `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json` at `1d3917394a03c6f5f288ef213d1b90dd98f9097f`, SHA-256 `b18db8505b652640a7777d678eb67f1847e9b129d6ea0a965dae2ba2ca313618`
- `quantum`: `quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json` at `04e9d20c2c5dd7b2d3fa62492fdc7e12e2fe1f61`, SHA-256 `aa7edc21c7250349531559657d4ec69eee2dd9100de3eedf242a8e29829e874c`

## Claim boundary

The dossier consolidates sector-indexed results. It does not promote a universal D-gauge verdict, an interacting Cartan theorem, a quantum anomaly result, or an asymptotic charge theorem.

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
