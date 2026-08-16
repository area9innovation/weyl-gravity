# Strict typed residual cyclicity v1

**Result:** `STRICT_TYPED_RESIDUAL_CYCLICITY_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**M4R:** `COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Outcome

The action-identified residual cotangent carrier has
940 coordinates and exact odd-pairing rank
940.  An independent sparse replay reconstructs
all five energy blocks and verifies the cyclic contraction identities with
0 defects.  In particular, `q_res=0` is cyclic,
`pi_cotangent=iota_cotangent^sharp`, the homotopy is skew-adjoint, inclusion
preserves the odd pairing, and every normalized SDR side condition holds.

This closes M4R on represented energies two through six.  M3RC-B is essential:
it identifies the 470 degree-one coordinates with compact-source causal
classes and identifies the residual signed-permutation form with the
action-derived Cauchy/Green pairing.

## Boundary

The 8980-coordinate source used in the replay is
the explicit formal shifted-cotangent comparison source.  This certificate
does not declare it to be the authoritative full classical BV source.  M1 must
still bind all local, nonlinear, causal and residual objects under one common
manifest.  Gate A therefore remains fail closed, and no Hadamard,
renormalization, QME or residual quantum-transfer claim is promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_typed_residual_cyclicity.py --check
python3 quantum-weyl/classical_import/check_strict_typed_residual_cyclicity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_typed_residual_cyclicity.py
```
