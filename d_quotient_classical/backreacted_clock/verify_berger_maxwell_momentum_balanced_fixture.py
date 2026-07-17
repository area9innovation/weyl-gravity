#!/usr/bin/env python3
"""Independent replay of the momentum-balanced Berger Maxwell fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-momentum-balanced-fixture-v1.schema.json"
CONTRACTION = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
RETAINED = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _constant_matrix(record, shape):
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _digest(body):
        raise AssertionError("independent operator hash replay failed")
    u, v = 3 * sp.sqrt(10) / 20, 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if not any(exponents):
                matrix[row, column] += sp.sympify(raw, locals={"u": u, "v": v, "alpha_B": 5})
    return sp.simplify(matrix)


def _field(components):
    matrix = sp.zeros(4)
    for (left, right), value in components.items():
        matrix[left, right] = value
        matrix[right, left] = -value
    return matrix


def _stress(field):
    eta = sp.diag(-1, 1, 1, 1)
    contraction = sum(eta[a, c] * eta[b, d] * field[a, b] * field[c, d] for a in range(4) for b in range(4) for c in range(4) for d in range(4))
    return (field * eta * field.T - eta * contraction / 4).applyfunc(sp.trigsimp)


def _direct_cubic(field):
    eta = sp.diag(-1, 1, 1, 1)
    h, amplitude = sp.symbols("h amplitude", real=True)
    result = sp.zeros(10, 1)
    for index, (left, right) in enumerate(PAIRS):
        variation = sp.zeros(4)
        variation[left, right] = variation[right, left] = 1
        metric = eta + h * variation
        inverse = metric.inv()
        contraction = sum(inverse[a, c] * inverse[b, d] * field[a, b] * field[c, d] for a in range(4) for b in range(4) for c in range(4) for d in range(4))
        density = -sp.Rational(1, 4) * sp.sqrt(-metric.det()) * amplitude**2 * contraction
        result[index] = sp.trigsimp(sp.diff(density, h, amplitude, amplitude).subs({h: 0, amplitude: 0}))
    return result.applyfunc(sp.simplify)


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
        if json.loads(path.read_text())["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency result mismatch: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source hash mismatch: {path}")

    beta = 2 * sp.sqrt(10) / 3
    time = sp.symbols("time", real=True)
    sine, cosine = sp.sin(beta * time), sp.cos(beta * time)
    forward = _field({(0, 1): -beta * sine, (0, 2): beta * cosine, (1, 3): beta * sine, (2, 3): -beta * cosine})
    reverse = _field({(0, 1): -beta * sine, (0, 2): -beta * cosine, (1, 3): -beta * sine, (2, 3): -beta * cosine})
    standing = forward + reverse
    stress = _stress(standing)
    expected_stress = sp.Matrix([[2 * beta**2, 0, 0, 0], [0, -2 * beta**2, 0, 0], [0, 0, 2 * beta**2, 0], [0, 0, 0, 2 * beta**2]])
    if stress != expected_stress:
        raise AssertionError("independent coherent standing stress replay failed")
    direct = _direct_cubic(standing)
    expected_source = sp.Matrix([sp.Rational(160, 9), 0, 0, 0, -sp.Rational(160, 9), 0, 0, sp.Rational(160, 9), 0, sp.Rational(160, 9)])
    if 2 * direct != expected_source:
        raise AssertionError("independent direct-action normalization replay failed")

    contraction = json.loads(CONTRACTION.read_text())["contraction"]["pi_cl"]
    pi = _constant_matrix(contraction, (26, 54))
    if pi[13:23, 27:37] != sp.eye(10):
        raise AssertionError("independent pi_cl metric block replay failed")
    retained = json.loads(RETAINED.read_text())["q1_blocks"]
    hessian = _constant_matrix(retained["H_retained"], (10, 10))
    noether = _constant_matrix(retained["minus_K_spatial_sharp"], (3, 10))
    if noether * expected_source != sp.zeros(3, 1):
        raise AssertionError("independent q1 closure replay failed")
    primitive = sp.Matrix([-sp.Rational(10240, 567), 0, 0, 0, sp.Rational(4933120, 147819), 0, 0, sp.Rational(153410560, 4582389), 0, sp.Rational(28160, 1953)])
    correction = -primitive / 2
    if hessian * primitive != expected_source:
        raise AssertionError("independent exact primitive replay failed")
    if hessian * correction + expected_source / 2 != sp.zeros(10, 1):
        raise AssertionError("independent Maurer-Cartan correction replay failed")
    witness = sp.zeros(10, 1)
    witness[3] = -sp.Rational(9, 160)
    if (witness.T * expected_source)[0] != 0:
        raise AssertionError("independent Hopf witness cancellation replay failed")
    if hessian.rank() != hessian.row_join(expected_source).rank():
        raise AssertionError("independent exactness rank replay failed")
    if certificate["projection_and_solution"]["binary_verdict"] != "EXACT_PRIMITIVE":
        raise AssertionError("persisted balanced verdict drifted")
    if certificate["flags"]["BERGER_FULL_BACKREACTED_SOLUTION"] is not False:
        raise AssertionError("second-order fixture was promoted to all orders")
    print("BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE independent replay: PASS")


if __name__ == "__main__":
    main()
