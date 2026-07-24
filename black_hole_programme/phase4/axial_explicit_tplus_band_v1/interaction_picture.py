#!/usr/bin/env python3
"""Exact and point-fixture support for the outgoing interaction picture.

The exact layer uses SymPy rationals.  The physical point fixture uses the
same reduced four-state coefficient functions as the pinned Forge rail, but
is deliberately only a high-precision consistency check: the interval
successor is produced separately by the Forge implementation.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Callable

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = HERE / "checkpoint.json"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def _matrix(values: list[list[int]]) -> sp.Matrix:
    return sp.Matrix(values)


def exact_fixture() -> dict:
    """Return an exact rational witness for every interaction identity."""

    A = _matrix([[1, 2], [-1, 3]])
    E = _matrix([[2, -1], [4, 1]])
    D = _matrix([[1, 3], [2, -2]])
    C = _matrix([[-2, 1], [5, 2]])
    Ax = _matrix([[0, 1], [-3, 2]])
    P = _matrix([[2, 1], [1, 1]])
    R = _matrix([[1, 2], [3, 7]])
    Q = _matrix([[1, -1], [2, 3]])
    dotP = _matrix([[3, 1], [-2, 4]])
    dotQ = _matrix([[2, 5], [1, -3]])

    Pp = A * P
    Rp = Ax * R
    dotPp = E * P + A * dotP
    Qp = A * Q + D * R
    dotQp = E * Q + A * dotQ + C * R

    Pinv = P.inv()
    J = Pinv * dotP
    K = Pinv * Q
    dotK = Pinv * dotQ - J * K

    Pinvp = -Pinv * Pp * Pinv
    Jp = Pinvp * dotP + Pinv * dotPp
    Kp = Pinvp * Q + Pinv * Qp
    dotKp = (
        Pinvp * dotQ
        + Pinv * dotQp
        - Jp * K
        - J * Kp
    )

    expected_Jp = Pinv * E * P
    expected_Kp = Pinv * D * R
    expected_dotKp = Pinv * C * R - J * Pinv * D * R

    zero = sp.zeros(2)
    F6 = sp.diag(P, P, R) * sp.Matrix.vstack(
        sp.Matrix.hstack(sp.eye(2), J, J * K + dotK),
        sp.Matrix.hstack(zero, sp.eye(2), K),
        sp.Matrix.hstack(zero, zero, sp.eye(2)),
    )
    expected_F6 = sp.Matrix.vstack(
        sp.Matrix.hstack(P, dotP, dotQ),
        sp.Matrix.hstack(zero, P, Q),
        sp.Matrix.hstack(zero, zero, R),
    )

    # A rational chart-transition fixture; logarithms are represented by
    # their multiplicative amplitudes z=exp(lambda), avoiding branch choices.
    q = sp.Rational(3, 2)
    q_tau = sp.Rational(-5, 7)
    z = sp.Rational(11, 5)
    z_tau = sp.Rational(13, 17) * z
    p = 1 / q
    p_tau = -q_tau / q**2
    z2 = z * q
    z2_tau = z_tau * q + z * q_tau
    y_q = sp.Matrix([z, z * q])
    dy_q = sp.Matrix([z_tau, z_tau * q + z * q_tau])
    y_p = sp.Matrix([z2 * p, z2])
    dy_p = sp.Matrix(
        [z2_tau * p + z2 * p_tau, z2_tau]
    )

    def encode_matrix(value: sp.Matrix) -> list[list[str]]:
        return [
            [str(value[i, j]) for j in range(value.cols)]
            for i in range(value.rows)
        ]

    residuals = {
        "J_prime": Jp - expected_Jp,
        "K_prime": Kp - expected_Kp,
        "dotK_prime": dotKp - expected_dotKp,
        "six_state_reconstruction": F6 - expected_F6,
        "chart_base": y_q - y_p,
        "chart_tangent": dy_q - dy_p,
    }
    return {
        "inputs": {
            name: encode_matrix(value)
            for name, value in {
                "A": A,
                "E": E,
                "D": D,
                "C": C,
                "Ax": Ax,
                "P": P,
                "R": R,
                "Q": Q,
                "dotP": dotP,
                "dotQ": dotQ,
            }.items()
        },
        "derived": {
            name: encode_matrix(value)
            for name, value in {
                "J": J,
                "K": K,
                "dotK": dotK,
                "F6": F6,
            }.items()
        },
        "chart_fixture": {
            "q": str(q),
            "q_tau": str(q_tau),
            "z": str(z),
            "z_tau": str(z_tau),
            "p": str(p),
            "p_tau": str(p_tau),
            "z2": str(z2),
            "z2_tau": str(z2_tau),
        },
        "residuals": {
            name: encode_matrix(value) for name, value in residuals.items()
        },
        "all_zero": all(value == sp.zeros(*value.shape) for value in residuals.values()),
    }


def _coefficient_functions(r: float, w: float) -> tuple[np.ndarray, np.ndarray]:
    """Complex 4x4 base/tangent generators from the pinned Forge formulas."""

    t: dict[int, float] = {}
    t[0] = 1.0 / r
    t[1] = 2.0 * t[0]
    t[2] = w * t[1] * (r + 2.0)
    t[3] = -t[2]
    t[4] = r**2
    t[5] = 1.0 / t[4]
    t[6] = r - 2.0
    t[7] = 1.0 / t[6]
    t[8] = 6.0 * t[5] * t[7] * (r - 1.0)
    t[9] = t[0] * t[7]
    t[10] = t[9] * (r - 4.0)
    t[11] = 8.0 * w * t[9]
    t[12] = 1.0 / t[6] ** 2
    t[13] = -t[1] * t[12]
    t[14] = -t[9] * (5.0 * r - 4.0)
    t[15] = 3.0 * r
    t[16] = 2.0 * w * t[12] * (3.0 * r - 4.0)
    t[17] = -t[11]
    t[18] = -t[16]
    t[19] = 3.0 * r - 2.0
    t[20] = t[0] * t[19]
    t[21] = w**2
    t[22] = t[21] * t[4]
    t[23] = 1.0 / (t[22] + 4.0) ** 2
    t[24] = (t[22] + 8.0) * t[23] / 512.0
    t[25] = -t[20] * t[24]
    t[26] = r**3
    t[27] = t[21] * t[26]
    t[28] = w**4
    t[29] = r**5 * t[28]
    t[30] = t[23] / 2048.0
    t[31] = -t[30] * (
        32.0 * r - 8.0 * t[22] - 8.0 * t[27] - 3.0 * t[29] - 64.0
    )
    t[32] = t[23] / 4096.0
    t[33] = t[32] * (
        3.0 * r**6 * t[28]
        + 160.0 * r
        + 16.0 * t[27]
        - 16.0 * t[22]
        - 4.0 * t[29]
        - 48.0 * t[4]
        - 128.0
    )
    t[34] = -r * t[33]
    t[35] = t[32] * t[6]
    t[36] = -t[35] * (16.0 * r - 4.0 * t[27] - t[29] - 32.0)
    t[37] = -t[36] * t[4]
    t[38] = w * t[30]
    t[39] = t[38] * (3.0 * t[22] + 20.0)
    t[40] = t[19] * t[39]
    t[41] = -t[40]
    t[42] = 6.0 * t[22]
    t[43] = t[38] * (44.0 * r + 9.0 * t[27] - t[42] - 40.0)
    t[44] = r * t[43]
    t[45] = -t[44]
    t[46] = t[38] * (
        6.0 * r**4 * t[21]
        - 60.0 * r
        - 13.0 * t[27]
        + 24.0 * t[4]
        + t[42]
        + 40.0
    )
    t[47] = t[4] * t[46]
    t[48] = w * t[35] * (20.0 * r - 2.0 * t[22] + 3.0 * t[27] - 24.0)
    t[49] = t[26] * t[48]
    t[50] = t[19] * t[24] * t[5]
    t[51] = -t[0] * t[31]
    t[52] = r * t[36]
    t[53] = t[20] * t[39]
    t[54] = r * t[46]
    t[55] = -t[54]
    t[56] = t[4] * t[48]
    t[57] = -t[56]
    t[58] = -t[47]
    t[59] = -t[49]
    t[60] = -t[53]
    t[61] = -t[43]

    base = np.zeros((8, 8), dtype=float)
    tangent = np.zeros((8, 8), dtype=float)

    def put(target: np.ndarray, row: int, col: int, value: float) -> None:
        target[row, col] = value

    for row, col, index in (
        (0, 0, 0), (0, 4, 3), (1, 0, 8), (1, 1, 10), (1, 5, 11),
        (2, 2, 0), (2, 6, 3), (3, 2, 13), (3, 3, 14), (3, 6, 16),
        (3, 7, 11), (4, 0, 2), (4, 4, 0), (5, 1, 17), (5, 4, 8),
        (5, 5, 10), (6, 2, 2), (6, 6, 0), (7, 2, 18), (7, 3, 17),
        (7, 6, 13), (7, 7, 14),
    ):
        put(base, row, col, t[index])
    for row, col in ((0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)):
        put(base, row, col, 1.0)

    for row, col, index in (
        (0, 0, 25), (0, 1, 31), (0, 2, 34), (0, 3, 37),
        (0, 4, 41), (0, 5, 45), (0, 6, 47), (0, 7, 49),
        (1, 0, 50), (1, 1, 51), (1, 2, 33), (1, 3, 52),
        (1, 4, 53), (1, 5, 43), (1, 6, 55), (1, 7, 57),
        (4, 0, 40), (4, 1, 44), (4, 2, 58), (4, 3, 59),
        (4, 4, 25), (4, 5, 31), (4, 6, 34), (4, 7, 37),
        (5, 0, 60), (5, 1, 61), (5, 2, 54), (5, 3, 56),
        (5, 4, 50), (5, 5, 51), (5, 6, 33), (5, 7, 52),
    ):
        put(tangent, row, col, t[index])

    # Realification is [[Re G,-Im G],[Im G,Re G]].
    if not np.allclose(base[4:, :4], -base[:4, 4:]) or not np.allclose(
        base[4:, 4:], base[:4, :4]
    ):
        raise RuntimeError("base realification structure drift")
    if not np.allclose(tangent[4:, :4], -tangent[:4, 4:]) or not np.allclose(
        tangent[4:, 4:], tangent[:4, :4]
    ):
        raise RuntimeError("tangent realification structure drift")
    return base[:4, :4] - 1j * base[:4, 4:], tangent[:4, :4] - 1j * tangent[:4, 4:]


def _central_complex_columns(name: str) -> np.ndarray:
    document = json.loads(PREDECESSOR.read_text())
    c0 = document["payload"][name]["coefficients"][0]
    real = np.array(
        [[float(Fraction(entry)) for entry in row] for row in c0],
        dtype=float,
    )
    return real[:4, :] + 1j * real[4:, :]


def _solve(
    rhs: Callable[[float, np.ndarray], np.ndarray],
    interval: tuple[float, float],
    initial: np.ndarray,
) -> np.ndarray:
    result = solve_ivp(
        rhs,
        interval,
        initial,
        method="DOP853",
        rtol=2.0e-13,
        atol=2.0e-14,
    )
    if not result.success:
        raise RuntimeError(result.message)
    return result.y[:, -1]


def _line_rhs(
    w: float,
    block: str,
    chart: str,
    tangent: bool,
) -> Callable[[float, np.ndarray], np.ndarray]:
    def rhs(r: float, state: np.ndarray) -> np.ndarray:
        base, variation = _coefficient_functions(r, w)
        offset = 0 if block == "spin2" else 2
        A = base[offset : offset + 2, offset : offset + 2]
        E = (
            variation[offset : offset + 2, offset : offset + 2]
            if tangent
            else np.zeros((2, 2), dtype=complex)
        )
        a, b, c, d = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
        at, bt, ct, dt = E[0, 0], E[0, 1], E[1, 0], E[1, 1]
        x, logamp = state[0], state[1]
        if chart == "q":
            xp = c + (d - a) * x - b * x * x
            lp = a + b * x
            if tangent:
                xt, lt = state[2], state[3]
                xtp = (
                    ct
                    + (dt - at) * x
                    - bt * x * x
                    + ((d - a) - 2.0 * b * x) * xt
                )
                ltp = at + bt * x + b * xt
                return np.array([xp, lp, xtp, ltp], dtype=complex)
        else:
            xp = b + (a - d) * x - c * x * x
            lp = c * x + d
            if tangent:
                xt, lt = state[2], state[3]
                xtp = (
                    bt
                    + (at - dt) * x
                    - ct * x * x
                    + ((a - d) - 2.0 * c * x) * xt
                )
                ltp = ct * x + c * xt + dt
                return np.array([xp, lp, xtp, ltp], dtype=complex)
        return np.array([xp, lp], dtype=complex)

    return rhs


def _reconstruct_line(state: np.ndarray, chart: str, tangent: bool) -> tuple[np.ndarray, np.ndarray | None]:
    x, logamp = state[0], state[1]
    amp = np.exp(logamp)
    if chart == "q":
        base = amp * np.array([1.0, x], dtype=complex)
        if tangent:
            xt, lt = state[2], state[3]
            derivative = amp * np.array([lt, lt * x + xt], dtype=complex)
        else:
            derivative = None
    else:
        base = amp * np.array([x, 1.0], dtype=complex)
        if tangent:
            xt, lt = state[2], state[3]
            derivative = amp * np.array([xt + lt * x, lt], dtype=complex)
        else:
            derivative = None
    return base, derivative


def physical_point_fixture() -> dict:
    """Compare direct, interaction and projective transports on the new panel."""

    r0 = float(Fraction(487, 16))
    r1 = float(Fraction(3895, 128))
    rm = 0.5 * (r0 + r1)
    w = float(Fraction(8193, 16384))
    base0 = _central_complex_columns("base")
    tangent0 = _central_complex_columns("tangent")

    def direct_rhs(r: float, state: np.ndarray) -> np.ndarray:
        G, Gt = _coefficient_functions(r, w)
        base = state[:8].reshape((4, 2))
        tangent = state[8:].reshape((4, 2))
        return np.concatenate(
            ((G @ base).reshape(-1), (G @ tangent + Gt @ base).reshape(-1))
        )

    direct_initial = np.concatenate((base0.reshape(-1), tangent0.reshape(-1)))
    direct_final = _solve(direct_rhs, (r0, r1), direct_initial)
    direct_base = direct_final[:8].reshape((4, 2))
    direct_tangent = direct_final[8:].reshape((4, 2))

    def interaction_rhs(r: float, state: np.ndarray) -> np.ndarray:
        G, Gt = _coefficient_functions(r, w)
        A, D, Ax = G[:2, :2], G[:2, 2:], G[2:, 2:]
        E, C = Gt[:2, :2], Gt[:2, 2:]
        matrices = [
            state[index : index + 4].reshape((2, 2))
            for index in range(0, 20, 4)
        ]
        P, R, J, K, dotK = matrices
        Pinv = np.linalg.inv(P)
        drive = Pinv @ D @ R
        derivatives = [
            A @ P,
            Ax @ R,
            Pinv @ E @ P,
            drive,
            Pinv @ C @ R - J @ drive,
        ]
        trace = np.array(
            [np.trace(A), np.trace(Ax)], dtype=complex
        )
        return np.concatenate(
            [matrix.reshape(-1) for matrix in derivatives] + [trace]
        )

    identity = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    interaction_initial = np.concatenate(
        [
            identity.reshape(-1),
            identity.reshape(-1),
            zero.reshape(-1),
            zero.reshape(-1),
            zero.reshape(-1),
            np.zeros(2, dtype=complex),
        ]
    )
    interaction_final = _solve(interaction_rhs, (r0, r1), interaction_initial)
    P, R, J, K, dotK = [
        interaction_final[index : index + 4].reshape((2, 2))
        for index in range(0, 20, 4)
    ]
    logW2, logW1 = interaction_final[20:22]
    F4 = np.block([[P, P @ K], [zero, R]])
    Fdot = np.block([[P @ J, P @ (J @ K + dotK)], [zero, zero]])
    interaction_base = F4 @ base0
    interaction_tangent = Fdot @ base0 + F4 @ tangent0

    # Projective/log transport of P.  Column 1 starts in q and is switched
    # at the midpoint; column 2 starts in the reciprocal p chart.
    q_half = _solve(
        _line_rhs(w, "spin2", "q", True),
        (r0, rm),
        np.zeros(4, dtype=complex),
    )
    if abs(q_half[0]) < 1.0e-12:
        raise RuntimeError("reciprocal chart switch denominator collapsed")
    p_half = np.array(
        [
            1.0 / q_half[0],
            q_half[1] + np.log(q_half[0]),
            -q_half[2] / q_half[0] ** 2,
            q_half[3] + q_half[2] / q_half[0],
        ],
        dtype=complex,
    )
    p_first = _solve(
        _line_rhs(w, "spin2", "p", True), (rm, r1), p_half
    )
    p_second = _solve(
        _line_rhs(w, "spin2", "p", True),
        (r0, r1),
        np.zeros(4, dtype=complex),
    )
    P1, dotP1 = _reconstruct_line(p_first, "p", True)
    P2, dotP2 = _reconstruct_line(p_second, "p", True)
    projective_P = np.column_stack((P1, P2))
    projective_dotP = np.column_stack((dotP1, dotP2))

    # The two spin-one lines use the same reciprocal atlas but no tau tangent.
    q1_half = _solve(
        _line_rhs(w, "spin1", "q", False),
        (r0, rm),
        np.zeros(2, dtype=complex),
    )
    if abs(q1_half[0]) < 1.0e-12:
        raise RuntimeError("spin-one reciprocal switch denominator collapsed")
    p1_half = np.array(
        [1.0 / q1_half[0], q1_half[1] + np.log(q1_half[0])],
        dtype=complex,
    )
    p1_first = _solve(
        _line_rhs(w, "spin1", "p", False), (rm, r1), p1_half
    )
    p1_second = _solve(
        _line_rhs(w, "spin1", "p", False),
        (r0, r1),
        np.zeros(2, dtype=complex),
    )
    R1, _ = _reconstruct_line(p1_first, "p", False)
    R2, _ = _reconstruct_line(p1_second, "p", False)
    projective_R = np.column_stack((R1, R2))

    residuals = {
        "direct_vs_interaction_base": np.max(np.abs(direct_base - interaction_base)),
        "direct_vs_interaction_tangent": np.max(np.abs(direct_tangent - interaction_tangent)),
        "projective_vs_P": np.max(np.abs(projective_P - P)),
        "projective_tau_vs_PJ": np.max(np.abs(projective_dotP - P @ J)),
        "projective_vs_R": np.max(np.abs(projective_R - R)),
        "wronskian_spin2": abs(np.linalg.det(P) - np.exp(logW2)),
        "wronskian_spin1": abs(np.linalg.det(R) - np.exp(logW1)),
    }
    threshold = 2.0e-10
    return {
        "status": "POINT_FIXTURE_PASS" if max(residuals.values()) < threshold else "POINT_FIXTURE_REFUSED",
        "frequency": "8193/16384",
        "radial_start": "487/16",
        "radial_end": "3895/128",
        "forced_chart_switch": {
            "radius": "7791/256",
            "spin2_abs_q": abs(q_half[0]),
            "spin1_abs_q": abs(q1_half[0]),
        },
        "residuals": {key: float(value) for key, value in residuals.items()},
        "threshold": threshold,
        "does_not_establish": (
            "This high-precision center fixture is not a validated enclosure; "
            "the separate Forge micro-panel carries the interval claim."
        ),
    }
