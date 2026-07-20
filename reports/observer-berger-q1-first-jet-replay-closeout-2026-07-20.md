# Observer close-out: Berger scalar-q1 first-jet replay

Work item: `sf:program/work/berger-108-row-q1-pbw-first-jet-replay`
Owner: observer

## Stop-condition audit

The work item permits closure either when all four first-jet unary
coefficients are odd-cyclic and square to zero in the certified
same-background quotient, or when a nonzero exact quotient witness is
certified with the downstream activations false.

`BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION` satisfies the second
branch. It composes the complete scalar 108-row first jet and proves:

- all four coefficient operators are exactly odd-cyclic;
- the zeroth-order, `kappa`, and mixed
  `epsilon_R_squared*kappa` square coefficients vanish;
- the pure `epsilon_R_squared` coefficient remains nonzero, with 355 PBW
  operator keys, 150 matrix positions, and 30,326 serialized coefficient
  monomials before quotient evaluation;
- the quotient leaves 374 defects on 54 matrix positions;
- an exact witness at output row 27, Weyl-ghost input row 4, and time mode
  `-2` has coefficient `-49/20`.

The certificate keeps apparatus `q2/q3`, tangent-cone observer response, and
the physical-branch bridge inactive. This is precisely the declared
obstruction branch of the stop condition.

## Verification

The current independent component replay passed on 2026-07-20:

```text
python3 -m closed_universe_observers.verify_berger_108_row_q1_pbw_first_jet_replay
```

Elapsed time was 94.37 seconds with peak RSS 264,808 KiB.

## Lifecycle boundary

The work package is DONE because its specified calculation reached a
certified stopping result. The mathematical first-jet unary gate remains
`OBSTRUCTED`: `EPSILON_R_SQUARED_Q1_SQUARED_ZERO_IN_BACKGROUND_QUOTIENT` is
false, and no downstream interaction or observer-response activation follows.
The later nonlinear-clock work items are separate successors and do not
retroactively turn this first-jet result into nilpotency.

This close-out does not establish scalar `q1^2=0`, apparatus `q2/q3`,
`K_Berger` equivariance, observer-morphism stability, tangent-cone detector
response, Bridge 3, finite-parameter causality, or a quantum result.

CLOSE-OUT: DONE — the exact nonzero quotient-witness branch of the declared stop condition is certified with every downstream activation false.
EVIDENCE: closed_universe_observers/certificates/BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION.json
