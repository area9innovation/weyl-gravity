# Positive-jet super-cotangent redefinition convention

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact lift transposes every derivative-bearing input by its PBW formal
adjoint over the output-antifield/remaining-input product. It reproduces all
`934` F2 and
`5050` F3 zero-word base labels of the frozen
algebraic convention. An odd first-derivative mutation changes the dual
components, while the noncommuting word `(2,1)` produces the required
positive-order Berger commutator tail.

This freezes the convention prerequisite only. The full-BV order-two replay
and its primitive/obstruction verdict remain the next gate.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_positive_jet_super_cotangent_redefinition_convention.py --check` | 6.52 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_positive_jet_super_cotangent_redefinition_convention.py` | 6.24 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_positive_jet_super_cotangent_redefinition_convention -v` | 11.52 s | PASS (4 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-positive-jet-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json` | 3.01 s | PASS |

Tier 2 is the complete zero-word restriction replay plus the exact
positive-jet mutation controls. Tier 3 was not run because this prerequisite
does not change shared core algebra or promote a theorem lifecycle.
