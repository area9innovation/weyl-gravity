#!/usr/bin/env python3
"""Independent pointwise spin-one mismatch cross-check.

This rail deliberately does not use the validated Riccati transport.  It
integrates the two-component reduced scalar equations with SciPy DOP853 and
only checks agreement with the rigorous complex ball at the disk centre.
It is an independent numerical control, not the source of the enclosure.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SELECTOR_RUN = (
    ROOT
    / "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_contour_completion/"
    "local_selector_v1/local-selector-run.json"
)
OUTPUT = HERE / "crosscheck.json"


def infinity_coefficients(omega: complex, order: int) -> list[complex]:
    aa = [0, 0, 1, -4, 4]
    bb = [2j * omega, 2 - 4j * omega, -10, 12]
    cc = [-6, 12]
    coefficients = [1.0 + 0.0j]
    for n in range(order - 1):
        target = n + 1
        known = 0.0j
        pivot = 0.0j
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(coefficients):
                known += value * coefficients[k]
        coefficients.append(-known / pivot)
    return coefficients


def horizon_coefficients(omega: complex, order: int) -> list[complex]:
    aa = [0, 4, 4, 1]
    bb = [
        4 + 16j * omega,
        2 + 24j * omega,
        12j * omega,
        2j * omega,
    ]
    cc = [-12, -6]
    coefficients = [1.0 + 0.0j]
    for n in range(order - 1):
        target = n + 1
        known = 0.0j
        pivot = 0.0j
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                if k == target:
                    pivot += term
                elif k < len(coefficients):
                    known += term * coefficients[k]
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(coefficients):
                known += value * coefficients[k]
        coefficients.append(-known / pivot)
    return coefficients


def evaluate_infinity(coefficients: list[complex], r: float) -> np.ndarray:
    z = 1.0 / r
    value = sum(c * z**n for n, c in enumerate(coefficients))
    derivative_r = sum(
        -n * c * z ** (n + 1)
        for n, c in enumerate(coefficients)
        if n
    )
    derivative_x = (r - 2.0) / r * derivative_r
    return np.array([value, derivative_x], dtype=np.complex128)


def evaluate_horizon(coefficients: list[complex], rho: float) -> np.ndarray:
    value = sum(c * rho**n for n, c in enumerate(coefficients))
    derivative_r = sum(
        n * c * rho ** (n - 1)
        for n, c in enumerate(coefficients)
        if n
    )
    r = 2.0 + rho
    derivative_x = (r - 2.0) / r * derivative_r
    return np.array([value, derivative_x], dtype=np.complex128)


def rhs(r: float, state: np.ndarray, omega: complex) -> np.ndarray:
    value, derivative_x = state
    c = r / (r - 2.0)
    potential = 6.0 * (r - 2.0) / r**3
    return np.array(
        [
            c * derivative_x,
            c * (2j * omega * derivative_x + potential * value),
        ],
        dtype=np.complex128,
    )


def compute() -> dict:
    selector = json.loads(SELECTOR_RUN.read_text())
    omega = complex(
        float(Fraction(selector["domain"]["parent_center_re"])),
        float(Fraction(selector["domain"]["parent_center_im"])),
    )
    order = 36
    infinity_initial = evaluate_infinity(
        infinity_coefficients(omega, order), 45.0
    )
    infinity_solution = solve_ivp(
        lambda r, y: rhs(r, y, omega),
        (45.0, 32.0),
        infinity_initial,
        method="DOP853",
        rtol=2e-13,
        atol=2e-15,
    )
    rho = 2.0**-18
    horizon_initial = evaluate_horizon(
        horizon_coefficients(omega, order), rho
    )
    # For the moving ingoing phase, omega is replaced by -omega.
    horizon_solution = solve_ivp(
        lambda r, y: rhs(r, y, -omega),
        (2.0 + rho, 32.0),
        horizon_initial,
        method="DOP853",
        rtol=2e-13,
        atol=2e-15,
    )
    if not infinity_solution.success or not horizon_solution.success:
        raise RuntimeError("independent DOP853 cross-check failed")
    infinity_final = infinity_solution.y[:, -1]
    horizon_final = horizon_solution.y[:, -1]
    q_out = infinity_final[1] / infinity_final[0]
    q_horizon = horizon_final[1] / horizon_final[0]
    delta = q_horizon - q_out + 2j * omega
    return {
        "schema": "phase3-axial-qnm-spin-one-local-unit-crosscheck-v1",
        "method": (
            "independent two-component reduced scalar DOP853 transport; "
            "not used as the rigorous enclosure"
        ),
        "omega": [omega.real, omega.imag],
        "order": order,
        "horizon_seed_rho": rho,
        "infinity_steps": len(infinity_solution.t) - 1,
        "horizon_steps": len(horizon_solution.t) - 1,
        "q_outgoing": [q_out.real, q_out.imag],
        "q_horizon": [q_horizon.real, q_horizon.imag],
        "delta": [delta.real, delta.imag],
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
