# Classical import Gate-A reconciliation v3

**Result:** `CLASSICAL_IMPORT_GATE_V3_RECONCILIATION`

**Lifecycle:** `CLASSIFIED`

**Gate A:** `FAIL_CLOSED`

## Outcome

The historical residual-map portability gap is closed in one exact scope:
the strict pure-Weyl BGG-adapted `D`-finite blocks at energies two through six.
The receiver replays **4490 full**
and **470 residual**
coordinates.  Gate A remains fail-closed because these are not the maps on one
common full support-local carrier.

## Three map exports

| Export | Current status | Still required for Gate A |
|---|---|---|
| `classical_inclusion_iota_cl` | `RECEIVER_VERIFIED_SCOPED` | Construct the inclusion on the one common full support-local strict carrier, including every required nonminimal and local row. |
| `classical_projection_pi_cl` | `RECEIVER_VERIFIED_SCOPED` | Construct pi_cl on the one common full support-local strict carrier and bind it to the common pairing and residual payload. |
| `classical_homotopy_s_cl` | `RECEIVER_VERIFIED_SCOPED` | Construct s_cl on the one common full support-local strict carrier with the complete nonminimal field domain and shared conventions. |

## Four freeze identities

| Check | Current status | Boundary |
|---|---|---|
| `pi_cl_iota_cl_identity` | `RECEIVER_VERIFIED_SCOPED` | Exact finite-block identity does not imply a common support-local carrier exists. |
| `classical_contraction_identity` | `RECEIVER_VERIFIED_SCOPED` | The finite split contraction omits the complete nonminimal field domain and cannot be relabelled as a causal Green homotopy. |
| `q0_iota_intertwining` | `RECEIVER_VERIFIED_SCOPED` | A zero finite positive-energy residual differential is not the complete residual CE/BFV action. |
| `pi_q0_intertwining` | `RECEIVER_VERIFIED_SCOPED` | The finite split projection does not serialize the full SO(4,2) residual action or centered complex. |

## M3 is narrowed, not deleted

The exact finite payload is now the receiver control.  The remaining M3 task is
to extend or reconstruct the maps with the complete nonminimal field domain and
shared cyclic conventions on the same support-local carrier required by M1,
M2 and M4.  A finite-mode direct sum does not prove that continuum object.

## Gate verdict

No accepted common snapshot hash exists.  Strict `q2`, `D`, the full cyclic
pairing, the complete residual SO(4,2) payload and centered representatives
remain outside one common snapshot.  No Hadamard, QME or residual-transfer
claim is promoted.

## Exact commands

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v3_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v3_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v3_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v3_reconciliation.py
```

## What this does not establish

- normalized Weyl-square representative coefficient vectors.
- explicit centered H3 and H5 bases.
- a BRST-compatible Hadamard state.
- renormalized Lorentzian products.
- QME restoration or residual quantum transfer.
- that the D-finite split residual SDR is the common full support-local Gate-A residual contraction.
- that finite exact arithmetic proves the all-energy direct sum or continuum carrier.
