#!/usr/bin/env python3
"""Independent symbolic replay of the relative endpoint normalization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-endpoint-normalization-v1.schema.json"


def load(path: Path):
    return json.loads(path.read_text())


def main() -> None:
    value = load(CERT)
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for artifact in value["dependencies"].values():
        path = ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {path}")

    theta, phi = sp.symbols("theta phi", real=True)
    expected = {
        "H": {"c_0_star": sp.Integer(1)},
        "P_x": {"c_1_star": sp.Integer(1)},
        "J_1": {"c_3_star": sp.Integer(1)},
        "J_2": {"c_2_star": sp.cos(phi), "c_3_star": -sp.sin(phi) * sp.cot(theta)},
        "J_3": {"c_2_star": sp.sin(phi), "c_3_star": sp.cos(phi) * sp.cot(theta)},
    }
    parsed = {}
    locals_ = {"theta": theta, "phi": phi, "sin": sp.sin, "cos": sp.cos, "cot": sp.cot}
    for record in value["A2"]:
        parsed[record["generator"]] = {
            term["row"]: sp.sympify(term["coefficient"], locals=locals_)
            for term in record["target_terms"]
        }
    for generator in expected:
        if set(parsed[generator]) != set(expected[generator]):
            raise AssertionError(f"row support drift: {generator}")
        if any(sp.simplify(parsed[generator][row] - coefficient) != 0 for row, coefficient in expected[generator].items()):
            raise AssertionError(f"endpoint formula drift: {generator}")

    base = {theta: sp.pi / 2, phi: 0}
    point_vectors = []
    rows = ["c_0_star", "c_1_star", "c_2_star", "c_3_star"]
    for generator in ("H", "P_x", "J_1", "J_2", "J_3"):
        point_vectors.append([sp.simplify(parsed[generator].get(row, sp.Integer(0)).subs(base)) for row in rows])
    point_rank = sp.Matrix(point_vectors).rank()
    if point_rank != 4 or value["equatorial_basepoint_values"]["pointwise_rank"] != 4:
        raise AssertionError("equatorial pointwise rank drifted")
    if value["equatorial_basepoint_values"]["global_map_rank"] != 5:
        raise AssertionError("global endpoint rank drifted")

    order_zero = load(ROOT / value["dependencies"]["order_zero_obstruction"]["path"])
    for record in order_zero["kernel_classification"]["basis"]:
        targets = {term["output"] for term in record["terms"] if term["map"] == "A2"}
        if targets != {"lambda_cov_star"}:
            raise AssertionError("order-zero A2 kernel classification drifted")
    if any(term["row"] in {"lambda_cov_star", "sigma_W_star"} for record in value["A2"] for term in record["target_terms"]):
        raise AssertionError("forbidden identity endpoint component")

    print(json.dumps({"status": "PASS", "endpoint_generators": 5, "pointwise_rank": point_rank, "global_rank": 5, "positive_order_open": True}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
