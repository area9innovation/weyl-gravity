# Berger PBW operator backend

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `ARITY_ONE_OPERATOR_BACKEND_READY_ND2_ASSEMBLY_BLOCKED`

## Result

The independently imported retained Berger minimal `q1` now has a reusable,
content-addressed operator backend.  The backend declares its coefficient
domain, supported arities, exact capabilities, implementation manifest, and
assembly status.  It accepts the checked-in 26-row import, re-runs its full
PBW verification, and returns a typed receipt with the three block hashes,
891 PBW terms, and maximum differential order four.

## Why this is not an ND2 evaluator

The distinction is mathematical rather than administrative.  The imported
operator has coefficients in

```text
Q[alpha_B,u,v] tensor U(e_Berger)
```

with noncommuting invariant-frame derivatives.  The current finite ND2 Cartan
engine uses `Fraction` coefficients.  Coercing the PBW operator into that
engine would require either:

1. a declared exact finite mode/spectral specialization, carrying the
   `REDUCED-MODE` dependency tag; or
2. an extension of the Cartan complex and solver to a declared PBW-module
   coefficient domain.

Neither route is silently selected.  The registered backend therefore has

```text
supported_arities = [1]
assembly_mode = OPERATOR_VALIDATION_ONLY
nd2_physical_assembly_authorized = false
```

The future classical `q2/D` export can reuse the coefficient parser, PBW
normal form, composition, adjoint, and order-audit capabilities.  Bilinear
polydifferential composition and a compatible Cartan solver remain new work.

## Machine receipt

- `quantum-weyl/transfer/certificates/BERGER_PBW_OPERATOR_BACKEND.json`

## Verification commands

```text
python3 quantum-weyl/transfer/berger_pbw_backend_certificate.py --check
python3 -m unittest quantum-weyl.transfer.tests.test_berger_pbw_backend
python3 quantum-weyl/transfer/nd2_physical_run_certificate.py --check
```

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Backend, ND2 physical-run, and nonlinear aggregate certificate checks | 10.48 | PASS | 2 |
| Strict AJV Draft-2020-12 validation of the backend receipt | 4.61 | PASS | 0 |
| Strict AJV Draft-2020-12 validation of the extended ND2 receipt | 1.27 | PASS | 0 |
| Focused backend, ND2, and nonlinear aggregate tests | 11.41 | PASS (14 tests) | 2 |
| Complete transfer suite | 69.45 | FAIL (119 tests pass; pre-existing ND1 reproduction receipt is stale) | 2 |
| Independent ND1 drift audit | 6.60 | PASS (only the classical-status dependency hash and its manifest hash differ) | 2 |
| Python compile, JSON parsing, and scoped `git diff --check` | 0.12 | PASS | 0 |

The complete-suite failure is not counted as a pass and was not repaired in
this change.  The other seven ND1 semantic and mutation tests pass.  The stale
reproduction differs only because the concurrently maintained
`CLASSICAL_D_QUOTIENT_STATUS.json` dependency moved; the PBW backend does not
consume that ND1 receipt.

Tier 3 is unnecessary: this registers a validation-only backend, changes no
classical tensor, and leaves every physical, interacting, causal, and quantum
gate false.
