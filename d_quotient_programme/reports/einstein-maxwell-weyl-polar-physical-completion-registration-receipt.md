# Physical polar Weyl–Maxwell completion registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json` at
commit `c5098cc1cda5f5085763e2029bbe3d6f8134692e`, SHA-256
`110b2f226f89b9766a7549c3f48b84828046ea8b9d53f2ea81d7e13e3522948d`.

The registered G2 promotion replaces the generic-field interpretation by an
all-physical-fibre theorem:

```text
Image(Einstein polar)=complete q-primary summand,
Q_extra^polar=(K[omega]/(p))^2
```

for every `lambda=ell(ell+1)>=6` and every allowed compact momentum,
including `k=0`.  The action normalization is separately derived from the
four-dimensional first variation and harmonic norms.

The direct polar Lee–Wald current, ungauged lift, and final residual quotient
remain fail-closed.

Verification (Tier 1):

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

Tier 3 was not run because no causal, quantum, release, or paper-freeze state
is promoted.
