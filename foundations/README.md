# Reverse foundations

This directory couples the repository's reverse-physics programme to reverse
mathematics and foundational analysis.  Its question is not merely which
physical assumptions select a law, but which combinations of

1. physical postulates,
2. mathematical carriers and existence principles, and
3. background logic

are sufficient or necessary for a stated physical conclusion.

Start with
[`reports/foundational-assumption-atlas.md`](reports/foundational-assumption-atlas.md).
The report gives the conceptual separation, a first literature map, and the
initial Weyl/Krein audit questions.  The sources used by that report are pinned
in [`literature-ledger.json`](literature-ledger.json), and the deliberately
non-theorem-level machine-readable result is
[`results/FOUNDATIONAL_ASSUMPTION_ATLAS_V0.json`](results/FOUNDATIONAL_ASSUMPTION_ATLAS_V0.json).

The verifier checks internal references, dependency tags, source hashes,
claim boundaries, and the distinction between logical, set-theoretic,
infinity, carrier, physical, and target-claim axes:

```bash
python3 foundations/verify_foundational_assumption_atlas.py
python3 -m unittest foundations.tests.test_foundational_assumption_atlas
```

The first populated comparison is
[`reports/foundational-coverage-and-low-hanging-fruit.md`](reports/foundational-coverage-and-low-hanging-fruit.md).
It compares sixteen representative programmes across the six axes and ranks
nine bounded case studies without promoting the literature map to a theorem.
Its machine result and source supplement are
[`results/FOUNDATIONAL_COVERAGE_MATRIX_V0.json`](results/FOUNDATIONAL_COVERAGE_MATRIX_V0.json)
and
[`literature-supplement-known-attempts-v1.json`](literature-supplement-known-attempts-v1.json).

```bash
python3 foundations/verify_foundational_coverage_matrix.py
python3 -m unittest foundations.tests.test_foundational_coverage_matrix
```

The first bounded theorem-level case is
[`reports/free-bv-energy2-pra-sdr.md`](reports/free-bv-energy2-pra-sdr.md).
It proves that Primitive Recursive Arithmetic suffices to check the fixed
energy-2 integral BV contraction and that its retained `p,j,h` witness avoids
general separation, complement-selection, rank, and nullspace machinery:

```bash
python3 foundations/check_free_bv_energy2_primitive.py
python3 foundations/verify_free_bv_energy2_weak_base.py
python3 -m unittest foundations.tests.test_free_bv_energy2_weak_base
```

The next theorem-level audit is
[`reports/krein-explicit-j-zf-audit.md`](reports/krein-explicit-j-zf-audit.md).
It proves that the repository's explicitly labeled one-particle Krein
symmetry and occupation-number Fock lift are constructible in ZF without
Countable Choice.  Finite cutoffs remain PRA-checkable; actual infinity and
Hilbert completion, rather than Choice, are the first stronger commitments:

```bash
python3 foundations/check_krein_explicit_j.py
python3 foundations/verify_krein_explicit_j_zf.py
python3 -m unittest foundations.tests.test_krein_explicit_j_zf
```

The companion spectral-fragment audit is
[`reports/explicit-energy-spectral-fragment-audit.md`](reports/explicit-energy-spectral-fragment-audit.md).
It shows that the cylinder energy operator and its Fock lift use an explicit
diagonal-domain proof, not an abstract spectral theorem:

```bash
python3 foundations/check_explicit_energy_spectral_fragment.py
python3 foundations/verify_explicit_energy_spectral_fragment.py
python3 -m unittest foundations.tests.test_explicit_energy_spectral_fragment
```

The energy result now exponentiates directly to
[`explicit free-mode Krein and C*-dynamics in ZF`](reports/explicit-mode-dynamics-zf.md).
The coordinate unitary group is strongly continuous and J-unitary, while its
conjugation action is point-norm continuous on the unitized compact algebra.
The exact rail uses Laurent degrees rather than numerical time samples and
fills four dynamics cells without claiming interactions or causal propagation:

```bash
python3 foundations/check_explicit_mode_dynamics.py
python3 foundations/verify_explicit_mode_dynamics_zf.py
python3 -m unittest foundations.tests.test_explicit_mode_dynamics_zf
```

The first state-level Krein bridge is
[`Krein state existence versus physical selection in ZF`](reports/krein-state-selection-zf.md).
It constructs explicit positive normalized coordinate and Fock states without
Choice, proves a scoped density-state symmetry obstruction, and promotes three
cube cells while keeping physical state selection, generalized Born
probability, singular states, and Lorentzian claims open:

```bash
python3 foundations/check_krein_state_selection.py
python3 foundations/verify_krein_state_selection_zf.py
python3 -m unittest foundations.tests.test_krein_state_selection_zf
```

The first Phase C audit is the
[`BT separable C*-algebra/state chain`](reports/bt-separable-cstar-state-chain.md).
It separates the compact detector algebra, explicit ZF states and GNS,
semifinite weight, physical state selection, and nonlinear dynamics:

