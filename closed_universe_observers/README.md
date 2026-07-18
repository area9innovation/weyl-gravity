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
python3 -m closed_universe_observers.generate_berger_84_row_unary_pairing_green_gate --check
python3 -m closed_universe_observers.verify_berger_84_row_unary_pairing_green_gate
python3 -m closed_universe_observers.generate_berger_84_row_rod_gravity_unary --check
python3 -m closed_universe_observers.verify_berger_84_row_rod_gravity_unary
python3 -m closed_universe_observers.generate_berger_84_row_mixed_r_kappa_unary_gate --check
python3 -m closed_universe_observers.verify_berger_84_row_mixed_r_kappa_unary_gate
python3 -m closed_universe_observers.generate_berger_84_row_normalized_profile_mixed_unary --check
python3 -m closed_universe_observers.verify_berger_84_row_normalized_profile_mixed_unary
python3 -m closed_universe_observers.generate_berger_84_row_apparatus_q2_q3_k_gate --check
python3 -m closed_universe_observers.verify_berger_84_row_apparatus_q2_q3_k_gate
python3 -m closed_universe_observers.generate_berger_affine_k_observer_morphism --check
python3 -m closed_universe_observers.verify_berger_affine_k_observer_morphism
python3 -m closed_universe_observers.generate_berger_cg4_record_poisson_algebra --check
python3 -m closed_universe_observers.verify_berger_cg4_record_poisson_algebra
python3 -m closed_universe_observers.generate_berger_localized_emitter_rank_two_transfer --check
python3 -m closed_universe_observers.verify_berger_localized_emitter_rank_two_transfer
python3 -m closed_universe_observers.generate_berger_dynamical_emitter_recoil_gate --check
python3 -m closed_universe_observers.verify_berger_dynamical_emitter_recoil_gate
python3 -m closed_universe_observers.generate_berger_polarization_emitter_handoff --check
python3 -m closed_universe_observers.verify_berger_polarization_emitter_handoff
python3 -m closed_universe_observers.generate_berger_108_row_emitter_unary_recoil --check
python3 -m closed_universe_observers.verify_berger_108_row_emitter_unary_recoil
python3 -m closed_universe_observers.generate_berger_108_row_emitter_causal_chain --check
python3 -m closed_universe_observers.verify_berger_108_row_emitter_causal_chain
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
homogeneous over the compact `S3`; at that transfer gate spatially localized
emitters and the source-rod-memory quotient descent remain open.  The
interaction import gate
then imports the repaired cyclic 64-row gravity-clock-Maxwell `q2` and retains
rank two only as a probe-limit baseline.  Its corrected apparatus interface
uses composite polarization, keeps the present currents external, and records
`p*A`, `p*A*deltaR`, and `p*A*deltaR^2` as `q1`, `q2`, and `q3` contributions,
respectively.  The exact two-channel memory--Maxwell unary and its finite
advanced/retarded inverse are certified; together with the base rows they
form a 72-row causal subcomplex.  The six clock-dressed rod diffeomorphism
blocks, their cotangent adjoints, the action-derived gravity--rod Hessian, and
the coupled causal witness are now also exported.  An exact Schur--Laurent
inverse certifies the rod--gravity `epsilon_R^2` coefficient formally.  A
subsequent bidegree audit corrects `delta_r T` from `Q11` to `Q10`, computes it
and its frozen-pairing adjoint exactly, and repairs the memory portion of the
separate `r` axis.  A corrected payload audit treats
`q2(Phi2,-)` as a fourth-order diagonal principal deformation and explicitly
exhibits the nonzero contracted principal coefficient `623/81`; it explicitly
does not claim finite-parameter Green hyperbolicity.  The physical `Phi2` is
now exported in one canonical tensor/harmonic/frequency order, and the mixed
coefficient ring and varied-adjoint requirements are frozen.  The actual
old `epsilon_R^2*kappa` profile obstruction is now closed by normalizing each
transverse bump against the induced clock-slice volume in its three assigned
rod coordinates.  This fixes
`sigma_a=1/2 tr(G_a^-1 delta G_a)` and gives
`d1+sigma_a=-Phi2_00/2` at both certified detector events.  The four nonzero
`Q11` blocks, their adjoints, all-84-row mixed nilpotency/cyclicity, and the
bivariate formal Green coefficient are exact.  This is still only a
coefficientwise first-jet theorem; finite-parameter Green hyperbolicity and
the interacting full-84 theorem remain open.  The
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
construction input.  The shifted Euler equations and unary complex close on
the separate `(0,0)`, `(epsilon_R^2,0)`, and `(0,kappa)` axes, with a formal
coefficientwise causal contraction.  The mixed first jet is now also closed;
finite-parameter Green theory and the observer morphism remain open.  The
action-derived apparatus gate now exports the normalized cubic and quartic
tensors (`q2,q3`) as exact derivative families with cyclic cotangent
completion.  Their unshifted identities and first shifted arity-two identity
close, while shifted arity three requires the unavailable
`q4(K0,-,-,-)`.  The six existing rods have rank-eight time-translation
closure, so no constant six-by-six internal rotation repairs the 84-row
carrier.  Formal unary response rank remains two before quotient descent.
The next gate is therefore the exact `q4` contraction or a recomputed
co-rotating rod completion with at least 88 rows, followed by morphism replay.
The affine-Ward successor closes the narrower and sufficient first option:
it differentiates simultaneous `K` invariance to fix only
`q4(K0,-,-,-)`, verifies the identity on an independent genuine fifth
derivative, and certifies the rank-two coefficientwise family observer
morphism through arity three.  Full `q4`, fixed-background linear-`K`
descent, finite-parameter Green theory, and quantum claims remain open.
The C-G4 successor evaluates the circular two-phase mode directly in the two
detector windows.  Its exact moment matrix has strictly positive determinant,
so the C-G4 phase plane and persistent records are isomorphic.  Transporting
the reduced bracket makes the record polynomial algebra closed under both
products and a nonzero constant Poisson bracket.  The localization successor
uses `H1(S3)=H2(S3)=0`, constraint-potential bumps, finite propagation, and
staggered source times to construct two compact conserved receiver-adjacent
emitters.  Their response is triangular with determinant
`-beta^2 S0 C1 != 0`.  A common emitter at the original Hopf event and
dynamical emitter recoil remain open.
The recoil input successor proves why that next coefficient cannot yet be
computed: two local cyclic polarization-field completions reproduce the same
external current but give exact recoil coefficients `1/2` and `1/5` on a
shared mode.  The emitter carrier and action are therefore new physical
input.  Rank two nevertheless survives every compatible formal completion
because `-40 S0 C1/9` is the determinant's nonzero constant term.
The selected successor is a standard massive polarization two-form model on
`gHat`, with compact relational switches `h_b(Theta)`.  Its current
`J_b=g_b delta(h_b K_b)` is conserved off shell and its reciprocal equation
contains the Maxwell recoil.  Two six-component fields plus cotangent partners
extend the apparatus from 84 to 108 rows.  The complete 108-row differential,
causal contraction, actual Cauchy-preparation rank, and stress backreaction are
the next construction.  The unary successor now explicitly indexes the 24
emitter rows and their rank-24 odd pairing, closes the new nilpotency and
cyclicity paths, and constructs the exact massive-two-form Green operator and
the first formal Maxwell recoil self-energy through order `g^2`.  This is a
coupled Euler inverse, not yet the full 108-row BV inclusion/projection/homotopy
package.  Exporting those chain maps and realizing rank two with actual free
emitter Cauchy data are the immediate next gates.  The causal-chain successor
now appends the emitter witness `W_K(K_b_plus)=K_b`, constructs
`Lambda_108,+/-=W_108 G_P108,+/-`, and proves
`q Lambda+Lambda q=1` coefficientwise through `g^2` on a gauge-complete graded
fixture.  The remaining operational gate is therefore the choice of two
localized free-emitter Cauchy preparations and the rank of their actual
detector matrix.  Finite-parameter/all-orders Green hyperbolicity remains
separate.
The comparison ledger replays its
historical imports exactly, checks current compatibility separately, and
remains fail-closed on the classical-map and quantum gates.
