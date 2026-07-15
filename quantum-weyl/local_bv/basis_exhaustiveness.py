"""Integer grading signatures for dimension-four AFN0 local monomials."""

from __future__ import annotations

from .algebra import canonical_sha256


def grading_signature_manifest(ghost_number: int) -> dict[str, object]:
    """Enumerate nonnegative solutions of the declared engineering grading.

    This is an independent structural check on symbolic generation, not yet an
    exhaustiveness proof: tensor-index singlets, integration by parts, pure
    Diff ghosts, and generalized-connection expansion remain separate gates.
    """

    if ghost_number not in {0, 1}:
        raise ValueError("the AFN0 dimension-four manifest supports ghost number 0 or 1")
    solutions: list[dict[str, int]] = []
    ghost_factors = ghost_number
    for curvature_count in range(3):
        for tensor_derivative_count in range(5):
            ghost_derivative_orders = range(5) if ghost_number else (0,)
            for ghost_derivative_order in ghost_derivative_orders:
                if (
                    2 * curvature_count
                    + tensor_derivative_count
                    + ghost_derivative_order
                    != 4
                ):
                    continue
                solutions.append(
                    {
                        "curvature_count": curvature_count,
                        "tensor_derivative_count": tensor_derivative_count,
                        "weyl_ghost_factor_count": ghost_factors,
                        "weyl_ghost_derivative_order": ghost_derivative_order,
                    }
                )
    solutions.sort(
        key=lambda row: tuple(row[key] for key in sorted(row))
    )
    generated = [
        row
        for row in solutions
        if row["weyl_ghost_derivative_order"] == 0
        and row["curvature_count"] in {1, 2}
    ]
    manifest = {
        "generator_algebra": {
            "curvature_or_weyl_tensor": {
                "engineering_dimension": 2,
                "ghost_number": 0,
            },
            "covariant_derivative": {
                "engineering_dimension": 1,
                "ghost_number": 0,
            },
            "weyl_ghost": {
                "engineering_dimension": 0,
                "ghost_number": 1,
                "derivative_cost": 1,
            },
            "metric_inverse_metric_levi_civita": {
                "engineering_dimension": 0,
                "ghost_number": 0,
            },
        },
        "grading_equations": [
            "2*n_curvature + n_tensor_derivative + n_ghost_derivative = 4",
            f"n_weyl_ghost = {ghost_number}",
            "all signature variables are nonnegative integers",
        ],
        "integer_solutions_for_monomial_types": solutions,
        "integer_solution_count": len(solutions),
        "currently_generated_signature_count": len(generated),
        "currently_generated_signatures": generated,
        "excluded_types_with_reason": [
            {
                "type": "pure_metric_derivatives",
                "reason": "metric compatibility gives no nonconstant tensor seed",
            },
            {
                "type": "pure_diffeomorphism_ghost_signatures",
                "reason": "engineering convention and index-orbit enumeration are pending",
            },
            {
                "type": "unexpanded_generalized_connection_signatures",
                "reason": "Euler generalized-connection bidegree expansion is in progress",
            },
        ],
        "generated_orbit_count": "PENDING_INDEX_ORBIT_ENUMERATION",
        "canonical_dimension": "PENDING_COMPLETE_IDENTITY_QUOTIENT",
        "exhaustiveness_status": "IN_PROGRESS",
    }
    return {**manifest, "grading_manifest_hash": canonical_sha256(manifest)}