```bash
python3 foundations/check_bt_separable_state_chain.py
python3 foundations/verify_bt_separable_state_chain.py
python3 -m unittest foundations.tests.test_bt_separable_state_chain
```

The first operational-reconstruction proof audit is
[`Hardy's continuity exclusion of K=N`](reports/hardy-continuity-kn-foundational-audit.md).
It distinguishes pointwise continuity from a path supplied with an explicit
uniform modulus and proves an `RCA_0` sufficiency upper bound only for the
latter encoding:

```bash
python3 foundations/check_hardy_continuity_kn.py
python3 foundations/verify_hardy_continuity_kn.py
python3 -m unittest foundations.tests.test_hardy_continuity_kn
```

The finite-objects comparison is
[`finite field versus finite mode`](reports/finite-field-versus-finite-mode.md).
It records pairwise witnesses showing that finite-field phase space, an
energy-mode regulator, finite-dimensional complex Hilbert space, and
foundational finitism are not interchangeable:

```bash
python3 foundations/check_finite_field_finite_mode.py
python3 foundations/verify_finite_field_finite_mode.py
python3 -m unittest foundations.tests.test_finite_field_finite_mode
```

The first continuum-PDE dependency cut is
[`the typed biwave Green theorem audit`](reports/typed-biwave-green-foundational-dependencies.md).
It separates fixed exact resolvent identities from normally-hyperbolic Green
existence, Sobolev completion, energy estimates, Volterra convergence,
uniqueness, causal support, and adjoint duality:

```bash
python3 foundations/check_typed_biwave_green_dependencies.py
python3 foundations/verify_typed_biwave_green_dependencies.py
python3 -m unittest foundations.tests.test_typed_biwave_green_dependencies
```

The flat causal benchmark now extends from the scalar wave equation to the
[`exact scalar biwave Green construction`](reports/scalar-minkowski-biwave-green-v1.md).
It composes the canonical retarded and advanced maps, checks both inverse
identities and adjoint duality with exact rational fixtures, and records the
finite-horizon four-data energy boundary:

```bash
python3 foundations/check_scalar_minkowski_biwave_green.py
python3 foundations/verify_scalar_minkowski_biwave_green.py
python3 -m unittest foundations.tests.test_scalar_minkowski_biwave_green
```

The companion
[`scalar-biwave-to-Weyl-BV dependency delta`](reports/scalar-biwave-to-weyl-bv-dependency-delta-v1.md)
classifies sixteen transfer gates. It imports the scoped positive Nariai
four-row result, the open Berger route, both scoped architectural no-go
theorems, and the still-failed authoritative classical import gate without
promoting a full Lorentzian Weyl BV propagator:

```bash
python3 foundations/check_scalar_biwave_to_weyl_bv_delta.py
python3 foundations/verify_scalar_biwave_to_weyl_bv_delta.py
python3 -m unittest foundations.tests.test_scalar_biwave_to_weyl_bv_delta
```

The first topos/Weyl-BV artifact is the
[`glossary and obstruction ledger`](reports/topos-weyl-bv-obstruction-ledger.md).
It maps ordinary objects to candidate internal objects and checks the
prerequisite DAG, while keeping every continuum, causal, state, renormalization,
and QME construction flag false:

```bash
python3 foundations/check_topos_weyl_bv_obstructions.py
python3 foundations/verify_topos_weyl_bv_obstructions.py
python3 -m unittest foundations.tests.test_topos_weyl_bv_obstructions
```

The closure audit is the
[`ranked opportunity completion matrix`](reports/ranked-opportunity-completion-matrix.md).
It maps all nine source-ranked first artifacts to eight content-pinned results
(ranks 1 and 3 deliberately share the finite BV witness), reruns every child
verifier, and keeps all deeper-programme flags open:

```bash
python3 foundations/check_ranked_opportunity_completion.py
python3 foundations/verify_ranked_opportunity_completion.py
python3 -m unittest foundations.tests.test_ranked_opportunity_completion
```

A generated Markdown projection combines a 6-by-6-by-6 intersection cube,
the detailed 16-by-6 coverage atlas, nine completion rows, and all 45
literature points in
[`completion-matrix.md`](reports/completion-matrix.md):

```bash
python3 foundations/render_completion_matrix_md.py
python3 foundations/render_completion_matrix_md.py --check
python3 -m unittest foundations.tests.test_render_completion_matrix_md
```

The cube is independently checkable. It uses mathematical regime,
carrier/analysis, and physical obligation as its three dimensions, and renders
all six foundation slices with explicit unmapped-versus-priority-gap status:

```bash
python3 foundations/check_intersection_cube.py
python3 foundations/verify_intersection_cube.py
python3 -m unittest foundations.tests.test_intersection_cube
```

