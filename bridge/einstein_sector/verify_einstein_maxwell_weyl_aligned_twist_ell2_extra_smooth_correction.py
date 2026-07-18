#!/usr/bin/env python3
"""Independently verify the aligned twist--extra correction certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator as _polar_action


CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json"
SOURCE = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_source_fixture.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _axial_action(ell: int) -> tuple[sp.Matrix, sp.Symbol]:
    rows, symbols = _axial_rows()
    fields = sp.Matrix([symbols[name] for name in ("h_t", "h_x", "q_t", "q_x")])
    equations = sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    matrix = sp.diag(symbols["lambda"], -symbols["lambda"], 1, 1) * equations.jacobian(fields)
    return matrix.subs({symbols["lambda"]: ell * (ell + 1), symbols["k"]: 0}).applyfunc(sp.factor), symbols["omega"]


def _full_operator(parity: str, ell: int) -> tuple[sp.Matrix, sp.Symbol]:
    if parity == "axial":
        return _axial_action(ell)
    matrix, (eigenvalue, momentum, frequency) = _polar_action()
    return matrix.subs({eigenvalue: ell * (ell + 1), momentum: 0}).applyfunc(sp.factor), frequency


def _apply(matrix: sp.Matrix, frequency: sp.Symbol, field: sp.Matrix, time: sp.Symbol) -> sp.Matrix:
    omega0 = 4 / sp.sqrt(3)
    result = sp.zeros(4, 1)
    maximum = max(sp.Poly(entry, frequency).degree() for entry in matrix if entry != 0)
    for order in range(maximum + 1):
        derivative = field.diff(time, order)
        coefficient = matrix.diff(frequency, order).subs(frequency, omega0) / sp.factorial(order)
        result += sp.I**order * coefficient * derivative
    return result.applyfunc(lambda value: sp.factor(sp.expand(value)))


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    source_fixture = json.loads(SOURCE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if certificate["schema_sha256"] != _sha256(SCHEMA):
        raise AssertionError("schema hash changed")
    for relative, digest in certificate["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise AssertionError(f"source hash changed: {relative}")

    time = sp.symbols("t", real=True)
    solved = 0
    zeros = 0
    for case_id, case in certificate["cases"].items():
        ell = int(case_id.rsplit("L", 1)[1])
        fixture = source_fixture["sources"][case_id]
        if case["status"] == "ZERO_SOURCE":
            zeros += 1
            if any(sp.sympify(value, locals={"t": time, "I": sp.I}) != 0 for key in ("axial_action_source", "polar_action_source") for value in fixture[key]):
                raise AssertionError(f"{case_id}: source is not zero")
            continue
        solved += 1
        parity = case["output_parity"]
        source = sp.Matrix([sp.sympify(value, locals={"t": time, "I": sp.I}) for value in fixture[f"{parity}_action_source"]])
        if [str(sp.factor(sp.expand(value))) for value in source] != case["source_action_rows"]:
            raise AssertionError(f"{case_id}: stored source differs from direct fixture")
        field = sp.Matrix([sp.sympify(value, locals={"t": time, "I": sp.I}) for value in case["correction_coefficients"]])
        matrix, frequency = _full_operator(parity, ell)
        remainder = _apply(matrix, frequency, field, time) + source
        if remainder.applyfunc(lambda value: sp.factor(sp.expand(value))) != sp.zeros(4, 1):
            raise AssertionError(f"{case_id}: full action remainder survived: {remainder}")
        if case["full_action_remainder"] != ["0", "0", "0", "0"]:
            raise AssertionError(f"{case_id}: certificate does not expose zero remainder")
        if ell == 1:
            if parity == "axial" and field[0] != 0:
                raise AssertionError(f"{case_id}: axial exceptional slice h_t=0 violated")
            if parity == "polar" and field[3] != 0:
                raise AssertionError(f"{case_id}: polar exceptional slice U=0 violated")
    if (solved, zeros) != (13, 3):
        raise AssertionError(f"case count changed: {(solved, zeros)}")
    flags = certificate["classification"]
    if not flags["aligned_twist_extra_L1_L3_block_coefficient_explicit"]:
        raise AssertionError("scoped coefficient theorem not certified")
    if flags["complete_arbitrary_orbit_correction_coefficient_explicit"]:
        raise AssertionError("scoped theorem silently promoted the complete orbit")
    if flags["bounded_correction_certified"] or flags["causal_retarded_correction_certified"]:
        raise AssertionError("correction-class boundary was crossed")
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SMOOTH_CORRECTION_VERIFIER: PASS")


if __name__ == "__main__":
    main()
