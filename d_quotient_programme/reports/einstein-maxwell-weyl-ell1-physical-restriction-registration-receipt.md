# Physical `ell=1` Weyl--Maxwell restriction registration receipt

The aggregate programme ledger imports
`bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json`
through the Einstein-team contribution at source commit
`cd507d2086970698289fbda40fb654de467fd7a7`, SHA-256
`2596e01ea18030ffeced787629b3d5eba3f6a3d14c3e881e1a4dffd82405e674`.

The registered verdict is
`G3_PHYSICAL_ELL1_ALL_N_M_FACTOR_FOUR_QUOTIENT_RESTRICTION`.  It records direct
gauge descent in both exceptional parities and the source-normalized theorem

```text
Omega_WM|physical ell=1 = 4 Omega_EM|physical ell=1.
```

It also records why the generic polar all-`ell` matrix cannot be continued to
`lambda=2`: the continued matrix is not null on the certified residual
diffeomorphism.  The massive physical triplets are kept separate from the
zero-frequency axial twist.

Homogeneous, twist, extra fourth-order, nonlinear, final-quotient, causal,
scattering, one-particle, and quantum claims remain open.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
