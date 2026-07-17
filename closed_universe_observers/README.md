# Closed-universe observer comparison

This namespace contains the isolated external reproduction and the first typed
comparison requested by `notes/closed-universe-observer-team-brief.md`.

Current lifecycle: `EXTERNAL_FIXTURE_REPRODUCED`.

Current overall verdict: `QUANTUM_COMPARISON_NOT_YET_DEFINED`.

Run the exact fixture and the comparison ledger checks with:

```bash
python3 closed_universe_observers/generate_rank_one_fixture.py --check
python3 closed_universe_observers/verify_rank_one_fixture.py
python3 closed_universe_observers/generate_berger_detector_records.py --check
python3 closed_universe_observers/verify_berger_detector_records.py
python3 closed_universe_observers/verify_comparison_ledger.py
python3 -m pytest -q closed_universe_observers/tests
```

The fixture is generated from
`fixtures/rank_one_cloned_observer_input.json`.  The certificate does not
hard-code rank: it derives the global and observer matrices, retains all 36
global two-by-two minor witnesses, and stores a nonzero observer determinant.
The verifier independently reconstructs these matrices and replays every
mutation.  The detector fixture constructs two independent, localized,
clock-labelled field-strength record functionals, while keeping the imported
pulse's two-window nonvanishing and the rod-sector quotient descent open.  The
comparison ledger replays its historical imports exactly, checks current
compatibility separately, and remains fail-closed on the classical-map and
quantum gates.
