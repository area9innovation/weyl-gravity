#!/usr/bin/env python3
"""Close the zero-jet full-BV ell3 screen with the certified ghost shear."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.polys.matrices import DomainMatrix

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_full_bv_coderivation_redefinition as base,
)


ROOT = base.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-zero-jet-ghost-shear-completion-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-zero-jet-ghost-shear-completion.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_zero_jet_ghost_shear_completion.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_zero_jet_ghost_shear_completion.py"
OBSTRUCTION = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1.json"
GHOST_SHEAR_LABELS = ((26, (0, 28)), (26, (1, 29)), (26, (2, 30)))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extended_matrix() -> dict[str, object]:
    data = base.exact_matrix()
    q1, q2, _ = base.retained_maps_zero()
    columns = []
    for label in GHOST_SHEAR_LABELS:
        column = base.coboundary(q1, q2, base.cotangent_column(*label), {})
        if base.cyclicity_defects(column):
            raise ValueError(f"certified ghost-shear column lost cyclicity: {label}")
        columns.append(
            {key: value for key, value in column.items() if base._lowered_maxwell_count(key) == 2}
        )
    row_basis = list(data["row_basis"])
    new_rows = sorted(set().union(*(set(column) for column in columns)) - set(row_basis))
    row_basis.extend(new_rows)
    row_index = {key: row for row, key in enumerate(row_basis)}
    matrix = data["matrix"].col_join(sp.zeros(len(new_rows), data["matrix"].cols))
    extension = sp.MutableSparseMatrix(
        len(row_basis),
        len(columns),
        {
            (row_index[key], column): coefficient
            for column, value in enumerate(columns)
            for key, coefficient in value.items()
        },
    )
    matrix = matrix.row_join(extension)
    target = data["target"].col_join(sp.zeros(len(new_rows), 1))
    return {
        "matrix": matrix,
        "target": target,
        "row_basis": tuple(row_basis),
        "labels": (
            *data["labels"],
            *(("F2", output, inputs) for output, inputs in GHOST_SHEAR_LABELS),
        ),
        "target_map": data["target_map"],
        "new_rows": tuple(new_rows),
    }


def exact_solve() -> dict[str, object]:
    data = extended_matrix()
    component = base.target_component(data)
    matrix = component["matrix"]
    target = component["target"]
    field = sp.QQ.algebraic_field(sp.sqrt(10))
    domain_matrix = DomainMatrix.from_Matrix(matrix).convert_to(field)
    rank = domain_matrix.rank()
    augmented_rank = DomainMatrix.from_Matrix(matrix.row_join(target)).convert_to(field).rank()
    if (rank, augmented_rank) != (132, 132):
        raise ValueError("ghost-shear completion rank ledger drifted")
    _, row_pivots = domain_matrix.transpose().rref()
    reduced = matrix[list(row_pivots), :]
    reduced_target = target[list(row_pivots), :]
    _, column_pivots = DomainMatrix.from_Matrix(reduced).convert_to(field).rref()
    square = reduced[:, list(column_pivots)]
    numerator, denominator = DomainMatrix.from_Matrix(square).convert_to(field).solve_den(
        DomainMatrix.from_Matrix(reduced_target).convert_to(field)
    )
    coefficients = numerator.to_Matrix() / field.to_sympy(denominator)
    solution = sp.zeros(matrix.cols, 1)
    for column, coefficient in zip(column_pivots, coefficients, strict=True):
        solution[column] = sp.factor(coefficient)
    if matrix * solution != target:
        raise ValueError("ghost-shear primitive reconstruction failed")
    primitive = []
    for local_column, coefficient in enumerate(solution):
        if not coefficient:
            continue
        global_column = component["columns"][local_column]
        kind, output, inputs = data["labels"][global_column]
        primitive.append(
            {
                "kind": kind,
                "output": output,
                "inputs": list(inputs),
                "coefficient": str(sp.factor(coefficient)),
            }
        )
    if len(primitive) != 67:
        raise ValueError("ghost-shear primitive support drifted")
    return {
        "data": data,
        "component": component,
        "rank": rank,
        "augmented_rank": augmented_rank,
        "primitive": primitive,
    }


def _coefficient(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"sqrt": sp.sqrt})


def primitive_replay(primitive: list[Mapping[str, object]]) -> dict[str, object]:
    q1, q2, target = base.retained_maps_zero()
    reconstructed: base.Taylor = {}
    ghost_records = []
    for record in primitive:
        kind = record["kind"]
        output = int(record["output"])
        inputs = tuple(int(row) for row in record["inputs"])
        coefficient = _coefficient(str(record["coefficient"]))
        lift = base.cotangent_column(output, inputs)
        column = base.coboundary(
            q1,
            q2,
            lift if kind == "F2" else {},
            lift if kind == "F3" else {},
        )
        for key, value in column.items():
            if base._lowered_maxwell_count(key) == 2:
                base._add(reconstructed, key[0], key[1], coefficient * value)
        if (output, inputs) in GHOST_SHEAR_LABELS:
            ghost_records.append((output, inputs, coefficient))
    target_mixed = {key: value for key, value in target.items() if base._lowered_maxwell_count(key) == 2}
    if reconstructed != target_mixed:
        missing = len(set(target_mixed) - set(reconstructed))
        extra = len(set(reconstructed) - set(target_mixed))
        changed = sum(
            reconstructed.get(key) != target_mixed.get(key)
            for key in set(reconstructed) & set(target_mixed)
        )
        raise ValueError(f"primitive replay failed: missing={missing}, extra={extra}, changed={changed}")
    expected_ghosts = [(output, inputs, sp.Integer(-1)) for output, inputs in GHOST_SHEAR_LABELS]
    if ghost_records != expected_ghosts:
        raise ValueError("minimal ghost-shear carrier coefficients drifted")
    return {
        "primitive_nonzero_coefficients": len(primitive),
        "F2_nonzero_coefficients": sum(record["kind"] == "F2" for record in primitive),
        "F3_nonzero_coefficients": sum(record["kind"] == "F3" for record in primitive),
        "certified_ghost_shear_coefficients": [
            {"output": output, "inputs": list(inputs), "coefficient": str(coefficient)}
            for output, inputs, coefficient in ghost_records
        ],
        "reconstructed_two_Maxwell_zero_word_coefficients": len(reconstructed),
        "missing_coefficients": 0,
        "extra_coefficients": 0,
        "changed_coefficients": 0,
    }


def exhaustive_build() -> dict[str, object]:
    started = time.monotonic()
    solved = exact_solve()
    replay = primitive_replay(solved["primitive"])
    value = {
        "schema": "pure-weyl-berger-retained-mixed-ell3-zero-jet-ghost-shear-completion-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1",
        "result_state": "ZERO_JET_FULL_BV_TRIVIALIZATION_EXISTS_WITH_CERTIFIED_GHOST_SHEAR",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "dependency_refs": {
            "scoped_obstruction": {"path": str(OBSTRUCTION.relative_to(ROOT)), "sha256": _sha256(OBSTRUCTION)},
            "typed_ghost_shear_source": {
                "path": "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3.py",
                "sha256": _sha256(ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3.py"),
            },
        },
        "extended_matrix_audit": {
            "shape": list(solved["data"]["matrix"].shape),
            "nonzero_entries": len(solved["data"]["matrix"].todok()),
            "new_row_count": len(solved["data"]["new_rows"]),
            "target_connected_shape": list(solved["component"]["matrix"].shape),
            "target_connected_nonzero_entries": len(solved["component"]["matrix"].todok()),
            "rank": solved["rank"],
            "augmented_rank": solved["augmented_rank"],
            "target_compatible": True,
            "elapsed_seconds": round(time.monotonic() - started, 6),
        },
        "primitive": solved["primitive"],
        "primitive_replay": replay,
        "PBW_augmentation_ideal": base.pbw_augmentation_replay(),
        "claim_flags": {
            "ZERO_JET_FULL_BV_TRIVIALIZATION_EXISTS": True,
            "SCOPED_PHYSICAL_ONLY_OBSTRUCTION_SUPERSEDED": True,
            "FULL_JET_BOUNDED_CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "TOTAL_PBW_ORDER_TWO_CLOSED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_PBW_ORDER_TWO_FULL_BV_REDEFINITION_V1",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_zero_jet_ghost_shear_completion.py --check",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_zero_jet_ghost_shear_completion.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_zero_jet_ghost_shear_completion -v",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_zero_jet_ghost_shear_completion.py --write-exhaustive",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-zero-jet-ghost-shear-completion-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1.json",
        ],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC G0 result extends the zero-PBW two-Maxwell full-BV "
            "redefinition screen by exactly the three retained components of the "
            "certified typed Maxwell covariant-ghost shear. The extended target block "
            "is compatible and an explicit 67-coefficient F2 primitive reconstructs "
            "all 186 canonical zero-word Taylor coefficients with no missing, extra or "
            "changed coefficients in that sector. It supersedes the physical-only "
            "zero-page obstruction by identifying and supplying its smallest missing "
            "carrier. It does not close positive PBW orders one and two, decide a full "
            "cyclic deformation class, descend to residual cohomology, or make a quantum claim."
        ),
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def fast_validate(value: Mapping[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["primitive_replay"] != primitive_replay(value["primitive"]):
        raise ValueError("stored primitive replay drifted")
    if value["PBW_augmentation_ideal"] != base.pbw_augmentation_replay():
        raise ValueError("PBW augmentation replay drifted")
    for dependency in value["dependency_refs"].values():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency hash drifted: {dependency['path']}")
    for relative, expected in value["source_manifest"].items():
        if _sha256(ROOT / relative) != expected:
            raise ValueError(f"source hash drifted: {relative}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-exhaustive", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write_exhaustive:
        value = exhaustive_build()
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif args.check:
        fast_validate(json.loads(OUTPUT.read_text()))
    else:
        parser.error("select --write-exhaustive or --check")
    print("BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1: PASS")


if __name__ == "__main__":
    main()
