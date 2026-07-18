# Retained mixed ell3 order-two source

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact order-two consumer is now frozen, but the scientific compatibility
verdict is still open. Quartic densities are mapped to their variational Euler
images after exact Berger-frame PBW reduction. This realizes the quotient by
total derivatives without selecting an integration-by-parts pivot table.

The consumer first reproduces both frozen lower pages: the zero-jet and
first-jet primitives have zero Euler residual when evaluated at their declared
summed differential orders. Four first-total-derivative and sixteen
second-total-derivative mutations also have identically zero Euler image.

At summed pre-reduction differential order two, the exported lower primitive
leaves 724 PBW-order-one and 5,212 PBW-order-two mixed density terms. Their
Euler image has 1,221 order-one and 8,822 order-two coordinates. The complete
symmetric second-input-jet physical ansatz contains 155,640 `F2/F3` labels;
the independent first-jet enumeration control gives 26,240 labels, exactly
four copies of the certified 6,560-column per-axis ansatz.

This nonzero source is not an obstruction. The next calculation must decide
whether it lies in the image of the 155,640-column second-jet map while
retaining the affine freedom of the lower primitives, and then lift any
physical solution through the positive-jet full-BV completion.

## Verification receipt

Commands below were run from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_second_jet_redefinition.py --check` | 34.77 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_second_jet_source.py` | 20.05 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_second_jet_source -v` | 39.68 s | PASS (5 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-source-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_SOURCE_V1.json` | 6.10 s | PASS |

Tier 2 is represented by replay against the pinned typed unary/pairing,
gravity and mixed binary payloads, retained mixed ternary payload, and frozen
first-jet certificate. Tier 3 was not run because no shared algebra or theorem
lifecycle state is promoted by this fail-closed source certificate.
