"""Coarse ambient AFN0 lower-form signatures in total degrees three to six."""

from __future__ import annotations

from functools import lru_cache

from .algebra import canonical_sha256


TOTAL_DEGREES = (3, 4, 5, 6)
PARITIES = ("even", "odd")


def _refinement(signature: dict[str, object]) -> tuple[str, str]:
    if not (
        2 * int(signature["curvature_count"])
        + int(signature["tensor_derivative_count"])
        + int(signature["weyl_ghost_derivative_count"])
        + int(signature["diff_ghost_derivative_count"])
        - int(signature["diff_ghost_count"])
        - int(signature["form_degree"])
        == 0
    ):
        raise AssertionError("ambient lower-form engineering equation drifted")
    if (
        signature["curvature_count"] == 0
        and signature["tensor_derivative_count"]
    ):
        return "REJECTED", "tensor derivatives have no curvature seed because nabla g=0"
    if (
        signature["weyl_ghost_count"] == 0
        and signature["weyl_ghost_derivative_count"]
    ):
        return "REJECTED", "Weyl-ghost derivatives have no Weyl-ghost factor"
    if (
        signature["diff_ghost_count"] == 0
        and signature["diff_ghost_derivative_count"]
    ):
        return "REJECTED", "Diff-ghost derivatives have no Diff-ghost factor"
    if int(signature["weyl_ghost_derivative_count"]) < max(
        0, int(signature["weyl_ghost_count"]) - 1
    ):
        return "REJECTED", "insufficient Weyl-ghost derivatives force two undifferentiated scalar ghosts and hence vanish by Grassmann oddness"
    if int(signature["total_index_slots_with_dx"]) % 2:
        return "REJECTED", "metric/epsilon contraction cannot absorb an odd total index count"
    if signature["epsilon_count"] and int(signature["total_index_slots_with_dx"]) < 4:
        return "REJECTED", "the four-dimensional epsilon carrier lacks four index slots"
    return "REFINED_ADMISSIBLE", "passes seed, Grassmann, engineering, and scalar-index constraints"


def _signature(
    *,
    total_degree: int,
    form_degree: int,
    parity: str,
    curvature_count: int,
    tensor_derivative_count: int,
    weyl_ghost_count: int,
    weyl_ghost_derivative_count: int,
    diff_ghost_count: int,
    diff_ghost_derivative_count: int,
) -> dict[str, object]:
    ghost_number = weyl_ghost_count + diff_ghost_count
    coefficient_dimension = (
        2 * curvature_count
        + tensor_derivative_count
        + weyl_ghost_derivative_count
        + diff_ghost_derivative_count
        - diff_ghost_count
    )
    tensor_slots = 4 * curvature_count + tensor_derivative_count
    ghost_slots = (
        weyl_ghost_derivative_count
        + diff_ghost_count
        + diff_ghost_derivative_count
    )
    payload = {
        "total_degree": total_degree,
        "ghost_number": ghost_number,
        "form_degree": form_degree,
        "parity": parity,
        "curvature_count": curvature_count,
        "tensor_derivative_count": tensor_derivative_count,
        "weyl_ghost_count": weyl_ghost_count,
        "weyl_ghost_derivative_count": weyl_ghost_derivative_count,
        "diff_ghost_count": diff_ghost_count,
        "diff_ghost_derivative_count": diff_ghost_derivative_count,
        "epsilon_count": 0 if parity == "even" else 1,
        "coefficient_engineering_dimension": coefficient_dimension,
        "dx_engineering_dimension": -form_degree,
        "total_form_engineering_dimension": coefficient_dimension - form_degree,
        "tensor_index_slots": tensor_slots,
        "ghost_index_slots": ghost_slots,
        "horizontal_dx_index_slots": form_degree,
        "total_index_slots_with_dx": tensor_slots + ghost_slots + form_degree,
    }
    if ghost_number + form_degree != total_degree:
        raise AssertionError("ambient lower-form total degree drifted")
    status, reason = _refinement(payload)
    row = {**payload, "refinement_status": status, "refinement_reason": reason}
    return {**row, "signature_sha256": canonical_sha256(row)}


def ambient_signatures(total_degree: int, parity: str) -> tuple[dict[str, object], ...]:
    if total_degree not in TOTAL_DEGREES:
        raise ValueError("ambient AFN0 total degree must lie in 3,...,6")
    if parity not in PARITIES:
        raise ValueError("ambient AFN0 parity must be even or odd")
    rows: list[dict[str, object]] = []
    for form_degree in range(5):
        ghost_number = total_degree - form_degree
        if ghost_number < 0:
            continue
        for diff_ghost_count in range(ghost_number + 1):
            weyl_ghost_count = ghost_number - diff_ghost_count
            # The engineering equation bounds 2*n_curvature by
            # p+n_diff <= total_degree <= 6, hence n_curvature <= 3.
            for curvature_count in range(4):
                derivative_total = (
                    form_degree + diff_ghost_count - 2 * curvature_count
                )
                if derivative_total < 0:
                    continue
                for tensor_derivative_count in range(derivative_total + 1):
                    remaining = derivative_total - tensor_derivative_count
                    for weyl_ghost_derivative_count in range(remaining + 1):
                        diff_ghost_derivative_count = (
                            remaining - weyl_ghost_derivative_count
                        )
                        rows.append(
                            _signature(
                                total_degree=total_degree,
                                form_degree=form_degree,
                                parity=parity,
                                curvature_count=curvature_count,
                                tensor_derivative_count=tensor_derivative_count,
                                weyl_ghost_count=weyl_ghost_count,
                                weyl_ghost_derivative_count=weyl_ghost_derivative_count,
                                diff_ghost_count=diff_ghost_count,
                                diff_ghost_derivative_count=diff_ghost_derivative_count,
                            )
                        )
    return tuple(
        sorted(
            rows,
            key=lambda row: tuple(
                row[key]
                for key in (
                    "form_degree",
                    "diff_ghost_count",
                    "curvature_count",
                    "tensor_derivative_count",
                    "weyl_ghost_derivative_count",
                    "diff_ghost_derivative_count",
                )
            ),
        )
    )


