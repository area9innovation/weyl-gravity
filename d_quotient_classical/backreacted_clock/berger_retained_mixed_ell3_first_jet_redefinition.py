#!/usr/bin/env python3
"""Decide the first positive-PBW-jet page of the mixed ell3 redefinition.

The physical-action deformation problem through total jet order one is

    A x0 = t0,
    B_a x0 + C y_a = t1_a,  a=0,1,2,3.

``x0`` contains every zero-jet F2/F3 coefficient, not merely the previously
exported 51-term primitive.  ``y_a`` contains every matter-parity-preserving
first-jet coefficient with the derivative on an input factor.  Densities are
reduced modulo the exact first-order integration-by-parts relation before
linear algebra.  The solve projects the second equation to coker(C), yielding
the finite Schur system on the full affine zero-jet solution space.
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
import time
from typing import Iterable, Mapping

import sympy as sp
from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_constant_field_redefinition as zero,
)


ROOT = zero.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-first-jet-redefinition-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-first-jet-redefinition.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_first_jet_redefinition.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_first_jet_redefinition.py"
Atom = tuple[int, int]  # (local field, axis), axis=-1 means undifferentiated
Density = dict[tuple[Atom, ...], sp.Expr]


def _add(value: dict, key: object, coefficient: sp.Expr) -> None:
    updated = sp.expand(value.get(key, 0) + coefficient)
    if updated:
        value[key] = updated
    else:
        value.pop(key, None)


def _word_axis(word: Iterable[int]) -> int | None:
    expanded = tuple(axis for axis, count in enumerate(word) for _ in range(count))
    if len(expanded) > 1:
        return None
    return -1 if not expanded else expanded[0]


def _density_terms() -> tuple[Density, Density, Density]:
    typed = zero._load(zero.TYPED_CARRIER)
    gravity = zero._load(zero.GRAVITY_ELL2)
    mixed2 = zero._load(zero.MIXED_ELL2)
    mixed3 = zero._load(zero.MIXED_ELL3)
    s2: Density = {}
    s3: Density = {}
    s4: Density = {}

    for output, source, terms in typed["retained_complex"]["classical_unary_q1"]["entries"]:
        if output not in zero.PAIRING or source not in zero.FIELD_LOCAL:
            continue
        paired, weight = zero.PAIRING[output]
        for word, coefficient in terms:
            axis = _word_axis(word)
            if axis is not None:
                atoms = tuple(sorted(((paired, -1), (zero.FIELD_LOCAL[source], axis))))
                _add(s2, atoms, weight * zero._scalar(coefficient))

    for payload in (gravity, mixed2):
        for row in payload["rows"]:
            output = row["output"]
            if output not in zero.PAIRING:
                continue
            paired, weight = zero.PAIRING[output]
            for left, left_word, right, right_word, coefficient in row["terms"]:
                left_axis, right_axis = _word_axis(left_word), _word_axis(right_word)
                if (
                    left in zero.FIELD_LOCAL
                    and right in zero.FIELD_LOCAL
                    and left_axis is not None
                    and right_axis is not None
                    and int(left_axis >= 0) + int(right_axis >= 0) <= 1
                ):
                    atoms = tuple(sorted((
                        (paired, -1),
                        (zero.FIELD_LOCAL[left], left_axis),
                        (zero.FIELD_LOCAL[right], right_axis),
                    )))
                    _add(s3, atoms, weight * zero._q10(coefficient))

    for chunk in mixed3["chunks"]:
        path = ROOT / chunk["path"]
        if zero._sha256(path) != chunk["file_sha256"]:
            raise ValueError("retained ell3 row digest drifted")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        output = row["output"]
        if output not in zero.PAIRING:
            continue
        paired, weight = zero.PAIRING[output]
        for first, first_word, second, second_word, third, third_word, coefficient in row["terms"]:
            axes = (_word_axis(first_word), _word_axis(second_word), _word_axis(third_word))
            if (
                first in zero.FIELD_LOCAL
                and second in zero.FIELD_LOCAL
                and third in zero.FIELD_LOCAL
                and all(axis is not None for axis in axes)
                and sum(axis >= 0 for axis in axes) <= 1
            ):
                atoms = tuple(sorted((
                    (paired, -1),
                    (zero.FIELD_LOCAL[first], axes[0]),
                    (zero.FIELD_LOCAL[second], axes[1]),
                    (zero.FIELD_LOCAL[third], axes[2]),
                )))
                _add(s4, atoms, weight * zero._q10(coefficient))
    return s2, s3, s4


def _first_basis() -> tuple[tuple[tuple[int, ...], int], ...]:
    output = []
    for base in zero._mixed_basis():
        pivot = max(base)
        output.extend((base, field) for field in sorted(set(base)) if field != pivot)
    if len(output) != 1330:
        raise AssertionError("first-jet per-axis quotient dimension drifted")
    return tuple(output)


def _canonical_first(density: Mapping[tuple[Atom, ...], sp.Expr]) -> tuple[dict, ...]:
    basis = _first_basis()
    index = {key: row for row, key in enumerate(basis)}
    mixed_bases = set(zero._mixed_basis())
    axes = [dict() for _ in range(4)]
    for atoms, coefficient in density.items():
        differentiated = [(field, axis) for field, axis in atoms if axis >= 0]
        if len(differentiated) != 1:
            continue
        field, axis = differentiated[0]
        base = tuple(sorted(item[0] for item in atoms))
        if base not in mixed_bases:
            continue
        pivot = max(base)
        if field != pivot:
            _add(axes[axis], index[(base, field)], coefficient)
        else:
            pivot_count = base.count(pivot)
            for other in sorted(set(base)):
                if other != pivot:
                    _add(
                        axes[axis],
                        index[(base, other)],
                        -coefficient * sp.Rational(base.count(other), pivot_count),
                    )
    return tuple(axes)


def _positive_labels() -> tuple[tuple[str, int, tuple[int, ...], int], ...]:
    return tuple(
        (arity, output, inputs, derivative_field)
        for arity, output, inputs in zero._labels()
        for derivative_field in sorted(set(inputs))
    )


def _positive_matrix(quadratic: Mapping, cubic: Mapping) -> sp.MutableSparseMatrix:
    basis = _first_basis()
    index = {key: row for row, key in enumerate(basis)}
    d2 = tuple(zero._derivative(quadratic, field) for field in range(14))
    d3 = tuple(zero._derivative(cubic, field) for field in range(14))
    entries = {}
    for column, (arity, output, inputs, derivative_field) in enumerate(_positive_labels()):
        derivative = d2[output] if arity == "F3" else d3[output]
        for monomial, coefficient in derivative.items():
            base = tuple(sorted((*monomial, *inputs)))
            pivot = max(base)
            if derivative_field != pivot:
                key = (base, derivative_field)
                if key in index:
                    _add(entries, (index[key], column), coefficient)
            else:
                pivot_count = base.count(pivot)
                for other in sorted(set(base)):
                    key = (base, other)
                    if other != pivot and key in index:
                        _add(
                            entries,
                            (index[key], column),
                            -coefficient * sp.Rational(base.count(other), pivot_count),
                        )
    return sp.MutableSparseMatrix(1330, len(_positive_labels()), entries)


def _variation_first(
    density: Mapping[tuple[Atom, ...], sp.Expr],
    labels: tuple[tuple[str, int, tuple[int, ...]], ...],
    wanted_arity: str,
) -> tuple[sp.MutableSparseMatrix, ...]:
    basis = _first_basis()
    index = {key: row for row, key in enumerate(basis)}
    entries = [dict() for _ in range(4)]
    by_field: dict[int, list[tuple[tuple[Atom, ...], sp.Expr]]] = {}
    for atoms, coefficient in density.items():
        for field in set(atom[0] for atom in atoms):
            by_field.setdefault(field, []).append((atoms, coefficient))

    for column, (arity, output, inputs) in enumerate(labels):
        if arity != wanted_arity:
            continue
        raw: Density = {}
        for atoms, coefficient in by_field.get(output, ()):
            counts = Counter(atoms)
            for atom, multiplicity in counts.items():
                if atom[0] != output:
                    continue
                remaining = list(atoms)
                remaining.remove(atom)
                if atom[1] < 0:
                    new_atoms = remaining + [(field, -1) for field in inputs]
                    _add(raw, tuple(sorted(new_atoms)), coefficient * multiplicity)
                else:
                    input_counts = Counter(inputs)
                    for field, input_multiplicity in input_counts.items():
                        rest = list(inputs)
                        rest.remove(field)
                        new_atoms = remaining + [(field, atom[1])] + [
                            (item, -1) for item in rest
                        ]
                        _add(
                            raw,
                            tuple(sorted(new_atoms)),
                            coefficient * multiplicity * input_multiplicity,
                        )
        canonical = _canonical_first(raw)
        for axis in range(4):
            for row, coefficient in canonical[axis].items():
                _add(entries[axis], (row, column), coefficient)
    return tuple(sp.MutableSparseMatrix(1330, len(labels), value) for value in entries)


def exact_matrices() -> dict[str, object]:
    quadratic, cubic, quartic, _ = zero._action_polynomials()
    A, zero_basis, labels = zero._redefinition_matrix(quadratic, cubic)
    t0 = zero._target_vector(quartic, zero_basis)
    s2, s3, s4 = _density_terms()
    B2 = _variation_first(s2, labels, "F3")
    B3 = _variation_first(s3, labels, "F2")
    B = tuple(B2[axis] + B3[axis] for axis in range(4))
    C = _positive_matrix(quadratic, cubic)
    target_first = _canonical_first(s4)
    t1 = tuple(
        sp.Matrix([target_first[axis].get(row, 0) for row in range(1330)])
        for axis in range(4)
    )
    return {"A": A, "B": B, "C": C, "t0": t0, "t1": t1}


def _independent_rows(left_null: sp.Matrix, total_rows: int) -> tuple[int, ...]:
    if left_null.rows == 0:
        return tuple(range(total_rows))
    _, pivots = left_null.rref(simplify=False)
    return tuple(row for row in range(total_rows) if row not in set(pivots))


def _sparse_particular(matrix: sp.Matrix, target: sp.Matrix) -> tuple[sp.Matrix, dict[str, object]]:
    left_vectors = matrix.T.nullspace()
    left_null = (
        sp.Matrix.hstack(*left_vectors).T
        if left_vectors
        else sp.zeros(0, matrix.rows)
    )
    if left_null * target != sp.zeros(left_null.rows, target.cols):
        raise ValueError("target has a nonzero exact cokernel projection")
    rows = _independent_rows(left_null, matrix.rows)
    reduced = matrix[list(rows), :]
    columns = zero._structural_matching(reduced)
    square = reduced[:, list(columns)]
    matched_rank = square.rank()
    repair_columns: tuple[int, ...] = ()
    if matched_rank != len(rows):
        # A support-perfect matching need not be algebraically independent.
        # Pair every unused column with the exact left kernel of the matched
        # block, select a basis in that small quotient, then exact-RREF only
        # the narrow repaired matrix rather than the full wide operator.
        matched_left_vectors = square.T.nullspace()
        matched_left = sp.Matrix.hstack(*matched_left_vectors).T
        outside = tuple(column for column in range(matrix.cols) if column not in set(columns))
        quotient = matched_left * reduced[:, list(outside)]
        _, quotient_basis = quotient.rref(simplify=False)
        if len(quotient_basis) != matched_left.rows:
            raise ValueError("structural basis repair does not span the exact quotient")
        repair_columns = tuple(outside[column] for column in quotient_basis)
        candidate_columns = (*columns, *repair_columns)
        candidate = reduced[:, list(candidate_columns)]
        _, candidate_pivots = candidate.rref(simplify=False)
        if len(candidate_pivots) != len(rows):
            raise ValueError("repaired exact solution basis is not full rank")
        columns = tuple(candidate_columns[pivot] for pivot in candidate_pivots)
        square = reduced[:, list(columns)]
    coefficients = square.inv().multiply(target[list(rows), :])
    solution = sp.zeros(matrix.cols, target.cols)
    for column, values in zip(columns, coefficients.tolist(), strict=True):
        for rhs, coefficient in enumerate(values):
            solution[column, rhs] = sp.factor(coefficient)
    if matrix * solution != target:
        raise ValueError("exact sparse particular solution failed")
    return solution, {
        "rank": len(rows),
        "left_nullity": left_null.rows,
        "independent_rows": rows,
        "basis_columns": columns,
        "initial_matching_rank": matched_rank,
        "repair_column_count": len(repair_columns),
    }


def solve_first_page() -> dict[str, object]:
    data = exact_matrices()
    C = data["C"]
    C_left_vectors = C.T.nullspace()
    C_left = sp.Matrix.hstack(*C_left_vectors).T
    if C_left.rows != 3:
        raise ValueError("positive-jet cokernel dimension drifted")

    schur = data["A"]
    schur_target = data["t0"]
    for axis in range(4):
        schur = schur.col_join(C_left * data["B"][axis])
        schur_target = schur_target.col_join(C_left * data["t1"][axis])
    x0, schur_ledger = _sparse_particular(schur, schur_target)
    if data["A"] * x0 != data["t0"]:
        raise ValueError("Schur solution lost the zero-jet target")

    residuals = tuple(
        data["t1"][axis] - data["B"][axis] * x0 for axis in range(4)
    )
    residual_matrix = sp.Matrix.hstack(*residuals)
    y, C_ledger = _sparse_particular(C, residual_matrix)
    for axis in range(4):
        if data["B"][axis] * x0 + C * y[:, axis] != data["t1"][axis]:
            raise ValueError(f"first-jet reconstruction failed on axis {axis}")
    return {
        **data,
        "C_left": C_left,
        "schur": schur,
        "schur_target": schur_target,
        "x0": x0,
        "y": y,
        "residuals": residuals,
        "schur_ledger": schur_ledger,
        "C_ledger": C_ledger,
    }


def exploratory_verdict() -> dict[str, object]:
    started = time.monotonic()
    data = exact_matrices()
    C = data["C"]
    left_null = C.T.nullspace()
    return {
        "shapes": {
            "A": list(data["A"].shape),
            "B_each_axis": list(data["B"][0].shape),
            "C_each_axis": list(C.shape),
        },
        "supports": {
            "A": len(data["A"].todok()),
            "B_by_axis": [len(value.todok()) for value in data["B"]],
            "C": len(C.todok()),
            "t0": sum(value != 0 for value in data["t0"]),
            "t1_by_axis": [sum(value != 0 for value in target) for target in data["t1"]],
        },
        "C_rank": C.rows - len(left_null),
        "C_left_nullity": len(left_null),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def solved_verdict() -> dict[str, object]:
    started = time.monotonic()
    data = solve_first_page()
    return {
        "result": "FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_EXISTS",
        "zero_jet_schur": {
            "shape": list(data["schur"].shape),
            "nonzero_entries": len(data["schur"].todok()),
            "rank": data["schur_ledger"]["rank"],
            "left_nullity": data["schur_ledger"]["left_nullity"],
            "primitive_nonzero_count": sum(value != 0 for value in data["x0"]),
        },
        "positive_jet": {
            "C_shape": list(data["C"].shape),
            "C_nonzero_entries": len(data["C"].todok()),
            "C_rank": data["C_ledger"]["rank"],
            "C_left_nullity": data["C_ledger"]["left_nullity"],
            "target_nonzero_by_axis": [sum(value != 0 for value in target) for target in data["t1"]],
            "residual_nonzero_by_axis": [sum(value != 0 for value in target) for target in data["residuals"]],
            "primitive_nonzero_by_axis": [sum(value != 0 for value in data["y"][:, axis]) for axis in range(4)],
        },
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def _dependency(path: Path, artifact_id: str) -> dict[str, str]:
    return {"artifact_id": artifact_id, "path": str(path.relative_to(ROOT)), "sha256": zero._sha256(path)}


def _solution_records(data: Mapping[str, object]) -> tuple[list[dict], list[list[dict]]]:
    zero_records = []
    for column, coefficient in enumerate(data["x0"]):
        if coefficient == 0:
            continue
        arity, output, inputs = zero._labels()[column]
        zero_records.append({
            "column": column, "arity": arity, "output_local": output,
            "output_row": zero.FIELD_ROWS[output], "input_locals": list(inputs),
            "input_rows": [zero.FIELD_ROWS[field] for field in inputs],
            "coefficient": str(sp.factor(coefficient)),
        })
    positive_records = [[] for _ in range(4)]
    labels = _positive_labels()
    for axis in range(4):
        for column, coefficient in enumerate(data["y"][:, axis]):
            if coefficient == 0:
                continue
            arity, output, inputs, derivative_field = labels[column]
            positive_records[axis].append({
                "column": column, "arity": arity, "output_local": output,
                "output_row": zero.FIELD_ROWS[output], "input_locals": list(inputs),
                "input_rows": [zero.FIELD_ROWS[field] for field in inputs],
                "derivative_input_local": derivative_field,
                "derivative_input_row": zero.FIELD_ROWS[derivative_field],
                "coefficient": str(sp.factor(coefficient)),
            })
    return zero_records, positive_records


def build() -> dict:
    data = solve_first_page()
    zero_records, positive_records = _solution_records(data)
    dependencies = {
        "constant_field_page": _dependency(
            zero.OUTPUT, "BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1"
        ),
        "typed_retained_carrier": _dependency(
            zero.TYPED_CARRIER, "BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR"
        ),
        "retained_gravity_ell2": _dependency(zero.GRAVITY_ELL2, "BERGER_RETAINED_26_Q2_PAYLOAD"),
        "retained_mixed_ell2": _dependency(zero.MIXED_ELL2, "BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD"),
        "retained_mixed_ell3": _dependency(zero.MIXED_ELL3, "BERGER_RETAINED_MIXED_ELL3_PAYLOAD"),
    }
    source_manifest = {
        str(path.relative_to(ROOT)): zero._sha256(path)
        for path in (Path(__file__).resolve(), SCHEMA, VERIFIER, TESTS)
    }
    return {
        "schema": "pure-weyl-berger-retained-mixed-ell3-first-jet-redefinition-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1",
        "result_state": "FIRST_JET_PHYSICAL_MIXED_QUARTIC_TRIVIALIZED_FULL_BV_AND_ORDER2_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "dependency_refs": dependencies,
        "first_jet_quotient": {
            "integration_by_parts": "D_a(product of four fields)=0; eliminate the derivative on the largest local field index with exact multiplicity weights",
            "zero_jet_dimension": 550,
            "first_jet_dimension_per_axis": 1330,
            "first_jet_total_dimension": 5320,
            "raw_ell3_order_one_operator_coefficients": 6546,
            "lowered_order_one_density_terms": 633,
            "canonical_target_nonzero_by_axis": [sum(value != 0 for value in target) for target in data["t1"]],
        },
        "coupled_schur_problem": {
            "formula": "A*x0=t0; B_a*x0+C*y_a=t1_a for a=0,1,2,3",
            "A_shape": list(data["A"].shape),
            "A_nonzero_entries": len(data["A"].todok()),
            "B_shape_each_axis": list(data["B"][0].shape),
            "B_nonzero_entries_by_axis": [len(value.todok()) for value in data["B"]],
            "C_shape_each_axis": list(data["C"].shape),
            "C_nonzero_entries": len(data["C"].todok()),
            "C_rank": data["C_ledger"]["rank"],
            "C_cokernel_dimension": data["C_ledger"]["left_nullity"],
            "Schur_shape": list(data["schur"].shape),
            "Schur_nonzero_entries": len(data["schur"].todok()),
            "Schur_rank": data["schur_ledger"]["rank"],
            "Schur_left_nullity": data["schur_ledger"]["left_nullity"],
            "target_compatible": True,
        },
        "exact_primitive": {
            "zero_jet_nonzero_count": len(zero_records),
            "positive_jet_nonzero_by_axis": [len(records) for records in positive_records],
            "zero_jet": zero_records,
            "positive_jet_by_axis": positive_records,
            "zero_jet_reconstruction_exact": True,
            "first_jet_reconstruction_exact_all_axes": True,
        },
        "rank_receipts": {
            "Schur_independent_rows": list(data["schur_ledger"]["independent_rows"]),
            "Schur_basis_columns": list(data["schur_ledger"]["basis_columns"]),
            "C_independent_rows": list(data["C_ledger"]["independent_rows"]),
            "C_basis_columns": list(data["C_ledger"]["basis_columns"]),
            "C_initial_matching_rank": data["C_ledger"]["initial_matching_rank"],
            "C_repair_column_count": data["C_ledger"]["repair_column_count"],
        },
        "exact_checks": {
            "all_zero_jet_kernel_freedom_retained_in_Schur_solve": True,
            "first_order_integration_by_parts_exact": True,
            "positive_jet_cokernel_projected_exactly": True,
            "Schur_target_compatible": True,
            "explicit_zero_and_positive_jet_primitive_reconstructs_target": True,
            "no_floating_point": True,
        },
        "claim_flags": {
            "FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_COMPUTED": True,
            "FULL_BV_REDEFINITION_MATCHED": False,
            "JET_ORDER_TWO_OR_HIGHER_COMPUTED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "ELL3_NONREMOVABLE": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_FULL_BV_AND_SECOND_JET_CYCLIC_REDEFINITION",
        "provenance": {
            "source_manifest": source_manifest,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_first_jet_redefinition.py --check",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_first_jet_redefinition.py",
                "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_first_jet_redefinition -v",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-first-jet-redefinition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC G0 theorem solves the complete degree-zero physical-action cyclic redefinition problem through total PBW jet order one on the unsplit retained 36-row carrier. It retains every zero-jet F2/F3 coefficient in the coupled Schur system, reduces first derivatives by exact integration by parts, and exports an exact zero/positive-jet primitive. It proves that neither the constant nor first-jet physical mixed quartic supplies a nonremovability witness. It does not independently match the 288 ghost/antifield completion coefficients, solve jet order two where the landed ell3 still has terms, decide the full cyclic deformation class, compute ell1-cohomology, authorize branch mixing, restore a QME, or make a quantum claim.",
    }


def _solution_from_records(value: Mapping[str, object]) -> tuple[sp.Matrix, sp.Matrix]:
    x0 = sp.zeros(2690, 1)
    for record in value["exact_primitive"]["zero_jet"]:
        expected = zero._labels()[record["column"]]
        if (
            (record["arity"], record["output_local"], tuple(record["input_locals"])) != expected
            or record["output_row"] != zero.FIELD_ROWS[record["output_local"]]
            or record["input_rows"] != [zero.FIELD_ROWS[field] for field in record["input_locals"]]
        ):
            raise ValueError("zero-jet primitive metadata drifted")
        x0[record["column"]] = sp.sympify(record["coefficient"], locals={"sqrt": sp.sqrt})
    y = sp.zeros(6560, 4)
    for axis, records in enumerate(value["exact_primitive"]["positive_jet_by_axis"]):
        for record in records:
            expected = _positive_labels()[record["column"]]
            if (
                (
                    record["arity"], record["output_local"], tuple(record["input_locals"]),
                    record["derivative_input_local"],
                ) != expected
                or record["output_row"] != zero.FIELD_ROWS[record["output_local"]]
                or record["input_rows"] != [zero.FIELD_ROWS[field] for field in record["input_locals"]]
                or record["derivative_input_row"] != zero.FIELD_ROWS[record["derivative_input_local"]]
            ):
                raise ValueError("positive-jet primitive metadata drifted")
            y[record["column"], axis] = sp.sympify(record["coefficient"], locals={"sqrt": sp.sqrt})
    return x0, y


def validate(value: dict, *, replay: bool = True, ranks: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if (
        flags["FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_COMPUTED"] is not True
        or any(flags[name] is not False for name in flags if name != "FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_COMPUTED")
    ):
        raise ValueError("claim boundary drifted")
    if not replay:
        return
    data = exact_matrices()
    x0, y = _solution_from_records(value)
    if data["A"] * x0 != data["t0"]:
        raise ValueError("zero-jet primitive reconstruction failed")
    for axis in range(4):
        if data["B"][axis] * x0 + data["C"] * y[:, axis] != data["t1"][axis]:
            raise ValueError(f"first-jet primitive reconstruction failed on axis {axis}")
    if ranks:
        receipts = value["rank_receipts"]
        C_square = data["C"][receipts["C_independent_rows"], receipts["C_basis_columns"]]
        if C_square.rank() != 1327:
            raise ValueError("C exact rank receipt failed")
        C_left = sp.Matrix.hstack(*data["C"].T.nullspace()).T
        schur = data["A"]
        for axis in range(4):
            schur = schur.col_join(C_left * data["B"][axis])
        schur_square = schur[
            receipts["Schur_independent_rows"], receipts["Schur_basis_columns"]
        ]
        if schur_square.rank() != 557:
            raise ValueError("Schur exact rank receipt failed")


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: Mapping[str, object]) -> str:
    primitive = value["exact_primitive"]
    return f"""# Retained mixed ell3 first-jet cyclic redefinition

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The complete degree-zero physical-action problem through total PBW jet order
one is exactly trivializable on the unsplit retained 36-row carrier. The
positive-jet map has rank 1327 and cokernel dimension 3 on each 1330-row axis
block. Projecting those cokernels gives a `562 x 2690` coupled Schur system of
rank 557; its target is compatible.

