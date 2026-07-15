"""Fail-closed antifield-zero dimension-four production-run manifests.

These records execute the already complete top curvature-carrier generators
and bind their exact identities and known primitives.  They deliberately do
not promote familiar representatives to relative cohomology classes until
the lower-form and coboundary bases are exhaustive under the same bounds.
"""

from __future__ import annotations

from functools import lru_cache

from .algebra import canonical_sha256
from .dimension_four_candidates import dimension_four_candidate_analysis


def _candidate_payload(record: dict[str, object]) -> dict[str, object]:
    exact = record["class_status"] == "EXACT"
    return {
        "representative_id": record["class_id"],
        "representative_sha256": record["representative_sha256"],
        "relative_cohomology_status": "EXACT" if exact else "UNDECIDED",
        "closure_witness": {
            "status": "CLOSED",
            "certificate": record["descent_certificate"],
        },
        "exactness_witness": record["trivialization"] if exact else None,
        "nontriviality_witness": None,
    }


def _basis_manifest(
    analysis: dict[str, object],
    *,
    ghost_number: int,
    parity: str,
    candidate_ids: tuple[str, ...],
) -> dict[str, object]:
    curvature = analysis["quadratic_curvature_analysis"]
    target = analysis["target_analysis"][parity]
    manifest = {
        "basis_generation_rules": [
            "generate pairwise contractions of two algebraic Riemann tensors",
            "canonicalize intrinsic symmetries and dummy indices",
            "quotient the algebraic Bianchi identities exactly",
            "generate the parity carrier with the certified Hodge convention",
            "adjoin Box R with its explicit divergence primitive",
            "for ghost number one multiply carriers by the undifferentiated Weyl ghost",
        ],
        "dimension_and_bidegree_bounds": {
            "spacetime_dimension": 4,
            "form_degree": 4,
            "ghost_number": ghost_number,
            "antifield_number": 0,
            "engineering_dimension": 4,
            "parity": parity,
        },
        "raw_monomial_count": curvature["raw_pairing_count"],
        "canonical_basis_count": curvature["symmetry_canonical_monomial_count"],
        "identity_quotient_ranks": {
            "algebraic_bianchi_rank": curvature["bianchi_relation_rank"],
            "quadratic_curvature_quotient_dimension": curvature["quotient_dimension"],
            "weyl_target_relation_rank": target["relation_rank"],
            "weyl_target_quotient_dimension": target["quotient_dimension"],
        },
        "candidate_ids": list(candidate_ids),
        "top_form_carrier_basis_status": "COMPLETE",
        "lower_form_mapping_cone_basis_status": "IN_PROGRESS",
        "pure_diff_ghost_basis_status": (
            "NOT_APPLICABLE" if ghost_number == 0 else "IN_PROGRESS"
        ),
        "complete_relative_ansatz_status": "IN_PROGRESS",
    }
    return {**manifest, "basis_manifest_hash": canonical_sha256(manifest)}


def _select(
    records: tuple[dict[str, object], ...], ids: tuple[str, ...]
) -> list[dict[str, object]]:
    by_id = {str(record["class_id"]): record for record in records}
    if set(ids) - set(by_id):
        raise AssertionError("AFN0 slice requested an unknown candidate")
    return [_candidate_payload(by_id[class_id]) for class_id in ids]


@lru_cache(maxsize=1)
def afn0_production_results() -> dict[str, dict[str, object]]:
    analysis = dimension_four_candidate_analysis()
    counterterms = analysis["counterterms"]
    anomalies = analysis["anomalies"]

    h04_even_ids = ("CT_C2", "CT_E4", "CT_BOX_R")
    h04_odd_ids = ("CT_C_DUAL_C",)
    h14_even_ids = ("ANOM_OMEGA_C2", "ANOM_OMEGA_BOX_R")
    h14_odd_ids = ("ANOM_OMEGA_C_DUAL_C",)

    common = {
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "result_state": "IN_PROGRESS",
        "full_bv_promotion_status": "BLOCKED_CLASSICAL_ANTIFIELD_EXPORT",
        "coefficient_status": "NOT_COMPUTED",
    }
    h04_slices = [
        {
            "slice_id": "H04_AFN0_EVEN",
            "parity": "even",
            "basis_completeness": _basis_manifest(
                analysis,
                ghost_number=0,
                parity="even",
                candidate_ids=h04_even_ids,
            ),
            "candidates": _select(counterterms, h04_even_ids),
            "relative_cohomology_status": "UNDECIDED",
        },
        {
            "slice_id": "H04_AFN0_ODD",
            "parity": "odd",
            "basis_completeness": _basis_manifest(
                analysis,
                ghost_number=0,
                parity="odd",
                candidate_ids=h04_odd_ids,
            ),
            "candidates": _select(counterterms, h04_odd_ids),
            "relative_cohomology_status": "UNDECIDED",
        },
    ]
    h14_slices = [
        {
            "slice_id": "H14_AFN0_EVEN_WITHOUT_EULER",
            "parity": "even",
            "basis_completeness": _basis_manifest(
                analysis,
                ghost_number=1,
                parity="even",
                candidate_ids=h14_even_ids,
            ),
            "candidates": _select(anomalies, h14_even_ids),
            "relative_cohomology_status": "UNDECIDED",
            "excluded_required_candidate": {
                "representative_id": "ANOM_OMEGA_E4",
                "reason": "intrinsic Euler descent is in progress",
            },
        },
        {
            "slice_id": "H14_AFN0_ODD",
            "parity": "odd",
            "basis_completeness": _basis_manifest(
                analysis,
                ghost_number=1,
                parity="odd",
                candidate_ids=h14_odd_ids,
            ),
            "candidates": _select(anomalies, h14_odd_ids),
            "relative_cohomology_status": "UNDECIDED",
            "excluded_required_candidate": None,
        },
    ]
    h04 = {
        "result_id": "H04_AFN0_RESULT",
        **common,
        "ghost_number": 0,
        "form_degree": 4,
        "antifield_number": 0,
        "slices": h04_slices,
        "production_boundary": [
            "lower-form mapping-cone basis is not yet exhaustive",
            "dual nontriviality witnesses will be emitted only against that complete boundary space",
        ],
    }
    h14 = {
        "result_id": "H14_AFN0_RESULT",
        **common,
        "ghost_number": 1,
        "form_degree": 4,
        "antifield_number": 0,
        "slices": h14_slices,
        "production_boundary": [
            "intrinsic omega-Euler tower is incomplete",
            "lower-form mapping-cone and pure-Diff ghost bases are not yet exhaustive",
            "dual nontriviality witnesses will be emitted only against that complete boundary space",
        ],
    }
    return {"H04_AFN0_RESULT": h04, "H14_AFN0_RESULT": h14}
