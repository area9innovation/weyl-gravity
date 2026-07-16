# Generic axial direct Lee–Wald completion registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json` at
commit `e2b7e20bdf545dafeb1059d627c33c07bee91040`, SHA-256
`de86c6af1439a9f47ddf8b50f2647fc6f706272e95cd7da7ace8677e63695567`.

The registered G2 result is the complete generic compact axial classical
Lee–Wald block before final residual quotient.  The Einstein and extra primary
modules are symplectically orthogonal.  The Einstein-image branches have
signature `(1,1)`, the extra block `(2,0)`, and the full target `(3,1)` in the
declared direct action convention.

The registration distinguishes the independent Einstein--Maxwell source form
`Omega_EM`, the Weyl--Maxwell pullback `iota^*Omega_WM`, and the full target
form `Omega_WM`.  The negative target-current direction lies in an
Einstein-image branch, but the pullback differs from `Omega_EM` by
branch-dependent factors.  It is therefore not, by itself, a negative
Einstein--Maxwell particle norm.

This does not register a particle, quantum ghost, causal boundary, Hadamard,
or scattering theorem.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Verification receipt:

```text
python3 -m py_compile d_quotient_programme/verify_programme_status.py
PASS

python3 -m json.tool \
  d_quotient_programme/contributions/einstein-maxwell-weyl-axial-lee-wald-completion.json
PASS

python3 d_quotient_programme/verify_programme_status.py --check --guards
PASS; mutation guards PASS; elapsed 0.30 s

python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_lee_wald_completion
PASS; 4 tests; elapsed 0.64 s

python3 -m unittest \
  bridge.einstein_sector.tests.test_weyl_maxwell_axial_general_lee_wald_fixture
PASS; 1 test; elapsed 0.30 s

git diff --check -- <scoped programme, report, and brief paths>
PASS
```

Tier 2 was not rerun: the mathematical input and content-addressed Lee--Wald
certificate are unchanged from commit
`e2b7e20bdf545dafeb1059d627c33c07bee91040`; this change registers and
clarifies that certified result and updates the pinned downstream team state.
Tier 3 was not run because no shared algebra, lifecycle promotion, freeze, or
release gate changed.
