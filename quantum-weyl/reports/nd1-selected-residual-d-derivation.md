# ND1 selected residual arity-two D-derivation defect

Date: 2026-07-15

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Result state: `SELECTED_RESIDUAL_Q2_D_DEFECT_COMPUTED_FULL_LOCAL_INPUT_BLOCKED`

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

The first nonlinear `D`-quotient calculation is now executable on the complete
field domain exported by HT1.  For every available binary Taylor block, the
certificate computes the full tensor

```text
Delta_D q2(x,y) = L_D q2(x,y) - q2(L_D x,y) - q2(x,L_D y).
```

The result is exactly zero:

| selected HT1 block | nonzero `q2` components | checked defect coefficients | nonzero defect coefficients | `D`-weight violations | particle-number change |
|---|---:|---:|---:|---:|---:|
| ghost, ghost -> ghost | 180 | 3,375 | 0 | 0 | 0 |
| ghost, matter -> matter | 1,808 | 261,360 | 0 | 0 | 0 |
| matter, matter -> ghost momentum | 1,808 | 261,360 | 0 | 0 | -2 |
| ghost, ghost momentum -> ghost momentum | 180 | 3,375 | 0 | 0 | 0 |

Thus all 3,976 nonzero selected components preserve their derived `D` weight,
and all 529,470 coefficients of the four derivation-defect tensors vanish.
The ghost/momentum and bra/ket `D` weights are opposite, so the selected
pairing weights are neutral.  The sparse machine payload records each full
defect shape and coordinate convention; its empty entry lists are computed
outputs, not assumed answers.

This excludes an arity-two `D`-derivation counterexample inside the selected
finite residual BFV model.  It is consistent with the exact conformal
equivariance already implicit in the HT1 cubic master-equation certificate,
but is independently evaluated here component by component.

## Claim boundary

This is not yet the verdict requested by the nonlinear `D`-quotient brief.
The selected residual bracket is downstream of endpoint projection and does
not serialize the arbitrary-input support-local `q2`.  The Diff/Weyl
ghost-metric rows, antifield rows, full `q1`, portable cyclic pairing, and the
classical contraction maps `pi_cl`, `iota_cl`, and `s_cl` have not passed the
import gate.  Consequently no correction `iota_D^(2)` has been constructed
and no obstruction class in the full deformation complex has been
trivialized.

The imported classical setting ledger also remains decisive: `D` is charged
on unrestricted `P_lin` and becomes gauge only after restriction to the
declared full Taub-zero derived sector.  Zero residual defect does not erase
that sector distinction.

No `q3`, arity-three identity, quartic instability channel, boundary charge,
scalar clock, quantum correction, or `LORENTZIAN-CAUSAL` theorem is claimed.

## Next exact gate

Import the complete support-local `q2`, its ghost and antifield completions,
and the certified free contraction.  Then recompute the same full defect and
solve

```text
[q1, iota_D^(2)] = -Delta_D q2
```

with an explicit primitive, or retain the normalized nontrivial obstruction
class.  Only that calculation can promote the vacuum-cylinder verdict to
`INTERACTING_CARTAN_EXISTS` or `INTERACTING_CARTAN_OBSTRUCTED`.

## Machine receipt

`quantum-weyl/transfer/certificates/ND1_SELECTED_RESIDUAL_D_DERIVATION.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/d_derivation_certificate.py --emit` | 3.37 | PASS | 1 |
| `python3 -m unittest quantum-weyl/transfer/tests/test_d_derivation_defect.py -v` | 8.00 | PASS (8 tests, including a generated nonzero defect) | 1 |
| `python3 quantum-weyl/transfer/residual_cubic_certificate.py --check` | 46.20 | PASS | 2 |
| `python3 d_quotient_classical/verify_classical_status.py --guards` | 0.03 | PASS (6 mutation guards) | 2 |
| `PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check` | 0.07 | PASS (related quantum rail remains fail-closed) | 2 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 46.87 | PASS (42 tests) | 1 |

The affected nonlinear bootstrap consumer is regenerated in the same commit.
Tier 3 is unnecessary because the calculation consumes unchanged
content-addressed inputs, changes no shared algebra, and promotes no complete
interacting, quantum, paper, or Lorentzian claim.
