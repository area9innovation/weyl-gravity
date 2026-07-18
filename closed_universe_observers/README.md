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
python3 -m closed_universe_observers.generate_berger_dynamical_emitter_rank_two --check
python3 -m closed_universe_observers.verify_berger_dynamical_emitter_rank_two
python3 -m closed_universe_observers.generate_berger_dynamical_emitter_recoil_preflight --check
python3 -m closed_universe_observers.verify_berger_dynamical_emitter_recoil_preflight
python3 -m closed_universe_observers.generate_berger_emitter_switch_profiles --check
python3 -m closed_universe_observers.verify_berger_emitter_switch_profiles
python3 -m closed_universe_observers.generate_berger_exact_detector_smearings --check
python3 -m closed_universe_observers.verify_berger_exact_detector_smearings
python3 -m closed_universe_observers.generate_berger_positive_energy_emitter_profiles --check
python3 -m closed_universe_observers.verify_berger_positive_energy_emitter_profiles
python3 -m closed_universe_observers.generate_berger_peter_weyl_form_laplacian --check
python3 -m closed_universe_observers.verify_berger_peter_weyl_form_laplacian
python3 -m closed_universe_observers.generate_berger_quantitative_detector_chart --check
python3 -m closed_universe_observers.verify_berger_quantitative_detector_chart
python3 -m closed_universe_observers.generate_berger_mode_green_kernels --check
python3 -m closed_universe_observers.verify_berger_mode_green_kernels
python3 -m closed_universe_observers.generate_berger_validated_flat_bump_moments --check
python3 -m closed_universe_observers.verify_berger_validated_flat_bump_moments
python3 -m closed_universe_observers.generate_berger_local_su2_profile_coefficients --check
python3 -m closed_universe_observers.verify_berger_local_su2_profile_coefficients
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
separate.  The Cauchy-preparation successor now uses Green adjunction and an
exact constraint-compatible massive polarization to choose two compact local
free-emitter data sets.  With the second relational switch after `D0`, their
actual leading matrix is `[[kappa_0,0],[mu,kappa_1]]`, where both diagonal
witnesses are nonzero.  Thus dynamical-emitter rank two is certified; the
next calculation is the detector-level `g^2` recoil correction for those fixed
preparations.  The recoil preflight corrects that shorthand: the leading
emitter-data signal is absolute order `g`, the absolute `g^2` detector term
vanishes by bipartite `A`--`K` parity, and the first feedback is absolute
order `g^3` (relative order `g^2`).  Its operator and formal rank stability
are exact.  A numerical detector coefficient is input-blocked until explicit
compact preparation profiles and their massive Green images are exported.
The switch-profile successor closes the other half of that input gate with
two exact nonnegative flat bumps normalized to unit clock integral.  After
the exact conversion `dTheta/dt=3/4`, `h_0` lies strictly before `D0` and
`h_1` lies strictly between `D0` and `D1`, with physical-time margins `1/24`
and clock-phase margins `1/32`.  The remaining Cauchy profiles cannot be
chosen as arbitrary explicit bumps: they must be selected against the actual
advanced detector covectors so that the leading detector functionals do not
annihilate them.
The detector-smearing successor removes another hidden arbitrariness: it fixes
unit-integral flat clock bumps, unit-integral radial rod-chart bumps, and the
advanced Maxwell-to-emitter adjoint chain defining each Cauchy covector.  The
spatial radii remain exact parameters `0<epsilon_a<r_chart,a<=1/64`, because
the local inverse-function theorem exports no numerical chart radius.  The
advanced Green images and coordinate-level Cauchy data are still open.
The positive-energy successor removes the remaining preparation-selection
ambiguity without waiting for a harmonic expansion: for advanced Cauchy data
`(q_a,p_a)`, it sets `u_a=(-p_a,L_a q_a)`.  Its detector response is the
strictly positive massive-two-form energy.  Harmonic coefficients and the
absolute-`g^3` recoil integral remain open.
The Peter--Weyl successor now supplies exact de Rham and form-Laplacian
matrices in every requested finite Berger `SU(2)` block.  It independently
reproduces the rod eigenvalue `29/18`.  Validated bump coefficients and
spectral-tail bounds are the remaining analytic inputs to the Green images.
The quantitative-chart successor uses the explicit global rods to fix both
detector radii to `1/128`, with exact `|y|^2<1/10000` support on the unique
positive `S3` branch.  No free detector-radius parameter remains.
The finite-mode Green successor applies exact entire matrix spectral calculus
to the Maxwell and massive two-form blocks, including the Maxwell zero-mode
limit.  Finite truncations are explicitly not treated as support-local; the
full profile expansion and tail bounds remain necessary.
The validated-moment successor supplies directed-rounding Darboux enclosures
for both standard flat-bump cores through even order twelve and scales them
exactly to clock radius `1/64` and detector rod radius `1/128`.  This removes
the universal bump moments from the quadrature obstruction.  At that stage,
local `SU(2)` mode coefficients, the `y0` remainder, and the infinite
spectral tail were still open.
The local-coefficient successor matches the quaternion convention to the
certified Berger generators and interval-encloses the normalized scalar bump
Fourier matrices through `two_j=4`.  Axial symmetry makes them diagonal, and
odd-spin `y0` terms carry validated remainders below `10^-24`.  Clock
integration, form polarizations and coderivatives, higher modes, and the
evaluated infinite tail remain open.
The emitter backreaction successor now varies the same selected action with
respect to `gHat` and `Theta`.  It exports the free massive-two-form stress,
the metric stress of `g_b h_b<K_b,dA>`, and the reciprocal clock source
`-g_b h_b'(Theta)<K_b,dA>` into the existing metric- and clock-antifield
rows.  Representative common-action third derivatives are cyclic, and an
exact reduced fixture verifies off-shell energy exchange with the clock.
This closes the emitter-added `q2` stress/clock jet, not the complete
componentwise 108-row `q1 q2` identity or a solved backreacted branch.
The master-identity successor now closes the covariant all-row step over the
imported apparatus `r`-first-jet ring.  It classifies every output row
0--107, checks the Maxwell, clock, Weyl, Diff-cotangent, and common-action
cyclic orbits, and derives `[q1,q2]=0` from the cubic BV master-equation
coefficient.  It explicitly leaves the sparse support-local PBW payload and
coefficient-by-coefficient PBW replay open.
The comparison ledger replays its
historical imports exactly, checks current compatibility separately, and
remains fail-closed on the classical-map and quantum gates.
