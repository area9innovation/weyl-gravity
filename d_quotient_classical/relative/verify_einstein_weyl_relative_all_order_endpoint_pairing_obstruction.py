#!/usr/bin/env python3
"""Independent geometric replay of the all-order endpoint-pairing obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-all-order-endpoint-pairing-obstruction-v1.schema.json"
ENDPOINT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def verify() -> None:
    value = _load(OUTPUT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    endpoint = _load(ENDPOINT)
    if any(
        term["row"] == "lambda_cov_star"
        for record in endpoint["A2"]
        for term in record["target_terms"]
    ):
        raise AssertionError("source endpoint is no longer diffeomorphism-only")

    t, x, theta, phi = sp.symbols("t x theta phi", real=True)
    coordinates = (t, x, theta, phi)
    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    field = sp.zeros(4)
    field[2, 3] = sp.sin(theta)
    field[3, 2] = -sp.sin(theta)
    vectors = {
        "H": sp.Matrix([1, 0, 0, 0]),
        "P_x": sp.Matrix([0, 1, 0, 0]),
        "J_1": sp.Matrix([0, 0, 0, 1]),
        "J_2": sp.Matrix(
            [0, 0, sp.cos(phi), -sp.cot(theta) * sp.sin(phi)]
        ),
        "J_3": sp.Matrix(
            [0, 0, sp.sin(phi), sp.cot(theta) * sp.cos(phi)]
        ),
    }
    compensators = {
        "H": sp.S.Zero,
        "P_x": sp.S.Zero,
        "J_1": -sp.cos(theta),
        "J_2": -sp.sin(theta) * sp.sin(phi),
        "J_3": sp.sin(theta) * sp.cos(phi),
    }
    names = tuple(vectors)

    for name, vector in vectors.items():
        lie_metric = sp.Matrix(
            4,
            4,
            lambda mu, nu: sp.simplify(
                sum(
                    vector[rho] * sp.diff(metric[mu, nu], coordinates[rho])
                    for rho in range(4)
                )
                + sum(
                    metric[rho, nu] * sp.diff(vector[rho], coordinates[mu])
                    for rho in range(4)
                )
                + sum(
                    metric[mu, rho] * sp.diff(vector[rho], coordinates[nu])
                    for rho in range(4)
                )
            ),
        )
        if lie_metric != sp.zeros(4):
            raise AssertionError(f"{name} is not Killing")
        residual = sp.Matrix(
            [
                sp.simplify(
                    sp.diff(compensators[name], coordinates[mu])
                    + sum(vector[nu] * field[nu, mu] for nu in range(4))
                )
                for mu in range(4)
            ]
        )
        if residual != sp.zeros(4, 1):
            raise AssertionError(f"{name} Maxwell reducibility failed")

    raw = sp.Matrix(
        5,
        5,
        lambda row, column: sp.trigsimp(
            (vectors[names[row]].T * metric * vectors[names[column]])[0]
        ),
    )
    corrected = sp.Matrix(
        5,
        5,
        lambda row, column: sp.trigsimp(
            raw[row, column]
            + compensators[names[row]] * compensators[names[column]]
        ),
    )
    if corrected != sp.diag(-1, 1, 1, 1, 1):
        raise AssertionError("independent compensated Gram identity failed")
    witness = sp.trigsimp(raw[2, 2])
    if witness != sp.sin(theta) ** 2:
        raise AssertionError("independent raw Gram witness failed")
    derivative = sp.trigsimp(sp.diff(witness, theta))
    if sp.simplify(derivative - 2 * sp.sin(theta) * sp.cos(theta)) != 0:
        raise AssertionError("independent nonconstant derivative failed")

    recorded = value["correlated_maxwell_compensator"]
    if recorded["corrected_gram"] != [
        ["-1", "0", "0", "0", "0"],
        ["0", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "0"],
        ["0", "0", "0", "0", "1"],
    ]:
        raise AssertionError("serialized corrected Gram drifted")
    if value["minimal_repair"]["new_target_rows"] != 0:
        raise AssertionError("repair no longer uses the existing Maxwell row")
    if value["classification"]["corrected_endpoint_chain_map_constructed"]:
        raise AssertionError("pairing repair was overpromoted to a chain map")

    manifest = value["provenance"]["source_manifest"]
    for relative, digest in manifest.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != digest:
            raise AssertionError(f"source manifest drift: {relative}")
    print(
        json.dumps(
            {
                "status": "PASS",
                "raw_witness": "sin(theta)**2",
                "raw_witness_derivative_nonzero": True,
                "maxwell_reducibility_residual_nonzero": 0,
                "corrected_gram": "diag(-1,1,1,1,1)",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    verify()
