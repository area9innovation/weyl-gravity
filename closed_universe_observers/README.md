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
python3 closed_universe_observers/generate_berger_observer_interaction_import_gate.py --check
python3 closed_universe_observers/verify_berger_observer_interaction_import_gate.py
python3 -m closed_universe_observers.generate_berger_global_detector_rods --check
python3 -m closed_universe_observers.verify_berger_global_detector_rods
python3 -m closed_universe_observers.generate_berger_global_rod_q1_solvability --check
python3 -m closed_universe_observers.verify_berger_global_rod_q1_solvability
python3 -m closed_universe_observers.generate_berger_84_row_apparatus_handoff --check
python3 -m closed_universe_observers.verify_berger_84_row_apparatus_handoff
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
source-rod-memory quotient descent remain open.  The interaction import gate
then imports the repaired cyclic 64-row gravity-clock-Maxwell `q2` and retains
rank two only as a probe-limit baseline.  Its corrected apparatus interface
uses composite polarization, keeps the present currents external, and records
`p*A`, `p*A*deltaR`, and `p*A*deltaR^2` as `q1`, `q2`, and `q3` contributions,
respectively.  An extended unary/Green complex is still absent. The
observer team now also exports six exact global detector-indexed rod fields
on the compact Berger cylinder.  They reproduce both detector-event identity
charts and determine a conserved global rod source in the finite spatial
`j=0,1` and temporal `0,+-sqrt(58)/3` sector.  Detector indexing corrects the
prospective apparatus carrier from 78 to 84 rows.  The complete compact rod
source sector then evaluates exactly against the retained Berger metric
Hessian.  Sparse primitives prove `H_retained Phi2=-q0^rod` on every
`j=0,1` and temporal `0,+-sqrt(58)/3` block, so there is no compact Taub
obstruction through order `epsilon_R^2`.  An all-orders backreacted branch
and the 84-row causal interacting complex remain open.  The authoritative
forward handoff now freezes the ordered 84-row carrier and pairing, bulk
clock-transported memories, detector-block-local composite polarizations,
independent `epsilon_R`/`kappa` grading, the exact profile two-jet through
`q3`, external-source boundary, and the physical real two-detector `Phi2`.
The historical 78-row gate remains scoped history and is not a forward
construction input.  The comparison ledger replays its
historical imports exactly, checks current compatibility separately, and
remains fail-closed on the classical-map and quantum gates.
