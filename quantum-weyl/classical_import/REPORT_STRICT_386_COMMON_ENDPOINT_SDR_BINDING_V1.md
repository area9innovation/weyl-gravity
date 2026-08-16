# Strict 386-row common endpoint-SDR binding

**Result:** `STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Result

M3L is complete.  One content-addressed receiver manifest now binds the exact
386-row graph basis, pairing, q1, local endpoint inclusion, projection and
homotopy, complementary projectors, transported suspension, represented Green
names, cylinder-flow D action, and the exact graph-transport DAGs for source q2
and q3.

The manifest contains 17 canonical object hashes
and 10 artifact pins.  All
15 independent cross-certificate links
agree.  The endpoint contraction, normalized side conditions, endpoint SDR
cyclicity, q1/q2, q2 cyclicity, D/q2, arity three, q3 cyclicity and D/q3 defect
counts are zero on the pinned artifacts.

## What changed

No new homotopy was invented.  The result proves that the already exact local
graph SDR and the later q2/q3/D layers use the same basis, odd pairing, split
q1, canonical shear and graph q1 bytes.  This is the common binding requested
by `M3L_COMMON_ENDPOINT_SDR_BINDING`.

## Boundary

M3R remains open.  This manifest contains no harmonic restriction, W+/W-
projection or zero-mode projection, and it does not identify thirty endpoint
field species with any global coefficient carrier.  Full residual cyclicity,
nonlinear Green compatibility, Gate A, Hadamard, renormalized products, QME and
residual quantum transfer remain open.  No new Gate-A top-level hash is
accepted by this scoped binding.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_common_endpoint_sdr_binding.py --check
python3 quantum-weyl/classical_import/check_strict_386_common_endpoint_sdr_binding.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_common_endpoint_sdr_binding.py
```
