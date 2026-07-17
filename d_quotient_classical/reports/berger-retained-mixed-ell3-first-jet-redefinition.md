# Retained mixed ell3 first-jet cyclic redefinition

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The complete degree-zero physical-action problem through total PBW jet order
one is exactly trivializable on the unsplit retained 36-row carrier. The
positive-jet map has rank 1327 and cokernel dimension 3 on each 1330-row axis
block. Projecting those cokernels gives a `562 x 2690` coupled Schur system of
rank 557; its target is compatible.

An explicit primitive uses 51 zero-jet
coefficients and `[43, 94, 95, 108]` positive-jet
coefficients on axes 0 through 3. It reconstructs all 550 constant and 5,320
possible first-jet quotient coordinates exactly (the target has
`[58,136,136,126]` nonzero first-jet coordinates).

This does not match the 288 ghost/antifield completion coefficients and does
not solve total jet order two. The full cyclic deformation class, cohomology
operation, branch mixing, QME, and every quantum claim remain open.

## Verification receipt

All commands below passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_first_jet_redefinition.py --check` | 43.83 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_first_jet_redefinition.py` | 43.55 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_first_jet_redefinition -v` | 54.38 s | PASS (4 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-first-jet-redefinition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json` | 10.26 s | PASS |

Tier 2 is represented by the affected first-jet chain replay against pinned,
content-addressed unary, binary, ternary, pairing and SDR inputs. Unchanged
branch-obstruction inputs were checked by hash and not rebuilt. Tier 3 was not
run because this result remains `WRITING_STARTED`; it neither freezes a
theorem nor promotes a lifecycle state.
