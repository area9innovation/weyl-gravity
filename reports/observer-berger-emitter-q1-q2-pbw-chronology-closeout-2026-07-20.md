# Observer close-out: Berger emitter q1-q2 PBW input

Work item: `sf:program/work/berger-emitter-q1-q2-pbw`
Owner: observer

## Stop-condition audit

The work item permits closure either with a canonical scalar support-local
108-row `q2` payload and independent coefficient replay, or with an exact
proof that the declared covariant inputs do not determine a unique PBW
payload. `BERGER_108_ROW_PBW_INPUT_OBSTRUCTION` satisfies the second branch.

The certificate preserves the covariant `q1 q2` identity and the pinned
64-row base. It then gives two exact non-uniqueness witnesses inside the
allowed profile contracts:

- replacing an admissible normalized radial bump width `epsilon` by
  `epsilon/2` changes its centre coefficient by exactly eight;
- replacing an admissible normalized flat-switch radius `r` by `r/2`
  changes its centre coefficient by exactly two.

The corresponding mutations are detected. The certificate names the missing
declarations: exact profiles and switches in the dependency closure, a
differential coefficient-jet grammar, a canonical component/cotangent
crosswalk, and complete scalar `q1/q2` serializers.

## Verification

The current independent verifier passed on 2026-07-20:

```text
python3 -m closed_universe_observers.verify_berger_108_row_pbw_input_obstruction
```

Elapsed time was 0.09 seconds with peak RSS 25,028 KiB.

## Chronology repair and boundary

The legacy ACTIVE and OBSTRUCTED events share the same date and carry no
causal sequence. Science Forge therefore folds them to `AMBIGUOUS`. This
report authorizes a new sequence-bearing DONE event because the exact
non-uniqueness branch of the stop condition is satisfied; it does not rewrite
either historical event.

Later profile and switch certificates do not retroactively turn the original
dependency closure into a canonical PBW map. This close-out does not export
the requested component payload, certify scalar `q1 q2`, choose physical
parameters, activate apparatus `q2/q3`, establish tangent-cone response or
Bridge 3, or make a quantum claim.

CLOSE-OUT: DONE — the exact two-realization non-uniqueness branch of the declared stop condition is certified.
EVIDENCE: closed_universe_observers/certificates/BERGER_108_ROW_PBW_INPUT_OBSTRUCTION.json
