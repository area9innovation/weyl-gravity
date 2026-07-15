"""Exact local primitives for the dimension-four ``Box R`` sector."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .curvature import RIEMANN
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    total_covariant_derivative,
)
from .weyl_target import WEYL_GHOST


def _scalar_curvature_factor(*, derivatives: tuple[int, ...] = ()) -> TensorFactor:
    """Return ``R`` as the trace ``R_{ab}{}^{ab}`` with optional derivatives."""

    return TensorFactor(RIEMANN, (1, 2, 1, 2), derivatives)


def _omega_factor(*, derivatives: tuple[int, ...] = ()) -> TensorFactor:
    return TensorFactor(WEYL_GHOST, (), derivatives)


@lru_cache(maxsize=1)
def box_r_triviality_analysis() -> dict[str, object]:
    """Verify both total-derivative and relative-BRST trivializations exactly.

    In four dimensions the infinitesimal Weyl row is

    ``Q_W(sqrt(g) R^2) = -12 sqrt(g) R Box(omega)``.

    The current ``J^a = R nabla^a omega - omega nabla^a R`` obeys
    ``div J = R Box(omega) - omega Box(R)``.  Consequently

    ``omega Box(R) = -(1/12) Q_W(R^2) - div J``.
    """

    gradient_r = TensorMonomial((_scalar_curvature_factor(derivatives=(0,)),))
    box_r = total_covariant_derivative(gradient_r, 0)

    r_box_omega = TensorExpression.monomial(
        TensorMonomial(
            (
                _scalar_curvature_factor(),
                _omega_factor(derivatives=(0, 0)),
            )
        )
    )
    omega_box_r = TensorExpression.monomial(
        TensorMonomial(
            (
                _omega_factor(),
                _scalar_curvature_factor(derivatives=(0, 0)),
            )
        )
    )
    current = TensorExpression(
        {
            TensorMonomial(
                (
                    _scalar_curvature_factor(),
                    _omega_factor(derivatives=(0,)),
                )
            ): 1,
            TensorMonomial(
                (
                    _omega_factor(),
                    _scalar_curvature_factor(derivatives=(0,)),
                )
            ): -1,
        }
    )
    current_divergence = TensorExpression()
    for monomial, coefficient in current.terms.items():
        current_divergence = current_divergence + coefficient * total_covariant_derivative(
            monomial, 0
        )
    current_identity_residual = current_divergence - r_box_omega + omega_box_r
    if current_identity_residual:
        raise AssertionError("Box R anomaly current identity failed")

    weyl_brst_r_squared = -12 * r_box_omega
    relative_residual = (
        omega_box_r
        + Fraction(1, 12) * weyl_brst_r_squared
        + current_divergence
    )
    if relative_residual:
        raise AssertionError("omega Box R relative trivialization failed")

    return {
        "box_r": box_r,
        "box_r_primitive": gradient_r,
        "r_box_omega": r_box_omega,
        "omega_box_r": omega_box_r,
        "anomaly_current": current,
        "anomaly_current_divergence": current_divergence,
        "weyl_brst_r_squared": weyl_brst_r_squared,
        "counterterm_coefficient": Fraction(-1, 12),
        "current_identity_residual": current_identity_residual,
        "relative_trivialization_residual": relative_residual,
    }