@lru_cache(maxsize=1)
def ambient_lower_form_signature_analysis() -> dict[str, object]:
    manifests = []
    for parity in PARITIES:
        for total_degree in TOTAL_DEGREES:
            rows = ambient_signatures(total_degree, parity)
            manifests.append(
                {
                    "parity": parity,
                    "total_degree": total_degree,
                    "coarse_signature_count": len(rows),
                    "refined_signature_count": sum(
                        row["refinement_status"] == "REFINED_ADMISSIBLE"
                        for row in rows
                    ),
                    "signatures": list(rows),
                }
            )
    even = [row for row in manifests if row["parity"] == "even"]
    odd = [row for row in manifests if row["parity"] == "odd"]
    if [row["coarse_signature_count"] for row in even] != [80, 190, 360, 610]:
        raise AssertionError("even ambient coarse signature counts drifted")
    if [row["refined_signature_count"] for row in even] != [22, 51, 105, 183]:
        raise AssertionError("even ambient refined signature counts drifted")
    if [row["coarse_signature_count"] for row in odd] != [80, 190, 360, 610]:
        raise AssertionError("odd ambient coarse signature counts drifted")
    if [row["refined_signature_count"] for row in odd] != [20, 51, 105, 183]:
        raise AssertionError("odd ambient refined signature counts drifted")
    payload = {
        "result_id": "AFN0_AMBIENT_LOWER_FORM_SIGNATURE_CERTIFICATE",
        "result_state": "AMBIENT_GRADING_EXHAUSTIVE_TENSOR_QUOTIENT_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "declared_bounds": {
            "total_degrees": list(TOTAL_DEGREES),
            "form_degrees": [0, 1, 2, 3, 4],
            "spacetime_dimension": 4,
            "antifield_number": 0,
            "total_form_engineering_dimension": 0,
            "curvature_count_upper_bound": 3,
        },
        "generator_algebra": {
            "curvature": "dimension 2, covariant rank four",
            "covariant_derivative": "dimension 1, covariant rank one",
            "weyl_ghost": "dimension 0, ghost number 1, scalar Grassmann odd",
            "diff_ghost": "dimension -1, ghost number 1, contravariant rank one Grassmann odd",
            "horizontal_dx": "dimension -1, form degree 1",
            "epsilon": "dimension 0, rank four, parity odd",
        },
        "grading_equations": [
            "ghost_number + form_degree = total_degree",
            "2*n_curvature + n_tensor_derivative + n_domega + n_dxi - n_xi - form_degree = 0",
            "n_curvature <= 3 follows from total_degree <= 6",
            "all signature variables are nonnegative integers",
        ],
        "manifests": manifests,
        "totals": {
            "coarse_signature_count": sum(
                row["coarse_signature_count"] for row in manifests
            ),
            "refined_signature_count": sum(
                row["refined_signature_count"] for row in manifests
            ),
            "rejected_signature_count": sum(
                row["coarse_signature_count"] - row["refined_signature_count"]
                for row in manifests
            ),
        },
        "checks": {
            "integer_grading_enumeration": "EXHAUSTIVE_UNDER_DECLARED_GENERATOR_ALGEBRA",
            "engineering_dimension_zero": "VERIFIED_EVERY_SIGNATURE",
            "total_degree_range_three_through_six": "VERIFIED",
            "seed_constraints": "VERIFIED",
            "undifferentiated_weyl_ghost_nilpotence": "VERIFIED",
            "scalar_index_parity": "VERIFIED",
        },
        "next_gates": {
            "tensor_graph_realizability": "NOT_COMPUTED",
            "Bianchi_and_Grassmann_quotient": "NOT_COMPUTED",
            "integration_by_parts_quotient": "NOT_COMPUTED",
            "dimension_specific_antisymmetrization": "NOT_COMPUTED",
            "production_Q_dh_matrices": "NOT_COMPUTED",
        },
        "claim_boundary": [
            "the certificate is exhaustive only at the integer multigrading-signature level",
            "a refined signature is not yet a tensor-realizable or canonically nonzero local form",
            "no relative-cohomology dimension or nontriviality witness is promoted",
        ],
    }
    return {**payload, "analysis_sha256": canonical_sha256(payload)}