The targeted primary-source expansion and exact finite-interaction rail raise
the deliberately assessed portion from 59 to 162 cells (75%).  The expansion
keeps direct literature results, bounded local results, non-composable pieces,
and reviewed gaps as different statuses.  Its 20-source ledger has 18
content-pinned PDFs and two fail-closed metadata-only records:

```bash
python3 foundations/check_finite_qubit_interaction_core.py
python3 foundations/verify_finite_qubit_interaction_core.py
python3 foundations/expand_intersection_cube.py --check
python3 foundations/verify_intersection_cube_expansion.py
python3 -m unittest foundations.tests.test_finite_qubit_interaction_core \
  foundations.tests.test_intersection_cube_expansion
```

Use `python3 foundations/expand_intersection_cube.py --rebuild --write` only
when deliberately regenerating the reviewed 103-cell crosswalk and cube.  A
normal no-option run is read-only and reports its current counts and digest.

The generated
[`pair-frontier analysis`](reports/pair-frontier-analysis.md) projects the cube
onto all 108 products of two dimensions. It ranks pairs only when an assessed
evidence foothold and assessed open work coexist, keeps important-but-unseeded
gaps separate, and never treats an unmapped cell as a literature-absence claim:

```bash
python3 foundations/analyze_pair_frontiers.py
python3 foundations/analyze_pair_frontiers.py --check
python3 foundations/check_pair_frontiers.py
python3 foundations/verify_pair_frontiers.py
python3 -m unittest foundations.tests.test_pair_frontiers
```

The
[`refined intersection cube`](reports/refined-intersection-cube.md) preserves
the v0 cube and splits its overloaded physical-obligation axis from six labels
into sixteen independently auditable questions.  The resulting Cartesian
space has 576 possible coordinates.  Evidence descends into a split child only
through an explicit capability registration; otherwise the cell is marked
`MIGRATION_UNRESOLVED`, not silently inherited or called absent:

```bash
python3 foundations/refine_intersection_cube.py --check
python3 foundations/check_refined_intersection_cube.py
python3 foundations/verify_refined_intersection_cube.py
python3 -m unittest foundations.tests.test_refined_intersection_cube
```

The current physics-to-mathematics implication rail is the
[`cylinder-wave strength ladder v2`](reports/cylinder-wave-strength-ladder-v2.md).
It retains the exact finite Fourier and named-tail rungs, and now certifies an
`RCA_0` upper bound for one explicit polygonal fast-Cauchy energy representation.
It keeps that represented Cauchy theorem separate from a subsystem reversal,
spacetime distributions, and causal Green operators. Its typed graph also
records why finite spectral truncation does not establish causal support:

```bash
python3 foundations/check_cylinder_wave_strength_ladder.py
python3 foundations/verify_cylinder_wave_strength_ladder.py
python3 foundations/build_coded_polygonal_wave_rca0.py --check
python3 foundations/verify_coded_polygonal_wave_rca0.py
python3 foundations/build_cylinder_wave_strength_ladder_v2.py --check
python3 foundations/verify_cylinder_wave_strength_ladder_v2.py
```

The follow-on
[`coded observable reconstruction`](reports/coded-wave-observable-reconstruction-v1.md)
names a rational periodic detector and constructs finite rational dyadic-time
interpolants for three declared rational wave data.  Over `RCA_0` they converge
uniformly on every rational bounded time interval with the explicit,
data-dependent cutoff `N(k)=k+ell(K)+1`; all fixed-code arithmetic is primitive
recursive.  This reconstructs one bounded smeared observable, not the full
field or causal support:

```bash
python3 foundations/build_coded_wave_observable_reconstruction.py --check
python3 foundations/check_coded_wave_observable_reconstruction.py
python3 foundations/verify_coded_wave_observable_reconstruction.py
python3 -m unittest foundations.tests.test_coded_wave_observable_reconstruction
```

The next
[`localized weak-wave test certificate`](reports/coded-local-weak-wave-test-class-v1.md)
uses ten compact-time rational polynomial bumps on the common five-cell
partition of the declared fixtures.  Their labelled chiral measurement matrix
is diagonal of exact rank ten, so the tests separate the declared finite
coefficient carrier.  PRA verifies every pairing and coefficient residual;
`RCA_0` transfers the finitely many bounded weak identities to the represented
completion.  The result is deliberately not a theorem for every smooth test,
an unlabelled scalar reconstruction, causal support, or a Green operator:

```bash
python3 foundations/build_coded_local_weak_wave_test_class.py --check
python3 foundations/check_coded_local_weak_wave_test_class.py
python3 foundations/verify_coded_local_weak_wave_test_class.py
python3 -m unittest foundations.tests.test_coded_local_weak_wave_test_class
```

