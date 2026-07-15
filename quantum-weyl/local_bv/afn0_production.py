"""Fail-closed antifield-zero dimension-four production-run manifests.

These records execute the already complete top curvature-carrier generators
and bind their exact identities and known primitives.  They deliberately do
not promote familiar representatives to relative cohomology classes until
the lower-form and coboundary bases are exhaustive under the same bounds.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .algebra import canonical_sha256
from .basis_exhaustiveness import grading_signature_manifest
from .dimension_four_candidates import dimension_four_candidate_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
DESCENT_DATABASE_PATH = (
    "quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json"
)


@lru_cache(maxsize=None)
def _load_artifact(relative_path: str) -> tuple[dict[str, object], str]:
    path = REPOSITORY_ROOT / relative_path
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"closure artifact is not an object: {relative_path}")
    return payload, hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_receipt(relative_path: str) -> dict[str, str]:
    payload, digest = _load_artifact(relative_path)
    result_id = payload.get("result_id")
    if not isinstance(result_id, str):
        raise ValueError(f"closure artifact has no result_id: {relative_path}")
    return {"path": relative_path, "sha256": digest, "result_id": result_id}


def _verify_intrinsic_certificate(
    representative_id: str,
    relative_path: str,
) -> str:
    certificate, _ = _load_artifact(relative_path)
    result_id = certificate.get("result_id")
    if representative_id in {"CT_E4", "ANOM_OMEGA_E4"}:
        if not (
            result_id == "EULER_TRANSGRESSION_CERTIFICATE"
            and certificate.get("checks", {}).get(
                "epsilon_contracted_top_reconstruction"
            )
            == "VERIFIED"
        ):
            raise ValueError("Euler closure certificate is incomplete")
        if representative_id == "CT_E4":
            if (
                certificate.get("checks", {}).get(
                    "QE4_plus_d_descent_descendant"
                )
                != "VERIFIED"
            ):
                raise ValueError("Euler counterterm transgression is incomplete")
            return "EULER_VARIATIONAL_TRANSGRESSION_AND_HEAD_VERIFIED"
        if (
            certificate.get("checks", {}).get(
                "omega_E4_intrinsic_descent_continuation"
            )
            != "NONTRIVIAL_COMPLETE"
        ):
            raise ValueError("Euler anomaly intrinsic tower is incomplete")
        return "EULER_INTRINSIC_TOWER_AND_HEAD_VERIFIED"
    if representative_id in {"CT_BOX_R", "ANOM_OMEGA_BOX_R"}:
        trivializations = certificate.get("trivializations", {})
        if not (
            result_id == "TRIVIALITY_CERTIFICATE"
            and isinstance(trivializations, dict)
            and trivializations.get(representative_id, {}).get("class_status")
            == "EXACT"
        ):
            raise ValueError(f"exact closure witness is incomplete: {representative_id}")
        return "EXPLICIT_RELATIVE_TRIVIALIZATION_VERIFIED"

    catalogues = certificate.get("catalogues", {})
    catalogue_key = (
        "anomaly_candidate_ids"
        if representative_id.startswith("ANOM_")
        else "counterterm_candidate_ids"
    )
    if not (
        result_id == "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE"
        and representative_id in catalogues.get(catalogue_key, [])
        and certificate.get("checks", {}).get("strict_density_diff_descent")
        == "VERIFIED"
    ):
        raise ValueError(f"candidate closure certificate is incomplete: {representative_id}")
    return "STRICT_DENSITY_CANDIDATE_CLOSURE_VERIFIED"


def _closure_candidate_payload(record: dict[str, object]) -> dict[str, object]:
    representative_id = str(record["class_id"])
    descent_path = str(record["descent_certificate"])
    intrinsic_path = str(record["intrinsic_weyl_descent_certificate"])
    horizontal, _ = _load_artifact(descent_path)
    database, database_digest = _load_artifact(DESCENT_DATABASE_PATH)
    if not (
        horizontal.get("result_id") == "HORIZONTAL_BICOMPLEX_CERTIFICATE"
        and horizontal.get("database", {}).get("sha256")
        == canonical_sha256(database)
        and horizontal.get("checks", {}).get(
            "totalized_Q_dh_anticommutator_zero"
        )
        == "VERIFIED"
    ):
        raise ValueError("horizontal closure certificate or descent database drifted")
    entries = {
        entry["representative_id"]: entry
        for entry in database.get("entries", [])
        if isinstance(entry, dict) and "representative_id" in entry
    }
    entry = entries.get(representative_id)
    if not (
        entry
        and entry.get("diff_descent_status") == "NONZERO_DIFF_TOWER"
        and entry.get("intrinsic_weyl_descent_status")
        == record["intrinsic_weyl_descent_status"]
        and entry.get("relative_cohomology_status")
        == ("EXACT" if record["class_status"] == "EXACT" else "UNDECIDED")
    ):
        raise ValueError(f"descent database status drifted: {representative_id}")
    intrinsic_semantic_check = _verify_intrinsic_certificate(
        representative_id, intrinsic_path
    )
    return {
        "representative_id": representative_id,
        "representative_sha256": record["representative_sha256"],
        "closure_status": "CLOSED",
        "closure_witness": {
            "certificate": _artifact_receipt(descent_path),
            "intrinsic_certificate": _artifact_receipt(intrinsic_path),
            "descent_database": {
                **_artifact_receipt(DESCENT_DATABASE_PATH),
                "canonical_sha256": canonical_sha256(database),
            },
            "semantic_status": {
                "diff_descent_status": entry["diff_descent_status"],
                "intrinsic_weyl_descent_status": entry[
                    "intrinsic_weyl_descent_status"
                ],
                "relative_cohomology_status": entry[
                    "relative_cohomology_status"
                ],
                "intrinsic_certificate_check": intrinsic_semantic_check,
                "verification_status": "VERIFIED_FROM_HASH_BOUND_ARTIFACTS",
            },
        },
    }


def _quotient_candidate_payload(record: dict[str, object]) -> dict[str, object]:
    exact = record["class_status"] == "EXACT"
    return {
        "representative_id": record["class_id"],
        "representative_sha256": record["representative_sha256"],
        "relative_cohomology_status": "EXACT" if exact else "UNDECIDED",
        "exactness_witness": record["trivialization"] if exact else None,
        "nonmembership_witness": None,
        "permitted_nonmembership_witness_type": (
            "NOT_APPLICABLE_EXACT"
            if exact
            else "TRUNCATED_NONMEMBERSHIP_WITNESS"
        ),
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
        "structural_grading_enumeration": grading_signature_manifest(
            ghost_number, parity
        ),
        "candidate_ids": list(candidate_ids),
        "top_curvature_carrier_basis_status": "COMPLETE",
        "full_top_form_basis_status": "IN_PROGRESS",
        "lower_form_mapping_cone_basis_status": "IN_PROGRESS",
        "pure_diff_ghost_basis_status": (
            "NOT_APPLICABLE" if ghost_number == 0 else "IN_PROGRESS"
        ),
        "complete_relative_ansatz_status": "IN_PROGRESS",
    }
    return {**manifest, "basis_manifest_hash": canonical_sha256(manifest)}


def _select(
    records: tuple[dict[str, object], ...], ids: tuple[str, ...]
) -> tuple[dict[str, object], ...]:
    by_id = {str(record["class_id"]): record for record in records}
    if set(ids) - set(by_id):
        raise AssertionError("AFN0 slice requested an unknown candidate")
    return tuple(by_id[class_id] for class_id in ids)


def _slice(
    *,
    analysis: dict[str, object],
    slice_id: str,
    closure_result_id: str,
    quotient_result_id: str,
    ghost_number: int,
    parity: str,
    records: tuple[dict[str, object], ...],
    candidate_ids: tuple[str, ...],
    excluded_required_candidate: dict[str, str] | None = None,
) -> dict[str, object]:
    selected = _select(records, candidate_ids)
    return {
        "slice_id": slice_id,
        "parity": parity,
        "basis_completeness": _basis_manifest(
            analysis,
            ghost_number=ghost_number,
            parity=parity,
            candidate_ids=candidate_ids,
        ),
        "closure_result": {
            "result_id": closure_result_id,
            "result_state": "CLOSURE_RESULT",
            "closure_scope": "TOP_RELATIVE_CLOSURE",
            "candidates": [
                _closure_candidate_payload(record) for record in selected
            ],
        },
        "truncated_quotient_result": {
            "result_id": quotient_result_id,
            "result_state": "TRUNCATED_QUOTIENT_RESULT",
            "basis_exhaustiveness_status": "TRUNCATED",
            "relative_cohomology_status": "UNDECIDED",
            "candidates": [
                _quotient_candidate_payload(record) for record in selected
            ],
        },
        "excluded_required_candidate": excluded_required_candidate,
    }


@lru_cache(maxsize=1)
def afn0_production_results() -> dict[str, dict[str, object]]:
    analysis = dimension_four_candidate_analysis()
    counterterms = analysis["counterterms"]
    anomalies = analysis["anomalies"]

    h04_even_ids = ("CT_C2", "CT_E4", "CT_BOX_R")
    h04_odd_ids = ("CT_C_DUAL_C",)
    h14_even_ids = (
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_BOX_R",
    )
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
        _slice(
            analysis=analysis,
            slice_id="H04_AFN0_EVEN",
            closure_result_id="H04_AFN0_EVEN_CLOSURE",
            quotient_result_id="H04_AFN0_EVEN_TRUNCATED_QUOTIENT",
            ghost_number=0,
            parity="even",
            records=counterterms,
            candidate_ids=h04_even_ids,
        ),
        _slice(
            analysis=analysis,
            slice_id="H04_AFN0_ODD",
            closure_result_id="H04_AFN0_ODD_CLOSURE",
            quotient_result_id="H04_AFN0_ODD_TRUNCATED_QUOTIENT",
            ghost_number=0,
            parity="odd",
            records=counterterms,
            candidate_ids=h04_odd_ids,
        ),
    ]
    h14_slices = [
        _slice(
            analysis=analysis,
            slice_id="H14_AFN0_EVEN",
            closure_result_id="H14_AFN0_EVEN_CLOSURE",
            quotient_result_id="H14_AFN0_EVEN_TRUNCATED_QUOTIENT",
            ghost_number=1,
            parity="even",
            records=anomalies,
            candidate_ids=h14_even_ids,
        ),
        _slice(
            analysis=analysis,
            slice_id="H14_AFN0_ODD",
            closure_result_id="H14_AFN0_ODD_CLOSURE",
            quotient_result_id="H14_AFN0_ODD_TRUNCATED_QUOTIENT",
            ghost_number=1,
            parity="odd",
            records=anomalies,
            candidate_ids=h14_odd_ids,
        ),
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
            "the complete intrinsic omega-Euler tower is included, but its relative class is undecided",
            "lower-form mapping-cone and pure-Diff ghost bases are not yet exhaustive",
            "dual nontriviality witnesses will be emitted only against that complete boundary space",
        ],
    }
    return {"H04_AFN0_RESULT": h04, "H14_AFN0_RESULT": h14}


def afn0_slice_results() -> dict[str, dict[str, object]]:
    """Return independently addressable closure and provisional quotient receipts."""

    outputs: dict[str, dict[str, object]] = {}
    for parent_id, parent in afn0_production_results().items():
        for slice_ in parent["slices"]:
            shared = {
                "parent_result_id": parent_id,
                "slice_id": slice_["slice_id"],
                "classical_commit": parent["classical_commit"],
                "dependency_tags": parent["dependency_tags"],
                "scope_label": parent["scope_label"],
                "ghost_number": parent["ghost_number"],
                "form_degree": parent["form_degree"],
                "antifield_number": parent["antifield_number"],
                "parity": slice_["parity"],
                "basis_manifest_hash": slice_["basis_completeness"][
                    "basis_manifest_hash"
                ],
            }
            for key in ("closure_result", "truncated_quotient_result"):
                payload = slice_[key]
                result_id = str(payload["result_id"])
                outputs[result_id] = {**shared, **payload}
    return outputs
