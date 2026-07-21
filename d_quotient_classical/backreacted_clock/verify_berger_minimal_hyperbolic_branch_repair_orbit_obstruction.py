#!/usr/bin/env python3
"""Independent residual-orbit replay for the minimal hyperbolic repair."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-v1.schema.json"
ATLAS = ROOT / "residual_atlas/berger-minimal-hyperbolic-branch-repair-residual-orbit-obstruction-fragment-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_stf2_generators() -> tuple[list[sp.Matrix], sp.Matrix, sp.Matrix]:
    e = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        matrix = sp.zeros(3)
        matrix[i, j] = matrix[j, i] = 1
        e.append(matrix)
    basis = e + [sp.diag(1, -1, 0), sp.diag(1, 1, -2)]
    axes = [
        sp.Matrix([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
        sp.Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]]),
    ]
    gram = sp.Matrix([[sp.trace(left.T * right) for right in basis] for left in basis])
    generators = []
    for axis in axes:
        columns = []
        for tensor in basis:
            moved = axis * tensor - tensor * axis
            rhs = sp.Matrix([sp.trace(item.T * moved) for item in basis])
            columns.append(gram.inv() * rhs)
        generators.append(sp.Matrix.hstack(*columns))
    plus = sp.Matrix([0, 0, 0, sp.Rational(-1, 2), sp.Rational(1, 2)])
    cross = sp.Matrix([0, 0, -1, 0, 0])
    return generators, plus, cross


def validate_claims(value: dict) -> None:
    flags = value["claim_flags"]
    if flags["TWO_ROW_REAL_RESIDUAL_EQUIVARIANT_REPAIR"] is not False:
        raise AssertionError("two-row residual repair was falsely promoted")
    if flags["GLOBAL_NONCONTRACTIBLE_STF2_REPAIR_CONSTRUCTED"] is not False:
        raise AssertionError("unconstructed noncontractible STF2 carrier was promoted")
    if flags["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is not False:
        raise AssertionError("ell3 branch projection was activated before unary repair")
    if value["minimal_residual_orbit_enlargement"]["standard_null_fibre"]["minimum_added_BV_rows"] != 4:
        raise AssertionError("real fibrewise orbit lower bound drifted")
    if value["minimal_residual_orbit_enlargement"]["global_support_local_tensor_bundle"]["minimum_added_BV_rows"] != 10:
        raise AssertionError("global STF2 orbit lower bound drifted")
    if value["minimal_residual_orbit_enlargement"]["existing_rank46_graph_negative_control"]["repairs_beta_1"] is not False:
        raise AssertionError("contractible graph was relabelled as a repair")
    ledger = {entry["gate"]: entry["status"] for entry in value["ordered_compatibility_ledger"]}
    if ledger["REAL_ROTATIONAL_RESIDUAL_EQUIVARIANCE"] != "OBSTRUCTED":
        raise AssertionError("first later gate no longer obstructed")
    for gate in ("LATER_FILTERED_CHAIN_PAGES", "Q2_Q3_EXTENSION_TO_REPAIRED_CARRIER", "RETAINED_ELL3_COMPATIBILITY_AND_BRANCH_PROJECTION"):
        if ledger[gate] != "NOT_ACTIVATED":
            raise AssertionError(f"downstream gate illegally activated: {gate}")


def main() -> None:
    value = load(CERTIFICATE)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for record in value["dependency_refs"].values():
        path = ROOT / record["path"]
        payload = load(path)
        if sha256(path) != record["sha256"] or payload["result_id"] != record["result_id"]:
            raise AssertionError(f"dependency drift: {path}")

    page = load(ROOT / value["dependency_refs"]["page_obstruction"]["path"])
    physical = load(ROOT / value["dependency_refs"]["physical_helicity"]["path"])
    graph = load(ROOT / value["dependency_refs"]["contractible_stf2_graph"]["path"])
    phase1 = load(ROOT / value["dependency_refs"]["phase1_disposition"]["path"])
    if page["first_obstruction_class"]["normalized_evaluation"] != [["1", "0"]]:
        raise AssertionError("rank-one page source drifted")
    if graph["flags"]["CYCLIC_GRAPH_SDR_46_TO_36"] is not True:
        raise AssertionError("contractible negative control drifted")
    if phase1["branch_and_cohomology"]["einstein_extra_weyl_maxwell_branch_mixing"] != "NO_CERTIFIED_MAP":
        raise AssertionError("current branch boundary drifted")

    generators, plus, cross = derive_stf2_generators()
    frame = sp.Matrix.hstack(plus, cross)
    little = sp.Matrix.hstack(*[
        sp.Matrix(list(sp.linsolve((frame, generators[0] * vector)))[0])
        for vector in (plus, cross)
    ])
    if little.tolist() != physical["normalized_standard_null_fibre"]["little_group_generator"]:
        raise AssertionError("independent little-group replay disagrees with source")
    if little.charpoly().as_expr() != sp.Symbol("lambda") ** 2 + 4:
        raise AssertionError("little-group characteristic polynomial drifted")
    defect = little * sp.Matrix([1, 0])
    if defect != sp.Matrix([0, -2]) or -sp.Rational(1, 2) * defect[1] != 1:
        raise AssertionError("normalized residual-equivariance witness failed")

    orbit = [plus]
    while True:
        old = len(orbit)
        for candidate in [generator * vector for generator in generators for vector in list(orbit)]:
            if sp.Matrix.hstack(*orbit, candidate).rank() > len(orbit):
                orbit.append(candidate)
        if len(orbit) == old:
            break
    if len(orbit) != 5:
        raise AssertionError("full residual orbit is not STF2")
    if sum((generator * generator for generator in generators), sp.zeros(5)) != -6 * sp.eye(5):
        raise AssertionError("spin-two Casimir failed")

    unknown = sp.symbols("a0:25")
    matrix = sp.Matrix(5, 5, unknown)
    equations = []
    for generator in generators:
        equations.extend(list(matrix * generator - generator * matrix))
    linear, _ = sp.linear_eq_to_matrix(equations, unknown)
    if 25 - linear.rank() != 1:
        raise AssertionError("equivariant coupling commutant is not scalar")
    validate_claims(value)

    mutations = []
    for name, mutate in (
        ("stale_page_hash", lambda item: item["dependency_refs"]["page_obstruction"].__setitem__("sha256", "0" * 64)),
        ("two_rows_called_equivariant", lambda item: item["claim_flags"].__setitem__("TWO_ROW_REAL_RESIDUAL_EQUIVARIANT_REPAIR", True)),
        ("contractible_graph_called_repair", lambda item: item["minimal_residual_orbit_enlargement"]["existing_rank46_graph_negative_control"].__setitem__("repairs_beta_1", True)),
        ("ell3_activated", lambda item: item["claim_flags"].__setitem__("ELL3_BRANCH_PROJECTION_AUTHORIZED", True)),
        ("cross_orbit_deleted", lambda item: item["minimal_residual_orbit_enlargement"]["standard_null_fibre"].__setitem__("minimum_added_BV_rows", 2)),
    ):
        changed = deepcopy(value)
        mutate(changed)
        rejected = False
        try:
            if name == "stale_page_hash":
                record = changed["dependency_refs"]["page_obstruction"]
                if sha256(ROOT / record["path"]) != record["sha256"]:
                    raise AssertionError("stale hash")
            validate_claims(changed)
        except AssertionError:
            rejected = True
        if not rejected:
            raise AssertionError(f"mutation survived: {name}")
        mutations.append(name)
    if len(mutations) != 5:
        raise AssertionError("mutation ledger incomplete")

    atlas = load(ATLAS)
    evidence = atlas["entries"][0]["evidence"][0]
    if evidence["sha256"] != sha256(CERTIFICATE) or evidence["result_id"] != value["result_id"]:
        raise AssertionError("atlas evidence drifted")
    print("BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1 independent replay: PASS")


if __name__ == "__main__":
    main()
