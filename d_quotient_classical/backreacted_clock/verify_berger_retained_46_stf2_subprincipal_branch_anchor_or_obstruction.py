#!/usr/bin/env python3
"""Independent replay of the rank-46 subprincipal obstruction witness."""

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


CERT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(rows: int, columns: int, entries: list[list[object]]) -> sp.Matrix:
    value = sp.zeros(rows, columns)
    for row, column, coefficient in entries:
        value[int(row), int(column)] = sp.sympify(coefficient)
    return value


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source-manifest digest drifted: {relative}")

    dependencies = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
        if name != "V2_artifact":
            dependencies[name] = json.loads(path.read_text())

    physical = dependencies["physical_helicity_filtered_quotient"]
    q1 = dependencies["retained_minimal_q1"]
    rank36 = dependencies["rank_36_fixture_authority"]
    fibre = physical["normalized_standard_null_fibre"]
    field_inclusion = _sparse(10, 2, fibre["field_inclusion_entries"])
    equation_inclusion = _sparse(10, 2, fibre["equation_inclusion_entries"])

    p = sp.symbols("p0:4")
    point = {p[0]: 1, p[1]: 1, p[2]: 0, p[3]: 0}
    h4 = sp.Matrix(_symbol(_matrix_from_record(q1["q1_blocks"]["H_retained"]), 4)).subs(point)
    alpha_b = next(symbol for symbol in h4.free_symbols if symbol.name == "alpha_B")
    h4 = h4.subs(alpha_b, 5)
    gauge = sp.Matrix(_symbol(_matrix_from_record(q1["q1_blocks"]["K_spatial"]), 1)).subs(point)

    v2_record = value["dependency_refs"]["V2_artifact"]
    v2 = sp.Matrix(
        _symbol(_matrix_from_record(json.loads((ROOT / v2_record["path"]).read_text())), 2)
    ).subs(point)
    u = next(symbol for symbol in v2.free_symbols if symbol.name == "u")
    v = next(symbol for symbol in v2.free_symbols if symbol.name == "v")
    fixture = rank36["normalized_obstruction_witness"]["fixture"]
    substitution = {u: sp.sympify(fixture["u"]), v: sp.sympify(fixture["v"])}

    boundary = h4.row_join(equation_inclusion).row_join(v2 * gauge).subs(substitution)
    image = (v2 * field_inclusion).subs(substitution)
    ranks = {
        "allowed_boundary": int(boundary.rank()),
        "plus_augmented": int(boundary.row_join(image[:, 0]).rank()),
        "cross_augmented": int(boundary.row_join(image[:, 1]).rank()),
        "both_augmented": int(boundary.row_join(image).rank()),
    }
    if ranks != value["filtered_lift_problem"]["rank_ledger"]:
        raise ValueError("independent filtered rank ledger disagrees")

    witness = sp.Matrix([sp.sympify(entry) for entry in value["normalized_obstruction"]["normalized_left_null_covector"]])
    if witness.T * boundary != sp.zeros(1, boundary.cols):
        raise ValueError("normalized witness does not annihilate boundaries")
    if witness.T * image != sp.Matrix([[1, 0]]):
        raise ValueError("normalized witness does not expose the obstruction")
    if image[:, 1] != sp.Rational(71, 40) * equation_inclusion[:, 1]:
        raise ValueError("independent cross-column lift disagrees")

    flags = value["claim_flags"]
    if (
        flags["RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED"] is not True
        or flags["RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED"] is not False
        or flags["GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO"] is not False
        or flags["ELL3_BRANCH_MIXING_AUTHORIZED"] is not False
    ):
        raise ValueError("claim boundary drifted")
    print("BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
