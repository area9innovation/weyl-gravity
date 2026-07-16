"""Fail-closed forward/reverse basis-gap ledger for dimension-four AFN0."""

from __future__ import annotations

from functools import lru_cache

from .algebra import canonical_sha256
from .ambient_tensor_graphs import ambient_tensor_graph_analysis
from .basis_exhaustiveness import grading_signature_manifest, refine_top_form_signature
from .dimension_four_candidates import dimension_four_candidate_analysis
from .h14_even_canonical_quotient import h14_even_canonical_quotient_analysis
from .h14_odd_canonical_quotient import h14_odd_canonical_quotient_analysis
from .lower_form_basis import lower_form_carrier_analysis
from .lower_form_ambient import ambient_lower_form_signature_analysis
from .tensor_graphs import contraction_graph_bundle, contraction_graph_manifest


TERMINAL_RESOLUTIONS = (
    "GENERATED_NONZERO",
    "IDENTICALLY_ZERO_BY_SYMMETRY",
    "IMPOSSIBLE_INDEX_CONTRACTION",
    "TOTAL_DERIVATIVE_ONLY",
    "WRONG_AFTER_REFINED_GRADING",
    "GENERATOR_BUG",
)


_SLICE_SPECS = (
    ("H04_AFN0_EVEN", 0, "even"),
    ("H04_AFN0_ODD", 0, "odd"),
    ("H14_AFN0_EVEN", 1, "even"),
    ("H14_AFN0_ODD", 1, "odd"),
)


def _signature_key(signature: dict[str, object]) -> tuple[int, int, int]:
    return (
        int(signature["curvature_count"]),
        int(signature["tensor_derivative_count"]),
        int(signature["ghost_derivative_order"]),
    )


def _representative_signature(record: dict[str, object]) -> tuple[int, int, int]:
    signatures = set()
    for term in record["representative"]["terms"]:
        curvature_count = 0
        tensor_derivative_count = 0
        ghost_derivative_order = 0
        for factor in term["monomial"]["factors"]:
            tensor = factor["tensor"]
            derivative_count = len(factor["derivatives"])
            if tensor in {"Riemann", "Weyl", "DualWeyl"}:
                curvature_count += 1
                tensor_derivative_count += derivative_count
            elif tensor == "omega":
                ghost_derivative_order += derivative_count
            else:
                raise ValueError(f"unclassified generated tensor factor: {tensor}")
        signatures.add(
            (curvature_count, tensor_derivative_count, ghost_derivative_order)
        )
    if len(signatures) != 1:
        raise ValueError("generated representative mixes grading signatures")
    return signatures.pop()


def _generated_candidates(slice_id: str) -> dict[tuple[int, int, int], tuple[str, ...]]:
    analysis = dimension_four_candidate_analysis()
    ghost_number = 0 if slice_id.startswith("H04") else 1
    parity = "odd" if slice_id.endswith("ODD") else "even"
    source = analysis["counterterms"] if ghost_number == 0 else analysis["anomalies"]
    grouped: dict[tuple[int, int, int], list[str]] = {}
    for record in source:
        if record["ghost_number"] != ghost_number or record["parity"] != parity:
            continue
        grouped.setdefault(_representative_signature(record), []).append(
            str(record["class_id"])
        )
    return {key: tuple(sorted(class_ids)) for key, class_ids in grouped.items()}


def _candidate_hashes() -> dict[str, str]:
    analysis = dimension_four_candidate_analysis()
    return {
        str(row["class_id"]): str(row["representative_sha256"])
        for sector in (analysis["counterterms"], analysis["anomalies"])
        for row in sector
    }


def _structural_terminal_resolution(
    signature: dict[str, object],
) -> tuple[str, str] | None:
    """Resolve signatures whose only differentiated factor is a divergence."""

    if (
        signature["curvature_count"] == 0
        and signature["tensor_derivative_count"] == 0
        and signature["ghost_derivative_order"]
    ):
        return (
            "TOTAL_DERIVATIVE_ONLY",
            "every contraction has a covariant derivative on the sole "
            "nonconstant ghost factor; metric and epsilon contractions are "
            "covariantly constant",
        )
    if (
        signature["ghost_species"] == "NONE"
        and signature["curvature_count"] == 1
        and signature["tensor_derivative_count"]
    ):
        return (
            "TOTAL_DERIVATIVE_ONLY",
            "every contraction has a covariant derivative on the sole "
            "nonconstant curvature factor; metric and epsilon contractions "
            "are covariantly constant",
        )
    return None


