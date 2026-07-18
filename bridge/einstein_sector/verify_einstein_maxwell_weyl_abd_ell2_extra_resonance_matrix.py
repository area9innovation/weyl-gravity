#!/usr/bin/env python3
"""Fast exact verifier for the homogeneous a,b,d resonance submatrix."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.schema.json"


def _parse(value: str, time: sp.Symbol | None = None) -> sp.Expr:
    locals_map = {"I": sp.I, "sqrt": sp.sqrt}
    if time is not None:
        locals_map["t"] = time
    return sp.sympify(value, locals=locals_map)


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    time = sp.symbols("t", real=True)
    expected = {
        "axial": {
            "a": ["540 + 144*sqrt(3)*I*t", "344/9 - 208*sqrt(3)*I*t/27"],
            "b": ["540*t + 72*sqrt(3)*I*t**2 - 144*sqrt(3)*I", "344*t/9 - 104*sqrt(3)*I*t**2/27 + 44*sqrt(3)*I/3"],
            "d": ["72*sqrt(3)*I", "-104*sqrt(3)*I/27"],
        },
        "polar": {
            "a": ["27 - 12*sqrt(3)*I*t", "4916 + 1104*sqrt(3)*I*t"],
            "b": ["27*t - 6*sqrt(3)*I*t**2", "4916*t + 552*sqrt(3)*I*t**2 + 1160*sqrt(3)*I"],
            "d": ["-6*sqrt(3)*I", "552*sqrt(3)*I"],
        },
    }
    stored = value["projected_resonance_polynomials"]
    for parity in expected:
        for global_case in expected[parity]:
            for index, expression in enumerate(expected[parity][global_case]):
                if sp.simplify(
                    _parse(stored[parity][global_case][index], time)
                    - _parse(expression, time)
                ) != 0:
                    raise AssertionError(f"{parity} {global_case} projection changed")
    for parity in expected:
        for index in range(2):
            polynomials = [
                sp.Poly(_parse(expected[parity][case][index], time), time)
                for case in ("a", "b", "d")
            ]
            height = max(polynomial.degree() for polynomial in polynomials) + 1
            coefficient_matrix = sp.Matrix(
                [[polynomial.nth(power) for polynomial in polynomials] for power in range(height)]
            )
            if coefficient_matrix.rank() != 3:
                raise AssertionError(f"{parity} e{index + 1} polynomial rank changed")
    flags = value["classification"]
    if not flags["every_parity_polarization_abd_polynomial_chain_rank_three"]:
        raise AssertionError("rank-three classification missing")
    if flags["twist_position_velocity_columns_computed"] or flags["full_second_order_equation_solved"]:
        raise AssertionError("open gates were promoted")
    print("EINSTEIN_MAXWELL_WEYL_ABD_ELL2_EXTRA_RESONANCE_MATRIX fast verification: PASS")


if __name__ == "__main__":
    main()
