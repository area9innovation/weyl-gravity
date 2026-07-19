#!/usr/bin/env python3
"""Independent exact verifier for the axial-axial L=4 source matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_axial_L4_q2_slice.json"
QMINUS_SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str, **locals_: sp.Expr) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, **locals_})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


Interval = tuple[Fraction, Fraction]


def multiply(left: Interval, right: Interval) -> Interval:
    values = (
        left[0] * right[0], left[0] * right[1],
        left[1] * right[0], left[1] * right[1],
    )
    return min(values), max(values)


def integer_power(value: Interval, exponent: int) -> Interval:
    if exponent < 0:
        powered = integer_power(value, -exponent)
        assert not (powered[0] <= 0 <= powered[1])
        values = 1 / powered[0], 1 / powered[1]
        return min(values), max(values)
    if exponent == 0:
        return Fraction(1), Fraction(1)
    if exponent % 2 == 0 and value[0] <= 0 <= value[1]:
        return Fraction(0), max(abs(value[0]), abs(value[1])) ** exponent
    values = value[0] ** exponent, value[1] ** exponent
    return min(values), max(values)


def sqrt_endpoint(value: Fraction, scale: int) -> tuple[Fraction, Fraction]:
    assert value >= 0
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    lower = Fraction(floor, scale)
    return (lower, lower) if lower * lower == value else (lower, Fraction(floor + 1, scale))


def rational_interval(expression: sp.Expr, digits: int) -> Interval:
    scale = 10**digits

    def evaluate(value: sp.Expr) -> Interval:
        if value.is_Rational:
            exact = Fraction(int(sp.numer(value)), int(sp.denom(value)))
            return exact, exact
        if value.is_Add:
            lower = upper = Fraction(0)
            for term in value.args:
                term_lower, term_upper = evaluate(term)
                lower += term_lower
                upper += term_upper
            return lower, upper
        if value.is_Mul:
            result = Fraction(1), Fraction(1)
            for factor in value.args:
                result = multiply(result, evaluate(factor))
            return result
        if value.is_Pow and value.exp.is_Rational:
            exponent = sp.Rational(value.exp)
            if exponent.q == 1:
                return integer_power(evaluate(value.base), int(exponent.p))
            assert exponent.q == 2
            numerator = int(exponent.p)
            powered = integer_power(evaluate(value.base), abs(numerator))
            assert powered[0] >= 0
            root = sqrt_endpoint(powered[0], scale)[0], sqrt_endpoint(powered[1], scale)[1]
            return integer_power(root, -1) if numerator < 0 else root
        raise TypeError(f"unsupported interval node: {value}")

    assert not expression.has(sp.I)
    return evaluate(expression)


def fraction_string(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def verify_generic_slice_calibration() -> None:
    generic = json.loads(SLICE.read_text())
    narrow = json.loads(QMINUS_SLICE.read_text())
    assert generic["parent"]["q2_sha256"] == sha(Q2)
    assert generic["parent"]["row_layout_sha256"] == sha(ROW_LAYOUT)
    assert generic["parent"]["action_sha256"] == sha(ACTION)
    k_1, omega_1, k_2, omega_2 = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    local = {
        "k_1": k_1, "omega_1": omega_1,
        "k_2": k_2, "omega_2": omega_2,
        **{str(value): value for value in (*first, *second)},
    }
    source = sp.Matrix([parse(row, **local) for row in generic["source_action_rows"]])
    q_first = sp.Matrix([2 * k_1, -2 * omega_1, -2 * sp.sqrt(3) * k_1, 2 * sp.sqrt(3) * omega_1])
    q_second = sp.Matrix([2 * k_2, -2 * omega_2, -2 * sp.sqrt(3) * k_2, 2 * sp.sqrt(3) * omega_2])
    specialized = source.subs({
        **dict(zip(first, q_first, strict=True)),
        **dict(zip(second, q_second, strict=True)),
    }, simultaneous=True)
    expected = sp.Matrix([parse(row, k_1=k_1, omega_1=omega_1, k_2=k_2, omega_2=omega_2) for row in narrow["source_action_rows"]])
    assert (specialized - expected).applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(4, 1)


def branch_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }[branch]


def target_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 20 - 2 * sp.sqrt(10),
        "p_extra": sp.Rational(58, 3),
        "q_plus": 20 + 2 * sp.sqrt(10),
    }[branch]


def independently_verify(exhaustive: bool = False) -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    assert value["source_slice"]["sha256"] == sha(SLICE)
    for item in value["provenance"]["inputs"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    verify_generic_slice_calibration()

    workload = {
        row["candidate_index"]: row
        for row in json.loads(PARITY.read_text())["source_workload"]["rows"]
        if row["output_ell"] == 4
    }
    assert [row["candidate_index"] for row in value["candidate_rows"]] == sorted(workload)
    fixtures = coefficients = zeros = 0
    for row in value["candidate_rows"]:
        expected = workload[row["candidate_index"]]
        assert (row["first_branch"], row["second_branch"], row["target_branch"]) == (
            expected["first_branch"], expected["second_branch"], expected["target_branch"]
        )
        rho = parse(row["rho"])
        momenta = [sign * sp.sqrt(rho) for sign in row["signed_momenta"]]
        frequencies = [
            sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])),
            sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"])),
        ]
        assert canonical(
            (frequencies[0] + frequencies[1]) ** 2
            - (momenta[0] + momenta[1]) ** 2
            - target_mass(row["target_branch"])
        ) == 0
        for fixture in row["basis_fixtures"]:
            fixtures += 1
            pairings = [parse(item) for item in fixture["pairings"]]
            intervals = fixture["pairing_intervals"]
            coefficients += len(pairings)
            for pairing, stored in zip(pairings, intervals, strict=True):
                if pairing == 0:
                    zeros += 1
                    assert stored is None
                    continue
                assert stored is not None
                actual = rational_interval(pairing, int(stored["decimal_digits"]))
                assert [fraction_string(item) for item in actual] == [stored["lower"], stored["upper"]]
                assert actual[0] > 0 or actual[1] < 0
            witness = intervals[int(fixture["nonzero_component"])]
            assert witness is not None and fixture["bounded_status"] == "OBSTRUCTED"
    assert (fixtures, coefficients, zeros) == (20, 27, 1)
    assert value["matrix_summary"]["nonzero_target_adjoint_coefficients"] == 26
    assert not value["classification"]["arbitrary_axial_linear_combinations_classified"]
    if exhaustive:
        # The producer's exhaustive replay is deliberately a separate slow rail.
        # Equality of its regenerated certificate checks every specialized source
        # and cokernel contraction, while this verifier independently checks its
        # inputs, shell geometry, interval arithmetic and q-minus calibration.
        import subprocess
        subprocess.run(
            [
                "python3", "-m",
                "bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix",
                "--recompute-exhaustive",
            ],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args()
    independently_verify(args.exhaustive)
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_AXIAL_L4_MATRIX independent verification: PASS")
