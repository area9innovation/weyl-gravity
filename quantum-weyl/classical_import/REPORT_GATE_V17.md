# Classical import Gate-A reconciliation v17

**Result:** `CLASSICAL_IMPORT_GATE_V17_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

The finite centered coefficient package `M6` is now complete.  Its ordered
`C3/C4/C5` dimensions are `[727, 3084, 8532]`.  An
independent receiver reconstructs 85,091
nonzero differential coefficients, obtains ranks `[636, 2446]`, and
proves a two-dimensional `H4` with Gram matrix `[[1, 0], [0, 1]]` and
**0** declared identity defects.

This creates a real representative-hash candidate, but adds **zero**
accepted common-freeze hashes.  Gate A still accepts one of seven hashes.
The status totals are now 17 of
20 exports receiver-verified in declared scopes, with the three legacy
rows unchanged.  Three replacement packages remain: `M1`, `M3`, and `M4`.

The adjacent `C3` and `C5` bases are not claims that `H3` or `H5` cohomology
has been computed.  The two `H4` classes are deformation/vertex classes,
not one-particle states.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v17_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v17_reconciliation.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_classical_import_gate_v17_reconciliation.py'
```
