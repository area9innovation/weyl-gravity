# Strict centered cohomology payload v1

**Result:** `STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Gate A:** `FAIL_CLOSED`

The centered finite complex is now portable rather than summarized by names
and dimensions.  It contains ordered bases

| carrier | dimension |
|---|---:|
| `C3` | 727 |
| `C4` | 3084 |
| `C5` | 8532 |

The certificate serializes the finite coefficient actions.  A receiver that
does not import the producer reconstructs `d3` and `d4`, checks exact
nilpotency, and obtains ranks `636` and `2446`.  Two independently
exhibited non-boundary cocycles saturate the remaining rational kernel, so
`dim H4 = 2` exactly.

The two representatives are explicit sparse vectors over `Q(sqrt(10))` in
the declared 3,084-coordinate `C4` basis.  Their Gram matrix is `I2`, and
orientation reversal exchanges them.  They are the deformation/vertex
classes `W_+^2 v_-` and `W_-^2 v_-`; they are not one-particle states.

This closes the finite coefficient package `M6_CENTERED_REPRESENTATIVES`.
Its candidate hash is not accepted by Gate A.  The common support-local
residual SDR, the full cyclic pairing and a single all-object freeze remain
open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_centered_cohomology_payload.py --check
python3 quantum-weyl/classical_import/check_strict_centered_cohomology_payload.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_strict_centered_cohomology_payload.py'
```
