#!/usr/bin/env python3
"""Screen the retained mixed ell3 against constant-field cyclic redefinitions.

This is the first, deliberately scoped, page of the N-G4 deformation test.  It
sets every PBW derivative word to zero, lowers the physical operations with the
typed retained odd pairing, and works on the complete mixed quartic space

    Sym^2(G^*) tensor Sym^2(A^*)

for the ten dressed metric fields ``G`` and four Maxwell potentials ``A``.
Matter-parity-preserving base-field maps ``F2`` and ``F3`` are extended by
their BV-canonical cotangent lift.  On the lowered action their infinitesimal
arity-three coboundary is

    delta S4 = sum_i (partial_i S2) F3^i + sum_i (partial_i S3) F2^i.

The result is a constant-field/G0 screen.  Derivative-dependent redefinitions
and the full jet-bounded deformation complex remain downstream.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Mapping

from jsonschema import Draft202012Validator
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
LEGACY_CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
TYPED_CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
GRAVITY_ELL2 = ROOT / "quantum-weyl/transfer/certificates/BERGER_RETAINED_26_Q2_PAYLOAD.json"
MIXED_ELL2 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD.json"
MIXED_ELL3 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_PAYLOAD.json"
TRANSFER = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-constant-field-redefinition-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-constant-field-redefinition.md"
VERIFIER = HERE / "verify_berger_retained_mixed_ell3_constant_field_redefinition.py"
TESTS = HERE / "tests/test_berger_retained_mixed_ell3_constant_field_redefinition.py"

SQRT10 = sp.sqrt(10)
GRAVITY = tuple(range(10))
MAXWELL = tuple(range(10, 14))
FIELD_ROWS = tuple(range(3, 13)) + tuple(range(27, 31))
FIELD_LOCAL = {row: index for index, row in enumerate(FIELD_ROWS)}
PAIRING = {
    **{row: (FIELD_LOCAL[row - 10], sp.Integer(1)) for row in range(13, 23)},
    **{row: (FIELD_LOCAL[row - 4], sp.Integer(2)) for row in range(31, 35)},
}

Monomial = tuple[int, ...]
Polynomial = dict[Monomial, sp.Expr]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _scalar(value: object) -> sp.Expr:
    if isinstance(value, int):
        return sp.Integer(value)
    if isinstance(value, str):
        return sp.sympify(value, locals={"sqrt": sp.sqrt})
    if not isinstance(value, dict):
        raise ValueError(f"invalid exact scalar: {value!r}")
    return sp.Rational(int(value["numerator"]), int(value["denominator"]))


def _q10(value: Mapping[str, object]) -> sp.Expr:
    return sp.expand(_scalar(value["rational"]) + SQRT10 * _scalar(value["sqrt10"]))


def _add(poly: Polynomial, monomial: Iterable[int], coefficient: sp.Expr) -> None:
    key = tuple(sorted(monomial))
    value = sp.expand(poly.get(key, sp.Integer(0)) + coefficient)
    if value == 0:
        poly.pop(key, None)
    else:
        poly[key] = value


def _derivative(poly: Mapping[Monomial, sp.Expr], field: int) -> Polynomial:
    value: Polynomial = {}
    for monomial, coefficient in poly.items():
        multiplicity = monomial.count(field)
        if multiplicity:
            reduced = list(monomial)
            reduced.remove(field)
            _add(value, reduced, coefficient * multiplicity)
    return value


def _dependency(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _action_polynomials() -> tuple[Polynomial, Polynomial, Polynomial, dict[str, object]]:
    legacy = _load(LEGACY_CARRIER)
    typed = _load(TYPED_CARRIER)
    gravity = _load(GRAVITY_ELL2)
    mixed2 = _load(MIXED_ELL2)
    mixed3 = _load(MIXED_ELL3)
    transfer = _load(TRANSFER)

    rows = legacy["retained_complex"]["component_rows"]
    if [row["index"] for row in rows if row["degree"] == 0] != list(FIELD_ROWS):
        raise ValueError("retained physical-field ledger drifted")
    if typed["retained_complex"]["typed_cyclic_pairing"]["shape"] != [36, 36]:
        raise ValueError("typed retained pairing drifted")
    if transfer["retained_ell3"]["maximum_total_jet_order"] != 2:
        raise ValueError("retained ell3 jet ledger drifted")

    quadratic: Polynomial = {}
    for output, source, terms in typed["retained_complex"]["classical_unary_q1"]["entries"]:
        if output not in PAIRING or source not in FIELD_LOCAL:
            continue
        paired, weight = PAIRING[output]
        for word, coefficient in terms:
            if sum(word) == 0:
                _add(quadratic, (paired, FIELD_LOCAL[source]), weight * _scalar(coefficient))

    cubic: Polynomial = {}
    for payload in (gravity, mixed2):
        for row in payload["rows"]:
            output = row["output"]
            if output not in PAIRING:
                continue
            paired, weight = PAIRING[output]
            for left, left_word, right, right_word, coefficient in row["terms"]:
                if (
                    left in FIELD_LOCAL
                    and right in FIELD_LOCAL
                    and sum(left_word) + sum(right_word) == 0
                ):
                    _add(
                        cubic,
                        (paired, FIELD_LOCAL[left], FIELD_LOCAL[right]),
                        weight * _q10(coefficient),
                    )

    quartic: Polynomial = {}
    seen: set[int] = set()
    for chunk in mixed3["chunks"]:
        path = ROOT / chunk["path"]
        if _sha256(path) != chunk["file_sha256"]:
            raise ValueError(f"retained ell3 row digest drifted: {chunk['output']}")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        output = row["output"]
        if output in seen:
            raise ValueError("duplicate retained ell3 output row")
        seen.add(output)
        if output not in PAIRING:
            continue
        paired, weight = PAIRING[output]
        for first, first_word, second, second_word, third, third_word, coefficient in row["terms"]:
            if (
                first in FIELD_LOCAL
                and second in FIELD_LOCAL
                and third in FIELD_LOCAL
                and sum(first_word) + sum(second_word) + sum(third_word) == 0
            ):
                _add(
                    quartic,
                    (paired, FIELD_LOCAL[first], FIELD_LOCAL[second], FIELD_LOCAL[third]),
                    weight * _q10(coefficient),
                )
    if seen != set(range(36)):
        raise ValueError("retained ell3 row ledger is incomplete")
    return quadratic, cubic, quartic, {
        "legacy_carrier": legacy,
        "typed_carrier": typed,
        "gravity_ell2": gravity,
        "mixed_ell2": mixed2,
        "mixed_ell3": mixed3,
        "transfer": transfer,
    }


def _mixed_basis() -> tuple[Monomial, ...]:
    return tuple(
        tuple(sorted((*gravity, *Maxwell)))
        for gravity in itertools.combinations_with_replacement(GRAVITY, 2)
        for Maxwell in itertools.combinations_with_replacement(MAXWELL, 2)
    )


def _labels() -> tuple[tuple[str, int, Monomial], ...]:
    labels: list[tuple[str, int, Monomial]] = []
    for output in GRAVITY:
        for gravity in GRAVITY:
            for Maxwell in itertools.combinations_with_replacement(MAXWELL, 2):
                labels.append(("F3", output, (gravity, *Maxwell)))
    for output in MAXWELL:
        for gravity in itertools.combinations_with_replacement(GRAVITY, 2):
            for Maxwell in MAXWELL:
                labels.append(("F3", output, (*gravity, Maxwell)))
    for output in GRAVITY:
        for gravity in itertools.combinations_with_replacement(GRAVITY, 2):
            labels.append(("F2", output, gravity))
        for Maxwell in itertools.combinations_with_replacement(MAXWELL, 2):
            labels.append(("F2", output, Maxwell))
    for output in MAXWELL:
        for gravity in GRAVITY:
            for Maxwell in MAXWELL:
                labels.append(("F2", output, (gravity, Maxwell)))
    return tuple(labels)


def _column(
    derivative: Mapping[Monomial, sp.Expr],
    inputs: Monomial,
    row_index: Mapping[Monomial, int],
) -> dict[int, sp.Expr]:
    value: dict[int, sp.Expr] = {}
    for monomial, coefficient in derivative.items():
        target = tuple(sorted((*monomial, *inputs)))
        if target in row_index:
            row = row_index[target]
            value[row] = sp.expand(value.get(row, 0) + coefficient)
    return {row: coefficient for row, coefficient in value.items() if coefficient != 0}


def _redefinition_matrix(
    quadratic: Mapping[Monomial, sp.Expr],
    cubic: Mapping[Monomial, sp.Expr],
) -> tuple[sp.MutableSparseMatrix, tuple[Monomial, ...], tuple[tuple[str, int, Monomial], ...]]:
    basis = _mixed_basis()
    if len(basis) != 550 or len(set(basis)) != 550:
        raise AssertionError("mixed quartic basis count drifted")
    row_index = {monomial: row for row, monomial in enumerate(basis)}
    labels = _labels()
    if len(labels) != 2690:
        raise AssertionError("redefinition ansatz count drifted")
    d2 = tuple(_derivative(quadratic, field) for field in range(14))
    d3 = tuple(_derivative(cubic, field) for field in range(14))
    entries: dict[tuple[int, int], sp.Expr] = {}
    for column, (arity, output, inputs) in enumerate(labels):
        derivative = d2[output] if arity == "F3" else d3[output]
        for row, coefficient in _column(derivative, inputs, row_index).items():
            entries[(row, column)] = coefficient
    return sp.MutableSparseMatrix(550, len(labels), entries), basis, labels


def _target_vector(quartic: Mapping[Monomial, sp.Expr], basis: tuple[Monomial, ...]) -> sp.Matrix:
    outside = set(quartic) - set(basis)
    if outside:
        raise ValueError(f"constant physical ell3 contains non-g2A2 monomial: {min(outside)}")
    return sp.Matrix([quartic.get(monomial, 0) for monomial in basis])


def _structural_matching(matrix: sp.Matrix) -> tuple[int, ...]:
    """Return a deterministic row-to-column perfect matching of the support.

    The matching is only a sparse-basis heuristic.  The selected block is
    subsequently checked and solved over the exact algebraic coefficient
    field, so no floating-point or structural-rank claim enters the theorem.
    """

    support = sorted(matrix.todok())
    rows = np.fromiter((row for row, _ in support), dtype=np.int64)
    columns = np.fromiter((column for _, column in support), dtype=np.int64)
    graph = csr_matrix(
        (np.ones(len(support), dtype=np.int8), (rows, columns)),
        shape=matrix.shape,
    )
    matching = maximum_bipartite_matching(graph, perm_type="column")
    if len(matching) != matrix.rows or np.any(matching < 0):
        raise ValueError("constant-field redefinition support has no perfect matching")
    return tuple(int(column) for column in matching)


def _primitive(matrix: sp.Matrix, target: sp.Matrix) -> tuple[sp.Matrix, tuple[int, ...]]:
    # A deterministic support matching selects a sparse 550-column square
    # block.  Its exact full rank (not the matching alone) proves surjectivity.
    # Solving this block fixes one compact primitive; all other coefficients
    # are set to zero.
    pivots = _structural_matching(matrix)
    square = matrix[:, list(pivots)]
    if square.rank() != matrix.rows:
        raise ValueError("matched constant-field redefinition block is not exact full rank")
    solution = square.inv().multiply(target)
    primitive = sp.zeros(matrix.cols, 1)
    for pivot, coefficient in zip(pivots, solution, strict=True):
        primitive[pivot] = sp.factor(coefficient)
    if matrix * primitive != target:
        raise ValueError("exact constant-field primitive failed")
    return primitive, tuple(int(pivot) for pivot in pivots)


def exact_data() -> dict[str, object]:
    quadratic, cubic, quartic, inputs = _action_polynomials()
    matrix, basis, labels = _redefinition_matrix(quadratic, cubic)
    target = _target_vector(quartic, basis)
    primitive, pivots = _primitive(matrix, target)
    nonzero = [index for index, value in enumerate(primitive) if value != 0]
    reconstruction = matrix * primitive
    if reconstruction != target:
        raise AssertionError("primitive reconstruction drifted")
    return {
        "quadratic": quadratic,
        "cubic": cubic,
        "quartic": quartic,
        "inputs": inputs,
        "matrix": matrix,
        "basis": basis,
        "labels": labels,
        "target": target,
        "primitive": primitive,
        "pivots": pivots,
        "nonzero": nonzero,
    }


def _primitive_record(data: Mapping[str, object]) -> list[dict[str, object]]:
    labels = data["labels"]
    primitive = data["primitive"]
    return [
        {
            "arity": labels[index][0],
            "output_local": labels[index][1],
            "output_row": FIELD_ROWS[labels[index][1]],
            "input_locals": list(labels[index][2]),
            "input_rows": [FIELD_ROWS[field] for field in labels[index][2]],
            "coefficient": str(sp.factor(primitive[index])),
        }
        for index in data["nonzero"]
    ]


def build() -> dict:
    data = exact_data()
    dependencies = {
        "legacy_retained_carrier": _dependency(LEGACY_CARRIER, "BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR"),
        "typed_retained_carrier": _dependency(TYPED_CARRIER, "BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR"),
        "retained_gravity_ell2": _dependency(GRAVITY_ELL2, "BERGER_RETAINED_26_Q2_PAYLOAD"),
        "retained_mixed_ell2": _dependency(MIXED_ELL2, "BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD"),
        "retained_mixed_ell3": _dependency(MIXED_ELL3, "BERGER_RETAINED_MIXED_ELL3_PAYLOAD"),
        "retained_mixed_ell3_transfer": _dependency(TRANSFER, "BERGER_RETAINED_MIXED_ELL3_TRANSFER"),
    }
    source_manifest = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    target_nonzero = sum(value != 0 for value in data["target"])
    primitive = _primitive_record(data)
    arity_counts = Counter(record["arity"] for record in primitive)
    return {
        "schema": "pure-weyl-berger-retained-mixed-ell3-constant-field-redefinition-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1",
        "result_state": "CONSTANT_FIELD_PHYSICAL_MIXED_QUARTIC_TRIVIALIZED_FULL_BV_AND_POSITIVE_JET_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "dependency_refs": dependencies,
        "constant_field_quotient": {
            "operation": "ev_0 sets every PBW derivative word to zero after lowering with the typed retained odd pairing",
            "gravity_field_rows": list(FIELD_ROWS[:10]),
            "Maxwell_field_rows": list(FIELD_ROWS[10:]),
            "mixed_quartic_space": "Sym^2(G^*) tensor Sym^2(A^*)",
            "mixed_quartic_dimension": 550,
            "quadratic_action_monomials": len(data["quadratic"]),
            "cubic_action_monomials": len(data["cubic"]),
            "landed_mixed_quartic_monomials": len(data["quartic"]),
            "landed_nonzero_target_coordinates": target_nonzero,
        },
        "admissible_redefinition_ansatz": {
            "formula": "delta S4=sum_i (partial_i S2) F3^i + sum_i (partial_i S3) F2^i",
            "coefficient_field": "Q(sqrt(10))",
            "support_local": True,
            "maximum_jet_order": 0,
            "K_Berger_equivariant_reason": "K_Berger is represented by e0 on the frozen dressed rows; all ansatz coefficients are constant",
            "BV_cyclicity_reason": "each base-field polynomial map is extended by its canonical cotangent lift; the solve is performed on the lowered action tensor",
            "matter_parity": "F2 and F3 preserve Maxwell number modulo two",
            "F2_unknown_count": 810,
            "F3_unknown_count": 1880,
            "total_unknown_count": 2690,
        },
        "exact_verdict": {
            "coboundary_matrix_shape": [550, 2690],
            "coboundary_matrix_nonzero_entries": len(data["matrix"].todok()),
            "coboundary_rank": len(data["pivots"]),
            "augmented_rank": len(data["pivots"]),
            "cokernel_dimension": 0,
            "rank_basis_columns": list(data["pivots"]),
            "target_in_image": True,
            "primitive_nonzero_count": len(primitive),
            "primitive_arity_counts": {"F2": arity_counts["F2"], "F3": arity_counts["F3"]},
            "primitive": primitive,
            "reconstruction_exact": True,
        },
        "interpretation": {
            "displayed_zero_derivative_witnesses_define_invariant_class": False,
            "reason": "the entire 550-dimensional constant-field g^2 A^2 quartic sector is an exact image, so coefficient evaluations at zero PBW word cannot witness N-G4 nonremovability",
            "full_landed_ell3_trivialized": False,
            "constant_field_ghost_antifield_completion_matched": False,
            "derivative_dependent_redefinition_complex_computed": False,
            "operation_on_ell1_cohomology_computed": False,
            "branch_mixing_table_authorized": False,
        },
        "exact_checks": {
            "typed_pairing_lowering_used": True,
            "complete_constant_field_matter_parity_ansatz_enumerated": True,
            "constant_field_coboundary_map_surjective": True,
            "explicit_primitive_reconstructs_target": True,
            "no_floating_point": True,
        },
        "claim_flags": {
            "CONSTANT_FIELD_PHYSICAL_QUARTIC_TRIVIALIZATION_COMPUTED": True,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "FULL_JET_BOUNDED_REDEFINITION_COMPUTED": False,
            "ELL3_NONREMOVABLE": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_CYCLIC_REDEFINITION",
        "provenance": {
            "source_manifest": source_manifest,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_constant_field_redefinition.py --check",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_constant_field_redefinition.py",
                "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_constant_field_redefinition -v",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-constant-field-redefinition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1.json",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC G0 theorem evaluates the degree-zero lowered physical-action part of the landed retained mixed ell3 and all admissible matter-parity-preserving constant-coefficient, zero-jet cyclic cotangent-lift F2/F3 base-field redefinitions on the unsplit 36-row carrier. The exact coboundary map is surjective on the complete 550-dimensional constant-field g^2 A^2 quartic sector, and the exported primitive reconstructs all 63 nonzero physical target coordinates. Therefore the paper's zero-derivative physical evaluations do not by themselves define a nonremovable cyclic deformation class. This does not independently match the 288 ghost/antifield completion coefficients, trivialize any positive-jet coefficient, decide the full jet-bounded cyclic deformation complex, compute an operation on ell1 cohomology, authorize a branch mixing table, prove SDR invariance, or make a quantum claim.",
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if (
        flags["CONSTANT_FIELD_PHYSICAL_QUARTIC_TRIVIALIZATION_COMPUTED"] is not True
        or flags["CYCLIC_DEFORMATION_CLASS_DECIDED"] is not False
        or flags["FULL_JET_BOUNDED_REDEFINITION_COMPUTED"] is not False
        or flags["ELL3_NONREMOVABLE"] is not False
        or flags["ELL3_BRANCH_MIXING_AUTHORIZED"] is not False
        or flags["QUANTUM_CLAIM"] is not False
    ):
        raise ValueError("claim boundary drifted")
    verdict = value["exact_verdict"]
    if (
        verdict["coboundary_rank"] != 550
        or verdict["cokernel_dimension"] != 0
        or verdict["target_in_image"] is not True
        or verdict["reconstruction_exact"] is not True
    ):
        raise ValueError("constant-field exact verdict drifted")
    if not verdict["primitive"]:
        raise ValueError("constant-field primitive is empty")


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict) -> str:
    verdict = value["exact_verdict"]
    return f"""# Retained mixed ell3 constant-field redefinition screen

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

