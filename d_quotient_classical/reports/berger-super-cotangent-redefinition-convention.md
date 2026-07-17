# Super-cotangent redefinition convention

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact Taylor-level formula

`F^(i*) = -(-1)^parity(i) F^B`

reproduces the certified Maxwell covariant-ghost shear on all 64 rows. Its
four base components generate 8 cotangent
partners. Removing the odd-input sign fails exactly on retained-full rows
`[49, 50, 51, 52]`.

This freezes a convention prerequisite only. The full-BV ell3 redefinition
matrix and its primitive/obstruction verdict remain open.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_super_cotangent_redefinition_convention.py --check` | 0.39 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_super_cotangent_redefinition_convention.py` | 0.02 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_super_cotangent_redefinition_convention -v` | 0.43 s | PASS (3 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json` | 1.97 s | PASS |

Tier 2 is the exact 64-row scientific replay against the pinned landed shear.
Tier 3 was not run because this is a convention prerequisite, not a theorem
freeze, lifecycle promotion, shared-core release or quantum claim.
