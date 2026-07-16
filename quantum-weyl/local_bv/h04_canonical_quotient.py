"""Canonical antifield-zero ``H^{0,4}`` candidate quotients.

The calculation is deliberately scoped to the covariant local polynomial
algebra at engineering dimension four.  It generates both refined top-form
signatures, reduces the curvature contractions exactly, and assembles the
smallest relative complex needed to distinguish the Weyl-closed curvature
densities from ``Box R``.  Non-tensorial Chern--Simons primitives are not
members of this covariant carrier algebra; Euler and Pontryagin therefore
retain separate topological/global status fields.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .algebra import canonical_sha256
from .basis_exhaustiveness import BasisExhaustivenessProof, grading_signature_manifest
from .curvature import (
    RIEMANN,
    bianchi_relation,
    differential_bianchi_relation,
    pair_partitions,
    quadratic_curvature_analysis,
)
from .dimension_four_candidates import dimension_four_candidate_analysis
from .quotient import RelationQuotient
from .relative_cohomology import SparseMatrix
from .tensor_graphs import contraction_graph_artifact
from .tensors import TensorExpression, TensorFactor, TensorMonomial
from .triviality import box_r_triviality_analysis
from .weyl_target import dimension_four_weyl_target_analysis


EVEN_TOP_BASIS = ("CT_C2", "CT_E4", "CT_R2", "CT_BOX_R")
EVEN_INCOMING_DH_BASIS = ("CURRENT_GRAD_R",)
ODD_TOP_BASIS = ("CT_C_DUAL_C",)


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _vector(values: tuple[Fraction, ...]) -> list[dict[str, int]]:
    return [_fraction(value) for value in values]


def _signature(parity: str, curvature_count: int, derivative_count: int) -> dict[str, object]:
    rows = grading_signature_manifest(0, parity)["refined_grading_signatures"]
    matches = [
        row
        for row in rows
        if row["curvature_count"] == curvature_count
        and row["tensor_derivative_count"] == derivative_count
    ]
    if len(matches) != 1:
        raise AssertionError("ghost-zero refined signature is not unique")
    return matches[0]


def _two_derivative_curvature_monomial(
    pairing: tuple[tuple[int, int], ...]
) -> TensorMonomial:
    if sorted(slot for pair in pairing for slot in pair) != list(range(6)):
        raise ValueError("the two-derivative curvature pairing must cover six slots")
    labels = [0] * 6
    for index, (left, right) in enumerate(pairing):
        labels[left] = labels[right] = index
    return TensorMonomial(
        (TensorFactor(RIEMANN, tuple(labels[:4]), tuple(labels[4:])),)
    )


@lru_cache(maxsize=1)
def _even_derivative_sector() -> dict[str, object]:
    pairings = tuple(pair_partitions(tuple(range(6))))
    raw = tuple(_two_derivative_curvature_monomial(pairing) for pairing in pairings)
    basis = {
        canonical
        for monomial in raw
        for sign, canonical in (monomial.canonicalize(),)
        if sign and canonical is not None
    }
    relations: dict[str, TensorExpression] = {}
    for monomial in raw:
        for relation in (
            bianchi_relation(monomial, 0),
            differential_bianchi_relation(monomial, 0),
        ):
            if relation:
                relations.setdefault(relation.canonical_hash(), relation)
    quotient = RelationQuotient(basis, tuple(relations.values()))
    graph = contraction_graph_artifact(_signature("even", 1, 2))
    divergence = graph["divergence_witness"]
    if (
        len(pairings) != 15
        or len(basis) != 2
        or quotient.relation_rank != 1
        or quotient.quotient_dimension != 1
        or divergence["status"] != "VERIFIED_EVERY_RAW_GRAPH"
        or divergence["graphwise_current_count"] != 15
    ):
        raise AssertionError("even two-derivative curvature quotient drifted")
    return {
        "signature": _signature("even", 1, 2),
        "raw_pairing_count": len(pairings),
        "canonical_orbit_count": len(basis),
        "relation_count": len(relations),
        "relation_rank": quotient.relation_rank,
        "quotient_dimension_before_d_h": quotient.quotient_dimension,
        "graphwise_divergence_count": divergence["graphwise_current_count"],
        "graphwise_current_manifest_hash": divergence[
            "graphwise_current_manifest_hash"
        ],
        "quotient_dimension_mod_d_h": 0,
        "resolution": "TOTAL_DERIVATIVE_ONLY",
        "graph_artifact_hash": graph["artifact_hash"],
    }


def _pair(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


@lru_cache(maxsize=1)
def h04_canonical_quotient_analysis() -> dict[str, object]:
    candidates = dimension_four_candidate_analysis()
    curvature = quadratic_curvature_analysis()
    derivative = _even_derivative_sector()
    if curvature["quotient_dimension"] != 3 or candidates["closed_kernel_dimension"] != 2:
        raise AssertionError("even curvature-square closure dimensions drifted")

    # Coordinates are (C2, E4, R2, BoxR).  At AFN0 and ghost number zero
    # there is no negative-ghost-number Q source.  The sole covariant
    # dimension-four divergence is BoxR, while R2 has the nonzero integrated
    # Weyl row -12 R Box(omega).
    q_matrix = SparseMatrix.zero(len(EVEN_TOP_BASIS), 0)
    dh_matrix = SparseMatrix(
        len(EVEN_TOP_BASIS), len(EVEN_INCOMING_DH_BASIS), {(3, 0): Fraction(1)}
    )
    boundary_matrix = dh_matrix
    obstruction = SparseMatrix(1, len(EVEN_TOP_BASIS), {(0, 2): Fraction(-12)})
    if obstruction.compose(boundary_matrix).entries:
        raise AssertionError("the BoxR boundary failed relative closure")
    representatives = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
    )
    boundary_column = (Fraction(0), Fraction(0), Fraction(0), Fraction(1))
    closure_span = SparseMatrix.from_dense(tuple(zip(boundary_column, *representatives)))
    if boundary_matrix.rank() != 1 or obstruction.rank() != 1 or closure_span.rank() != 3:
        raise AssertionError("even H04 relative ranks drifted")
    for representative in representatives:
        if _pair(boundary_column, representative) or _pair(representative, representative) != 1:
            raise AssertionError("even H04 dual witness failed")

    odd_target = dimension_four_weyl_target_analysis()["odd"]
    odd_derivative_graph = contraction_graph_artifact(_signature("odd", 1, 2))
    odd_divergence = odd_derivative_graph["divergence_witness"]
    if (
        odd_target["quotient_dimension"] != 1
        or odd_derivative_graph["raw_generation"]["raw_contraction_graph_count"] != 15
        or odd_divergence["status"] != "VERIFIED_EVERY_RAW_GRAPH"
        or odd_divergence["graphwise_current_count"] != 15
    ):
        raise AssertionError("odd H04 carrier reduction drifted")
    odd_q = SparseMatrix.zero(1, 0)
    odd_dh = SparseMatrix.zero(1, 0)
    odd_obstruction = SparseMatrix.zero(0, 1)
    odd_representative = (Fraction(1),)

    top_manifest = {
        "even_basis": list(EVEN_TOP_BASIS),
        "odd_basis": list(ODD_TOP_BASIS),
        "signature_resolutions": {
            "even_nabla2_curvature": "ONE_BOX_R_DIRECTION_THEN_D_H_EXACT",
            "even_curvature_squared": "THREE_DIMENSIONAL_RIEMANN_BIANCHI_QUOTIENT",
            "odd_nabla2_curvature": "EVERY_RAW_GRAPH_HAS_COVARIANT_DIVERGENCE_WITNESS",
            "odd_curvature_squared": "ONE_DIMENSIONAL_FOUR_DIMENSIONAL_WEYL_PSEUDOSCALAR",
        },
    }
    identity_manifest = {
        "even_Q_matrix": q_matrix.canonical_payload(),
        "even_d_h_matrix": dh_matrix.canonical_payload(),
        "even_closure_obstruction": obstruction.canonical_payload(),
        "odd_Q_matrix": odd_q.canonical_payload(),
        "odd_d_h_matrix": odd_dh.canonical_payload(),
        "odd_closure_obstruction": odd_obstruction.canonical_payload(),
        "negative_ghost_number_afn0_sources": "EMPTY",
        "covariant_carrier_policy": "NON_TENSORIAL_CHERN_SIMONS_PRIMITIVES_EXCLUDED",
    }
    orbit_manifest = {
        "even_derivative": derivative,
        "even_quadratic": {
            "raw_pairing_count": curvature["raw_pairing_count"],
            "canonical_monomial_count": curvature[
                "symmetry_canonical_monomial_count"
            ],
            "bianchi_relation_rank": curvature["bianchi_relation_rank"],
            "quotient_dimension": curvature["quotient_dimension"],
        },
        "odd_derivative": {
            "raw_graph_count": 15,
            "signed_symmetry_orbit_count": odd_derivative_graph[
                "symmetry_quotient"
            ]["symmetry_canonical_orbit_count"],
            "graphwise_divergence_count": odd_divergence[
                "graphwise_current_count"
            ],
            "graph_artifact_hash": odd_derivative_graph["artifact_hash"],
        },
        "odd_quadratic": {
            "raw_pairing_count": odd_target["raw_pairing_count"],
            "tracefree_ambient_dimension": odd_target[
                "tracefree_ambient_dimension"
            ],
            "relation_rank": odd_target["relation_rank"],
            "quotient_dimension": odd_target["quotient_dimension"],
            "riemann_to_weyl_identity": "Pontryagin(Riemann)=Pontryagin(Weyl)_IN_4D",
        },
    }
    proof = BasisExhaustivenessProof.create(
        basis_manifest=top_manifest,
        declared_bounds={
            "spacetime_dimension": 4,
            "ghost_number": 0,
            "form_degree": 4,
            "antifield_number": 0,
            "engineering_dimension": 4,
            "parities": ["even", "odd"],
            "locality_algebra": "COVARIANT_TENSOR_POLYNOMIALS",
        },
        generator_algebra={
            "top_generators": ["Riemann", "covariant_derivative", "metric", "epsilon"],
            "boundary_generators": list(EVEN_INCOMING_DH_BASIS),
            "noncovariant_connection_primitives": "EXCLUDED_FROM_DECLARED_COMPLEX",
        },
        grading_solution={
            "coarse_signature_count_per_parity": 3,
            "refined_signature_count_per_parity": 2,
            "all_four_refined_signatures_resolved": True,
        },
        orbit_enumeration=orbit_manifest,
        identity_quotient=identity_manifest,
        proof_artifact={
            "even_boundary_rank": 1,
            "even_closure_rank": 3,
            "even_quotient_dimension": 2,
            "odd_boundary_rank": 0,
            "odd_closure_rank": 1,
            "odd_quotient_dimension": 1,
            "normalized_dual_pairings": [_fraction(1), _fraction(1), _fraction(1)],
        },
    )
    proof.verify(expected_basis_manifest_hash=canonical_sha256(top_manifest))
    triviality = box_r_triviality_analysis()
    if not triviality["box_r"] or not triviality["box_r_primitive"]:
        raise AssertionError("BoxR expression vanished")

    analysis_hash = canonical_sha256(
        {
            "top_manifest": top_manifest,
            "identity_manifest": identity_manifest,
            "orbit_manifest": orbit_manifest,
            "proof": proof.canonical_payload(),
        }
    )
    return {
        "even": {
            "derivative_sector": derivative,
            "q_matrix": q_matrix,
            "dh_matrix": dh_matrix,
            "boundary_matrix": boundary_matrix,
            "closure_obstruction_matrix": obstruction,
            "closure_span_matrix": closure_span,
            "boundary_rank": 1,
            "closure_rank": 3,
            "quotient_dimension": 2,
            "representatives": representatives,
            "dual_witnesses": representatives,
        },
        "odd": {
            "derivative_graph": odd_derivative_graph,
            "quadratic_target": odd_target,
            "q_matrix": odd_q,
            "dh_matrix": odd_dh,
            "closure_obstruction_matrix": odd_obstruction,
            "boundary_rank": 0,
            "closure_rank": 1,
            "quotient_dimension": 1,
            "representative": odd_representative,
            "dual_witness": odd_representative,
        },
        "basis_exhaustiveness_proof": proof,
        "analysis_sha256": analysis_hash,
    }


def canonical_quotient_payload() -> dict[str, object]:
    analysis = h04_canonical_quotient_analysis()
    even = analysis["even"]
    odd = analysis["odd"]
    return {
        "result_id": "AFN0_H04_CANONICAL_QUOTIENT",
        "result_state": "COMPLETE_AFN0_COVARIANT_COUNTERTERM_CANDIDATE_QUOTIENT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "bounds": {
            "spacetime_dimension": 4,
            "ghost_number": 0,
            "form_degree": 4,
            "antifield_number": 0,
            "engineering_dimension": 4,
            "locality_algebra": "COVARIANT_TENSOR_POLYNOMIALS",
        },
        "even_sector": {
            "top_basis": list(EVEN_TOP_BASIS),
            "incoming_q_basis": [],
            "incoming_dh_basis": list(EVEN_INCOMING_DH_BASIS),
            "Q_matrix": even["q_matrix"].canonical_payload(),
            "d_h_matrix": even["dh_matrix"].canonical_payload(),
            "closure_obstruction_matrix": even[
                "closure_obstruction_matrix"
            ].canonical_payload(),
            "boundary_rank": even["boundary_rank"],
            "closure_rank": even["closure_rank"],
            "quotient_dimension": even["quotient_dimension"],
            "derivative_sector": even["derivative_sector"],
            "classes": [
                {
                    "representative_id": representative_id,
                    "relative_cohomology_status": "NONTRIVIAL",
                    "representative_coordinates": _vector(representative),
                    "dual_witness_type": "COMPLETE_NONTRIVIALITY_WITNESS",
                    "dual_witness_coordinates": _vector(witness),
                    "dual_pairing": _fraction(_pair(representative, witness)),
                    "topological_status": topological_status,
                }
                for representative_id, representative, witness, topological_status in zip(
                    ("CT_C2", "CT_E4"),
                    even["representatives"],
                    even["dual_witnesses"],
                    ("NONE", "EULER_GLOBAL_TOPOLOGICAL"),
                )
            ],
            "exact_classes": [
                {
                    "representative_id": "CT_BOX_R",
                    "relative_cohomology_status": "EXACT",
                    "primitive_id": "CURRENT_GRAD_R",
                    "equation": "BoxR = d_h(nabla R)",
                }
            ],
            "nonclosed_carriers": [
                {
                    "representative_id": "CT_R2",
                    "closure_status": "NOT_CLOSED_MOD_D",
                    "obstruction_coefficient": _fraction(-12),
                }
            ],
        },
        "odd_sector": {
            "top_basis": list(ODD_TOP_BASIS),
            "incoming_q_basis": [],
            "incoming_dh_basis": [],
            "Q_matrix": odd["q_matrix"].canonical_payload(),
            "d_h_matrix": odd["dh_matrix"].canonical_payload(),
            "closure_obstruction_matrix": odd[
                "closure_obstruction_matrix"
            ].canonical_payload(),
            "boundary_rank": odd["boundary_rank"],
            "closure_rank": odd["closure_rank"],
            "quotient_dimension": odd["quotient_dimension"],
            "derivative_sector": {
                "raw_graph_count": 15,
                "graphwise_divergence_count": odd["derivative_graph"][
                    "divergence_witness"
                ]["graphwise_current_count"],
                "resolution": "TOTAL_DERIVATIVE_ONLY",
                "graph_artifact_hash": odd["derivative_graph"]["artifact_hash"],
            },
            "classes": [
                {
                    "representative_id": "CT_C_DUAL_C",
                    "relative_cohomology_status": "NONTRIVIAL",
                    "representative_coordinates": _vector(odd["representative"]),
                    "dual_witness_type": "COMPLETE_NONTRIVIALITY_WITNESS",
                    "dual_witness_coordinates": _vector(odd["dual_witness"]),
                    "dual_pairing": _fraction(1),
                    "topological_status": "PONTRYAGIN_GLOBAL_TOPOLOGICAL",
                }
            ],
        },
        "basis_exhaustiveness_proof": analysis[
            "basis_exhaustiveness_proof"
        ].canonical_payload(),
        "checks": {
            "all_refined_top_signatures_resolved": "VERIFIED",
            "negative_ghost_number_afn0_sources_empty": "VERIFIED",
            "BoxR_explicit_divergence_primitive": "VERIFIED",
            "even_closure_kernel_mod_boundary_dimension_two": "VERIFIED",
            "odd_covariant_candidate_quotient_dimension_one": "VERIFIED",
            "normalized_complete_dual_witnesses": "VERIFIED",
        },
        "claim_boundary": [
            "This is the complete ghost-zero AFN0 candidate quotient in the declared covariant tensor-polynomial algebra at dimension four.",
            "Euler and Pontryagin retain global topological status; non-tensorial Chern-Simons primitives are outside the declared covariant carrier algebra.",
            "This does not include antifield-dependent classes or prove the full minimal BV H^{0,4}(s|d) theorem.",
            "It is LOCAL-ALGEBRAIC and does not compute coefficients, restore the QME, perform residual transfer, or certify Lorentzian quantization.",
        ],
        "analysis_sha256": analysis["analysis_sha256"],
    }