After setting every PBW derivative word to zero and lowering with the typed
retained odd pairing, the mixed physical action lies in

```text
Sym^2(G*) tensor Sym^2(A*)
dimension = 550
```

The complete matter-parity-preserving zero-jet cotangent-lift ansatz has 810
`F2` and 1,880 `F3` coefficients. Its exact coboundary matrix has shape
`550 x 2690`, {verdict['coboundary_matrix_nonzero_entries']} nonzero entries,
rank 550, and zero-dimensional cokernel. The landed constant-field mixed
quartic has 63 nonzero coordinates and the exported
{verdict['primitive_nonzero_count']}-coefficient primitive reconstructs all
of them exactly.

## Meaning

The two zero-derivative representative evaluations printed in Paper 11 prove
that the frozen retained tensor is nonzero, but they cannot be used as
nonremovability witnesses: the *entire* constant-field mixed quartic sector is
an exact redefinition image.

This does **not** settle N-G4. The 288 ghost/antifield completion coefficients
have not been independently matched by this primitive. Positive-jet terms,
integration-by-parts relations, the complete jet-bounded cyclic redefinition
complex, descent to `ell1` cohomology, and branch-resolved mixing remain open. The next gate is
`BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_CYCLIC_REDEFINITION`.
"""


def write() -> dict:
    value = build()
    validate(value)
    OUTPUT.write_text(_json(value))
    REPORT.write_text(_report(value))
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.check:
        if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != value:
            raise SystemExit(f"constant-field redefinition certificate is stale: {OUTPUT}")
    if args.write or not args.check:
        OUTPUT.write_text(_json(value))
        REPORT.write_text(_report(value))
    print("BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1: PASS")


if __name__ == "__main__":
    main()
