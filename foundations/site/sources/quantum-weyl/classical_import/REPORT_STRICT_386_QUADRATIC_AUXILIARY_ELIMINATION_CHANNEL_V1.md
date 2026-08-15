# Strict 386-row quadratic auxiliary-elimination channel v1

**Result:** `STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1`

The source-to-split map has quadratic vector component
`F_(2)(v)=v tensor v-(1/2)g v^2`.  Expressing the
source action in split variables uses its inverse and contributes
**1** to the previously obstructing
cyclic channel.  The exact ledger is

- source before correction: **-1**;
- inverse-shift mass cross term: **1**;
- transformed source: **0**;
- trivial-stabilization candidate: **0**;
- residual: **0**.

The first nonlinear correction is therefore constructed and closes this one
channel.  Full q2/q3 pullback, the componentwise BV cotangent lift, causal
source closure and Gate A remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_quadratic_auxiliary_elimination_channel.py --check
python3 quantum-weyl/classical_import/check_strict_386_quadratic_auxiliary_elimination_channel.py
python3 quantum-weyl/classical_import/verify_strict_386_quadratic_auxiliary_elimination_channel.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_quadratic_auxiliary_elimination_channel
```