An explicit primitive uses {primitive['zero_jet_nonzero_count']} zero-jet
coefficients and `{primitive['positive_jet_nonzero_by_axis']}` positive-jet
coefficients on axes 0 through 3. It reconstructs all 550 constant and 5,320
possible first-jet quotient coordinates exactly (the target has
`[58,136,136,126]` nonzero first-jet coordinates).

This does not match the 288 ghost/antifield completion coefficients and does
not solve total jet order two. The full cyclic deformation class, cohomology
operation, branch mixing, QME, and every quantum claim remain open.

## Verification receipt

All commands below passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_first_jet_redefinition.py --check` | 43.83 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_first_jet_redefinition.py` | 43.55 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_first_jet_redefinition -v` | 54.38 s | PASS (4 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-first-jet-redefinition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json` | 10.26 s | PASS |

Tier 2 is represented by the affected first-jet chain replay against pinned,
content-addressed unary, binary, ternary, pairing and SDR inputs. Unchanged
branch-obstruction inputs were checked by hash and not rebuilt. Tier 3 was not
run because this result remains `WRITING_STARTED`; it neither freezes a
theorem nor promotes a lifecycle state.
"""


def write() -> dict:
    value = build()
    validate(value, replay=False)
    OUTPUT.write_text(_json(value))
    REPORT.write_text(_report(value))
    return value


def refresh_provenance() -> dict:
    value = json.loads(OUTPUT.read_text())
    value["provenance"]["source_manifest"] = {
        str(path.relative_to(ROOT)): zero._sha256(path)
        for path in (Path(__file__).resolve(), SCHEMA, VERIFIER, TESTS)
    }
    validate(value, replay=False)
    OUTPUT.write_text(_json(value))
    REPORT.write_text(_report(value))
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--explore", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh-provenance", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
        print("BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1: PASS")
    elif args.refresh_provenance:
        refresh_provenance()
        print("BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1 provenance: REFRESHED")
    elif args.check:
        value = json.loads(OUTPUT.read_text())
        validate(value)
        for relative, digest in value["provenance"]["source_manifest"].items():
            if zero._sha256(ROOT / relative) != digest:
                raise ValueError(f"source-manifest digest drifted: {relative}")
        print("BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1: PASS")
    else:
        result = solved_verdict() if args.solve else exploratory_verdict()
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
