# Classical import Gate-A reconciliation v18

**Result:** `CLASSICAL_IMPORT_GATE_V18_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

Gate V18 repairs a type error in the former `M3_RESIDUAL_SDR` requirement.
The exact graph SDR maps 386 local component
species onto 30 endpoint field species.
The D-finite SDR instead maps 4,490 harmonic
coefficients onto 470 W+/W- coefficients.
M5's separate number thirty counts conformal-Killing cotangent coefficients.
These are not interchangeable carriers.

A global constant or harmonic projector expands support, so the existing
reduced-mode receiver cannot be inserted as a support-local map in the causal
Green-transfer premise.  The old M3 item is replaced by:

- `M3L_COMMON_ENDPOINT_SDR_BINDING`, using the already exact local graph SDR;
- `M3R_TYPED_RESIDUAL_COMPARISON`, explicitly nonlocal and `REDUCED-MODE`.

Gate A still accepts one of seven hashes.  No export or freeze count is
promoted, and four typed packages remain: M1, M3L, M3R and M4.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v18_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v18_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v18_reconciliation.py
```