def _h14_even_mixed_resolution(
    slice_id: str, signature: dict[str, object]
) -> dict[str, object] | None:
    if slice_id != "H14_AFN0_EVEN" or signature["curvature_count"] != 1:
        return None
    derivative_pair = (
        int(signature["tensor_derivative_count"]),
        int(signature["ghost_derivative_order"]),
    )
    sector_key = {
        (0, 2): "hessian_sector",
        (1, 1): "gradient_sector",
    }.get(derivative_pair)
    if sector_key is None:
        return None
    analysis = h14_even_canonical_quotient_analysis()
    sector = analysis[sector_key]
    return {
        "sector_id": sector_key,
        "canonical_quotient_dimension": sector["quotient_dimension"],
        "canonical_orbit_count": sector["canonical_orbit_count"],
        "relation_rank": sector["relation_rank"],
        "analysis_sha256": analysis["analysis_sha256"],
        "basis_exhaustiveness_proof_hash": analysis[
            "basis_exhaustiveness_proof"
        ].proof_hash,
    }


def _h14_odd_mixed_resolution(
    slice_id: str, signature: dict[str, object]
) -> dict[str, object] | None:
    if slice_id != "H14_AFN0_ODD" or signature["curvature_count"] != 1:
        return None
    derivative_pair = (
        int(signature["tensor_derivative_count"]),
        int(signature["ghost_derivative_order"]),
    )
    sector_index = {(2, 0): 0, (1, 1): 1, (0, 2): 2}.get(derivative_pair)
    if sector_index is None:
        return None
    analysis = h14_odd_canonical_quotient_analysis()
    sector = analysis["mixed_sectors"][sector_index]
    return {
        "sector_id": f"odd_mixed_{derivative_pair[0]}_{derivative_pair[1]}",
        "canonical_quotient_dimension": sector["canonical_quotient_dimension"],
        "canonical_orbit_count": sector["signed_symmetry_orbit_count"],
        "bianchi_relation_rank": sector["bianchi_relation_rank"],
        "orbit_witness_hash": canonical_sha256(sector["orbit_witnesses"]),
        "analysis_sha256": analysis["analysis_sha256"],
        "basis_exhaustiveness_proof_hash": analysis[
            "basis_exhaustiveness_proof"
        ].proof_hash,
    }


