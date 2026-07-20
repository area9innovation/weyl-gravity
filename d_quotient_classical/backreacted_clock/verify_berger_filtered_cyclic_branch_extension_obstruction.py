#!/usr/bin/env python3
"""Independent replay of the filtered cyclic branch-extension obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (  # noqa: E402
    _matrix_from_record,
    _symbol,
)


CERT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-filtered-cyclic-branch-extension-obstruction-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependency(value: dict, name: str) -> dict:
    record = value["dependency_refs"][name]
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise ValueError(f"dependency digest drifted: {name}")
    dependency = json.loads(path.read_text())
    if dependency.get("result_id") != record["artifact_id"]:
        raise ValueError(f"dependency identity drifted: {name}")
    return dependency


def _sparse(rows: int, columns: int, entries: list[list[object]]) -> sp.Matrix:
    value = sp.zeros(rows, columns)
    for row, column, coefficient in entries:
        value[int(row), int(column)] = sp.sympify(coefficient)
    return value


def _actual_filtered_problem(value: dict) -> tuple[sp.Matrix, sp.Matrix]:
    subprincipal = _load_dependency(value, "subprincipal_lift_obstruction")
    physical_record = subprincipal["dependency_refs"][
        "physical_helicity_filtered_quotient"
    ]
    q1_record = subprincipal["dependency_refs"]["retained_minimal_q1"]
    rank36_record = subprincipal["dependency_refs"]["rank_36_fixture_authority"]
    v2_record = subprincipal["dependency_refs"]["V2_artifact"]

    for record in (physical_record, q1_record, rank36_record, v2_record):
        if _sha256(ROOT / record["path"]) != record["sha256"]:
            raise ValueError(f"transitive dependency digest drifted: {record['path']}")

    physical = json.loads((ROOT / physical_record["path"]).read_text())
    q1 = json.loads((ROOT / q1_record["path"]).read_text())
    rank36 = json.loads((ROOT / rank36_record["path"]).read_text())
    fibre = physical["normalized_standard_null_fibre"]
    field_inclusion = _sparse(10, 2, fibre["field_inclusion_entries"])
    equation_inclusion = _sparse(10, 2, fibre["equation_inclusion_entries"])

    p = sp.symbols("p0:4")
    point = {p[0]: 1, p[1]: 1, p[2]: 0, p[3]: 0}
    h4 = sp.Matrix(
        _symbol(_matrix_from_record(q1["q1_blocks"]["H_retained"]), 4)
    ).subs(point)
    alpha_b = next(symbol for symbol in h4.free_symbols if symbol.name == "alpha_B")
    h4 = h4.subs(alpha_b, 5)
    gauge = sp.Matrix(
        _symbol(_matrix_from_record(q1["q1_blocks"]["K_spatial"]), 1)
    ).subs(point)
    v2 = sp.Matrix(
        _symbol(
            _matrix_from_record(
                json.loads((ROOT / v2_record["path"]).read_text())
            ),
            2,
        )
    ).subs(point)
    u = next(symbol for symbol in v2.free_symbols if symbol.name == "u")
    v = next(symbol for symbol in v2.free_symbols if symbol.name == "v")
    fixture = rank36["normalized_obstruction_witness"]["fixture"]
    substitution = {u: sp.sympify(fixture["u"]), v: sp.sympify(fixture["v"])}
    boundary = h4.row_join(equation_inclusion).row_join(v2 * gauge).subs(
        substitution
    )
    target = (v2 * field_inclusion).subs(substitution)
    return boundary, target


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for relative, digest in value["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source-manifest digest drifted: {relative}")
    for name in value["dependency_refs"]:
        _load_dependency(value, name)

    boundary, target = _actual_filtered_problem(value)
    ranks = {
        "allowed_boundary": int(boundary.rank()),
        "plus_augmented": int(boundary.row_join(target[:, 0]).rank()),
        "cross_augmented": int(boundary.row_join(target[:, 1]).rank()),
        "both_augmented": int(boundary.row_join(target).rank()),
    }
    if ranks != value["first_obstruction_class"]["certified_rank_ledger"]:
        raise ValueError("independent actual rank ledger disagrees")
    obstruction_rank = ranks["both_augmented"] - ranks["allowed_boundary"]
    fixture = value["minimal_page_enlargement_classification"]["standard_fibre"]
    if obstruction_rank != fixture["obstruction_image_rank"] or obstruction_rank != 1:
        raise ValueError("independent obstruction-image rank disagrees")

    subprincipal = _load_dependency(value, "subprincipal_lift_obstruction")
    witness = sp.Matrix(
        [
            sp.sympify(entry)
            for entry in subprincipal["normalized_obstruction"][
                "normalized_left_null_covector"
            ]
        ]
    )
    if witness.T * boundary != sp.zeros(1, boundary.cols):
        raise ValueError("actual normalized witness misses the boundary image")
    if witness.T * target != sp.Matrix([[1, 0]]):
        raise ValueError("actual normalized obstruction is not (1,0)")

    # Independent normal-form and minimality replay.  Quotient rank one means
    # zero new columns cannot work.  Adding the obstructed target column itself
    # gives a one-column repair, and cyclicity doubles that generator count.
    if boundary.row_join(target).rank() == boundary.rank():
        raise ValueError("zero-generator repair was incorrectly accepted")
    repaired = boundary.row_join(target[:, 0])
    if repaired.row_join(target).rank() != repaired.rank():
        raise ValueError("canonical one-generator page repair failed")
    if fixture["minimum_new_field_directions"] != obstruction_rank:
        raise ValueError("minimal field-generator count disagrees")
    if fixture["minimum_cyclic_BV_rows"] != 2 * obstruction_rank:
        raise ValueError("cyclic completion did not double the minimal count")

    graph = _load_dependency(value, "rank_46_contractible_cyclic_graph")
    if (
        graph["flags"]["CYCLIC_GRAPH_SDR_46_TO_36"] is not True
        or graph["graph_construction"]["Schur_complement"] != "A10"
    ):
        raise ValueError("contractible graph premise drifted")
    ell3 = _load_dependency(value, "retained_mixed_ell3_obstruction")
    if (
        ell3["claim_flags"]["FILTERED_CYCLIC_REDEFINITION_OBSTRUCTED_AT_FIRST_PAGE"]
        is not True
        or ell3["claim_flags"]["BRANCH_PROJECTION_DECIDED"] is not False
    ):
        raise ValueError("ell3 independence boundary drifted")

    flags = value["claim_flags"]
    if (
        flags["FIRST_EXTENSION_OBSTRUCTION_CLASS_CERTIFIED"] is not True
        or flags["ARITY_ONE_BRANCH_SPLIT_EXISTS"] is not False
        or flags["CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS"] is not False
        or flags["GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED"] is not False
        or flags["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is not False
    ):
        raise ValueError("claim boundary drifted")

    print(
        "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1 "
        "independent verification: PASS"
    )
    return value


if __name__ == "__main__":
    verify()
