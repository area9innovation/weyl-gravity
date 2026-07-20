#!/usr/bin/env python3
"""Independent replay of the non-cone A104 boundary obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_evolution_extension_obstruction_v1/"
    "boundary_cokernel_witness.json"
)
NONCONE_DIFFERENTIAL = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_rational_nilpotence_feasibility_v1/"
    "rational_noncone_differential.json"
)
A104_OPERATOR = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_a104_endpoint_completion/global_A104.json"
)
DEGREES = tuple([-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6) * 2


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _rational_matrix(record: dict) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body):
        raise AssertionError("matrix internal hash drifted")
    result = sp.zeros(*record["shape"])
    for row, column, numerator, denominator in record["entries"]:
        result[row, column] = sp.Rational(numerator, denominator)
    return result


def _constant_a104() -> sp.Matrix:
    record = _load(A104_OPERATOR)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body):
        raise AssertionError("A104 internal hash drifted")
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {alpha_B: 2, u: 1, v: 3}
    result = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if any(exponents):
                continue
            result[row, column] += sp.sympify(
                coefficient,
                locals={"alpha_B": alpha_B, "u": u, "v": v},
            ).subs(substitutions)
    return result


def verify() -> None:
    certificate = _load(CERTIFICATE)
    witness = _load(PAYLOAD)
    witness_body = {
        key: value for key, value in witness.items() if key != "sha256"
    }
    if witness["sha256"] != _digest(witness_body):
        raise AssertionError("witness internal hash drifted")
    if (
        certificate["exact_obstruction"]["sha256"] != _sha(PAYLOAD)
        or certificate["pinned_inputs"]["noncone_rational_differential"][
            "sha256"
        ]
        != _sha(NONCONE_DIFFERENTIAL)
        or certificate["pinned_inputs"]["A104_operator"]["sha256"]
        != _sha(A104_OPERATOR)
    ):
        raise AssertionError("content-addressed input drifted")

    differential_record = _load(NONCONE_DIFFERENTIAL)["matrices"][
        "degree_minus1_to_0"
    ]
    differential = _rational_matrix(differential_record)
    source = sp.eye(24)[:, 16]
    image = differential * source
    expected = sp.zeros(80, 1)
    expected[5, 0] = 1
    if image != expected:
        raise AssertionError("pure-old boundary identity failed")

    cokernel = sp.eye(40)[:, 25]
    if cokernel.T * differential[:40, :] != sp.zeros(1, 24):
        raise AssertionError("boundary-cokernel identity failed")

    degree_zero = [
        index for index, degree in enumerate(DEGREES) if degree == 0
    ]
    evolution = _constant_a104().extract(degree_zero, degree_zero)
    evolved = evolution * image[:40, :]
    if (
        evolved[25, 0] != sp.Rational(-51, 2)
        or evolved[35, 0] != sp.Rational(111, 4)
        or sum(bool(entry) for entry in evolved) != 2
        or (cokernel.T * evolved)[0] != sp.Rational(-51, 2)
    ):
        raise AssertionError("normalized A104 obstruction failed")

    flags = certificate["classification"]
    if (
        flags["fixed_noncone_witness_A104_chain_extension_exists"]
        or flags["all_104_row_noncone_differentials_obstructed"]
        or flags["cyclic_pairing_constructed"]
    ):
        raise AssertionError("claim boundary drifted")
    print(
        "BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_"
        "OBSTRUCTION_V1 independent verification: PASS (-51/2)"
    )


if __name__ == "__main__":
    verify()
