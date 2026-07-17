# Generic polar Weyl–Maxwell operator registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json` at commit
`e344a69fb6c143b92738366bd095f06746096fd3`, SHA-256
`e8794a4571e85e382e183b418e4b98fd74b8429837fd1601875f83ea8498df20`.

The registered G2 result is the complete generic polar target Hessian on the
Weyl slice, its exact polynomial Einstein equation square, and the generic
primary decomposition

```text
T_WM^polar = (K[omega]/(p))^2 direct-sum K[omega]/(q),
p=omega^2-k^2-lambda+2/3.
```

This matches the generic axial equation-module multiplicity but does not yet
import the axial current theorem into the polar sector.  The direct polar
Lee–Wald matrix, physical-ring specialization, ungauged lift, and final
residual quotient remain open.

Verification (Tier 1):

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

Tier 3 was not run because this registration preserves the
`LOCAL-ALGEBRAIC`/`REDUCED-MODE` lifecycle boundary and does not promote a
causal, quantum, or paper-freeze claim.
