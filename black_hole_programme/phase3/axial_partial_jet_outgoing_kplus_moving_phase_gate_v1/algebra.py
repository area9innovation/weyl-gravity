"""Exact symbolic derivation of the outgoing intrinsic phase derivatives."""
from __future__ import annotations

import sympy as sp


def matrix(entries: list[list[str]], local: dict) -> sp.Matrix:
    return sp.Matrix(
        [[sp.sympify(value, locals=local) for value in row] for row in entries]
    )


def derive(exact_blocks: dict) -> dict:
    r, omega, z, tau, lam = sp.symbols(
        "r omega z tau lambda", nonzero=True
    )
    local = {"r": r, "omega": omega, "I": sp.I}
    a = matrix(exact_blocks["A_RW"], local)
    e = matrix(exact_blocks["E_RW_self_extension"], local)

    fixed_log_phase_derivative = -2 * sp.I * omega - 4 * sp.I * omega / r
    reduced = sp.simplify(
        a - fixed_log_phase_derivative * sp.eye(2)
    )
    reduced_z = reduced.subs(r, 1 / z)
    e_z = e.subs(r, 1 / z)

    characteristic = (
        lam * sp.eye(2) - (reduced_z + tau * e_z)
    ).det()
    p_tau = sp.diff(characteristic, tau).subs({tau: 0, lam: 0})
    p_lambda = sp.diff(characteristic, lam).subs({tau: 0, lam: 0})
    # The unperturbed outgoing reduced eigenvalue is O(z**2), so evaluation
    # at lambda=0 gives the exact constant and z coefficients of its first
    # tau derivative. Terms affected by lambda=O(z**2) start at z**2.
    local_eigenvalue_derivative = sp.factor(-p_tau / p_lambda)
    rate_derivative = sp.simplify(
        sp.limit(local_eigenvalue_derivative, z, 0)
    )
    power_derivative = sp.simplify(
        sp.limit(
            (local_eigenvalue_derivative - rate_derivative) / z,
            z,
            0,
        )
    )

    e12_linear = sp.simplify(sp.limit(e[0, 1] / r, r, sp.oo))
    e22_constant = sp.simplify(sp.limit(e[1, 1], r, sp.oo))
    reduced_constant = reduced.applyfunc(
        lambda value: sp.simplify(sp.limit(value, r, sp.oo))
    )
    e_irregular = e.applyfunc(
        lambda value: sp.simplify(sp.limit(value / r, r, sp.oo))
    )
    # Remove the r*E_-1 term with the canonical representative whose free
    # upper-right and lower-right centralizer entries vanish.
    polynomial_gauge = sp.diag(sp.Rational(3, 4), 0)
    irregular_homological_residual = sp.simplify(
        e_irregular
        + reduced_constant * polynomial_gauge
        - polynomial_gauge * reduced_constant
    )
    combined_moving_generator = sp.simplify(
        rate_derivative * sp.eye(2) + polynomial_gauge
    )
    derivative_remainder_order = sp.series(
        local_eigenvalue_derivative
        - rate_derivative
        - power_derivative * z,
        z,
        0,
        3,
    )

    return {
        "fixed_rate": -2 * sp.I * omega,
        "fixed_power": -4 * sp.I * omega,
        "rate_derivative": rate_derivative,
        "power_derivative": power_derivative,
        "E12_linear_coefficient": e12_linear,
        "E22_constant": e22_constant,
        "reduced_constant": reduced_constant,
        "E_irregular": e_irregular,
        "polynomial_gauge": polynomial_gauge,
        "irregular_homological_residual": irregular_homological_residual,
        "combined_moving_generator": combined_moving_generator,
        "local_eigenvalue_derivative": local_eigenvalue_derivative,
        "derivative_remainder_series": derivative_remainder_order,
    }
