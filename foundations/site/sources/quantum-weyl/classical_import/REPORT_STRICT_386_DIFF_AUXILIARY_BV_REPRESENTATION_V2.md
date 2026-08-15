# Strict 386-row Diff auxiliary BV representation v2

**Result:** `STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2`
**Dependency:** `LOCAL-ALGEBRAIC`

V1 used the source momentum-map sign for the auxiliary `c_star` outputs after
the minimal receiver had already adopted the canonical cotangent translation
`T(c_star)=-c_star`.  That mixed two coordinate conventions.  The append-only
V2 repair translates all **704** auxiliary
Diff momentum-map coefficients and changes no field or auxiliary-antifield
output.

The mismatch is executable rather than cosmetic.  Composing V1 with the full
unary table and the shifted-mass `q2` leaves
**336 nonzero rational
coefficients in 168 channels**.
After the certified translation, the same exhaustive row-0..65 composition
has **0 defects**.
The same cotangent translation retains the 264-term Hamiltonian-density
reconstruction and has **0 canonical
cyclicity defects**.

This closes the coupled auxiliary arity-two identity, but it does not yet bind
the minimal and auxiliary operations into one common source-q2 snapshot or
construct the metric-dependent auxiliary `q3`.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation_v2.py --check
python3 quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation_v2.py
python3 quantum-weyl/classical_import/verify_strict_386_diff_auxiliary_bv_representation_v2.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_diff_auxiliary_bv_representation_v2
```