The representation-aware
[`named H2 test completion`](reports/coded-weak-wave-h2-test-completion-v1.md)
closes the next finite-to-completed weak-equation gate.  Rational periodic
compact-time `C1` piecewise-polynomial codes are completed under a supplied
fast `H2` Cauchy name.  Exact Cauchy--Schwarz bounds give a
primitive-recursive residual cutoff for every declared energy fixture, so the
transport and scalar weak-wave identities extend to every represented test.
The fixed-slab name is a mathematical assumption: it neither constructs names
for bare extensional smooth tests nor recovers the unrestricted nonmetrizable
LF test-function topology.

```bash
python3 foundations/build_coded_weak_wave_h2_test_completion.py --check
python3 foundations/check_coded_weak_wave_h2_test_completion.py
python3 foundations/verify_coded_weak_wave_h2_test_completion.py
python3 -m unittest foundations.tests.test_coded_weak_wave_h2_test_completion
```

The generated
[`static matrix explorer`](site/index.html) turns the complete refined surface
into a browser-based research instrument. It displays all 576 coordinates as
sixteen coordinated heatmaps. Cube v9 emits and assesses all 576 coordinates:
115 carry local results, 93 literature results, 163 partial ingredients, 30
selected priority gaps, and 175 reviewed open gaps; zero remain `NOT_MAPPED`.
A `REVIEWED_GAP` is a formulated question with a typed missing certificate,
not a result, priority assignment, or literature-absence claim. The inspector
separates positive coverage evidence from evidence
reviewed only for migration. The bundle also provides multi-select filters,
evidence-aware search, comparison, one-axis neighbors, permalinks, filtered
exports, investigation briefs, the typed implication graph, the cylinder
strength ladder, and the resolved evidence catalogue. The **Theory profiles**
view adds a 36-profile coverage map, selectable obligation gates, six
foundation-specific carrier envelopes, and a non-scalar Pareto view. It keeps
three rails separate: obligation coverage is computed; cross-cell composition
is partially assessed; and observational agreement is not registered for those
cross-cell profiles. A multi-carrier maximum is therefore labelled a coverage envelope, not
a completed theory. The **Assemblies** view adds nine named research-programme
lenses, seven separately reported maturity rails, and 63 explicitly typed
cross-cell joins. Missing, premature, blocked, and failed work are distinct
states: red is reserved for an explicit obstruction or failed comparison.
Two scoped joins are now certified
`CONDITIONAL_BRIDGE` relations: finite-corner state-to-probability and free
ground-state-to-dynamics. They produce five compatible programme-interface
projections. The other
joins remain `NOT_ASSESSED`, and the candidate empirical ledger is empty, so
every cube-selected prototype remains fail-closed before theory or observational
completion.

The lenses make the larger conversations recognizable: mainstream GR/QFT,
algebraic QFT, finite/discrete exact models, Bateman--Turok, reverse mathematics,
Mannheim conformal gravity, this repository's pure-Weyl BV--BFV programme,
constructive/computable physics, and topos/internal quantum foundations. Each
profile states a central question, lineage, signature ideas, the narrower atlas
window actually sampled, and a caution against treating the map as an
endorsement or exhaustive account of that community.

The Bateman--Turok lens currently samples the positive Euclidean finite lattice.
Its exact import supplies five direct capabilities in
`FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL`, while reconstruction stays a
`PRIORITY_GAP`. A separate numerical rail records only coarse HMC/Metropolis
reproduction; the empirical and robustness rails remain empty. The certified
Euclidean/Krein carrier relation refuses identification as the same full
nonperturbative measure without ruling out every conditional bridge:

```bash
python3 foundations/build_bt_euclidean_lattice_import.py --check
python3 foundations/check_bt_euclidean_lattice_import.py
python3 foundations/verify_bt_euclidean_lattice_import.py
python3 foundations/refine_intersection_cube_v10.py --check
python3 foundations/check_refined_intersection_cube_v10.py
python3 foundations/verify_refined_intersection_cube_v10.py
```

The **Dimensions guide** begins one level earlier than the matrix. It explains
the cube as three public-facing questions---what rules count as proof and
existence, what kind of mathematical object carries the physics, and which
physical job has been completed. Regimes and carriers are grouped by motivation;
the sixteen obligations are arranged as a five-part journey from defining a
theory through dynamics, gauge/interactions, quantum consistency, and return to
observation. Worked GR and constructive-causality examples, a short glossary,
and a collapsed reviewer section keep the conceptual story separate from the
evidence-code mechanics.

The view now leads with two model-scoped vertical slices. The first is
[`FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1`](reports/gr-cassini-model-assembly-v1.md).
It keeps one standard-GR solar-vacuum model identity from the Einstein field
equations through the Schwarzschild solution, exact isotropic translation,
the PPN result `gamma=1`, the null-delay coefficient `gamma+1=2`, and a
separately typed comparison with the publisher's reported Cassini band. Its
applicability mask requires 3 of 16 atlas obligations, touches 2, and places 11
outside this bounded calculation. All five interfaces are registered (three
exact and two literature-scoped), so the assembly is complete within its
declared scope while remaining explicitly false for complete-theory, raw-data
reanalysis, held-out robustness, and Weyl-gravity-support claims:

