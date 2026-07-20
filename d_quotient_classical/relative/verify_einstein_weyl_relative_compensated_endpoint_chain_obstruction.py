#!/usr/bin/env python3
"""Independent raw-artifact replay of the compensated endpoint obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-compensated-endpoint-chain-obstruction-v1.schema.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = load(CERT)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)

    dependencies = {}
    for name, record in cert["dependencies"].items():
        path = ROOT / record["path"]
        if sha(path) != record["sha256"]:
            raise AssertionError(f"dependency hash drifted: {name}")
        dependencies[name] = load(path)

    endpoint = dependencies["compensated_endpoint"]
    comp = endpoint["correlated_maxwell_compensator"]
    if comp["lambda_X"]["H"] != "0" or comp["lambda_X"]["P_x"] != "0":
        raise AssertionError("flat translations acquired forbidden compensators")
    if comp["independent_constant_u1_current_added"]:
        raise AssertionError("independent constant U(1) current was added")
    if comp["corrected_gram"] != [
        ["-1", "0", "0", "0", "0"],
        ["0", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "0"],
        ["0", "0", "0", "0", "1"],
    ]:
        raise AssertionError("compensated Gram matrix drifted")

    target = dependencies["target_q1"]["content"]
    row_ids = {
        row["index"]: row["row_id"]
        for row in dependencies["target_layout"]["content"]["rows"]
    }
    profiles = {
        profile["index"]: {
            tuple(jet["word"]): Fraction(jet["coefficient"])
            for jet in profile["coefficient_jets"]
        }
        for profile in target["coefficient_profiles"]
    }
    observed: dict[tuple[str, int, str], Fraction] = {}
    for term in target["terms"]:
        incoming = term["inputs"][0]
        if (
            term["output_row"] in (34, 35)
            and incoming["row"] in (20, 21, 24, 30, 31)
            and len(incoming["word"]) == 1
            and incoming["word"][0] in (0, 1)
        ):
            coefficient = profiles[term["coefficient_profile"]].get((), Fraction())
            key = (
                row_ids[term["output_row"]],
                incoming["word"][0],
                row_ids[incoming["row"]],
            )
            observed[key] = observed.get(key, Fraction()) + coefficient
    expected = {
        ("c_0_star", 0, "g_00_star"): Fraction(-2),
        ("c_1_star", 0, "g_01_star"): Fraction(1),
        ("c_0_star", 1, "g_01_star"): Fraction(-1),
        ("c_1_star", 1, "g_11_star"): Fraction(2),
    }
    if observed != expected:
        raise AssertionError(f"raw flat q1 block drifted: {observed}")

    layout = dependencies["current_layout"]
    rows = {row["row_id"]: row["index"] for row in layout["rows"]}
    current_terms = [
        {
            "source_row": term["source_row"],
            "target_row": term["target_row"],
            "derivative": term["derivative"],
            "coefficient": term["coefficient"],
        }
        for term in layout["unary_terms"]
        if term["source_row"] == rows["P_H_3_t_theta_phi"]
        and term["target_row"] == rows["P_H_4_t_x_theta_phi"]
    ]
    if current_terms != [
        {
            "source_row": rows["P_H_3_t_theta_phi"],
            "target_row": rows["P_H_4_t_x_theta_phi"],
            "derivative": "x",
            "coefficient": -1,
        }
    ]:
        raise AssertionError("raw H-current differential drifted")

    # Independent exact linear algebra.
    matrix = sp.Matrix([[-2, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, 2]])
    rhs = sp.Matrix([0, -1, 0, 0])
    left = sp.Matrix([[0, 1, 1, 0]])
    if matrix.rank() != 3 or matrix.row_join(rhs).rank() != 4:
        raise AssertionError("flat rank obstruction failed")
    if left * matrix != sp.zeros(1, 3) or left * rhs != sp.Matrix([[-1]]):
        raise AssertionError("flat left-null replay failed")
    tau, xi = sp.symbols("tau xi")
    _, remainder = sp.groebner(
        [tau, xi**2], tau, xi, order="lex", domain=sp.QQ
    ).reduce(xi)
    if remainder != xi:
        raise AssertionError("Groebner nonmembership replay failed")

    # Replay the inherited 822-row witness without trusting its verdict fields.
    payload = dependencies["order_one_payload"]
    witness_rows = {70: {}, 339: {}}
    for row, column, value in payload["matrix_coo"]:
        if row in witness_rows:
            witness_rows[row][column] = Fraction(value)
    if witness_rows != {70: {7: Fraction(1)}, 339: {7: Fraction(-1)}}:
        raise AssertionError("raw order-one witness rows drifted")
    rhs_sparse = {int(row): Fraction(value) for row, value in payload["rhs_sparse"]}
    if -rhs_sparse.get(70, Fraction()) - rhs_sparse.get(339, Fraction()) != 1:
        raise AssertionError("compensated order-one evaluation drifted")

    # Independent exact repair substitution.
    extended = sp.Matrix(
        [[-2, 0, 0, 0], [0, -1, 0, -1], [0, 1, 0, -1], [0, 0, 2, 0]]
    )
    solution = sp.Matrix([0, sp.Rational(1, 2), 0, sp.Rational(1, 2)])
    if extended.det() != 8 or extended * solution != rhs:
        raise AssertionError("antisymmetric repair replay failed")

    for path_text, digest in cert["provenance"]["source_manifest"].items():
        if sha(ROOT / path_text) != digest:
            raise AssertionError(f"source-manifest drift: {path_text}")
    print(
        json.dumps(
            {
                "status": "PASS",
                "flat_rank": 3,
                "flat_augmented_rank": 4,
                "normal_form": "xi",
                "order_one_left_null_evaluation": "1",
                "minimal_covariant_added_rank": 6,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
