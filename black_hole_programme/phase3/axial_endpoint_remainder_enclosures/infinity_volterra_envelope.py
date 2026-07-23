"""Uniform real-frequency Volterra envelope for the axial infinity heads.

The proof is intentionally coarse.  It uses exact valuations plus rational
rectangle bounds at a very large normalization radius.  This is sufficient
to prove integrability and contraction; it is not global radial matching.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
    kernel_endpoint_data,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_metric_heads import (
    _parse,
    build_data as build_head_data,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    CI,
    RI,
    eval_rational_rect,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "infinity-volterra-envelope.json"
I = sp.I
RADIUS = 2**256
PRIMITIVE_LIMIT = 10**20
U_CONSTANT = 10**25
V_CONSTANT = 10**50
W_CONSTANT = 10**25
CELLS = (
    (Fraction(1, 2), Fraction(9, 16)),
    (Fraction(9, 16), Fraction(5, 8)),
    (Fraction(5, 8), Fraction(11, 16)),
    (Fraction(11, 16), Fraction(3, 4)),
)
LABELS = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")


class VolterraError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VolterraError(message)


def derivative(series: sp.Expr, rate: sp.Expr, power: sp.Expr, z: sp.Symbol) -> sp.Expr:
    return sp.expand(rate*series + power*z*series - z**2*sp.diff(series, z))


def exact_blocks(selected: str | None = None) -> dict:
    heads = build_head_data()
    system = build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    z = sp.Symbol("z", nonnegative=True)
    columns = []
    rates = []
    powers = []

    for label, branch in heads["branches"].items():
        if selected is not None and selected != label:
            continue
        rate = _parse(branch["rate"], omega)
        power = _parse(branch["carrier_power"], omega)
        pq = [[_parse(value, omega) for value in pair]
              for pair in branch["carrier_coefficients_PQ_used_by_H0_check"]]
        p_series = sum(pair[0]*z**n for n, pair in enumerate(pq))
        q_series = sum(pair[1]*z**n for n, pair in enumerate(pq))
        h_power = _parse(branch["H1"]["power"], omega)
        f_power = _parse(branch["F_equals_dH1_dr"]["power"], omega)
        h_series = sum(
            _parse(value, omega)*z**n for n, value in enumerate(
                branch["H1"]["coefficients_through_inverse_order_3"]
            )
        )
        f_series = sum(
            _parse(value, omega)*z**n for n, value in enumerate(
                branch["F_equals_dH1_dr"]["coefficients_through_inverse_order_3"]
            )
        )
        column = sp.Matrix([
            p_series,
            derivative(p_series, rate, power, z),
            q_series,
            derivative(q_series, rate, power, z),
            z**(power - h_power)*h_series,
            z**(power - f_power)*f_series,
        ])
        columns.append((label, column))
        rates.append(rate)
        powers.append(power)

    if selected is None:
        kernel = kernel_endpoint_data(system)["infinity"]
        for label in ("EI0", "EI2"):
            item = kernel[label]
            rate = _parse(item["rate"], omega)
            power = _parse(item["H1_power"], omega)
            h_series = sum(
                _parse(value, omega)*z**n
                for n, value in enumerate(item["H1_head"])
            )
            column = sp.Matrix([
                0, 0, 0, 0,
                h_series,
                derivative(h_series, rate, power, z),
            ])
            columns.append((label, column))
            rates.append(rate)
            powers.append(power)

    return {
        "system": system,
        "r": r,
        "omega": omega,
        "z": z,
        "columns": columns,
        "rates": rates,
        "powers": powers,
    }


def valuation(expr: sp.Expr, z: sp.Symbol) -> int:
    expr = sp.cancel(expr)
    if expr == 0:
        return 10**6
    numerator, denominator = sp.fraction(expr)
    numerator_poly = sp.Poly(numerator, z)
    denominator_poly = sp.Poly(denominator, z)
    return (
        min(monomial[0] for monomial, _ in numerator_poly.terms())
        - min(monomial[0] for monomial, _ in denominator_poly.terms())
    )


def scaled_bound(expr: sp.Expr, power: int, omega: sp.Symbol, z: sp.Symbol,
                 cell: tuple[Fraction, Fraction]) -> Fraction:
    if sp.cancel(expr) == 0:
        return Fraction(0)
    actual = valuation(expr, z)
    require(actual >= power, f"valuation {actual} is below declared {power}")
    scaled = sp.cancel(expr/z**power)
    environment = {
        omega: CI(RI(cell[0], cell[1])),
        z: CI(RI(0, Fraction(1, RADIUS))),
    }
    return eval_rational_rect(scaled, environment).norm_one_hi()


def matrix_bound(matrix: sp.Matrix, power: int, omega: sp.Symbol, z: sp.Symbol,
                 cell: tuple[Fraction, Fraction]) -> Fraction:
    return max(
        sum(scaled_bound(matrix[i, j], power, omega, z, cell)
            for j in range(matrix.cols))
        for i in range(matrix.rows)
    )


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def ci_box(value: CI) -> dict:
    return {
        "re": [fraction_text(value.re.lo), fraction_text(value.re.hi)],
        "im": [fraction_text(value.im.lo), fraction_text(value.im.hi)],
    }


def normalized_initializer_boxes() -> list[dict]:
    blocks = exact_blocks()
    omega, z = blocks["omega"], blocks["z"]
    basis = sp.Matrix.hstack(*(column for _, column in blocks["columns"]))
    basis_prime = sp.Matrix.hstack(*(
        column.applyfunc(lambda value: -z**2*sp.diff(value, z))
        + (rate + power*z)*column
        for (_, column), rate, power in zip(
            blocks["columns"], blocks["rates"], blocks["powers"]
        )
    ))
    output = []
    for lo, hi in CELLS:
        environment = {
            omega: CI(RI(lo, hi)),
            z: CI(Fraction(1, RADIUS)),
        }
        output.append({
            "omega_cell": [fraction_text(lo), fraction_text(hi)],
            "F_N_at_R": [
                [ci_box(eval_rational_rect(basis[i, j], environment))
                 for j in range(6)] for i in range(6)
            ],
            "F_N_prime_at_R": [
                [ci_box(eval_rational_rect(basis_prime[i, j], environment))
                 for j in range(6)] for i in range(6)
            ],
        })
    return output


def decay_tables() -> tuple[list[list[int]], list[list[int]], Fraction]:
    carrier_powers = (0, -1, 0, -1)
    kernel_powers = (0, 1)
    powers = [[99 for _ in range(6)] for _ in range(6)]
    constants = [[0 for _ in range(6)] for _ in range(6)]

    for i in range(4):
        for j in range(4):
            powers[i][j] = 6 + carrier_powers[i] - carrier_powers[j]
            constants[i][j] = U_CONSTANT
    # Appending the derivative-forced F4 terms to XI2/XI3 raises their raw
    # lower-block residual valuations from (2,1) to (3,2).  Hence every
    # cross-rate entry has p>=3 and its z-flow amplitude vanishes at z=0.
    raw_bottom = (3, 3, 3, 2)
    for i in range(2):
        for j in range(4):
            powers[i + 4][j] = raw_bottom[j] + kernel_powers[i] - carrier_powers[j]
            constants[i + 4][j] = V_CONSTANT
        for j in range(2):
            powers[i + 4][j + 4] = 5 + kernel_powers[i] - kernel_powers[j]
            constants[i + 4][j + 4] = W_CONSTANT

    row_q = []
    for i in range(6):
        total = Fraction(0)
        for j in range(6):
            if constants[i][j] == 0:
                continue
            p = powers[i][j]
            require(p > 1, f"nonintegrable Volterra entry {i},{j}: p={p}")
            total += Fraction(constants[i][j], p - 1) * Fraction(1, RADIUS)**(p - 1)
        row_q.append(total)
    return powers, constants, max(row_q)


def build_data() -> dict:
    powers, constants, q = decay_tables()
    require(q < Fraction(1, 4), "Volterra contraction is not below 1/4")
    return {
        "schema": "phase3-axial-infinity-volterra-envelope-v1",
        "scope": {
            "background": "Schwarzschild M=1 in ingoing EF coordinates",
            "sector": "axial ell=2",
            "frequency": "real omega in [1/2,3/4] on four rational cells",
            "normalization_radius_R": str(RADIUS),
            "basis_normalization": (
                "each scalar phase is exp(a*(r-R))*(r/R)^power, hence equals one at R"
            ),
        },
        "block_factorization": {
            "G": "[[C,0],[M,K]]",
            "inverse": "[[C^-1,0],[-K^-1*M*C^-1,K^-1]]",
            "weighted_carrier": "C_weighted=diag(z,z,z,z^2)*C",
            "determinant_identity": "det(C_weighted)=z^5*D(z,omega)",
            "D_at_zero": "4*omega**2",
            "interpretation": (
                "the z^5 determinant is compensated by the row weights; the "
                "unweighted C(0) is invertible and is bounded by a Neumann inverse"
            ),
        },
        "primitive_majorants": {
            "declared_common_ceiling": str(PRIMITIVE_LIMIT),
            "C_inverse_ceiling": "200",
            "K_inverse_ceiling": "200",
            "scaled_M_ceiling_for_z^3_M": str(PRIMITIVE_LIMIT),
            "scaled_Rc_ceiling_for_z^6_Rc": str(PRIMITIVE_LIMIT),
            "scaled_Rm_powers_by_column": [4, 4, 3, 2],
            "scaled_Rm_ceiling": str(PRIMITIVE_LIMIT),
            "scaled_Rk_ceiling_for_z^5_Rk": str(PRIMITIVE_LIMIT),
        },
        "volterra_kernel": {
            "labels": list(LABELS),
            "decay_p_ij": powers,
            "constant_C_ij": [[str(value) for value in row] for row in constants],
            "bound": "abs(K_N,ij(r)) <= C_ij*r^(-p_ij), r>=R",
            "q_infinity": fraction_text(q),
            "q_less_than_one_quarter": True,
            "correction_bound_q_over_one_minus_q": fraction_text(q/(1 - q)),
            "z_flow_continuity": {
                "transformation": "dZ/dz=-r^2*K_N*Z",
                "cross_rate_minimum_p": 3,
                "cross_rate_amplitude": "z^(p-2) tends to zero at z=0",
                "continuous_endpoint_callback": True,
            },
        },
        "initializer": {
            "columns": list(LABELS),
            "frequency_cells": normalized_initializer_boxes(),
        },
        "claim": {
            "statement": (
                "The phase-normalized six-column formal infinity basis has an "
                "omega-uniform integrable Volterra residual and a contraction "
                "constant below 1/4 on the declared real-frequency interval."
            ),
            "does_not_establish": [
                "horizon-to-infinity matching",
                "Lee-Wald flux conservation",
                "physical scattering channels",
                "complex-frequency pole exclusion",
                "PDE scattering or stability",
            ],
        },
    }


def verify_structure() -> None:
    blocks = exact_blocks()
    omega, z = blocks["omega"], blocks["z"]
    basis = sp.Matrix.hstack(*(column for _, column in blocks["columns"]))
    C = basis[:4, :4]
    K = basis[4:, 4:]
    require(sp.factor(C.subs(z, 0).det()) == 4*omega**2,
            "carrier D(0) changed")
    require(sp.factor(K.subs(z, 0).det()) == -2*I*omega,
            "kernel determinant changed")
    # det(diag(z,z,z,z^2))=z^5 proves the printed weighted identity.
    weights = sp.diag(z, z, z, z**2)
    require(sp.factor(weights.det()) == z**5, "carrier row weights changed")
    for cell in CELLS:
        environment = {omega: CI(RI(cell[0], cell[1])), z: CI(RI(0, Fraction(1, RADIUS)))}
        c0_inverse = C.subs(z, 0).inv()
        k0_inverse = K.subs(z, 0).inv()
        c0_bound = matrix_bound(c0_inverse, 0, omega, z, cell)
        k0_bound = matrix_bound(k0_inverse, 0, omega, z, cell)
        require(c0_bound < 100 and k0_bound < 100, "leading inverse ceiling failed")
        delta_c = matrix_bound(C - C.subs(z, 0), 1, omega, z, cell)
        delta_k = matrix_bound(K - K.subs(z, 0), 1, omega, z, cell)
        require(c0_bound*delta_c/RADIUS < Fraction(1, 2), "carrier Neumann gate failed")
        require(k0_bound*delta_k/RADIUS < Fraction(1, 2), "kernel Neumann gate failed")
        M = basis[4:, :4]
        require(matrix_bound(M, -3, omega, z, cell) < PRIMITIVE_LIMIT,
                "z^3 M ceiling failed")


def verify_carrier(label: str) -> None:
    blocks = exact_blocks(label)
    system, r = blocks["system"], blocks["r"]
    omega, z = blocks["omega"], blocks["z"]
    _, column = blocks["columns"][0]
    rate, power = blocks["rates"][0], blocks["powers"][0]
    top = column[:4, :]
    bottom = column[4:, :]
    carrier_flow = system["carrier"].subs(r, 1/z)
    full_flow = system["flow6"].subs(r, 1/z)
    rc = top.applyfunc(lambda value: -z**2*sp.diff(value, z)) + (rate + power*z)*top - carrier_flow*top
    rm = bottom.applyfunc(lambda value: -z**2*sp.diff(value, z)) + (rate + power*z)*bottom - full_flow[4:, :]*column
    rm_power = {"XI0": 4, "XI1": 4, "XI2": 3, "XI3": 2}[label]
    for cell in CELLS:
        require(matrix_bound(rc, 6, omega, z, cell) < PRIMITIVE_LIMIT,
                f"{label} z^-6 Rc ceiling failed")
        require(matrix_bound(rm, rm_power, omega, z, cell) < PRIMITIVE_LIMIT,
                f"{label} scaled Rm ceiling failed")


def verify_kernel(label: str) -> None:
    blocks = exact_blocks()
    system, r = blocks["system"], blocks["r"]
    omega, z = blocks["omega"], blocks["z"]
    index = LABELS.index(label)
    _, column = blocks["columns"][index]
    rate, power = blocks["rates"][index], blocks["powers"][index]
    bottom = column[4:, :]
    flow = system["flow6"].subs(r, 1/z)
    residual = bottom.applyfunc(lambda value: -z**2*sp.diff(value, z)) + (rate + power*z)*bottom - flow[4:, :]*column
    for cell in CELLS:
        require(matrix_bound(residual, 5, omega, z, cell) < PRIMITIVE_LIMIT,
                f"{label} z^-5 Rk ceiling failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-group", choices=("structure",) + LABELS)
    parser.add_argument("--verify-sequence-index", type=int)
    args = parser.parse_args()

    groups = ("structure",) + LABELS
    if args.verify_sequence_index is not None:
        require(0 <= args.verify_sequence_index < len(groups), "invalid sequence index")
        group = groups[args.verify_sequence_index]
        if group == "structure":
            verify_structure()
        elif group.startswith("XI"):
            verify_carrier(group)
        else:
            verify_kernel(group)
        print("PASS infinity Volterra group", group, flush=True)
        next_index = args.verify_sequence_index + 1
        if next_index < len(groups):
            os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()),
                                      "--verify-sequence-index", str(next_index)])
        data = build_data()
        encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
        require(OUTPUT.exists() and OUTPUT.read_text() == encoded, "Volterra JSON drift")
        print("PASS complete infinity Volterra envelope")
        return

    if args.verify_group:
        if args.verify_group == "structure":
            verify_structure()
        elif args.verify_group.startswith("XI"):
            verify_carrier(args.verify_group)
        else:
            verify_kernel(args.verify_group)
        print("PASS infinity Volterra group", args.verify_group)
        return

    data = build_data()
    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(OUTPUT.exists() and OUTPUT.read_text() == encoded, "Volterra JSON drift")
        print("PASS infinity Volterra JSON reproduces")
    else:
        OUTPUT.write_text(encoded)
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
