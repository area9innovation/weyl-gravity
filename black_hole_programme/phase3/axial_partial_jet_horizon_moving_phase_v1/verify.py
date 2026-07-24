#!/usr/bin/env python3
"""Independent verifier for the moving-phase horizon certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    CI,
    RI,
    eval_rational_rect,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
R = sp.Symbol("r", positive=True)
RHO = sp.Symbol("rho")
W = sp.Symbol("omega", real=True)
I = sp.I


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    doc = json.loads(CERTIFICATE.read_text())
    if doc["status"] != (
        "CERTIFIED_MOVING_PHASE_TAIL_AND_FIRST_PANEL_PARTIAL_JET_PASS"
    ):
        raise RuntimeError("status drift")
    for item in doc["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {path}")

    crosswalk_path = ROOT / doc["imports"]["partial_jet_crosswalk"]["path"]
    crosswalk = json.loads(crosswalk_path.read_text())
    a = matrix(crosswalk["exact_blocks"]["A_RW"]).subs(R, 2 + RHO)
    e = matrix(crosswalk["exact_blocks"]["E_RW_self_extension"]).subs(
        R, 2 + RHO
    )
    residue = (RHO * a).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    tangent_residue = (RHO * e).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    printed_residue = matrix(doc["moving_phase"]["residue"])
    printed_tangent = matrix(doc["moving_phase"]["tangent_residue"])
    if (residue - printed_residue).applyfunc(clean) != sp.zeros(2):
        raise RuntimeError("residue mismatch")
    if tangent_residue != printed_tangent or tangent_residue != sp.zeros(2):
        raise RuntimeError("tangent residue mismatch")

    right = sp.Matrix(
        [parse(value) for value in doc["moving_phase"]["selected_right_vector"]]
    )
    left = sp.Matrix(
        [[parse(value) for value in doc["moving_phase"]["selected_left_vector"]]]
    )
    pairing = clean((left * right)[0])
    dot_lambda = clean((left * tangent_residue * right)[0] / pairing)
    if pairing != 1 or dot_lambda != 0:
        raise RuntimeError("zero exponent derivative failed")
    if (residue * right).applyfunc(clean) != sp.zeros(2, 1):
        raise RuntimeError("selected right line is not regular")

    recurrence = doc["reduced_frobenius_recurrence"]
    base = [
        sp.Matrix([parse(value) for value in vector])
        for vector in recurrence["base_coefficients"]
    ]
    tangent = [
        sp.Matrix([parse(value) for value in vector])
        for vector in recurrence["tangent_coefficients"]
    ]
    regular_a = (a - residue / RHO).applyfunc(clean)
    order = doc["scope"]["frobenius_order"]
    a_coefficients = [
        regular_a.applyfunc(
            lambda value, n=n: clean(
                sp.limit(
                    sp.diff(value, RHO, n) / sp.factorial(n), RHO, 0
                )
            )
        )
        for n in range(order)
    ]
    e_coefficients = [
        e.applyfunc(
            lambda value, n=n: clean(
                sp.limit(
                    sp.diff(value, RHO, n) / sp.factorial(n), RHO, 0
                )
            )
        )
        for n in range(order)
    ]
    for n in range(1, order + 1):
        pivot = n * sp.eye(2) - residue
        expected_det = clean(n * (n + 1 + 4 * I * W))
        if clean(pivot.det() - expected_det) != 0:
            raise RuntimeError(f"pivot mismatch at order {n}")
        rhs = sum(
            (
                a_coefficients[k] * base[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(2, 1),
        )
        tangent_rhs = sum(
            (
                a_coefficients[k] * tangent[n - 1 - k]
                + e_coefficients[k] * base[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(2, 1),
        )
        if (pivot * base[n] - rhs).applyfunc(clean) != sp.zeros(2, 1):
            raise RuntimeError(f"base recurrence mismatch at order {n}")
        if (
            pivot * tangent[n] - tangent_rhs
        ).applyfunc(clean) != sp.zeros(2, 1):
            raise RuntimeError(f"tangent recurrence mismatch at order {n}")

    from fractions import Fraction

    environment = {
        W: CI(RI(Fraction(1, 2), Fraction(4097, 8192))),
        RHO: CI(
            RI(-Fraction(1, 2), Fraction(1, 2)),
            RI(-Fraction(1, 2), Fraction(1, 2)),
        ),
    }
    a_rows = []
    e_rows = []
    for value, target in ((regular_a, a_rows), (e, e_rows)):
        for row in range(2):
            target.append(
                sum(
                    (
                        eval_rational_rect(value[row, col], environment)
                        .norm_one_hi()
                        for col in range(2)
                    ),
                    Fraction(0),
                )
            )
    majorant_a = sp.Rational(max(a_rows))
    majorant_e = sp.Rational(max(e_rows))
    tail = doc["all_order_tail_majorant"]
    if parse(tail["M_A"]) != majorant_a or parse(tail["M_E"]) != majorant_e:
        raise RuntimeError("Cauchy row majorant mismatch")
    c = sp.Rational(5, 4)
    radius = sp.Rational(1, 2)
    rho0 = sp.Rational(1, 2**22)
    p = clean(c * majorant_a * radius)
    q = clean(c * majorant_e * radius)
    x = clean(rho0 / radius)
    coefficient_value = sp.Integer(1)
    harmonic = sp.Integer(0)
    for n in range(1, order + 2):
        harmonic = clean(harmonic + 1 / (p + n - 1))
        coefficient_value = clean(
            coefficient_value * (p + n - 1) / n
        )
    first_base = clean(coefficient_value * x ** (order + 1))
    first_tangent = clean(
        q * coefficient_value * harmonic * x ** (order + 1)
    )
    ratio_base = clean(x * (p + order + 1) / (order + 2))
    ratio_tangent = clean(x * (order + 1 + 2 * p) / (order + 2))
    tail_base = clean(first_base / (1 - ratio_base))
    tail_tangent = clean(first_tangent / (1 - ratio_tangent))
    if parse(tail["tail_base"]) != tail_base:
        raise RuntimeError("base tail mismatch")
    if parse(tail["tail_tangent"]) != tail_tangent:
        raise RuntimeError("tangent tail mismatch")
    if not (0 <= ratio_base < 1 and 0 <= ratio_tangent < 1):
        raise RuntimeError("tail ratio is not contractive")

    rail = doc["finite_seed_rail"]
    for key in ("source", "compile_log", "run_log"):
        path = ROOT / rail[f"{key}_path"]
        if sha256(path) != rail[f"{key}_sha256"]:
            raise RuntimeError(f"{key} hash mismatch")
    if not rail["passed"] or rail["compile_exit"] != 0 or rail["run_exit"] != 0:
        raise RuntimeError("finite seed rail did not pass")
    if "MOVING_PHASE_SEED status=PASS" not in (
        ROOT / rail["run_log_path"]
    ).read_text():
        raise RuntimeError("run token missing")
    flags = doc["claim_flags"]
    if not flags["dot_lambda_H_exactly_zero"]:
        raise RuntimeError("dot-lambda flag drift")
    for flag in (
        "endpoint_partial_jet_frame_constructed",
        "T_plus_recovered",
        "H4_pass_certified",
        "bounded_global_transport_certified",
    ):
        if flags[flag]:
            raise RuntimeError(f"fail-closed flag promoted: {flag}")
    if not flags["uniform_frobenius_tail_enclosed"]:
        raise RuntimeError("tail flag not promoted")
    if not flags["first_panel_transport_certified"]:
        raise RuntimeError("first-panel flag not promoted")
    panel = doc["first_panel_transport"]
    if not (
        panel["passed"]
        and panel["transport_hulls_overlap"]
        and panel["tail_enclosed_seed_outputs_overlap"]
    ):
        raise RuntimeError("first-panel comparison failed")
    print("PASS moving-phase tail and first pure-spin-two panel")


if __name__ == "__main__":
    verify()