```bash
python3 foundations/build_gr_cassini_assembly.py --check
python3 foundations/check_gr_cassini_assembly.py
python3 foundations/verify_gr_cassini_assembly.py
python3 -m unittest foundations.tests.test_gr_cassini_assembly
```

The second,
[`FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1`](reports/mannheim-ngc3198-model-assembly-v1.md),
keeps one Mannheim--Kazanas NGC 3198 thin-disk model fixed from the Weyl action
through local static/orbit certificates, the published disk equations and
parameter row, an independently evaluated endpoint, and a no-refit comparison
with a later SPARC curve. The endpoint and unweighted RMS pass declared coarse
audit gates, but the reduced-chi-squared gate based on SPARC random errors
fails. The assembly therefore remains partial and does not claim empirical
support. SPARC is explicitly recorded as a non-identical later data reduction,
and the massive-tracer matter-coupling dispute remains open:

```bash
python3 foundations/build_mannheim_ngc3198_assembly.py --check
python3 foundations/check_mannheim_ngc3198_assembly.py
python3 foundations/verify_mannheim_ngc3198_assembly.py
python3 -m unittest foundations.tests.test_mannheim_ngc3198_assembly
```

The follow-on [common-protocol comparison](reports/ngc3198-common-fit-comparison-v1.md)
fits Newtonian baryons-only, GR plus an NFW halo, and Mannheim conformal
gravity to the same 39 NGC 3198 velocities and analytic baryonic geometry.
The independent C++ checker uses standard-library Bessel functions and a
Nelder--Mead optimizer, distinct from the producer's quadrature and nested
grid. GR+NFW is the only family passing the declared random-error gate and
retains the best AICc after its extra parameters are penalized. This remains a
one-galaxy, random-error-only control, not a complete-theory selection:

```bash
python3 foundations/build_ngc3198_common_fit_comparison.py --write
python3 foundations/check_ngc3198_common_fit_comparison.py
python3 foundations/verify_ngc3198_common_fit_comparison.py
python3 -m unittest foundations.tests.test_ngc3198_common_fit_comparison
```

A separately labelled external standard-GR positive control supplies four
primary-source comparison records across three benchmark families; it
calibrates the display and is neither a cube-selected assembly nor evidence
for Weyl gravity:

```bash
python3 foundations/build_matrix_site_v2.py
python3 foundations/build_matrix_site_v2.py --check
python3 foundations/check_matrix_site_v2.py
python3 foundations/verify_matrix_site_v2.py
python3 foundations/verify_theory_viability.py
python3 foundations/verify_theory_assembly.py
python3 foundations/verify_bt_corner_born_interface.py
python3 foundations/verify_refined_intersection_cube_v5.py
python3 foundations/verify_krein_fock_ground_state_dynamics_interface.py
python3 foundations/verify_refined_intersection_cube_v6.py
python3 foundations/verify_finite_operator_ten_cell_closure.py
python3 foundations/verify_refined_intersection_cube_v7.py
python3 foundations/verify_finite_brst_twenty_cell_closure.py
python3 foundations/verify_refined_intersection_cube_v8.py
python3 foundations/verify_full_surface_gap_audit.py
python3 foundations/verify_refined_intersection_cube_v9.py
python3 foundations/verify_refined_intersection_cube_v10.py
python3 -m unittest foundations.tests.test_matrix_site
python3 -m unittest foundations.tests.test_theory_viability
python3 -m unittest foundations.tests.test_theory_assembly
python3 -m unittest foundations.tests.test_bt_corner_born_interface
python3 -m unittest foundations.tests.test_refined_intersection_cube_v5
python3 -m unittest foundations.tests.test_krein_fock_ground_state_dynamics_interface
python3 -m unittest foundations.tests.test_refined_intersection_cube_v6
python3 -m unittest foundations.tests.test_finite_operator_ten_cell_closure
python3 -m unittest foundations.tests.test_refined_intersection_cube_v7
python3 -m unittest foundations.tests.test_finite_brst_twenty_cell_closure
python3 -m unittest foundations.tests.test_refined_intersection_cube_v8
python3 -m unittest foundations.tests.test_full_surface_gap_audit
python3 -m unittest foundations.tests.test_refined_intersection_cube_v9
python3 -m http.server 8000 --directory foundations/site
```

The generator fails closed on dangling evidence IDs and records every source
and output hash in [`site/manifest.json`](site/manifest.json). Browser claims
are projections of the authoritative JSON artifacts, not a separately edited
scientific catalogue.

