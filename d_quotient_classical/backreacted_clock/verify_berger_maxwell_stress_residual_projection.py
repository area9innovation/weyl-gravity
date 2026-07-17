#!/usr/bin/env python3
"""Independent replay of the Berger Maxwell stress obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-stress-residual-projection-v1.schema.json"
CONTRACTION = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
RETAINED = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _constant_matrix(record, shape):
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _digest(body):
        raise AssertionError("independent operator hash check failed")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if not any(exponents):
                matrix[row, column] += sp.sympify(raw, locals={"u": u, "v": v, "alpha_B": 5})
    return sp.simplify(matrix)


def _field(component_data):
    matrix = sp.zeros(4)
    for (left, right), value in component_data.items():
        matrix[left, right] = value
        matrix[right, left] = -value
    return matrix


def _stress(first, second):
    eta = sp.diag(-1, 1, 1, 1)
    contraction = sum(
        eta[a, c] * eta[b, d] * first[a, b] * second[c, d]
        for a in range(4) for b in range(4) for c in range(4) for d in range(4)
    )
    return ((first * eta * second.T + second * eta * first.T) / 2 - eta * contraction / 4).applyfunc(sp.trigsimp)


def _connection(a, c):
    eta = sp.diag(-1, 1, 1, 1)
    structure = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for first, second, target, value in ((1, 2, 3, c / a**2), (2, 3, 1, 1 / c), (3, 1, 2, 1 / c)):
        structure[first][second][target] = value
        structure[second][first][target] = -value
    output = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for derivative in range(4):
        for vector in range(4):
            for lowered in range(4):
                lower = sp.Rational(1, 2) * (
                    eta[lowered, lowered] * structure[derivative][vector][lowered]
                    - eta[derivative, derivative] * structure[vector][lowered][derivative]
                    + eta[vector, vector] * structure[lowered][derivative][vector]
                )
                output[lowered][derivative][vector] += eta[lowered, lowered] * lower
    return output


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
    time = sp.symbols("s", real=True)
    cosine, sine = sp.cos(beta * time), sp.sin(beta * time)
    first = _field({(0, 1): -beta * sine, (0, 2): beta * cosine, (1, 3): beta * sine, (2, 3): -beta * cosine})
    second = _field({(0, 1): -beta * cosine, (0, 2): -beta * sine, (1, 3): beta * cosine, (2, 3): beta * sine})
    expected = beta**2 * sp.Matrix([[1, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 1]])
    if _stress(first, first) != expected or _stress(second, second) != expected:
        raise AssertionError("independent diagonal stress replay failed")
    if _stress(first, second) != sp.zeros(4):
        raise AssertionError("independent cross-stress replay failed")
    eta = sp.diag(-1, 1, 1, 1)
    stress_upper = eta * expected * eta
    connection = _connection(sp.S.One, 3 / (2 * sp.sqrt(10)))
    divergence = sp.Matrix([
        sp.simplify(sum(connection[a][a][c] * stress_upper[c, b] + connection[b][a][c] * stress_upper[a, c] for a in range(4) for c in range(4)))
        for b in range(4)
    ])
    if divergence != sp.zeros(4, 1):
        raise AssertionError("independent stress-conservation replay failed")

    source = sp.Matrix([sp.Rational(80, 9), 0, 0, -sp.Rational(160, 9), 0, 0, 0, 0, 0, sp.Rational(80, 9)])
    contraction = json.loads(CONTRACTION.read_text())
    pi = _constant_matrix(contraction["contraction"]["pi_cl"], (26, 54))
    if pi[13:23, 27:37] != sp.eye(10):
        raise AssertionError("independent pi_cl metric block replay failed")
    retained = json.loads(RETAINED.read_text())["q1_blocks"]
    hessian = _constant_matrix(retained["H_retained"], (10, 10))
    noether = _constant_matrix(retained["minus_K_spatial_sharp"], (3, 10))
    if noether * source != sp.zeros(3, 1):
        raise AssertionError("independent q1 closure replay failed")

    diagonal = sp.Matrix(source)
    diagonal[3] = 0
    primitive = sp.Matrix([-sp.Rational(5120, 567), 0, 0, 0, sp.Rational(10880, 651), 0, 0, sp.Rational(10880, 651), 0, sp.Rational(14080, 1953)])
    if hessian * primitive != diagonal:
        raise AssertionError("independent diagonal primitive replay failed")
    witness = sp.zeros(10, 1)
    witness[3] = -sp.Rational(9, 160)
    if witness.T * hessian != sp.zeros(1, 10) or (witness.T * source)[0] != 1:
        raise AssertionError("independent normalized obstruction witness failed")
    if hessian.rank() != 7 or hessian.row_join(source).rank() != 8:
        raise AssertionError("independent obstruction rank replay failed")
    if certificate["projection_and_verdict"]["binary_verdict"] != "OBSTRUCTION":
        raise AssertionError("persisted binary verdict drifted")
    if certificate["physical_mode_block"]["exact_data"]["stress_covariant_divergence"] != ["0"] * 4:
        raise AssertionError("persisted stress divergence drifted")
    if certificate["flags"]["BERGER_FULL_SUPPORT_LOCAL_MAXWELL_Q2"] is not False:
        raise AssertionError("reduced-mode result was promoted")
    print("BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION independent replay: PASS")


if __name__ == "__main__":
    main()
