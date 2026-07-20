# Observer close-out: Berger scalar-q1 background ideal

Work item: `sf:program/work/berger-108-row-q1-pbw-background-ideal`
Owner: observer

## Stop-condition audit

The work item permits closure either with a nilpotent/cyclic scalar 108-row
`q1`, or with an exact witness that the then-declared free coefficient-jet
dependencies did not determine the background quotient needed to kill a
`q1^2` path. The second branch was met: the four-term
`e1(Box R0_1)` free-jet normal form has the exact separating value one.

The original obstruction certificate is not used as the sole current
evidence because two of its pinned dependency hashes predate later
factor-two rod-source normalizations. A read-only reconstruction against the
current dependencies nevertheless reproduces exactly the same four-term
normal form, missing-object ledger, claim status, and separating value. The
current content-addressed successor chain is stronger:

- `BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL` exports the
  missing six-rod/physical-`Phi2` differential quotient and verifies that the
  former four free terms map exactly to zero.
- `BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION` composes the scalar
  108-row first jet over that quotient. Its independent replay proves that
  the old free-jet gate is resolved, then finds the next exact obstruction:
  the pure `epsilon_R_squared` coefficient has a `-49/20` Weyl witness.

Thus the legacy work item reached its declared obstruction stop condition;
its successor work items resolved that particular missing quotient and
advanced to a later gate. Closing this item does not claim that the complete
scalar unary is nilpotent.

## Verification

The following current-tree checks passed on 2026-07-20:

```text
python3 -m closed_universe_observers.verify_berger_108_row_background_specialization_differential_ideal
python3 -m closed_universe_observers.verify_berger_108_row_q1_pbw_first_jet_replay
python3 -c <semantic comparison of the original obstruction with a reconstruction from current dependencies>
```

Elapsed times were 0.64 seconds, 94.37 seconds, and 0.09 seconds
respectively. The semantic comparison asserted equality of the complete
free-jet obstruction, missing-object ledger and claim status, and rechecked
all six current rod wave residuals.

## Chronology repair and boundary

The legacy ACTIVE and OBSTRUCTED events share the same date and carry no
causal sequence. Science Forge therefore folds them to `AMBIGUOUS`, as
required by its fail-closed chronology rule. This report authorizes one new
sequence-bearing DONE event; no historical event or base work item is edited.

This close-out does not establish full scalar `q1^2=0`, scalar `q2`,
apparatus interaction stability, tangent-cone detector response, Bridge 3,
finite-parameter causality, or a quantum result. Those claims retain their
current lifecycle states.

CLOSE-OUT: DONE — the exact free-jet obstruction branch of the declared stop condition was met, and current successor certificates independently preserve and advance that result.
EVIDENCE: closed_universe_observers/certificates/BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION.json
