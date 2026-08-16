# Strict endpoint-to-residual spectral comparison

**Result:** `STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1`
**Dependency boundary:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M3R:** `COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Result

The thirty local endpoint species now have a typed comparison with the
positive-energy residual carrier after restricting to represented global
cylinder harmonics at energies two through six.  This is not a local
position-space projection.  It is a finite spectral comparison, and every
support-expanding map is labeled `REDUCED-MODE`.

| Energy | Total | W+ | W- | W+ family dimensions |
|---:|---:|---:|---:|---|
| E2 | 10 | 5 | 5 | E:5 |
| E3 | 40 | 20 | 20 | E:12, A:8 |
| E4 | 82 | 41 | 41 | E:21, A:15, L:5 |
| E5 | 136 | 68 | 68 | E:32, A:24, L:12 |
| E6 | 202 | 101 | 101 | E:45, A:35, L:21 |

The resulting ordered basis has 470 elements.  Each old generic label is
refined by chirality, E/A/L family, and exact doubled magnetic weights.  The
normalization of every magnetic state is determined by finite SU(2) lowering
from a coordinate-verified highest-weight metric representative.  The
portable BGG split then gives exact analysis and synthesis maps with
`pi_M3R iota_M3R=1`, `q0 iota_M3R=0`, and `pi_M3R q0=0`.

## Boundary

The certificate does not serialize raw coordinate tensors for all 470 modes
and does not claim a map on compactly supported sections, distributions, or
an all-energy smooth completion.  Energies zero and one are excluded and
remain in the separate conformal-Killing zero-mode payload.  No Hilbert or
Krein completion and no choice principle is used by the fixed finite core.

M4R residual cyclicity and the M1 common freeze remain open.  Consequently
Gate A, Hadamard, renormalization, QME, and quantum residual transfer remain
fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_endpoint_to_residual_spectral_comparison.py --check
python3 quantum-weyl/classical_import/check_strict_endpoint_to_residual_spectral_comparison.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_endpoint_to_residual_spectral_comparison.py
```
