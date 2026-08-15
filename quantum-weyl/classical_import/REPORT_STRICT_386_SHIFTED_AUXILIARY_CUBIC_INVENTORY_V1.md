# Strict 386-row shifted-auxiliary cubic inventory v1

**Result:** `STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1`
**Dependency:** `LOCAL-ALGEBRAIC`

The receiver embeds the exact vv nonlinear field map in the published 386-row
basis.  It serializes **22**
field-map and **16**
cotangent-partner coefficients.  All four `J_v C_b=(D_bF)^T J_f`
canonicality slices have zero defect.  The quadratic correction acts on 14
output rows and is zero on the other 372.

The imported shifted mass has **72** nonzero `h-f_hat-f_hat` coefficients,
whereas the interaction-inert candidate has 0.
Thus the vv shift closes the old `-1+1=0` channel but does not by itself
identify the source with the trivial stabilization.

Seven currently required cubic families are enumerated.  Two are now
component-complete; hh, hv and three Diff BV representation families remain
open.  The source manifest is not yet exhaustive for nonlinear Weyl/boost
ghost-antifield channels, so neither a full 386-row lift nor full equivalence is
claimed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_auxiliary_cubic_inventory.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_auxiliary_cubic_inventory.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_auxiliary_cubic_inventory.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_auxiliary_cubic_inventory
```
