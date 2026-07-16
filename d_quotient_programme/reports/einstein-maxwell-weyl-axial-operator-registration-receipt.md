# Generic axial Weyl–Maxwell operator registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_axial_operator.json` at commit
`b31cc2616d4dd187a25bd2e8e030aa98c1f806c2`, SHA-256
`483f3e3f7ff1852c3c3f72a09f2169fd14e5f848dd2f041c68eb8c5b947a2dc6`.

The registered G2 result is the complete generic axial target operator,
ungauged Noether lift, exact source-image identity, Smith classification, and
canonical generic quotient

```text
Q_extra_ax=(F[omega]/(p))^2,
p=omega^2-k^2-lambda+2/3.
```

This is registered as a new phase-space row rather than an upgrade of the
operator-module preflight.  It certifies two additional algebraic classical
solution polarizations before final residual quotient.  It does not certify
particles, ghosts, norms, causal boundary data, or scattering states.

Verification (Tier 1):

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

Tier 3 was not run because this is a `LOCAL-ALGEBRAIC`/`REDUCED-MODE`
registration and does not promote a causal, quantum, or release lifecycle.
