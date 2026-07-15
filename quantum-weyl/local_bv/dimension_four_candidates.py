"""Generated antifield-independent dimension-four curvature candidates.

This module generates the complete parity-even quadratic Riemann ansatz,
computes its infinitesimal Weyl-closed kernel modulo a total derivative, and
adjoins the independently generated odd Weyl carrier and ``Box R`` boundary
term.  It is a candidate catalogue, not a computation of the full local BV
cohomology.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .curvature import RIEMANN, named_quadratic_representatives, quadratic_curvature_analysis
from .quotient import exact_nullspace, exact_rank
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    total_covariant_derivative,
)
from .weyl_target import DUAL_WEYL, WEYL_GHOST, dimension_four_weyl_target_analysis
from .specialization import WEYL, replace_riemann_by_weyl


def _linear_combination(
    terms: tuple[tuple[Fraction | int, TensorExpression], ...]
) -> TensorExpression:
    result = TensorExpression()
    for coefficient, expression in terms:
        result = result + Fraction(coefficient) * expression
    return result


def _box_scalar_curvature() -> tuple[TensorExpression, TensorMonomial]:
    """Return ``Box R`` and its explicit divergence primitive ``nabla R``."""

    gradient = TensorMonomial(
        (TensorFactor(RIEMANN, (1, 2, 1, 2), (0,)),)
    )
    box_r = total_covariant_derivative(gradient, 0)
    if not box_r:
        raise AssertionError("Box R divergence witness vanished")
    return box_r, gradient


def multiply_by_weyl_ghost(expression: TensorExpression) -> TensorExpression:
    """Multiply a scalar density carrier by the odd Weyl ghost exactly."""

    terms: dict[TensorMonomial, Fraction] = {}
    ghost = TensorFactor(WEYL_GHOST, ())
    for monomial, coefficient in expression.terms.items():
        product = TensorMonomial((ghost,) + monomial.factors)
        terms[product] = terms.get(product, Fraction()) + coefficient
    return TensorExpression(terms)


def _fraction_payload(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _candidate_record(
    *,
    class_id: str,
    representative: TensorExpression,
    ghost_number: int,
    parity: str,
    topological_status: str,
    local_triviality: str,
    integrated_triviality: str,
    closure_status: str,
    proof_status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "class_id": class_id,
        "representative": representative.canonical_payload(),
        "representative_sha256": representative.canonical_hash(),
        "ghost_number": ghost_number,
        "antifield_number": 0,
        "form_degree": 4,
        "mass_dimension": 4,
        "parity": parity,
        "descent_length": "NOT_COMPUTED",
        "topological_status": topological_status,
        "local_triviality": local_triviality,
        "integrated_triviality": integrated_triviality,
        "closure_status": closure_status,
        "cohomology_status": "NOT_COMPUTED",
        "proof_status": proof_status,
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json"
        ),
        "residual_restriction_status": "NOT_COMPUTED",
        "notes": notes,
    }


@lru_cache(maxsize=1)
def dimension_four_candidate_analysis() -> dict[str, object]:
    """Generate the exact curvature-sector counterterm/anomaly candidates."""

    curvature = quadratic_curvature_analysis()
    quotient = curvature["quotient"]
    named = named_quadratic_representatives()
    ordered_names = (
        "Riemann_squared",
        "Ricci_squared",
        "scalar_curvature_squared",
    )
    named_expressions = tuple(named[name] for name in ordered_names)
    if quotient.rank_of_classes(named_expressions) != 3:
        raise AssertionError("quadratic curvature ansatz lost a named direction")

    # Rows are the exact coefficients of Ric^{ab} nabla_a nabla_b omega and
    # R Box omega in the local infinitesimal Weyl variations of the three
    # generated named directions.  Contracted Bianchi plus integration by
    # parts sends the first row to one half of the second carrier.
    local_weyl_variation = (
        (Fraction(-8), Fraction(-4), Fraction(0)),
        (Fraction(0), Fraction(-2), Fraction(-12)),
    )
    integrated_weyl_variation = (
        tuple(
            local_weyl_variation[1][column]
            + Fraction(1, 2) * local_weyl_variation[0][column]
            for column in range(3)
        ),
    )
    closed_kernel = exact_nullspace(integrated_weyl_variation)
    if len(closed_kernel) != 2:
        raise AssertionError("dimension-four Weyl-closed kernel drifted")

    c2_coordinates = (Fraction(1), Fraction(-2), Fraction(1, 3))
    e4_coordinates = (Fraction(1), Fraction(-4), Fraction(1))
    conventional_closed_basis = (c2_coordinates, e4_coordinates)
    if exact_rank(conventional_closed_basis) != 2 or any(
        sum(row[column] * vector[column] for column in range(3))
        for row in integrated_weyl_variation
        for vector in conventional_closed_basis
    ):
        raise AssertionError("conventional C2/E4 basis does not span the kernel")

    c2 = _linear_combination(tuple(zip(c2_coordinates, named_expressions)))
    e4 = _linear_combination(tuple(zip(e4_coordinates, named_expressions)))
    r2 = named["scalar_curvature_squared"]
    box_r, box_r_primitive = _box_scalar_curvature()

    target = dimension_four_weyl_target_analysis()
    c2_weyl_restriction = replace_riemann_by_weyl(c2)
    e4_weyl_restriction = replace_riemann_by_weyl(e4)
    even_quotient = target["even"]["quotient"]
    if c2_weyl_restriction != e4_weyl_restriction or not any(
        even_quotient.free_coordinates(c2_weyl_restriction)
    ):
        raise AssertionError("named even candidates lost their Weyl carrier")
    odd_representative = TensorExpression.monomial(
        TensorMonomial(
            (
                TensorFactor(DUAL_WEYL, (0, 1, 2, 3)),
                TensorFactor(WEYL, (0, 1, 2, 3)),
            )
        )
    )
    odd_quotient = target["odd"]["quotient"]
    if not any(odd_quotient.free_coordinates(odd_representative)):
        raise AssertionError("Pontryagin carrier vanished in the odd quotient")

    counterterms = (
        _candidate_record(
            class_id="CT_C2",
            representative=c2,
            ghost_number=0,
            parity="even",
            topological_status="NONE",
            local_triviality="NOT_COMPUTED",
            integrated_triviality="NONTRIVIAL_CANDIDATE",
            closure_status="STRICT_WEYL_CLOSED",
            proof_status="GENERATED_KERNEL_BASIS",
            notes="C^2 density; nontriviality in full H^{0,4}(s|d) is not claimed.",
        ),
        _candidate_record(
            class_id="CT_E4",
            representative=e4,
            ghost_number=0,
            parity="even",
            topological_status="EULER",
            local_triviality="DESCENT_REQUIRED",
            integrated_triviality="TOPOLOGICAL",
            closure_status="WEYL_CLOSED_MOD_D",
            proof_status="GENERATED_KERNEL_BASIS",
            notes="Euler density; kept distinct from the strictly Weyl-invariant class.",
        ),
        _candidate_record(
            class_id="CT_C_DUAL_C",
            representative=odd_representative,
            ghost_number=0,
            parity="odd",
            topological_status="PONTRYAGIN",
            local_triviality="DESCENT_REQUIRED",
            integrated_triviality="TOPOLOGICAL",
            closure_status="STRICT_WEYL_CLOSED",
            proof_status="TARGET_NATIVE_ODD_QUOTIENT",
            notes="Compressed dual-Weyl carrier with an explicit epsilon/Hodge audit.",
        ),
        _candidate_record(
            class_id="CT_BOX_R",
            representative=box_r,
            ghost_number=0,
            parity="even",
            topological_status="BOUNDARY",
            local_triviality="TOTAL_DERIVATIVE",
            integrated_triviality="TRIVIAL_MOD_D",
            closure_status="TRIVIAL_MOD_D",
            proof_status="EXPLICIT_DIVERGENCE_WITNESS",
            notes="The stored primitive is the covariant vector nabla^a R.",
        ),
    )

    anomaly_sources = {
        "ANOM_OMEGA_C2": c2,
        "ANOM_OMEGA_E4": e4,
        "ANOM_OMEGA_C_DUAL_C": odd_representative,
        "ANOM_OMEGA_BOX_R": box_r,
    }
    anomalies = []
    for class_id, density in anomaly_sources.items():
        is_box = class_id == "ANOM_OMEGA_BOX_R"
        is_euler = class_id == "ANOM_OMEGA_E4"
        anomalies.append(
            _candidate_record(
                class_id=class_id,
                representative=multiply_by_weyl_ghost(density),
                ghost_number=1,
                parity="odd" if "DUAL" in class_id else "even",
                topological_status=(
                    "EULER"
                    if is_euler
                    else "PONTRYAGIN"
                    if "DUAL" in class_id
                    else "BOUNDARY"
                    if is_box
                    else "NONE"
                ),
                local_triviality="EXPLICIT_BRST_TRIVIALIZATION" if is_box else "NOT_COMPUTED",
                integrated_triviality="COUNTERTERM_REMOVABLE" if is_box else "NOT_COMPUTED",
                closure_status=(
                    "EXPLICITLY_TRIVIAL_MOD_D"
                    if is_box
                    else "DESCENT_REQUIRED"
                    if is_euler
                    else "WEYL_CLOSED_CANDIDATE"
                ),
                proof_status=(
                    "OMEGA_BOX_R_EQUALS_MINUS_ONE_TWELFTH_S_R2_MOD_D"
                    if is_box
                    else "GHOST_LIFT_OF_GENERATED_DENSITY"
                ),
                notes=(
                    "Explicit integrated trivialization by -R^2/12; full Diff-Weyl descent remains open."
                    if is_box
                    else "Candidate only; descent and nontriviality remain to be computed."
                ),
            )
        )

    return {
        "quadratic_curvature_analysis": curvature,
        "quadratic_ansatz_dimension": quotient.quotient_dimension,
        "named_basis": ordered_names,
        "named_coordinates": tuple(
            quotient.free_coordinates(expression) for expression in named_expressions
        ),
        "local_weyl_variation": local_weyl_variation,
        "integrated_weyl_variation": integrated_weyl_variation,
        "closed_kernel": closed_kernel,
        "closed_kernel_dimension": len(closed_kernel),
        "conventional_closed_basis": conventional_closed_basis,
        "c2": c2,
        "e4": e4,
        "r2": r2,
        "box_r": box_r,
        "box_r_primitive": box_r_primitive,
        "odd_representative": odd_representative,
        "c2_weyl_restriction": c2_weyl_restriction,
        "e4_weyl_restriction": e4_weyl_restriction,
        "target_analysis": target,
        "counterterms": counterterms,
        "anomalies": tuple(anomalies),
        "box_anomaly_trivialization_coefficient": Fraction(-1, 12),
        "fraction_payload": _fraction_payload,
    }