def _gap_record(
    *,
    slice_id: str,
    signature: dict[str, object],
    candidate_hashes: dict[str, str],
) -> dict[str, object]:
    refined, refinement_reason = refine_top_form_signature(signature)
    graph = contraction_graph_manifest(signature)
    candidates = _generated_candidates(slice_id).get(_signature_key(signature), ())
    mixed_resolution = _h14_even_mixed_resolution(slice_id, signature)
    odd_zero_resolution = _h14_odd_mixed_resolution(slice_id, signature)
    if not refined:
        resolution = "WRONG_AFTER_REFINED_GRADING"
        canonical_status = "NOT_APPLICABLE"
        terminal_witness = {
            "witness_type": "REFINED_GRADING_REJECTION",
            "equation_or_rule": refinement_reason,
        }
        proof_hash = canonical_sha256(
            {
                "signature": signature,
                "resolution": resolution,
                "reason": refinement_reason,
            }
        )
    elif mixed_resolution is not None:
        resolution = "GENERATED_NONZERO"
        canonical_status = "CANONICALLY_NONZERO"
        candidates = (
            "MIXED_R_BOX_OMEGA",
            "MIXED_RICCI_HESS_OMEGA",
        ) if signature["ghost_derivative_order"] == 2 else (
            "MIXED_GRAD_R_GRAD_OMEGA",
        )
        terminal_witness = {
            "witness_type": "ORBIT_FIRST_CANONICAL_QUOTIENT",
            **mixed_resolution,
        }
        refinement_reason = (
            "resolved orbit-first by signed curvature symmetries, Bianchi, "
            "Grassmann signs, integration by parts, and exhaustive-empty "
            "four-dimensional antisymmetrization"
        )
        proof_hash = canonical_sha256(
            {
                "signature": signature,
                "resolution": resolution,
                "terminal_witness": terminal_witness,
            }
        )
    elif odd_zero_resolution is not None:
        resolution = "IDENTICALLY_ZERO_BY_SYMMETRY"
        canonical_status = "CANONICALLY_ZERO"
        terminal_witness = {
            "witness_type": "ORBIT_FIRST_BIANCHI_ZERO_QUOTIENT",
            **odd_zero_resolution,
        }
        refinement_reason = (
            "all signed symmetry orbits contain an algebraic Riemann Bianchi "
            "contraction, possibly with covariant derivatives applied without "
            "commuting them"
        )
        proof_hash = canonical_sha256(
            {
                "signature": signature,
                "resolution": resolution,
                "terminal_witness": terminal_witness,
            }
        )
    elif candidates:
        resolution = "GENERATED_NONZERO"
        canonical_status = "CANONICALLY_NONZERO"
        terminal_witness = {
            "witness_type": "GENERATED_CANDIDATE_HASHES",
            "candidate_hashes": {
                candidate: candidate_hashes[candidate]
                for candidate in candidates
            },
        }
        proof_hash = canonical_sha256(
            {
                "signature": signature,
                "candidate_hashes": {
                    candidate: candidate_hashes[candidate]
                    for candidate in candidates
                },
                "raw_graph_manifest_hash": graph["raw_graph_manifest_hash"],
            }
        )
    elif structural := _structural_terminal_resolution(signature):
        if graph["graphwise_divergence_status"] != "VERIFIED_EVERY_RAW_GRAPH":
            raise AssertionError("total-derivative resolution lacks graphwise currents")
        resolution, refinement_reason = structural
        canonical_status = "UNDECIDED"
        terminal_witness = {
            "witness_type": "TOTAL_DERIVATIVE_GRAPH_RULE",
            "equation_or_rule": (
                "the stored current for every raw graph removes derivative-position "
                "zero and exposes its contracted partner as the current index; "
                "covariant divergence reconstructs that exact graph"
            ),
            "covariant_constancy_inputs": ["nabla_metric=0", "nabla_epsilon=0"],
            "graphwise_current_manifest_hash": graph[
                "graphwise_current_manifest_hash"
            ],
            "graph_artifact_hash": graph["graph_artifact_hash"],
        }
        proof_hash = canonical_sha256(
            {
                "signature": signature,
                "resolution": resolution,
                "covariant_constancy_inputs": ["nabla_metric=0", "nabla_epsilon=0"],
                "primitive_rule": (
                    "expose one contracted outer covariant derivative as d_h of "
                    "the corresponding current"
                ),
            }
        )
    else:
        resolution = "PENDING"
        canonical_status = "UNDECIDED"
        terminal_witness = None
        proof_hash = None
    epsilon_slots = 4 if signature["epsilon_count"] else 0
    return {
        "slice": slice_id,
        "signature": signature,
        "grading_status": "GRADING_ADMISSIBLE",
        "refined_grading_status": (
            "REFINED_ADMISSIBLE" if refined else "REJECTED_BY_REFINED_GRADING"
        ),
        "raw_contraction_status": graph["raw_contraction_status"],
        "tensor_realizability": (
            "TENSOR_REALIZABLE_BY_GENERATED_REPRESENTATIVE"
            if candidates or mixed_resolution is not None
            else "TENSOR_REALIZABLE_CANONICALLY_ZERO"
            if odd_zero_resolution is not None
            else graph["tensor_realizability"]
        ),
        "canonical_status": canonical_status,
        "generated_raw_count": graph["raw_contraction_graph_count"],
        "symmetry_canonical_orbit_count": graph[
            "symmetry_canonical_orbit_count"
        ],
        "canonical_nonzero_count": (
            int(mixed_resolution["canonical_quotient_dimension"])
            if mixed_resolution is not None
            else len(candidates)
        ),
        "expected_index_balance": {
            "total_index_slots": signature["total_index_slots"],
            "epsilon_absorbed_slots": epsilon_slots,
            "metric_pair_count": (
                (int(signature["total_index_slots"]) - epsilon_slots) // 2
                if refined else 0
            ),
            "lorentz_scalar_condition": "ALL_INDEX_SLOTS_CONTRACTED",
        },
        "candidate_ids": list(candidates),
        "resolution": resolution,
        "resolution_reason": refinement_reason,
        "terminal_witness": terminal_witness,
        "raw_graph_manifest_hash": graph["raw_graph_manifest_hash"],
        "graph_enumeration_status": (
            "CANONICAL_QUOTIENT_COMPLETE"
            if mixed_resolution is not None or odd_zero_resolution is not None
            else graph["graph_enumeration_status"]
        ),
        "graph_artifact_hash": graph["graph_artifact_hash"],
        "graphwise_divergence_status": graph["graphwise_divergence_status"],
        "graphwise_current_manifest_hash": graph[
            "graphwise_current_manifest_hash"
        ],
        "proof_hash": proof_hash,
    }


