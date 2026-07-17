#!/usr/bin/env python3
"""Independent replay of the Berger rod compact-solvability screen."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from .berger_rod_tadpole_compact_solvability_gate import (
    CERTIFICATE_PATH,
    DEPENDENCIES,
    ROOT,
    SCHEMA_PATH,
)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _constant_matrix(record: dict, shape: tuple[int, int]) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _digest(body):
        raise AssertionError("independent operator hash check failed")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if not any(exponents):
                matrix[row, column] += sp.sympify(
                    raw, locals={"u": u, "v": v, "alpha_B": 5}
                )
    return sp.simplify(matrix)


def main() -> None:
    payload = json.loads(CERTIFICATE_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise AssertionError(f"dependency hash mismatch: {name}")
    for relative, digest in payload["provenance"]["source_manifest"].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source hash mismatch: {relative}")

    detector = json.loads(DEPENDENCIES["detector_input"].read_text())
    gradients = [
        sp.Matrix([sp.Rational(value) for value in row])
        for row in detector["rod_charts"][0]["relational_jacobian"][1:]
    ]
    eta = sp.diag(-1, 1, 1, 1)
    stress = sp.zeros(4)
    for gradient in gradients:
        stress += gradient * gradient.T - eta * (gradient.T * eta * gradient)[0] / 2
    if stress != sp.diag(sp.Rational(3, 2), -sp.Rational(1, 2), -sp.Rational(1, 2), -sp.Rational(1, 2)):
        raise AssertionError("independent rod stress replay failed")
    source = sp.Matrix([sp.Rational(3, 2), 0, 0, 0, -sp.Rational(1, 2), 0, 0, -sp.Rational(1, 2), 0, -sp.Rational(1, 2)])

    contraction = json.loads(DEPENDENCIES["gravity_contraction"].read_text())
    pi_cl = _constant_matrix(contraction["contraction"]["pi_cl"], (26, 54))
    if pi_cl[13:23, 27:37] * source != source:
        raise AssertionError("independent pi_cl replay failed")
    retained = json.loads(DEPENDENCIES["retained_unary"].read_text())["q1_blocks"]
    hessian = _constant_matrix(retained["H_retained"], (10, 10))
    noether = _constant_matrix(retained["minus_K_spatial_sharp"], (3, 10))
    if noether * source != sp.zeros(3, 1):
        raise AssertionError("independent closure replay failed")

    phi2 = sp.Matrix([
        sp.Rational(496, 63), 0, 0, 0, -sp.Rational(32, 7),
        0, 0, -sp.Rational(32, 7), 0, -sp.Rational(256, 63),
    ])
    if hessian * phi2 + source != sp.zeros(10, 1):
        raise AssertionError("independent primitive replay failed")
    witnesses = [
        sp.eye(10)[:, 3],
        sp.eye(10)[:, 6],
        sp.eye(10)[:, 8],
    ]
    for witness in witnesses:
        if witness.T * hessian != sp.zeros(1, 10) or (witness.T * source)[0] != 0:
            raise AssertionError("independent adjoint-kernel replay failed")
    if hessian.rank() != 7 or hessian.row_join(-source).rank() != 7:
        raise AssertionError("independent solvability ranks drifted")

    flags = payload["flags"]
    if flags["COMPACT_TAUB_PROJECTION_COMPUTED"] is not False:
        raise AssertionError("compact verdict was over-promoted")
    if payload["binary_scientific_verdict"]["verdict"] != "INPUT_BLOCKED":
        raise AssertionError("global compact verdict drifted")
    print("BERGER_ROD_TADPOLE_COMPACT_SOLVABILITY_GATE independent replay: PASS")


if __name__ == "__main__":
    main()
