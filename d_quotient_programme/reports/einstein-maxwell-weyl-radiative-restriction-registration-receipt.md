# Standard radiative Weyl--Maxwell restriction registration receipt

The aggregate programme ledger imports
`bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json`
through the Einstein-team contribution at source commit
`e3c44396c3d7c489a360ffb28c381c0aa07065e5`, SHA-256
`25a798211bea52cbf9d8becae64672ac327be7a09adb50e30e45fa8287a608b7`.

The registered verdict is
`G3_STANDARD_RADIATIVE_ALL_ELL_GE2_COMMON_SPECTRAL_NONDEGENERATE_INDEFINITE_RESTRICTION`.
It combines the published axial and polar direct-current certificates into the
solution-space identity

```text
Omega_WM(u,v)=Omega_EM(u,[1+(3/2)(M-lambda)]v).
```

The registration records explicit branch, parity, harmonic, and Fourier
orthogonality; relative coefficient signature `(2,2)` per real spatial
harmonic; and the real/complex multiplicity convention.  It is fail-closed
against interpreting the negative relative coefficient as a quantum
negative-norm or ghost theorem.

Physical `ell=1`, homogeneous, twist, extra fourth-order, nonlinear, causal,
residual-quotient, scattering, and quantum claims remain open.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
