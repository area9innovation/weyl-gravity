"""Generated universal Diff descent for strict Weyl-invariant densities."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .algebra import canonical_sha256
from .horizontal_forms import (
    STRICT_DENSITY,
    HorizontalForm,
    StrictDensityBRSTDifferential,
    strict_density_algebra,
)


def _flatten(form: HorizontalForm) -> dict[tuple[object, ...], Fraction]:
    return {
        (indices, monomial): coefficient
        for indices, expression in form.terms.items()
        for monomial, coefficient in expression.terms.items()
    }


def _proportional_ratio(
    left: HorizontalForm, right: HorizontalForm
) -> Fraction:
    """Return the exact ratio ``left/right`` or fail if none exists."""

    left_terms = _flatten(left)
    right_terms = _flatten(right)
    if not left_terms or set(left_terms) != set(right_terms):
        raise ValueError("forms do not have the same nonzero support")
    first = min(left_terms, key=repr)
    ratio = left_terms[first] / right_terms[first]
    if any(left_terms[key] != ratio * right_terms[key] for key in left_terms):
        raise ValueError("forms are not exactly proportional")
    return ratio


def _coefficient_ghost_number(form: HorizontalForm) -> int:
    ghost_numbers = {
        sum(variable.ghost_number for variable in monomial)
        for expression in form.terms.values()
        for monomial in expression.terms
    }
    if len(ghost_numbers) != 1:
        raise ValueError("form coefficients are not ghost-number homogeneous")
    return next(iter(ghost_numbers))


@lru_cache(maxsize=2)
def strict_density_descent(ghost_lift: bool) -> dict[str, object]:
    """Generate the complete four-step diffeomorphism descent.

    ``ghost_lift=False`` represents a strict ghost-number-zero density such
    as ``C^2``.  ``ghost_lift=True`` represents its Weyl-ghost lift
    ``omega C^2``.  The coefficients are solved from exact proportionality
    of the BRST and horizontal-differential rows; they are not inserted as a
    preselected factorial tower.
    """

    algebra = strict_density_algebra(4)
    differential = StrictDensityBRSTDifferential(algebra)
    coefficient = algebra.var(STRICT_DENSITY)
    if ghost_lift:
        coefficient = algebra.var("omega") * coefficient
    top = HorizontalForm.coefficient(4, coefficient).wedge(
        HorizontalForm.basis(4, range(4))
    )

    raw_tower = [top]
    for _ in range(4):
        raw_tower.append(raw_tower[-1].interior_xi(algebra))

    coefficients = [Fraction(1)]
    ratios = []
    for level in range(4):
        brst_row = raw_tower[level].brst(differential)
        horizontal_row = raw_tower[level + 1].horizontal_differential(algebra)
        ratio = _proportional_ratio(brst_row, horizontal_row)
        ratios.append(ratio)
        coefficients.append(-coefficients[-1] * ratio)

    tower = tuple(
        coefficient * raw for coefficient, raw in zip(coefficients, raw_tower)
    )
    for level in range(4):
        residual = tower[level].brst(differential) + tower[
            level + 1
        ].horizontal_differential(algebra)
        if residual:
            raise AssertionError(f"strict descent failed at level {level}")
    if tower[-1].brst(differential):
        raise AssertionError("strict descent bottom is not BRST closed")

    form_degrees = tuple(form.homogeneous_form_degree() for form in tower)
    ghost_numbers = tuple(_coefficient_ghost_number(form) for form in tower)
    expected_start = 1 if ghost_lift else 0
    if form_degrees != (4, 3, 2, 1, 0):
        raise AssertionError("strict descent form degrees drifted")
    if ghost_numbers != tuple(expected_start + level for level in range(5)):
        raise AssertionError("strict descent ghost numbers drifted")

    return {
        "ghost_lift": ghost_lift,
        "algebra": algebra,
        "differential": differential,
        "raw_tower": tuple(raw_tower),
        "tower": tower,
        "coefficients": tuple(coefficients),
        "brst_to_horizontal_ratios": tuple(ratios),
        "form_degrees": form_degrees,
        "ghost_numbers": ghost_numbers,
        "tower_sha256": canonical_sha256(
            [form.canonical_payload() for form in tower]
        ),
        "descent_length": 4,
    }


@lru_cache(maxsize=1)
def strict_candidate_descent_analysis() -> dict[str, object]:
    counterterm = strict_density_descent(False)
    anomaly = strict_density_descent(True)
    return {
        "counterterm": counterterm,
        "anomaly": anomaly,
        "computed_candidates": {
            "CT_C2": "counterterm",
            "CT_C_DUAL_C": "counterterm",
            "ANOM_OMEGA_C2": "anomaly",
            "ANOM_OMEGA_C_DUAL_C": "anomaly",
        },
        "not_computed_candidates": {
            "CT_E4": "requires the Euler Weyl-current descent",
            "ANOM_OMEGA_E4": "requires the nontrivial Euler Weyl descent",
        },
        "trivialized_candidates": {
            "CT_BOX_R": "explicit horizontal total derivative",
            "ANOM_OMEGA_BOX_R": "minus one twelfth s(R^2) modulo d",
        },
    }
