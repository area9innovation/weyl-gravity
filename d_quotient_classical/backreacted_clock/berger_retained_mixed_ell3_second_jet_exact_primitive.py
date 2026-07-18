#!/usr/bin/env python3
"""Exact physical-action primitive through total differential order two.

The certificate stores a sparse homogeneous correction to the frozen
zero/first-page primitive.  Validation replays all lower homogeneous equations
and the complete mixed quartic Euler image, so basis selection and the external
exact solver are not trusted by the theorem check.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_coupled_solver as coupled,
)


ROOT = second.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-exact-primitive-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-second-jet-exact-primitive.md"
RECORDS = ROOT / "d_quotient_classical/certificates/data/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1.records.json.gz"

ZERO_COLUMNS = 2690
FIRST_COLUMNS_PER_AXIS = 6560
FIRST_COLUMNS = 4 * FIRST_COLUMNS_PER_AXIS
SECOND_OFFSET = ZERO_COLUMNS + FIRST_COLUMNS


def _scalar(value: str) -> sp.Expr:
    result = sp.expand(sp.sympify(value, locals={"sqrt": sp.sqrt}))
    sqrt_coefficient = result.coeff(sp.sqrt(10))
    rational_coefficient = sp.expand(result - sqrt_coefficient * sp.sqrt(10))
    if (
        result.free_symbols
        or rational_coefficient.is_Rational is not True
        or sqrt_coefficient.is_Rational is not True
    ):
        raise ValueError("primitive coefficient escaped QQ(sqrt(10))")
    return sp.factor(result)


def _label(full_column: int) -> tuple[int, second.FLabel]:
    if full_column < 0 or full_column >= SECOND_OFFSET + len(second.second_jet_labels()):
        raise ValueError("primitive full column is out of range")
    if full_column < ZERO_COLUMNS:
        arity, output, inputs = second.zero._labels()[full_column]
        return 0, (arity, output, tuple((field, ()) for field in inputs))
    if full_column < SECOND_OFFSET:
        relative = full_column - ZERO_COLUMNS
        axis, local = divmod(relative, FIRST_COLUMNS_PER_AXIS)
        return 1, coupled._first_label(axis, first._positive_labels()[local])
    return 2, second.second_jet_labels()[full_column - SECOND_OFFSET]


def _record(full_column: int, coefficient: sp.Expr) -> dict[str, object]:
    jet_order, (arity, output, atoms) = _label(full_column)
    return {
        "full_column": full_column,
        "jet_order": jet_order,
        "arity": arity,
        "output_local": output,
        "input_atoms": [
            {"field_local": field, "PBW_word": list(word)} for field, word in atoms
        ],
        "coefficient": str(sp.factor(coefficient)),
    }


def records_from_solution(full_columns: list[int], coefficients: list[sp.Expr]) -> list[dict[str, object]]:
    if len(full_columns) != len(coefficients):
        raise ValueError("basis columns and coefficients have different lengths")
    records = [
        _record(int(column), coefficient)
        for column, coefficient in zip(full_columns, coefficients, strict=True)
        if coefficient != 0
    ]
    records.sort(key=lambda record: record["full_column"])
    return records


def _correction(records: list[Mapping[str, object]]) -> tuple[sp.Matrix, list[sp.Matrix], dict[int, sp.Expr]]:
    dx = sp.zeros(ZERO_COLUMNS, 1)
    dy = [sp.zeros(FIRST_COLUMNS_PER_AXIS, 1) for _ in range(4)]
    sparse: dict[int, sp.Expr] = {}
    previous = -1
    for record in records:
        full_column = int(record["full_column"])
        if full_column <= previous:
            raise ValueError("primitive records are not strictly column-sorted")
        previous = full_column
        jet_order, (arity, output, atoms) = _label(full_column)
        metadata = (
            int(record["jet_order"]),
            record["arity"],
            int(record["output_local"]),
            tuple(
                (int(atom["field_local"]), tuple(int(axis) for axis in atom["PBW_word"]))
                for atom in record["input_atoms"]
            ),
        )
        if metadata != (jet_order, arity, output, atoms):
            raise ValueError("primitive label metadata drifted")
        coefficient = _scalar(str(record["coefficient"]))
        if coefficient == 0:
            raise ValueError("primitive record contains a zero coefficient")
        sparse[full_column] = coefficient
        if jet_order == 0:
            dx[full_column] = coefficient
        elif jet_order == 1:
            relative = full_column - ZERO_COLUMNS
            axis, local = divmod(relative, FIRST_COLUMNS_PER_AXIS)
            dy[axis][local] = coefficient
    return dx, dy, sparse


def _image(full_column: int) -> second.EulerImage:
    jet_order, label = _label(full_column)
    if jet_order < 2:
        return second.redefinition_column(label, 2)
    return second.second_jet_column(label)


def exact_replay(records: list[Mapping[str, object]]) -> dict[str, object]:
    dx, dy, sparse = _correction(records)
    lower = first.exact_matrices()
    if lower["A"] * dx != sp.zeros(550, 1):
        raise ValueError("order-two correction violates the zero-page equation")
    for axis in range(4):
        if lower["B"][axis] * dx + lower["C"] * dy[axis] != sp.zeros(1330, 1):
            raise ValueError(f"order-two correction violates first-page axis {axis}")

    image: second.EulerImage = {}
    for full_column, coefficient in sparse.items():
        for key, value in _image(full_column).items():
            second._add(image, key, coefficient * value)
    source = second.exact_data()["euler"]
    missing = set(source) - set(image)
    extra = set(image) - set(source)
    changed = {
        key for key in set(source).intersection(image)
        if sp.expand(source[key] - image[key]) != 0
    }
    if missing or extra or changed:
        raise ValueError(
            f"order-two Euler replay failed: missing={len(missing)} extra={len(extra)} changed={len(changed)}"
        )

    frozen = second.zero._load(first.OUTPUT)
    x0, y0 = first._solution_from_records(frozen)
    final_x = x0 + dx
    final_y = [y0[:, axis] + dy[axis] for axis in range(4)]
    correction_counts = {
        "zero": sum(value != 0 for value in dx),
        "first_by_axis": [sum(value != 0 for value in vector) for vector in dy],
        "second": sum(column >= SECOND_OFFSET for column in sparse),
    }
    return {
        "correction_nonzero": correction_counts,
        "correction_total_nonzero": len(sparse),
        "final_lower_nonzero": {
            "zero": sum(value != 0 for value in final_x),
            "first_by_axis": [sum(value != 0 for value in vector) for vector in final_y],
        },
        "Euler_target_coordinates": len(source),
        "Euler_reconstruction_coordinates": len(image),
        "missing": len(missing),
        "extra": len(extra),
        "changed": len(changed),
    }


def _records_sha256(records: object) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def write_records(records: list[dict[str, object]]) -> None:
    payload = json.dumps(records, separators=(",", ":")).encode()
    RECORDS.parent.mkdir(parents=True, exist_ok=True)
    RECORDS.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))


def _load_records(value: Mapping[str, object]) -> list[dict[str, object]]:
    metadata = value["exact_correction"]
    path = ROOT / str(metadata["records_path"])
    if path != RECORDS or second.zero._sha256(path) != metadata["records_file_sha256"]:
        raise ValueError("primitive record file digest drifted")
    with gzip.open(path, "rt") as handle:
        records = json.load(handle)
    if not isinstance(records, list) or len(records) != metadata["nonzero_count"]:
        raise ValueError("primitive record count drifted")
    if metadata["records_sha256"] != _records_sha256(records):
        raise ValueError("primitive canonical record digest drifted")
    return records


def certificate(records: list[dict[str, object]]) -> dict[str, object]:
    replay = exact_replay(records)
    return {
        "artifact_id": "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1",
        "schema_version": "berger-retained-mixed-ell3-second-jet-exact-primitive-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality": "G0",
        "status": "PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZED",
        "dependency_refs": {
            str(path.relative_to(ROOT)): second.zero._sha256(path)
            for path in (second.OUTPUT, first.OUTPUT)
        },
        "quotient": {
            "method": "exact independent variational-Euler coordinates after Berger PBW reduction",
            "mixed_field_multisets": 550,
            "independent_coordinate_count": len(second.independent_mixed_euler_coordinates()),
            "multiplicity_pattern_dimensions": {
                "2+2": 35,
                "2+1+1": 55,
                "1+1+1+1": 91,
            },
        },
        "basis_selection_audit": {
            "active_component_shape": [5995, 18751],
            "rank_revealed": 5754,
            "selected_exact_square_shape": [5754, 5754],
            "selected_exact_square_nonzero_count": 26578,
            "selected_zero_columns": 175,
            "selected_first_columns_by_axis": [112, 212, 223, 239],
            "selected_second_columns": 4793,
            "selection_only_backend": "SuiteSparseQR tolerance 1e-9",
            "selection_is_not_trusted_by_replay": True,
            "second_jet_untouched_coordinate_count": 16,
            "untouched_C_cokernel_rank": 14,
            "untouched_C_compatible_dimension": 2,
            "untouched_Schur_constraint_rank": 1,
            "untouched_Schur_compatible_dimension": 1,
            "untouched_nonzero_target_evaluation_dimension": 0,
        },
        "exact_solver_audit": {
            "coefficient_field": "QQ(sqrt(10))",
            "sqrt10_row_parity_count": 1139,
            "sqrt10_column_parity_count": 787,
            "parity_conflicts": 0,
            "row_cleared_MPZ_nonzero_count": 26578,
            "backend": "SuiteSparse SPEX 3.2.4 exact sparse LU",
            "elapsed_seconds": "31.91",
            "peak_RSS_kB": 662048,
            "basis_square_exact_replay": True,
        },
        "exact_correction": {
            "records_sha256": _records_sha256(records),
            "records_file_sha256": second.zero._sha256(RECORDS),
            "records_path": str(RECORDS.relative_to(ROOT)),
            "nonzero_count": len(records),
        },
        "full_replay": replay,
        "claim_flags": {
            "PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED": True,
            "FULL_BV_POSITIVE_JET_REDEFINITION_MATCHED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "ELL3_NONREMOVABLE": False,
            "RESIDUAL_COHOMOLOGY_OPERATION_COMPUTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "LIFT_EXACT_ORDER_TWO_PHYSICAL_PRIMITIVE_TO_POSITIVE_JET_FULL_BV",
        "claim_boundary": "This LOCAL-ALGEBRAIC G0 theorem gives an exact physical-base F2/F3 correction which, when added to the frozen lower primitive, trivializes the complete mixed degree-zero physical action through summed differential order two. It does not yet match the positive-jet ghost/antifield completion, decide the full cyclic deformation class, descend to residual cohomology, prove SDR independence, or make a quantum claim.",
    }


def validate(value: Mapping[str, object], *, replay: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if flags["PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED"] is not True:
        raise ValueError("physical order-two claim flag drifted")
    if any(
        flags[name] is not False
        for name in flags
        if name != "PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED"
    ):
        raise ValueError("physical order-two claim boundary drifted")
    records = _load_records(value)
    if replay:
        result = exact_replay(records)
        if result != value["full_replay"]:
            raise ValueError("primitive replay receipt drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = json.loads(OUTPUT.read_text())
    validate(value)
    print("BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1: PASS")


if __name__ == "__main__":
    main()