The
[`normally-hyperbolic factor atlas`](reports/normal-hyperbolic-factor-foundations.md)
is the first focused research pass over the causal PDE frontier. It separates
classical Green theorems, represented computability upper bounds, adjacent ZF
operator theory, reverse-mathematical non-classification, strict finite support,
and Lieb–Robinson decay. Six primary sources are content-pinned in a dedicated
ledger. An independent exact certificate constructs finite graph-step retarded
and advanced kernels. The research-refined
[`cube v3`](reports/refined-intersection-cube-v3.md) applies nine status changes
and five evidence overlays without rewriting the v2 migration history:

```bash
python3 foundations/build_finite_graph_wave_causality.py --check
python3 foundations/verify_finite_graph_wave_causality.py
python3 foundations/build_normal_hyperbolic_factor_atlas.py --check
python3 foundations/verify_normal_hyperbolic_factor_atlas.py
python3 foundations/refine_intersection_cube_v3.py --check
python3 foundations/verify_refined_intersection_cube_v3.py
```

The independent follow-up literature pass keeps reverse mathematics, proof
mining, TTE computability, Bishop constructivity, and ZF without Countable
Choice as distinct evidence types. The
[`coded-wave frontier`](reports/coded-wave-frontier-v2.md) adds seven reviewed
primary records but finds no direct literature reversal or causal-support
theorem. The resulting [`cube v4`](reports/refined-intersection-cube-v4.md)
promotes two weak-arithmetic Hilbert/operator cells from `PIECES_ONLY` to
`LOCAL_RESULT` and adds five evidence overlays:

```bash
python3 foundations/build_coded_wave_frontier_v2.py --check
python3 foundations/verify_coded_wave_frontier_v2.py
python3 foundations/refine_intersection_cube_v4.py --check
python3 foundations/verify_refined_intersection_cube_v4.py
```

The first object-level cross-cell composition proof is the
[`finite-corner state-to-probability interface`](reports/bt-corner-born-interface.md).
It pins one algebraic corner state and reuses that identical functional to
evaluate public Krein process effects. Under five explicit hypotheses, exact
probabilities are nonnegative and normalized; the independent rational witness
gives `9/25`, `16/25`, and `0`. The append-only
[`cube v5`](reports/refined-intersection-cube-v5.md) therefore promotes the
classical-standard Krein probability cell from `PIECES_ONLY` to `LOCAL_RESULT`
without changing any earlier coordinate or migration decision:

```bash
python3 foundations/build_bt_corner_born_interface.py --check
python3 foundations/check_bt_corner_born_interface.py
python3 foundations/verify_bt_corner_born_interface.py
python3 foundations/refine_intersection_cube_v5.py --check
python3 foundations/check_refined_intersection_cube_v5.py
python3 foundations/verify_refined_intersection_cube_v5.py
```

The second object-level composition proof is the
[`free Krein--Fock ground-state-to-dynamics interface`](reports/krein-fock-ground-state-dynamics-interface.md).
On the shared occupation carrier, all one-particle energies are integers at
least two. The empty occupation is therefore the unique zero-energy ray and
selects the unique normal density state of zero extended mean energy. The
identical total energy generates the free Fock evolution, which fixes that
vacuum and leaves its state invariant. The append-only
[`cube v6`](reports/refined-intersection-cube-v6.md) overlays this direct
interface evidence without changing either endpoint's existing local-result
grade or any earlier migration decision:

```bash
python3 foundations/build_krein_fock_ground_state_dynamics_interface.py --check
python3 foundations/check_krein_fock_ground_state_dynamics_interface.py
python3 foundations/verify_krein_fock_ground_state_dynamics_interface.py
python3 foundations/refine_intersection_cube_v6.py --check
python3 foundations/check_refined_intersection_cube_v6.py
python3 foundations/verify_refined_intersection_cube_v6.py
```

The exact
[`finite-operator ten-cell closure`](reports/finite-operator-ten-cell-closure.md)
reconstructs all sixteen two-qubit Pauli words over Gaussian rationals and
checks their Hilbert basis, a genuine entangling interaction, a finite Krein
realization, the complete parity-preserving correction space, all 256 regulated
basis products, and a constructive finite-corner probability rule. The
append-only [`cube v7`](reports/refined-intersection-cube-v7.md) applies this
single certificate to exactly ten previously `NOT_MAPPED` coordinates: nine
become `LOCAL_RESULT`, while the finite regulated-product coordinate remains
`PIECES_ONLY` because no continuum renormalization construction is present:

```bash
python3 foundations/build_finite_operator_ten_cell_closure.py --check
python3 foundations/check_finite_operator_ten_cell_closure.py
python3 foundations/verify_finite_operator_ten_cell_closure.py
python3 foundations/refine_intersection_cube_v7.py --check
python3 foundations/check_refined_intersection_cube_v7.py
python3 foundations/verify_refined_intersection_cube_v7.py
```

