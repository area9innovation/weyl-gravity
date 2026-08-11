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
the detailed 16-by-6 coverage atlas, nine completion rows, and all 25
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

The bounded
[`low-hanging cell closure audit`](reports/low-hanging-cell-closure-audit.md)
imports the already-certified local BV cohomology and finite-cutoff dynamics,
corrects three stale open-cell labels, and gives every one of the 22 remaining
assessed open cells a typed missing gate.  Its exhaustion statement excludes
all 157 not-mapped cells and preserves the failed broader classical freeze
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
