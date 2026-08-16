# Strict M1B typed cyclic composite

**Result:** `STRICT_M1B_TYPED_CYCLIC_COMPOSITE_V1`
**Lifecycle:** `CLASSIFIED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Result

M1B is complete as a typed action-cyclic contraction on represented energies
two through six.  The certified primal and action-adjoint halves retract onto
470 primal plus
470 compact-source action-dual
residual classes.  Their odd action pairing has exact rank
940.

The independent finite core has 8,160
coordinates and replays thirteen contraction, chain, normalized-side-condition,
cyclicity, adjointness, skew-homotopy, and inclusion-isometry identities with
0 defects.

## What changed relative to the older M4R comparison

The old formal cotangent comparison had 8,980 coordinates.  The current replay
removes 820 coordinates: the
primal and dual copies of exactly 410 comparison-only test rows.  The remaining
finite dual half is still a check core, not an authoritative source.  Authority
comes from the rank-386 local action pairing, the typed primal graph composite,
and the compact-source residual dual dictionary.

## Boundary and next gate

M1B completion does not pass Gate A.  M1C must bind all twenty exports and
seven hashes into one immutable manifest and independently replay all ten gate
checks on those exact bytes.  Nonlinear Green compatibility, a BRST-compatible
Hadamard function, renormalized Lorentzian products, QME restoration, and
residual transfer remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m1b_typed_cyclic_composite.py --check
python3 quantum-weyl/classical_import/check_strict_m1b_typed_cyclic_composite.py
python3 -m pytest -q quantum-weyl/classical_import/tests/test_strict_m1b_typed_cyclic_composite.py
```