The exact
[`finite BRST twenty-cell closure`](reports/finite-brst-twenty-cell-closure.md)
uses a six-generator rational complex to classify `H^0` counterterms and `H^1`
anomalies, cancel a named one-loop defect, and only then transfer the restored
correction through an exact contraction. Its bounded Hilbert realization and
finite Krein adjoint are checked independently. The append-only
[`cube v8`](reports/refined-intersection-cube-v8.md) applies the certificate to
exactly twenty cube-v7 `NOT_MAPPED` coordinates. Seventeen become
`LOCAL_RESULT`; three matrix-product coordinates remain `PIECES_ONLY` because
finite closure does not supply continuum renormalization. The result is scoped
to this toy complex and does not promote a Weyl QME or Weyl residual transfer:

```bash
python3 foundations/build_finite_brst_twenty_cell_closure.py --check
python3 foundations/check_finite_brst_twenty_cell_closure.py
python3 foundations/verify_finite_brst_twenty_cell_closure.py
python3 foundations/refine_intersection_cube_v8.py --check
python3 foundations/check_refined_intersection_cube_v8.py
python3 foundations/verify_refined_intersection_cube_v8.py
```

The
[`full 576-coordinate gap audit`](reports/full-surface-gap-audit.md) identifies
the exact complement left by cube v8: 51 emitted blanks and 124 previously
browser-only coordinates. It formulates each as a coherent research question,
records the foundation and carrier requirements and missing theorem-level
certificate, and classifies all 175 as `REVIEWED_GAP`. The append-only
[`cube v9`](reports/refined-intersection-cube-v9.md) applies that audit while
preserving all 401 earlier classifications and both certified interfaces. Full
assessment is explicitly not full scientific or literature coverage.

The append-only [`cube v10`](reports/refined-intersection-cube-v10.md) then
changes exactly six declared finite-Euclidean coordinates: five become direct
local results and the reconstruction coordinate receives supporting evidence
without promotion. It adds the carrier non-identity on a separate interface
ledger rather than treating it as one of the seven theory-composition joins.

The append-only [`cube v11`](reports/refined-intersection-cube-v11.md) imports
the coded observable theorem into exactly two weak-arithmetic Hilbert/operator
coordinates.  Kinematics/observables and reconstruction/limits become direct
local results in that declared scalar-wave scope; the other 574 cells and all
interface ledgers remain byte-preserved.

The append-only [`cube v12`](reports/refined-intersection-cube-v12.md) imports
the localized coefficient-weak theorem into exactly three weak-arithmetic
smooth/distributional coordinates.  Kinematics/observables becomes a direct
local result; reconstruction moves to pieces-only; distributional
well-posedness remains pieces-only because a finite test span is compatibility
evidence, not an existence-and-uniqueness theorem.

The append-only [`cube v13`](reports/refined-intersection-cube-v13.md) imports
the named `H2` completion into exactly four weak-arithmetic
smooth/distributional coordinates.  State representation and scoped
energy-image well-posedness become direct local results.  Reconstruction stays
pieces-only because the conventional smooth-name translator, unrestricted LF
support topology, and uniqueness among arbitrary distributions remain open.

```bash
python3 foundations/build_full_surface_gap_audit.py --check
python3 foundations/check_full_surface_gap_audit.py
python3 foundations/verify_full_surface_gap_audit.py
python3 foundations/refine_intersection_cube_v9.py --check
python3 foundations/check_refined_intersection_cube_v9.py
python3 foundations/verify_refined_intersection_cube_v9.py
python3 foundations/refine_intersection_cube_v10.py --check
python3 foundations/check_refined_intersection_cube_v10.py
python3 foundations/verify_refined_intersection_cube_v10.py
python3 foundations/refine_intersection_cube_v11.py --check
python3 foundations/check_refined_intersection_cube_v11.py
python3 foundations/verify_refined_intersection_cube_v11.py
python3 foundations/refine_intersection_cube_v12.py --check
python3 foundations/check_refined_intersection_cube_v12.py
python3 foundations/verify_refined_intersection_cube_v12.py
python3 foundations/refine_intersection_cube_v13.py --check
python3 foundations/check_refined_intersection_cube_v13.py
python3 foundations/verify_refined_intersection_cube_v13.py
python3 -m unittest foundations.tests.test_full_surface_gap_audit \
  foundations.tests.test_refined_intersection_cube_v9 \
  foundations.tests.test_refined_intersection_cube_v10 \
  foundations.tests.test_refined_intersection_cube_v11 \
  foundations.tests.test_refined_intersection_cube_v12 \
  foundations.tests.test_refined_intersection_cube_v13
```

The append-only
[`migration-reviewed cube v2`](reports/refined-intersection-cube-v2.md) clears
the 112 v1 migration questions without confusing evidence transfer with
scientific coverage.  Its explicit
[`decision ledger`](reports/intersection-cube-migration-audit-v2.md) reviews 12
descendants of direct results first, batches 76 descendants of pieces-only
parents by 18 repeated evidence sets, and decomposes 24 evidence-free parent
gaps into child-specific programme gaps.  The result is 88
`REVIEWED_NO_TRANSFER` cells with coverage `NOT_MAPPED`, 24 reviewed child
gaps, and zero pending migrations.  `NOT_MAPPED` remains a non-absence state:

