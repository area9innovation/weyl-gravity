#!/usr/bin/env python3
"""Independent verifier for the spin-one Levelt first-panel certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def coefficient(matrix_value: sp.Matrix, order: int) -> sp.Matrix:
    return matrix_value.applyfunc(
        lambda value: clean(
            sp.limit(
                sp.diff(value, RHO, order) / sp.factorial(order),
                RHO,
                0,
            )
        )
    )


def row_bound(
    value: sp.Matrix, environment: dict[sp.Symbol, CI]
) -> sp.Rational:
    rows = []
    for row in range(value.rows):
        rows.append(
            sp.Rational(
                sum(
                    (
                        eval_rational_rect(value[row, col], environment)
                        .norm_one_hi()
                        for col in range(value.cols)
                    ),
                    Fraction(0),
                )
            )
        )
    return max(rows)


def verify() -> None:
    doc = json.loads(CERTIFICATE.read_text())
    if doc["status"] != (
        "CERTIFIED_SPIN_ONE_LEVELT_TAIL_AND_MIXED_FIRST_PANEL_PASS"
    ):
        raise RuntimeError("status drift")
    for item in doc["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {path}")
    crosswalk = json.loads(
        (ROOT / doc["imports"]["partial_jet_crosswalk"]["path"]).read_text()
    )
    blocks = crosswalk["exact_blocks"]
    a = matrix(blocks["A_RW"]).subs(R, 2 + RHO)
    e = matrix(blocks["E_RW_self_extension"]).subs(R, 2 + RHO)
    c = matrix(blocks["C_Lx_to_metric_RW"]).subs(R, 2 + RHO)
    d = matrix(blocks["D_Lx_to_carrier_RW"]).subs(R, 2 + RHO)
    ax = matrix(blocks["A_x"]).subs(R, 2 + RHO)
    spin_two = (a + sp.eye(2) / RHO).applyfunc(clean)
    levelt = sp.diag(RHO, RHO**2)
    spin_one = (
        levelt.diff(RHO) * levelt.inv()
        + levelt * ax * levelt.inv()
    ).applyfunc(clean)
    inv_levelt_source = sp.diag(1, 1 / RHO)
    d_regular = (d * inv_levelt_source).applyfunc(clean)
    c_regular = (c * inv_levelt_source).applyfunc(clean)
    base = sp.zeros(4)
    base[:2, :2] = spin_two
    base[:2, 2:4] = d_regular
    base[2:4, 2:4] = spin_one
    tangent = sp.zeros(4)
    tangent[:2, :2] = e
    tangent[:2, 2:4] = c_regular
    residue = (RHO * base).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    printed_residue = matrix(doc["levelt_frame"]["residue"])
    if (residue - printed_residue).applyfunc(clean) != sp.zeros(4):
        raise RuntimeError("Levelt residue mismatch")
    tangent_residue = (RHO * tangent).applyfunc(
        lambda value: clean(sp.limit(value, RHO, 0))
    )
    if tangent_residue != sp.zeros(4):
        raise RuntimeError("tangent residue is nonzero")
    selected = sp.Matrix(
        [parse(value) for value in doc["levelt_frame"]["selected_vector_Y_then_Z"]]
    )
    if (residue * selected).applyfunc(clean) != sp.zeros(4, 1):
        raise RuntimeError("selected Levelt line mismatch")

    recurrence = doc["resonant_recurrence"]
    f = [
        sp.Matrix([parse(value) for value in vector])
        for vector in recurrence["base_coefficients"]
    ]
    g = [
        sp.Matrix([parse(value) for value in vector])
        for vector in recurrence["tangent_coefficients"]
    ]
    order = doc["scope"]["frobenius_order"]
    regular_base = (base - residue / RHO).applyfunc(clean)
    base_coefficients = [
        coefficient(regular_base, n) for n in range(order)
    ]
    tangent_coefficients = [
        coefficient(tangent, n) for n in range(order)
    ]
    for n in range(1, order + 1):
        pivot = n * sp.eye(4) - residue
        rhs = sum(
            (
                base_coefficients[k] * f[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(4, 1),
        )
        tangent_rhs = sum(
            (
                base_coefficients[k] * g[n - 1 - k]
                + tangent_coefficients[k] * f[n - 1 - k]
                for k in range(n)
            ),
            sp.zeros(4, 1),
        )
        if (pivot * f[n] - rhs).applyfunc(clean) != sp.zeros(4, 1):
            raise RuntimeError(f"base recurrence mismatch at {n}")
        if (
            pivot * g[n] - tangent_rhs
        ).applyfunc(clean) != sp.zeros(4, 1):
            raise RuntimeError(f"tangent recurrence mismatch at {n}")
        if n == 1 and pivot.rank() != 3:
            raise RuntimeError("order-one resonance rank mismatch")
        if n >= 2 and clean(pivot.det()) == 0:
            raise RuntimeError(f"unexpected later resonance at {n}")
    if g[1] != sp.zeros(4, 1):
        raise RuntimeError("order-one tangent coefficient drift")

    frequency = CI(RI(Fraction(1, 2), Fraction(4097, 8192)))
    disk = {
        W: frequency,
        RHO: CI(
            RI(-Fraction(1, 2), Fraction(1, 2)),
            RI(-Fraction(1, 2), Fraction(1, 2)),
        ),
    }
    majorant_base = row_bound(regular_base, disk)
    majorant_tangent = row_bound(tangent, disk)
    tail = doc["all_order_tail_majorant"]
    if parse(tail["M_base"]) != majorant_base:
        raise RuntimeError("base Cauchy majorant mismatch")
    if parse(tail["M_tangent"]) != majorant_tangent:
        raise RuntimeError("tangent Cauchy majorant mismatch")
    for n in range(2, 13):
        inverse = (n * sp.eye(4) - residue).inv().applyfunc(clean)
        if clean(n * row_bound(inverse, {W: frequency})) > 3:
            raise RuntimeError(f"finite inverse bound failed at {n}")
    residue_bound = sp.Rational(6145, 1024)
    if clean(13 / (13 - residue_bound)) >= 3:
        raise RuntimeError("large-n inverse bound failed")
    p = clean(3 * majorant_base / 2)
    q = clean(3 * majorant_tangent / 2)
    x = sp.Rational(1, 2**21)
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
    if parse(tail["tail_base"]) != clean(first_base / (1 - ratio_base)):
        raise RuntimeError("base tail mismatch")
    if parse(tail["tail_tangent"]) != clean(
        first_tangent / (1 - ratio_tangent)
    ):
        raise RuntimeError("tangent tail mismatch")

    panel = doc["first_panel_transport"]
    for key in ("source", "compile_log", "run_log"):
        path = ROOT / panel[f"{key}_path"]
        if sha256(path) != panel[f"{key}_sha256"]:
            raise RuntimeError(f"{key} hash mismatch")
    parsed = panel["parsed_result"]
    if not (
        panel["passed"]
        and parsed["coefficient_equal"]
        and parsed["transport_overlap"]
        and parsed["seed_overlap"]
        and panel["compile_exit"] == 0
        and panel["run_exit"] == 0
    ):
        raise RuntimeError("mixed first-panel result failed")
    flags = doc["claim_flags"]
    for flag in (
        "multipanel_transport_certified",
        "K_H_computed",
        "endpoint_partial_jet_frame_constructed",
        "T_plus_recovered",
        "H4_pass_certified",
        "bounded_global_transport_certified",
    ):
        if flags[flag]:
            raise RuntimeError(f"fail-closed flag promoted: {flag}")
    print("PASS spin-one Levelt tail and mixed first panel")


if __name__ == "__main__":
    verify()