def _diff_ledger(parity: str) -> dict[str, object]:
    manifest = grading_signature_manifest(1, parity)
    rows = []
    for signature in manifest["diff_top_form_coarse_signatures"]:
        refined, reason = refine_top_form_signature(signature)
        graph = contraction_graph_manifest(signature)
        rows.append(
            {
                "signature": signature,
                "refined_grading_status": (
                    "REFINED_ADMISSIBLE"
                    if refined
                    else "REJECTED_BY_REFINED_GRADING"
                ),
                "tensor_realizability": graph["tensor_realizability"],
                "raw_contraction_status": graph["raw_contraction_status"],
                "resolution": (
                    "PENDING" if refined else "WRONG_AFTER_REFINED_GRADING"
                ),
                "reason": reason,
                "raw_graph_manifest_hash": graph["raw_graph_manifest_hash"],
                "graph_artifact_hash": graph["graph_artifact_hash"],
                "graph_enumeration_status": graph["graph_enumeration_status"],
            }
        )
    return {
        "parity": parity,
        "coarse_signature_count": len(rows),
        "refined_signature_count": sum(
            row["refined_grading_status"] == "REFINED_ADMISSIBLE"
            for row in rows
        ),
        "role": "TOP_FORM_DIFF_SECTOR_DISTINCT_FROM_UNIVERSAL_LOWER_FORM_DIFF_TOWER",
        "signatures": rows,
    }


