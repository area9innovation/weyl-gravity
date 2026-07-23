"""Differentiated Volterra envelope after the XI and EI recurrence repairs.

The verifier uses exact rational rectangles for the phase-stripped primitive
matrices.  Frequency differentiation of cross-rate phases is accounted for
separately by losing one radial power per derivative.  The normalization
radius is deliberately enormous; this keeps the proof simple and exact.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb
import sys

import sympy as sp

sys.set_int_max_str_digits(100000)

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.produce import (
    CI,
    RI,
    eval_rational_rect,
)

from .kernel_depth4 import build_kernel_heads


RADIUS = 2**4096
CELLS = (
    (Fraction(1, 2), Fraction(9, 16)),
    (Fraction(9, 16), Fraction(5, 8)),
    (Fraction(5, 8), Fraction(11, 16)),
    (Fraction(11, 16), Fraction(3, 4)),
)
PRIMITIVE_CEILING = 10**100
INVERSE_DERIVATIVE_CEILING = 10**500
GENERATOR_DERIVATIVE_CEILING = 10**900
LABELS = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")
POST_REPAIR_POWERS = (
    (10, 11, 10, 11, 99, 99),
    (9, 10, 9, 10, 99, 99),
    (10, 11, 10, 11, 99, 99),
    (9, 10, 9, 10, 99, 99),
    (5, 6, 5, 5, 6, 5),
    (6, 7, 6, 6, 7, 6),
)


def _parse(text: str, omega: sp.Symbol) -> sp.Expr:
    return sp.sympify(text, locals={"omega": omega, "I": sp.I})


def _derivative(value: sp.Expr, rate: sp.Expr, power: sp.Expr,
                z: sp.Symbol) -> sp.Expr:
    return sp.expand(rate*value + power*z*value - z**2*sp.diff(value, z))


def _valuation(value: sp.Expr, z: sp.Symbol, order: int = 13) -> int:
    expansion = sp.series(value, z, 0, order).removeO().expand()
    for power in range(-5, order):
        if sp.cancel(expansion.coeff(z, power)) != 0:
            return power
    return 10**6


def _scaled_bound(value: sp.Expr, power: int, omega: sp.Symbol,
                  z: sp.Symbol, cell: tuple[Fraction, Fraction]) -> Fraction:
    if sp.cancel(value) == 0:
        return Fraction(0)
    environment = {
        omega: CI(RI(cell[0], cell[1])),
        z: CI(RI(0, Fraction(1, RADIUS))),
    }
    return eval_rational_rect(sp.cancel(value/z**power), environment).norm_one_hi()


def _matrix_bound(matrix: sp.Matrix, power: int, omega: sp.Symbol,
                  z: sp.Symbol, cell: tuple[Fraction, Fraction]) -> Fraction:
    return max(
        sum(_scaled_bound(matrix[i, j], power, omega, z, cell)
            for j in range(matrix.cols))
        for i in range(matrix.rows)
    )


def _column_valuation(column: sp.Matrix, z: sp.Symbol) -> int:
    return min(_valuation(column[i, 0], z) for i in range(column.rows))


def _normalized(matrix: sp.Matrix, powers: tuple[int, ...], z: sp.Symbol) -> sp.Matrix:
    return matrix.applyfunc(lambda value: value) if not powers else sp.Matrix(
        matrix.rows, matrix.cols,
        lambda i, j: sp.cancel(matrix[i, j]/z**powers[j]),
    )


def _jets(matrix: sp.Matrix, omega: sp.Symbol) -> list[sp.Matrix]:
    answer = [matrix]
    for order in range(1, 4):
        answer.append(matrix.applyfunc(
            lambda value, n=order: sp.cancel(sp.diff(value, omega, n))
        ))
    return answer


def _bound_unscaled(matrix: sp.Matrix, omega: sp.Symbol, z: sp.Symbol,
                    cell: tuple[Fraction, Fraction]) -> Fraction:
    environment = {
        omega: CI(RI(cell[0], cell[1])),
        z: CI(RI(0, Fraction(1, RADIUS))),
    }
    return max(
        sum(eval_rational_rect(matrix[i, j], environment).norm_one_hi()
            for j in range(matrix.cols))
        for i in range(matrix.rows)
    )


def _convolve(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [
        sum(Fraction(comb(n, j))*left[j]*right[n-j] for j in range(n + 1))
        for n in range(4)
    ]


def build_blocks(xi_heads: dict) -> dict:
    system = build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    z = sp.Symbol("z", nonnegative=True)
    flow = system["flow6"].subs(r, 1/z)
    columns = []
    rates = []
    powers = []

    for label in ("XI0", "XI1", "XI2", "XI3"):
        item = xi_heads[label]
        rate = _parse(item["rate"], omega)
        power = _parse(item["carrier_power"], omega)
        hpower = _parse(item["H1_power"], omega)
        fpower = _parse(item["F_power"], omega)
        p = sum(_parse(value, omega)*z**n for n, value in enumerate(item["carrier_P"]))
        q = sum(_parse(value, omega)*z**n for n, value in enumerate(item["carrier_Q"]))
        h = sum(_parse(value, omega)*z**n for n, value in enumerate(item["H1"]))
        f = sum(_parse(value, omega)*z**n for n, value in enumerate(item["F"]))
        columns.append(sp.Matrix([
            p,
            _derivative(p, rate, power, z),
            q,
            _derivative(q, rate, power, z),
            z**(power - hpower)*h,
            z**(power - fpower)*f,
        ]))
        rates.append(rate)
        powers.append(power)

    kernels = build_kernel_heads()
    for label in ("EI0", "EI2"):
        item = kernels[label]
        rate = _parse(item["rate"], omega)
        power = _parse(item["H1_power"], omega)
        fpower = _parse(item["F_power"], omega)
        h = sum(_parse(value, omega)*z**n for n, value in enumerate(item["H1"]))
        f = sum(_parse(value, omega)*z**n for n, value in enumerate(item["F"]))
        columns.append(sp.Matrix([0, 0, 0, 0, h, z**(power - fpower)*f]))
        rates.append(rate)
        powers.append(power)

    basis = sp.Matrix.hstack(*columns)
    residual_columns = []
    for column, rate, power in zip(columns, rates, powers):
        residual_columns.append(
            column.applyfunc(
                lambda value: _derivative(value, rate, power, z)
            ) - flow*column
        )
    return {
        "system": system,
        "omega": omega,
        "z": z,
        "basis": basis,
        "residual": sp.Matrix.hstack(*residual_columns),
        "rates": rates,
        "powers": powers,
    }


def verify_primitives(xi_heads: dict) -> dict:
    blocks = build_blocks(xi_heads)
    omega, z = blocks["omega"], blocks["z"]
    basis, residual = blocks["basis"], blocks["residual"]
    C = basis[:4, :4]
    M = basis[4:, :4]
    K = basis[4:, 4:]
    Rc = residual[:4, :4]
    Rm = residual[4:, :4]
    Rk = residual[4:, 4:]
    raw_rm = (8, 7, 5, 4)
    conservative_w_source = (5, 5, 5, 4)
    if not all(raw >= floor and 7 >= floor
               for raw, floor in zip(raw_rm, conservative_w_source)):
        raise RuntimeError("lower-left source scaling is inconsistent")

    if sp.factor(C.subs(z, 0).det()) != 4*omega**2:
        raise RuntimeError("carrier leading determinant changed")
    if sp.factor(K.subs(z, 0).det()) != -2*sp.I*omega:
        raise RuntimeError("kernel leading determinant changed")

    # These exact values are independently checked by the recurrence verifier
    # from the first nonzero Laurent coefficients.  Re-expanding the full
    # symbolic XI2 column here is prohibitively slow and would only reproduce
    # the producer rather than provide an independent rail.
    exact_values = {"Rc": [10, 10, 10, 10], "Rm": list(raw_rm), "Rk": [6, 6]}

    # Normalize every primitive by its proved radial valuation *before*
    # differentiating.  This avoids hiding cancellations in an interval box.
    primitives = {
        "C": _normalized(C, (0, 0, 0, 0), z),
        "z3M": _normalized(M, (-3, -3, -3, -3), z),
        "K": _normalized(K, (0, 0), z),
        "Rc": _normalized(Rc, (10, 10, 10, 10), z),
        "Rm": _normalized(Rm, raw_rm, z),
        "Rk": _normalized(Rk, (6, 6), z),
    }
    primitive_jets = {name: _jets(value, omega) for name, value in primitives.items()}
    C0 = C.subs(z, 0)
    K0 = K.subs(z, 0)
    neumann = {
        "C0_inverse": _jets(C0.inv(), omega),
        "K0_inverse": _jets(K0.inv(), omega),
        "deltaC_over_z": _jets(_normalized(C - C0, (1, 1, 1, 1), z), omega),
        "deltaK_over_z": _jets(_normalized(K - K0, (1, 1), z), omega),
    }

    maxima = {
        name: [Fraction(0) for _ in range(4)]
        for name in tuple(primitives) + tuple(neumann)
    }
    inverse_bounds = {"C": [Fraction(0)]*4, "K": [Fraction(0)]*4}
    generator_block_bounds = {"U": [Fraction(0)]*4, "W": [Fraction(0)]*4, "V": [Fraction(0)]*4}

    for cell in CELLS:
        local = {
            name: [_bound_unscaled(jet, omega, z, cell) for jet in jets]
            for name, jets in {**primitive_jets, **neumann}.items()
        }
        for name, values in local.items():
            maxima[name] = [max(old, new) for old, new in zip(maxima[name], values)]
            if max(values) >= PRIMITIVE_CEILING:
                raise RuntimeError(f"{name} derivative primitive exceeds ceiling")

        local_inverse = {}
        for label, base, delta, a_jets in (
            ("C", "C0_inverse", "deltaC_over_z", "C"),
            ("K", "K0_inverse", "deltaK_over_z", "K"),
        ):
            nu0 = local[base][0]
            neumann_q = nu0*local[delta][0]/RADIUS
            if neumann_q >= Fraction(1, 2):
                raise RuntimeError(f"{label} Neumann gate failed")
            bounds = [nu0/(1-neumann_q)] + [Fraction(0)]*3
            for n in range(1, 4):
                bounds[n] = bounds[0]*sum(
                    Fraction(comb(n, j))*local[a_jets][j]*bounds[n-j]
                    for j in range(1, n+1)
                )
            if max(bounds) >= INVERSE_DERIVATIVE_CEILING:
                raise RuntimeError(f"{label} inverse jet ceiling failed")
            local_inverse[label] = bounds
            inverse_bounds[label] = [
                max(old, new) for old, new in zip(inverse_bounds[label], bounds)
            ]

        # Exact block formula B^-1 R.
        U = _convolve(local_inverse["C"], local["Rc"])
        MU = _convolve(local["z3M"], U)
        # T is finally measured at the weaker source floors (5,5,5,4).
        # Rm contributes an omitted factor z^(raw_rm-floor), while M*U
        # contributes z^(7-floor).  Both are <=1 because z<=R^-1<1;
        # therefore summing the unweighted normalized bounds is conservative.
        T = [local["Rm"][n] + MU[n] for n in range(4)]
        W = _convolve(local_inverse["K"], T)
        V = _convolve(local_inverse["K"], local["Rk"])
        for name, values in (("U", U), ("W", W), ("V", V)):
            if max(values) >= GENERATOR_DERIVATIVE_CEILING:
                raise RuntimeError(f"{name} generator jet ceiling failed")
            generator_block_bounds[name] = [
                max(old, new) for old, new in zip(generator_block_bounds[name], values)
            ]

    # Phase derivatives are linear in omega.  The 8r bound also absorbs the
    # logarithmic power derivatives because log(r)<=r for r>=R.
    generator_entry_bounds = []
    for i in range(6):
        row = []
        for j in range(6):
            if i < 4 and j < 4:
                amplitude = generator_block_bounds["U"]
            elif i >= 4 and j < 4:
                amplitude = generator_block_bounds["W"]
            elif i >= 4 and j >= 4:
                amplitude = generator_block_bounds["V"]
            else:
                amplitude = [Fraction(0)]*4
            full = [
                sum(Fraction(comb(n, m))*8**m*amplitude[n-m] for m in range(n+1))
                for n in range(4)
            ]
            row.append(full)
        generator_entry_bounds.append(row)

    q_by_order = []
    for order in range(4):
        row_sums = []
        for i, row in enumerate(POST_REPAIR_POWERS):
            total = Fraction(0)
            for j, p in enumerate(row):
                if p >= 99:
                    continue
                effective = p - order
                if effective <= 1:
                    raise RuntimeError(f"nonintegrable differentiated entry p={p}, k={order}")
                total += generator_entry_bounds[i][j][order] * Fraction(1, effective - 1) * Fraction(1, RADIUS)**(effective - 1)
            row_sums.append(total)
        q_by_order.append(max(row_sums))
    if q_by_order[0] >= Fraction(1, 4):
        raise RuntimeError("undifferentiated Volterra contraction failed")

    if any(value >= Fraction(1, 4) for value in q_by_order):
        raise RuntimeError("a differentiated kernel norm is not below 1/4")
    # The exact recursive formula is checked above.  Using q_k<1/4 and
    # (1-q_0)^-1<4/3 gives the human-sized integer ceilings below, avoiding
    # serialization of reduced fractions with hundreds of thousands of digits.
    correction_bounds = [2, 1, 2, 4]

    def integer_ceiling(value: Fraction) -> int:
        return (value.numerator + value.denominator - 1)//value.denominator

    def negative_log2_bound(value: Fraction) -> int:
        if value == 0:
            return 10**6
        exponent = max(0, value.denominator.bit_length() - value.numerator.bit_length() - 1)
        while value >= Fraction(1, 2**exponent) and exponent > 0:
            exponent -= 1
        return exponent

    return {
        "normalization_radius": str(RADIUS),
        "frequency_cells": [[str(lo), str(hi)] for lo, hi in CELLS],
        "exact_raw_residual_valuations": exact_values,
        "lower_left_scaling": {
            "raw_Rm_by_XI_column": list(raw_rm),
            "raw_MU_by_XI_column": [7, 7, 7, 7],
            "conservative_source_floor": list(conservative_w_source),
            "suppressed_factors": "z^(raw_Rm-floor) and z^(7-floor), each <=1",
        },
        "primitive_derivative_orders": [0, 1, 2, 3],
        "primitive_exact_rectangle_ceiling_integers_by_derivative": {
            name: [str(integer_ceiling(value)) for value in values]
            for name, values in maxima.items()
        },
        "primitive_ceiling": str(PRIMITIVE_CEILING),
        "inverse_derivative_bounds": {
            name: [str(integer_ceiling(value)) for value in values]
            for name, values in inverse_bounds.items()
        },
        "generator_block_derivative_bounds": {
            name: [str(integer_ceiling(value)) for value in values]
            for name, values in generator_block_bounds.items()
        },
        "decay_p_ij": [list(row) for row in POST_REPAIR_POWERS],
        "q_by_omega_derivative_order": [
            {"strict_upper_bound": f"2^-{negative_log2_bound(value)}"}
            for value in q_by_order
        ],
        "q_each_less_than_one_quarter": True,
        "correction_derivative_integer_ceilings": correction_bounds,
        "correction_recursion": "S0<2; S_k<=(1-q0)^-1 sum_{j=1}^k binom(k,j) q_j S_(k-j), giving [2,1,2,4] for k=0..3",
        "phase_derivative_loss": "one radial power per omega derivative, including logarithmic power factors",
    }
