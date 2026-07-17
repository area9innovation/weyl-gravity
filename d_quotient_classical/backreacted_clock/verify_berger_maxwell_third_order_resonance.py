#!/usr/bin/env python3
"""Independent replay of the Berger Maxwell third-order resonance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-third-order-resonance-v1.schema.json"
CONTRACTION = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
BALANCED = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json"


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _constant_matrix(record: dict, shape: tuple[int, int]) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _digest(body):
        raise AssertionError("independent operator hash replay failed")
    u, v = 3 * sp.sqrt(10) / 20, 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if not any(exponents):
                matrix[row, column] += sp.sympify(
                    raw, locals={"u": u, "v": v, "alpha_B": 5}
                )
    return sp.simplify(matrix)


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

    contraction = json.loads(CONTRACTION.read_text())
    balanced = json.loads(BALANCED.read_text())["balanced_Maxwell_fixture"]["exact_data"]
    q1 = _constant_matrix(contraction["classical_unary_q1"]["matrix"], (54, 54))
    iota = _constant_matrix(contraction["contraction"]["iota_cl"], (54, 26))
    pi_cl = _constant_matrix(contraction["contraction"]["pi_cl"], (26, 54))
    homotopy = _constant_matrix(contraction["contraction"]["S_cl"], (54, 54))
    source = sp.zeros(54, 1)
    source[27:37, 0] = sp.Matrix(
        [sp.sympify(value) for value in balanced["standing_repository_q2"]]
    )
    retained_correction = sp.zeros(26, 1)
    retained_correction[3:13, 0] = sp.Matrix(
        [sp.sympify(value) for value in balanced["second_order_Maurer_Cartan_correction"]]
    )
    full_correction = sp.simplify(iota * retained_correction - homotopy * source / 2)
    if homotopy * source != sp.zeros(54, 1):
        raise AssertionError("independent homotopy-source replay drifted")
    if q1 * source != sp.zeros(54, 1):
        raise AssertionError("independent full source closure failed")
    if q1 * full_correction + source / 2 != sp.zeros(54, 1):
        raise AssertionError("independent full Maurer--Cartan replay failed")
    if pi_cl * full_correction != retained_correction:
        raise AssertionError("independent projection replay failed")

    h00, h11, h22, h33 = retained_correction[3], retained_correction[7], retained_correction[10], retained_correction[12]
    trace_half = sp.factor((-h00 + h11 + h22 + h33) / 2)
    delta_k = sp.factor(trace_half + h00 - h11)
    delta_b = sp.factor(trace_half - h22 - h33)
    dispersion = sp.factor(delta_b - delta_k)
    if dispersion != -sp.Rational(7055360, 3991113):
        raise AssertionError("independent dispersion variation failed")
    beta = 2 * sp.sqrt(10) / 3
    source_cosine = sp.factor(-2 * beta**2 * dispersion)
    if source_cosine != sp.Rational(564428800, 35920017):
        raise AssertionError("independent mixed q2 source failed")
    witness = sp.factor(1 / source_cosine)
    if witness * source_cosine != 1:
        raise AssertionError("independent normalized witness failed")

    delta_beta = sp.factor(beta * dispersion / 2)
    t = sp.symbols("t", real=True)
    q3 = -2 * delta_beta * t * sp.sin(beta * t)
    q1_q3 = sp.factor(-(sp.diff(q3, t, 2) + beta**2 * q3))
    if sp.trigsimp(q1_q3 + source_cosine * sp.cos(beta * t)) != 0:
        raise AssertionError("independent frequency-renormalized continuation failed")
    if certificate["binary_verdict"]["fixed_frequency_periodic_primitive"] != "OBSTRUCTION":
        raise AssertionError("persisted fixed-frequency verdict drifted")
    if certificate["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] is not False:
        raise AssertionError("physical-shape q2 block was promoted to a complete BV export")
    print("BERGER_MAXWELL_THIRD_ORDER_RESONANCE independent replay: PASS")


if __name__ == "__main__":
    main()
