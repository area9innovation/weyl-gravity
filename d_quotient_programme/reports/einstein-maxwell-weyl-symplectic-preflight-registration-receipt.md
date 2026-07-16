# Einstein--Maxwell/Weyl--Maxwell symplectic-preflight registration receipt

The programme ledger imports
`bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json` at
source commit `eda065250c1b6b4f6ae7997b133bea310e3e94a3`, SHA-256
`22a948d0ef54efd0c4f2b9b8dd4c57a47a731f1511f40d6a6afbba780dd00591`.

The registered verdict is
`G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE`.  It records the exact
linear tangent quotient-injectivity theorem and freezes the current
calculation contract.  It does not promote the still-open Weyl--Maxwell
restriction, nonlinear solution embedding, final residual quotient, causal
scattering, or quantum theory.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symplectic_preflight --verify bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symplectic_preflight.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symplectic_preflight
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
