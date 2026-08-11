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

The first Phase C audit is the
[`BT separable C*-algebra/state chain`](reports/bt-separable-cstar-state-chain.md).
It separates the compact detector algebra, explicit ZF states and GNS,
semifinite weight, physical state selection, and nonlinear dynamics:

```bash
python3 foundations/check_bt_separable_state_chain.py
python3 foundations/verify_bt_separable_state_chain.py
python3 -m unittest foundations.tests.test_bt_separable_state_chain
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
