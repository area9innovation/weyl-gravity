# Strict D-finite cotangent-dual comparison

**Result:** `STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M3RC-A:** `COMPLETE`
**M3RC-B:** `OPEN`

## Same-source obstruction

The unchanged D-finite source does not contain the missing dual cohomology.

| Energy | degree-0 chain rows | degree-1 chain rows | H0 | H1 |
|---:|---:|---:|---:|---:|
| 2 | 110 | 10 | 10 | 0 |
| 3 | 220 | 20 | 40 | 0 |
| 4 | 385 | 44 | 82 | 0 |
| 5 | 616 | 92 | 136 | 0 |
| 6 | 924 | 174 | 202 | 0 |

Globally, the original source has H0 dimension 470 and H1 dimension zero.  A
deformation retract cannot change cohomology, so the 4,490-coordinate source
cannot retract onto the desired 940-coordinate cotangent residual carrier.

## Exact formal repair

The explicit shifted cotangent source has 8980 coordinates
and retracts onto 940 residual coordinates.  Its maps
are reconstructed exactly from the certified primal SDR:

```text
q_dual    = -q0^T
iota_dual =  pi_cl^T
pi_dual   =  iota_cl^T
s_dual    = -s_cl^T
```

All dual SDR identities, canonical-pairing cyclicity, homotopy skewness and
cotangent-inclusion isometry have zero exact defects.  The full and residual
canonical odd pairings have ranks 8980 and
940.

## Boundary and next gate

This is a finite algebraic cotangent completion, not yet the action-derived
dual of the original field complex.  The next step must declare paired
support/topology classes and prove that harmonic integration identifies the
formal evaluation pairing and transposed maps with the local BV density.  M4R,
M1, Gate A, Hadamard and QME remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_dfinite_cotangent_dual_comparison.py --check
python3 quantum-weyl/classical_import/check_strict_dfinite_cotangent_dual_comparison.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_dfinite_cotangent_dual_comparison.py
```
