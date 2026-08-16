# Strict M2 q2/q3 typed Green compatibility

**Result:** `STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1`

**Classical snapshot:** `STRICT_PURE_WEYL_BV_SNAPSHOT_07dc7271b95b263a`

**Causal envelope SHA-256:** `3d21d69778f9645f9358c8edd16d399e2998accdef1e22c41d1c02782f14fb7c`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

The authoritative Gate-A `q2` and `q3` now compose with both graph Green
homotopies on declared support spaces.  The retarded orientation maps compact
or past-compact sources to past-compact responses; the advanced orientation
maps compact or future-compact sources to future-compact responses.  Locality
of `q2` and `q3` preserves support intersections.  The unary homotopy,
arity-two, arity-three, cyclic and advanced/retarded adjoint identities replay
on the same rank-386 pairing with zero defects.

This is a post-freeze causal envelope over the immutable snapshot.  It does not
change the snapshot or silently insert the Green maps among the twenty Gate-A
exports.

## Nonlinear consequence

Every finite response tree built from same-orientation `Lambda q2` and
`Lambda q3` vertices is well-defined and continuous on fixed support steps.
More decisively, for every compact, `q1`-closed, suspended-degree-zero input
`x`, the second nonlinear source

```text
S2 = (1/2)(q2(x,r1) + q2(r1,x)) + (1/6)q3(x,x,x)
r1 = -(1/2)Lambda q2(x,x)
```

is compact and `q1`-closed.  The general arity-three identity gives
`q1 q3(x,x,x) = -3 J_q2(x)`, so the coefficient residual is
`1/2 - 3/6 = 0`.  The constrained field-equation Green component therefore
solves the second response modulo gauge in both orientations.  This retires
the old q2-only obstruction; it does not prove an all-order Moller theorem.

## Boundary and next gate

Mixed-sign trees are not uniformly defined on the present PC/FC spaces, no
infinite tree series is summed, and no distribution-kernel coordinate table is
serialized.  Most importantly, this is classical nonlinear causal
compatibility, not a Hadamard two-point function.  The next gate is to construct
a full-complex BRST-compatible Hadamard kernel—or prove a scoped obstruction
from an explicit incompatible subset of the bisolution, CCR, wavefront, Ward,
pairing and positivity requirements.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m2_q2_q3_typed_green_compatibility.py --check
python3 quantum-weyl/classical_import/check_strict_m2_q2_q3_typed_green_compatibility.py
python3 quantum-weyl/classical_import/verify_strict_m2_q2_q3_typed_green_compatibility.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_m2_q2_q3_typed_green_compatibility
```