```bash
python3 foundations/audit_intersection_migrations.py --check
python3 foundations/check_intersection_migration_audit.py
python3 foundations/verify_intersection_migration_audit.py
python3 foundations/refine_intersection_cube_v2.py --check
python3 foundations/check_refined_intersection_cube_v2.py
python3 foundations/verify_refined_intersection_cube_v2.py
```

The existing explorer is regenerated from this migration-reviewed cube. Its
content-addressed source bundle and manifest remain under [`site/`](site/), and
the inspector links each reviewed cell to the 112-decision JSON ledger and its
human-readable audit report.

The bounded
[`low-hanging cell closure audit`](reports/low-hanging-cell-closure-audit.md)
imports the already-certified local BV cohomology and finite-cutoff dynamics,
corrects three stale open-cell labels, and gives every one of the then-22
assessed open cells in that bounded audit a typed missing gate.  Its exhaustion statement excludes
all currently not-mapped cells and preserves the failed broader classical freeze
gate:

```bash
python3 foundations/check_low_hanging_cell_closure.py
python3 foundations/verify_low_hanging_cell_closure.py
python3 -m unittest foundations.tests.test_low_hanging_cell_closure
```

Native typed Scope/Question/WorkItem import is not yet available in the local
Science Forge adoption.  The exact integration boundary and first consumer are
filed in
[`foundations-scope-frontier-importer.json`](../planning/forge-requests/foundations-scope-frontier-importer.json);
the local analyzer remains the independent comparison rail.

## Lorentzian Weyl BV completion atlas

The
[`branch-by-stage completion atlas`](reports/lorentzian-weyl-bv-completion-atlas-v1.md)
compares seven physically distinct routes across eleven causal quantum gates.
It records two fronts instead of manufacturing one score: strict pure Weyl is
the identity-preserving target and already has a scoped 386-row classical
causal homotopy, while the Berger positive-clock branch is furthest along the
analytic lifecycle with a complete 54-row causal complex, cyclic D-Cartan
closure through arity three, and a 26-row exact-CCR Hadamard candidate whose
remaining Ward defect is smooth.  The atlas also reconciles the historical
fail-closed import gate with later exact repair receipts without treating those
receipts as an implicit replacement freeze certificate.

The audited
[`V2 completion atlas`](reports/lorentzian-weyl-bv-completion-atlas-v2.md)
incorporates the repaired standalone import replay and the complete eleven-step
Berger H26/C26 carrier decision chain.  It separates scoped failures from a
rational non-cone rank-feasibility control, so the known 104-row obstructions
are not misreported as a global no-go.  Its ranked research queue selects the
strict residual SDR payload as the most tractable high-leverage target-theory
gate and direct nonstationary q26-equivariant Hadamard selection as the leading
high-risk analytic experiment.  The existing static explorer exposes the same
seven-by-eleven route surface under **Weyl BV routes**.

The append-only
[`V3 completion atlas`](reports/lorentzian-weyl-bv-completion-atlas-v3.md)
records the first completed item from that queue.  Exact sparse matrices now
export the strict finite residual `iota_cl`, `pi_cl`, and `s_cl` on 4,490 full
and 470 residual coordinates, and an independent receiver replays all eight
SDR identities.  The atlas does not call this the continuum contraction:
Gate A retains zero accepted common-snapshot hashes, and M3 is narrowed to a
full support-local carrier extension.  The route queue therefore puts strict
support-local `q2`/`D` first, the full-carrier residual-SDR lift second, and
the direct nonstationary Berger selection third.  The existing explorer is
regenerated in place and presents both the progress and its boundary.

```bash
python3 foundations/build_lorentzian_weyl_bv_completion_atlas.py --check
python3 foundations/check_lorentzian_weyl_bv_completion_atlas.py
python3 foundations/verify_lorentzian_weyl_bv_completion_atlas.py
python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas
python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v2.py --check
python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v2.py
python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v2.py
python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v2
python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v3.py --check
python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v3.py
python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v3.py
python3 -m unittest foundations.tests.test_lorentzian_weyl_bv_completion_atlas_v3
```

## Lifecycle

This stream uses a literature/research lifecycle, not the quantum lifecycle:

```text
QUESTION_FORMED -> LITERATURE_SCOPED -> FORMALIZED -> SEPARATED
                -> NECESSITY_PROVED / SUFFICIENCY_PROVED
                -> EQUIVALENCE_PROVED
```

`LITERATURE_SCOPED` means that sources and candidate implications have been
identified.  It is not a theorem, a coefficient, a quantum-master-equation
result, or evidence for a Lorentzian claim.