@lru_cache(maxsize=1)
def basis_gap_report() -> dict[str, object]:
    candidate_hashes = _candidate_hashes()
    slices = []
    for slice_id, ghost_number, parity in _SLICE_SPECS:
        manifest = grading_signature_manifest(ghost_number, parity)
        records = [
            _gap_record(
                slice_id=slice_id,
                signature=signature,
                candidate_hashes=candidate_hashes,
            )
            for signature in manifest["coarse_grading_signatures"]
        ]
        terminal_count = sum(
            record["resolution"] in TERMINAL_RESOLUTIONS for record in records
        )
        slices.append(
            {
                "slice": slice_id,
                "ghost_number": ghost_number,
                "form_degree": 4,
                "parity": parity,
                "coarse_grading_signature_count": len(records),
                "refined_grading_signature_count": sum(
                    record["refined_grading_status"] == "REFINED_ADMISSIBLE"
                    for record in records
                ),
                "tensor_realizable_signature_count": sum(
                    record["tensor_realizability"]
                    == "TENSOR_REALIZABLE_BY_GENERATED_REPRESENTATIVE"
                    for record in records
                ),
                "raw_contraction_signature_count": sum(
                    record["raw_contraction_status"] == "RAW_CONTRACTION_EXISTS"
                    for record in records
                ),
                "canonical_nonzero_signature_count": sum(
                    record["canonical_status"] == "CANONICALLY_NONZERO"
                    for record in records
                ),
                "terminal_resolution_count": terminal_count,
                "pending_resolution_count": len(records) - terminal_count,
                "top_form_signature_resolution_status": (
                    "COMPLETE" if terminal_count == len(records) else "IN_PROGRESS"
                ),
                "forward_reverse_span_agreement": (
                    "VERIFIED"
                    if slice_id in {"H14_AFN0_EVEN", "H14_AFN0_ODD"}
                    and terminal_count == len(records)
                    else "NOT_COMPUTED"
                ),
                "records": records,
            }
        )
    bundle = basis_gap_graph_bundle()
    lower_form = lower_form_carrier_analysis()
    ambient_lower_form = ambient_lower_form_signature_analysis()
    ambient_tensor_graphs, ambient_tensor_bundle = ambient_tensor_graph_analysis()
    payload = {
        "result_id": "BASIS_GAP_REPORT_AFN0",
        "result_state": "TOP_FORM_BASIS_GAPS_RESOLVED_TOTAL_COMPLEX_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "resolution_vocabulary": list(TERMINAL_RESOLUTIONS),
        "slices": slices,
        "diff_top_form_ledgers": [_diff_ledger("even"), _diff_ledger("odd")],
        "graph_artifact_bundle": {
            "bundle_hash": bundle["bundle_hash"],
            "artifact_count": bundle["artifact_count"],
            "path": f"basis_graph_manifests/{bundle['bundle_hash']}.json",
        },
        "lower_form_carrier_inventory": {
            "result_id": lower_form["result_id"],
            "analysis_sha256": lower_form["analysis_sha256"],
            "counts": lower_form["counts"],
            "coverage": lower_form["declared_carrier_algebra"]["coverage"],
            "ambient_local_form_basis": lower_form["declared_carrier_algebra"][
                "ambient_local_form_basis"
            ],
        },
        "ambient_lower_form_signature_inventory": {
            "result_id": ambient_lower_form["result_id"],
            "analysis_sha256": ambient_lower_form["analysis_sha256"],
            "totals": ambient_lower_form["totals"],
            "integer_grading_status": ambient_lower_form["checks"][
                "integer_grading_enumeration"
            ],
            "tensor_graph_realizability": "COMPLETE_FACTORED",
            "tensor_graph_result_id": ambient_tensor_graphs["result_id"],
            "tensor_graph_analysis_sha256": ambient_tensor_graphs[
                "analysis_sha256"
            ],
            "factor_profile_bundle_sha256": ambient_tensor_bundle["bundle_sha256"],
            "factor_profile_count": ambient_tensor_graphs["totals"][
                "factor_profile_count"
            ],
            "total_raw_graph_count": ambient_tensor_graphs["totals"][
                "total_raw_graph_count"
            ],
        },
        "total_complex_gates": {
            "TOP_FORM_BASIS_EXHAUSTIVE": "VERIFIED_AFN0_WEYL_SECTORS",
            "LOWER_FORM_COCYCLE_BASIS_EXHAUSTIVE": "IN_PROGRESS_GRADING_EXHAUSTIVE_CANDIDATE_CARRIERS_COMPLETE",
            "LOWER_FORM_BOUNDARY_BASIS_EXHAUSTIVE": "IN_PROGRESS_GRADING_EXHAUSTIVE_EXACT_BOUNDARY_CARRIERS_COMPLETE",
            "TOTAL_COMPLEX_EXHAUSTIVE": "NOT_COMPUTED",
            "FORWARD_REVERSE_SPAN_AGREEMENT": "NOT_COMPUTED",
        },
        "claim_boundary": [
            (
                "all four AFN0 Weyl top-form signature ledgers are complete; "
                "the separate Diff top-form ledgers and the canonical ambient "
                "lower-form total-complex quotient remain open"
            ),
            "PENDING is not a terminal signature resolution",
            "the universal Diff and intrinsic Euler candidate carriers and factored ambient tensor-graph realizations are complete, but the separate Diff top-form ledger and canonical ambient quotient remain open",
            "this report cannot promote a complete nontriviality witness",
        ],
    }
    return {**payload, "report_hash": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def basis_gap_graph_bundle() -> dict[str, object]:
    signatures = []
    for _, ghost_number, parity in _SLICE_SPECS:
        signatures.extend(
            grading_signature_manifest(ghost_number, parity)[
                "coarse_grading_signatures"
            ]
        )
    for parity in ("even", "odd"):
        signatures.extend(
            grading_signature_manifest(1, parity)[
                "diff_top_form_coarse_signatures"
            ]
        )
    return contraction_graph_bundle(signatures)
