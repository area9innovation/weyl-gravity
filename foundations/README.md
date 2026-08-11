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
