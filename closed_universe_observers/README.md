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
python3 closed_universe_observers/generate_berger_smeared_retarded_transfer.py --check
python3 closed_universe_observers/verify_berger_smeared_retarded_transfer.py
python3 closed_universe_observers/verify_comparison_ledger.py
python3 -m pytest -q closed_universe_observers/tests
```

The fixture is generated from
`fixtures/rank_one_cloned_observer_input.json`.  The certificate does not
hard-code rank: it derives the global and observer matrices, retains all 36
global two-by-two minor witnesses, and stores a nonzero observer determinant.
The verifier independently reconstructs these matrices and replays every
mutation.  The detector preflight constructs local standard-sign rods, two
independent clock-labelled spacetime field-strength smearings, exact central no-wrap Hopf
rays, and persistent probe memories.  Two predeclared conserved polarization
currents then give the physical matrix `diag(C_00,C_11)` with both entries
positive, hence two distinguishable causal records.  Those currents are
homogeneous over the compact `S3`; spatially localized emitters and the
source-rod-memory quotient descent remain open.  The
comparison ledger replays its historical imports exactly, checks current
compatibility separately, and remains fail-closed on the classical-map and
quantum gates.
