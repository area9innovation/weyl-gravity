#!/usr/bin/env python3
"""Generate the common-envelope quantum residual-atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from analytic_completion.one_particle.krein import FAMILIES, FORM_SIGN
from bridge.metric_preimages.all_energy import BRANCH_MINIMUM


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
OUTPUT = HERE / "quantum-atlas-fragment.json"
SCHEMA = HERE / "schema/quantum-residual-atlas-fragment-v1.schema.json"
COMMON_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]

DEPENDENCIES = {
    "polarized_state": ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
    "one_particle_krein": ROOT / "analytic_completion/certificates/one_particle_krein.json",
    "positive_frequency_transform": ROOT / "covariant_completion/certificates/positive_frequency_transform.json",
    "curvature_CCR": QROOT / "lorentzian/certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json",
    "Berger_causal_chain": QROOT / "lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "Berger_Hadamard_gate": QROOT / "lorentzian/certificates/BERGER_HADAMARD_CONSTRUCTION_GATE.json",
    "Slavnov_preflight": QROOT / "anomalies/certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json",
    "Euclidean_elliptic_complex": QROOT / "spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "nonconformal_coefficient_match": QROOT / "spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
    "regulated_Slavnov_breaking": QROOT / "anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "unitary_matter_no_go": QROOT / "anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "WZ_compensator_preflight": QROOT / "anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "WZ_cotangent_lift": QROOT / "anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "WZ_extended_local_BV": QROOT / "anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "one_loop_Q1_disposition": QROOT / "transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_Gamma1": QROOT / "transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_TT_log_Gamma1": QROOT / "transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "curvature_squared_log_Gamma1": QROOT / "transfer/certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "FV_conformized_C2_log_Gamma1": QROOT / "transfer/certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
    "FV_anomaly_action_Ricci_sector": QROOT / "transfer/certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json",
    "algebraic_cubic_Weyl_carriers": QROOT / "transfer/certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json",
    "third_curvature_Weyl_manifest": QROOT / "transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "CPT_universal_third_curvature_kernels": QROOT / "transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
    "generic_physical_hessian_linear_curvature": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "generic_physical_hessian_n3_triangle_fixture": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json",
    "generic_physical_hessian_n3_five_carrier_projection": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_physical_hessian_n3_integration_obstruction": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json",
    "generic_physical_hessian_curvature_squared": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "generic_physical_hessian_mixed_H1_H2_corner_fixture": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json",
    "generic_physical_hessian_mellin_subtraction_scale_row": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json",
    "generic_physical_hessian_covariant_Volterra_carrier": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json",
    "generic_physical_hessian_H1_H2_contact_residue_projection": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json",
    "generic_physical_hessian_symmetric_mixed_boundary_incidence": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_triangle_corner_residues": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json",
    "generic_physical_hessian_full_boundary_incidence": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_H1_H2_contact_finite_rows": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json",
    "generic_physical_hessian_triangle_master_completeness": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json",
    "generic_physical_hessian_triangle_renormalized_master_values": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json",
    "generic_background_ghost_CPT_obstruction": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "generic_ghost_Endo_Duhamel_reduction": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json",
    "generic_ghost_n1_n2_Hodge_resolvent_reduction": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "generic_ghost_n1_n2_vector_CPT_projection": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json",
    "generic_ghost_longitudinal_Schur_resummation": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "generic_ghost_Schur_Schatten_split": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
    "generic_ghost_Schur_Wodzicki_residue": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
    "generic_ghost_Schur_weighted_trace_scale": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_ghost_Schur_finite_weighted_traces": QROOT / "spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
    "round_S4_ghost_Schur_zeta_factorization": QROOT / "spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json",
    "generic_ghost_Schur_weight_raised_zeta_factorization": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json",
    "generic_ghost_n3_adiabatic_carrier": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json",
    "generic_ghost_n3_triangle_kernel": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "generic_ghost_n3_five_carrier_projection": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_ghost_n3_barycentric_factorization": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json",
    "generic_ghost_n3_symmetric_point_simplex_integration": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json",
    "scalar_flat_K_Ricci_crosswalk": QROOT / "transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
    "BoxR_scheme_conversion": QROOT / "spectral/euclidean/certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json",
    "vacuum_cylinder_reduced_Bridge4": QROOT / "lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json",
    "general_tangent_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "finite_k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
    "smooth_secular_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
    "bounded_resonance_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(value: dict[str, Any]) -> str:
    identifier = value.get("result_id") or value.get("certificate_id") or value.get("schema")
    return str(identifier) if identifier is not None else "UNIDENTIFIED"


def _evidence(values: dict[str, dict[str, Any]], *names: str) -> list[dict[str, str]]:
    return [
        {
            "path": str(DEPENDENCIES[name].relative_to(ROOT)),
            "result_id": _artifact_id(values[name]),
            "sha256": _sha256(DEPENDENCIES[name]),
        }
        for name in names
    ]


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second_order(
    bounded: tuple[str, str],
    secular: tuple[str, str],
    causal: tuple[str, str],
) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _quantum_data(
    entry_kind: str,
    tags: list[str],
    *,
    imported: tuple[str, str],
    cocycle: tuple[str, str],
    exactness: tuple[str, str],
    pairing: tuple[str, str],
    complex_structure: tuple[str, str],
    hadamard: tuple[str, str],
    state_space: tuple[str, str],
    qme: tuple[str, str],
    lifecycle: tuple[str, str],
    particle: tuple[str, str],
    crosswalk: tuple[str, str],
) -> dict[str, Any]:
    return {
        "entry_kind": entry_kind,
        "dependency_tags": tags,
        "classical_mode_imported": _claim(*imported),
        "BRST_cocycle": _claim(*cocycle),
        "BRST_exactness": _claim(*exactness),
        "pairing_status": _claim(*pairing),
        "compatible_complex_structure": _claim(*complex_structure),
        "Hadamard_two_point_function": _claim(*hadamard),
        "state_space_status": _claim(*state_space),
        "anomaly_QME_dependency": _claim(*qme),
        "lifecycle_state": _claim(*lifecycle),
        "particle_interpretation": _claim(*particle),
        "carrier_crosswalk": _claim(*crosswalk),
    }


def _entry(
    identifier: str,
    scope: dict[str, Any],
    descriptions: dict[str, str],
    mode_data: dict[str, Any],
    quantum_data: dict[str, Any],
    evidence: list[dict[str, str]],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": mode_data,
        "quantum_data": quantum_data,
        "evidence": evidence,
        "claim_boundary": boundary,
    }


def _validate_inputs(values: dict[str, dict[str, Any]]) -> None:
    polarized = values["polarized_state"]
    krein = values["one_particle_krein"]
    transform = values["positive_frequency_transform"]
    curvature = values["curvature_CCR"]
    causal = values["Berger_causal_chain"]
    hadamard = values["Berger_Hadamard_gate"]
    slavnov = values["Slavnov_preflight"]
    elliptic = values["Euclidean_elliptic_complex"]
    coefficient = values["nonconformal_coefficient_match"]
    breaking = values["regulated_Slavnov_breaking"]
    matter_no_go = values["unitary_matter_no_go"]
    wz_preflight = values["WZ_compensator_preflight"]
    wz_lift = values["WZ_cotangent_lift"]
    wz_extended = values["WZ_extended_local_BV"]
    q1_disposition = values["one_loop_Q1_disposition"]
    anomaly_induced = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_log_Gamma1"]
    curvature_squared_log = values["curvature_squared_log_Gamma1"]
    fv_conformized_log = values["FV_conformized_C2_log_Gamma1"]
    fv_anomaly_ricci = values["FV_anomaly_action_Ricci_sector"]
    cubic_weyl = values["algebraic_cubic_Weyl_carriers"]
    third_curvature_weyl = values["third_curvature_Weyl_manifest"]
    cpt_kernels = values["CPT_universal_third_curvature_kernels"]
    physical_hessian_linear = values["generic_physical_hessian_linear_curvature"]
    physical_hessian_n3 = values["generic_physical_hessian_n3_triangle_fixture"]
    physical_hessian_n3_projection = values[
        "generic_physical_hessian_n3_five_carrier_projection"
    ]
    physical_hessian_n3_obstruction = values[
        "generic_physical_hessian_n3_integration_obstruction"
    ]
    physical_hessian_h2 = values["generic_physical_hessian_curvature_squared"]
    physical_hessian_mixed = values[
        "generic_physical_hessian_mixed_H1_H2_corner_fixture"
    ]
    physical_hessian_mellin = values[
        "generic_physical_hessian_mellin_subtraction_scale_row"
    ]
    physical_hessian_volterra = values[
        "generic_physical_hessian_covariant_Volterra_carrier"
    ]
    physical_hessian_contacts = values[
        "generic_physical_hessian_H1_H2_contact_residue_projection"
    ]
    physical_hessian_incidence = values[
        "generic_physical_hessian_symmetric_mixed_boundary_incidence"
    ]
    physical_hessian_triangle_residues = values[
        "generic_physical_hessian_triangle_corner_residues"
    ]
    physical_hessian_full_incidence = values[
        "generic_physical_hessian_full_boundary_incidence"
    ]
    physical_hessian_contact_finite = values[
        "generic_physical_hessian_H1_H2_contact_finite_rows"
    ]
    physical_hessian_triangle_masters = values[
        "generic_physical_hessian_triangle_master_completeness"
    ]
    physical_hessian_triangle_master_values = values[
        "generic_physical_hessian_triangle_renormalized_master_values"
    ]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n3_barycentric = values["generic_ghost_n3_barycentric_factorization"]
    generic_ghost_n3_symmetric = values["generic_ghost_n3_symmetric_point_simplex_integration"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    reduced_bridge4 = values["vacuum_cylinder_reduced_Bridge4"]
    general = values["general_tangent_cone"]
    k0 = values["finite_k0_cone"]
    smooth = values["smooth_secular_cone"]
    resonance = values["bounded_resonance_divisor"]

    if (
        FAMILIES != ("E", "A", "L")
        or BRANCH_MINIMUM != {"E": 2, "A": 3, "L": 4}
        or FORM_SIGN != {"E": 1, "A": -1, "L": -1}
        or polarized.get("schema") != "pure-weyl-polarized-state-complex-v1"
        or "L_+ and L_- are complementary Lagrangian polarizations"
        not in polarized.get("proved", [])
        or krein.get("classification") != "infinite-index Krein space"
        or transform.get("krein_signs") != {"A": -1, "E": 1, "L": -1}
        or transform.get("normalized_metric_modes_map_to_unit_coefficients") is not True
    ):
        raise ValueError("vacuum-cylinder reduced mode input drifted")

    comparison = curvature.get("observable_comparison", {})
    if (
        comparison.get("final_covariant_H4") != ["W_+^2", "W_-^2"]
        or comparison.get("final_H4_Gram") != [[1, 0], [0, 1]]
        or curvature.get("claim_flags", {}).get("CURVATURE_HADAMARD_STATE_CONSTRUCTED")
        is not False
        or causal.get("claim_flags", {}).get("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED")
        is not True
        or causal.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
        or hadamard.get("logical_separation", {}).get("complex_structure_or_covariance")
        != "NOT_CONSTRUCTED_ON_54_ROW_DISTRIBUTIONAL_COMPLEX"
        or hadamard.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
    ):
        raise ValueError("covariant/ Berger import boundary drifted")

    if (
        slavnov.get("claim_flags", {}).get("REGULATED_SLAVNOV_BREAKING_COMPUTED")
        is not False
        or slavnov.get("claim_flags", {}).get("QME_RESTORED") is not False
        or slavnov.get("claim_flags", {}).get("QME_OBSTRUCTED") is not False
    ):
        raise ValueError("QME lifecycle boundary drifted")
    if (
        elliptic.get("claim_flags", {}).get(
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"
        )
        is not True
        or coefficient.get("claim_flags", {}).get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not True
        or coefficient.get("coefficient_result", {}).get("coefficients", {}).get("C2")
        != {"numerator": 199, "denominator": 30}
        or breaking.get("classification", {}).get("status") != "NONTRIVIAL"
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or matter_no_go.get("classification", {}).get("solution_set") != "EMPTY"
        or matter_no_go.get("classification", {}).get("qme_status")
        != "REMAINS_OBSTRUCTED_IN_DECLARED_MATTER_CLASS"
        or wz_preflight.get("result_state")
        != "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN"
        or wz_preflight.get("qme_lifecycle", {}).get(
            "extended_AFN0_one_loop_breaking"
        )
        != "EXACT_REMOVABLE"
        or wz_preflight.get("qme_lifecycle", {}).get("full_extended_BV_QME")
        != "NOT_CERTIFIED"
        or wz_lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or wz_extended.get("H14", {}).get("even_quotient_dimension") != 0
        or wz_extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or wz_extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or wz_extended.get("lifecycle", {}).get("residual_transfer")
        != "FORBIDDEN_EXTENDED_CLASSICAL_CONTRACTION_NOT_SUPPLIED"
        or q1_disposition.get("finite_counterterm_ambiguity", {}).get(
            "bulk_response_rank"
        )
        != 2
        or q1_disposition.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or q1_disposition.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
        or anomaly_induced.get("claim_flags", {}).get(
            "ANOMALY_INDUCED_REPRESENTATIVE_SUPPLIED"
        )
        is not True
        or anomaly_induced.get("decision", {}).get("complete_finite_nonlocal_Gamma1")
        != "NO_CERTIFIED_FUNCTIONAL"
        or flat_tt_log.get("exact_logarithmic_form_factor", {}).get(
            "logarithmic_coefficient"
        )
        != {"numerator": -199, "denominator": 60}
        or flat_tt_log.get("claim_flags", {}).get("FLAT_TT_LOG_COEFFICIENT_FIXED")
        is not True
        or flat_tt_log.get("claim_flags", {}).get("FINITE_C2_NORMALIZATION_FIXED")
        is not False
        or flat_tt_log.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or curvature_squared_log.get("claim_flags", {}).get(
            "CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED"
        )
        is not True
        or curvature_squared_log.get("operator_choice_independence", {}).get(
            "first_difference_order"
        )
        != 3
        or curvature_squared_log.get("claim_flags", {}).get(
            "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"
        )
        is not False
        or curvature_squared_log.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
        or fv_conformized_log.get("decision", {}).get(
            "selected_C2_log_local_Weyl_completion"
        )
        != "CERTIFIED"
        or fv_conformized_log.get("carrier_crosswalk", {}).get("identity_status")
        != "DISTINCT_CARRIERS_NO_IDENTIFICATION"
        or fv_conformized_log.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
        )
        is not False
        or fv_anomaly_ricci.get("decision", {}).get("FV_anomaly_action")
        != "CERTIFIED"
        or fv_anomaly_ricci.get("decision", {}).get(
            "Ricci_scalar_sector_dependence"
        )
        != "CERTIFIED"
        or fv_anomaly_ricci.get("claim_flags", {}).get(
            "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"
        )
        is not False
        or cubic_weyl.get("decision", {}).get(
            "zero_derivative_algebraic_C3_carriers"
        )
        != "CERTIFIED_COMPLETE"
        or cubic_weyl.get("tensor_carriers", {}).get("parity_dimensions")
        != {"even": 1, "odd": 1}
        or cubic_weyl.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED"
        )
        is not False
        or third_curvature_weyl.get("raw_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 11
        or third_curvature_weyl.get("quotient_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 10
        or third_curvature_weyl.get("claim_flags", {}).get(
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "SCALAR_FLAT_I29_REVERSAL_IDENTITY_REPLAYED"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or [
            row.get("carrier_id")
            for row in cpt_kernels.get("universal_kernels", [])
        ]
        != ["I10", "I24", "I25", "I28", "I29"]
        or cpt_kernels.get("universal_kernels", [])[-1].get("stabilizer") != "S3"
        or cpt_kernels.get("source_fixture", {}).get("status")
        != "COEFFICIENT_COMPUTED"
        or cpt_kernels.get("claim_flags", {}).get(
            "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED"
        )
        is not True
        or cpt_kernels.get("claim_flags", {}).get(
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED"
        )
        is not False
        or cpt_kernels.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or cpt_kernels.get("repository_matching_audit", {}).get("verdict")
        != "NO_REPOSITORY_FORM_FACTOR_COEFFICIENT_CAN_BE_INFERRED_FROM_THE_CURRENT_SPECIAL_BACKGROUND_LEDGER"
        or generic_ghost_cpt.get("CPT_applicability_decision", {}).get("verdict")
        != "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED"
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"
        )
        is not False
        or generic_ghost_endo.get("exact_Endo_split", {}).get("local_perturbation")
        != "W=-2 Ric"
        or generic_ghost_endo.get("Duhamel_expansion", {}).get(
            "maximum_W_insertions_through_cubic_order"
        )
        != 3
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED"
        )
        is not True
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED"
        )
        is not False
        or generic_ghost_n1_n2.get("proper_time_to_resolvent", {}).get(
            "resolvent_identity"
        )
        != "G_H0=G_F-(1/3)d Delta_0^-2 delta"
        or generic_ghost_n1_n2.get("log_determinant_expansion", {}).get(
            "carrier_count"
        )
        != 5
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED"
        )
        is not True
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2_vector.get("minimal_operator_sign_flip", {}).get(
            "surviving_rows"
        )
        != [1, 3, 14]
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"
        )
        is not False
        or physical_hessian_linear.get("claim_flags", {}).get(
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"
        )
        is not True
        or physical_hessian_n3.get("claim_flags", {}).get(
            "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED"
        )
        is not True
        or physical_hessian_n3.get("claim_flags", {}).get(
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED"
        )
        is not True
        or physical_hessian_n3.get("claim_flags", {}).get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not False
        or physical_hessian_n3_projection.get("claim_flags", {}).get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or physical_hessian_n3_projection.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_INTEGRATED"
        )
        is not False
        or physical_hessian_n3_projection.get("interpolation_certificate", {}).get(
            "degree_six_box_evaluation_rank_mod_prime"
        )
        != 28
        or physical_hessian_n3_obstruction.get("relative_quotient", {}).get(
            "M14_rank_jump"
        )
        != 1
        or physical_hessian_n3_obstruction.get("corner_asymptotic", {}).get(
            "total_log_1_over_epsilon_coefficient"
        )
        != {"numerator": 1, "denominator": 2}
        or physical_hessian_n3_obstruction.get("claim_flags", {}).get(
            "H2_CANCELLATION_OF_CORNER_CLASS_PROVED"
        )
        is not False
        or physical_hessian_h2.get("claim_flags", {}).get(
            "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"
        )
        is not True
        or physical_hessian_h2.get("claim_flags", {}).get(
            "PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED"
        )
        is not False
        or physical_hessian_h2.get("scalar_flat_restriction", {}).get(
            "effective_term_count"
        )
        != 9
        or physical_hessian_mixed.get("claim_flags", {}).get(
            "RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE"
        )
        is not True
        or physical_hessian_mixed.get("claim_flags", {}).get(
            "RENORMALIZED_SUBTRACTION_FIXED"
        )
        is not False
        or physical_hessian_mixed.get("combined_raw_logarithm", {}).get("sum")
        != {"numerator": 15707, "denominator": 216}
        or physical_hessian_mellin.get("claim_flags", {}).get(
            "FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED"
        )
        is not True
        or physical_hessian_mellin.get("claim_flags", {}).get(
            "GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED"
        )
        is not False
        or physical_hessian_mellin.get("renormalization_scale_row", {}).get(
            "coefficient"
        )
        != {"numerator": 15707, "denominator": 216}
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"
        )
        is not True
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED"
        )
        is not False
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED"
        )
        is not False
        or physical_hessian_contacts.get("claim_flags", {}).get(
            "ALL_THREE_CONTACT_CELLS_PROJECTED"
        )
        is not True
        or physical_hessian_incidence.get("claim_flags", {}).get(
            "SYMMETRIC_POINT_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED"
        )
        is not True
        or physical_hessian_incidence.get("claim_flags", {}).get(
            "GENERIC_BOX_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED"
        )
        is not False
        or physical_hessian_incidence.get(
            "equal_box_tensor_reconstruction", {}
        ).get("combined_log_mu2_coefficient")
        != {"numerator": 15707, "denominator": 216}
        or physical_hessian_triangle_residues.get("claim_flags", {}).get(
            "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"
        )
        is not True
        or physical_hessian_full_incidence.get("claim_flags", {}).get(
            "FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"
        )
        is not True
        or physical_hessian_full_incidence.get("claim_flags", {}).get(
            "GENERIC_PHYSICAL_M14_DISPOSED"
        )
        is not True
        or physical_hessian_full_incidence.get("claim_flags", {}).get(
            "FINITE_LOCAL_MIXED_ROWS_FIXED"
        )
        is not False
        or physical_hessian_contact_finite.get("claim_flags", {}).get(
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED"
        )
        is not True
        or physical_hessian_contact_finite.get("claim_flags", {}).get(
            "RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED"
        )
        is not False
        or physical_hessian_contact_finite.get("equal_box_regression", {}).get(
            "combined_contact_finite_value"
        )
        != {"numerator": 3188, "denominator": 27}
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN"
        )
        is not True
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "STANDARD_S3_MASTER_PAIR_REQUIRED"
        )
        is not True
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"
        )
        is not False
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "RENORMALIZED_M14_SINGLET_VALUE_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "RENORMALIZED_STANDARD_S3_PAIR_VALUES_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        )
        is not False
        or generic_ghost_n3.get("angular_average", {}).get("coefficients", {}).get(
            "tr_R3"
        )
        != {"numerator": 503, "denominator": 648}
        or generic_ghost_n3.get("three_insertion_log_term", {}).get(
            "coefficients", {}
        ).get("tr_R3")
        != {"numerator": -503, "denominator": 243}
        or generic_ghost_n3.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"
        )
        is not False
        or generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "sector_count"
        )
        != 8
        or generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "total_Wick_rows"
        )
        != 20
        or generic_ghost_n3_triangle.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"
        )
        is not True
        or generic_ghost_n3_triangle.get("carrier_projection", {}).get(
            "repository_five_carrier_projection"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3_projection.get("quotient_section", {}).get(
            "raw_effective_channel_count"
        )
        != 11
        or generic_ghost_n3_projection.get("quotient_section", {}).get(
            "quotient_dimension"
        )
        != 10
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or generic_ghost_n3_symmetric.get("scope", {}).get("kinematic_point")
        != {"x1": 1, "x2": 1, "x3": 1}
        or len(generic_ghost_n3_symmetric.get("channel_rows", [])) != 11
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED"
        )
        is not True
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED"
        )
        is not False
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_exact_Delta_factor"
        )
        != 10
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_nonzero_direct_open_edge_restriction"
        )
        != ["I10_123"]
        or generic_ghost_n3_barycentric.get("claim_flags", {}).get(
            "GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED"
        )
        is not False
        or scalar_flat_k_ricci.get("linear_crosswalk", {}).get("identity")
        != "K_munu=Ric_munu+O(curvature^2)"
        or scalar_flat_k_ricci.get("cubic_order_counting", {}).get(
            "first_replacement_error_order"
        )
        != 4
        or scalar_flat_k_ricci.get("five_carrier_target", {}).get(
            "projection_status"
        )
        != "NOT_COMPUTED"
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED"
        )
        is not False
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED"
        )
        is not False
    ):
        raise ValueError("coefficient-bearing QME disposition drifted")
    if (
        reduced_bridge4.get("decision", {}).get(
            "Bridge_4_reduced_vacuum_cylinder"
        )
        != "CERTIFIED"
        or reduced_bridge4.get("decision", {}).get("Bridge_4_full_BV")
        != "NO_CERTIFIED_MAP"
        or reduced_bridge4.get("decision", {}).get("Bridge_4_Berger")
        != "NO_CERTIFIED_MAP"
        or reduced_bridge4.get("claim_flags", {}).get(
            "REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED"
        )
        is not True
        or reduced_bridge4.get("claim_flags", {}).get(
            "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"
        )
        is not True
        or reduced_bridge4.get("claim_flags", {}).get(
            "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED"
        )
        is not False
    ):
        raise ValueError("vacuum-cylinder reduced Bridge-4 input drifted")

    if (
        general.get("result_state")
        != "ABSTRACT_CORRECTION_CLASS_SENSITIVE_TANGENT_CONE_THEOREM_CERTIFIED"
        or general.get("theorem", {}).get("formula")
        != "Z_2^C={u in ker(q1): mu_X(u)=0 and R_j^C(u)=0 for every output block j}"
        or set(general.get("correction_classes", {}))
        != {"BOUNDED_OR_FINITE_QUASIPERIODIC", "SMOOTH_SECULAR", "CAUSAL_RETARDED"}
        or any(row.get("status") != "CERTIFIED" for row in general["correction_classes"].values())
        or general.get("flags", {}).get("BACKGROUND_SPECIFIC_TANGENT_CONE_CLASSIFICATION")
        is not False
        or k0.get("classification", {}).get(
            "complete_common_stabilizer_zero_cone_second_order_extendible"
        )
        is not True
        or smooth.get("classification", {}).get(
            "complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible"
        )
        is not True
        or resonance.get("classification", {}).get(
            "bounded_or_finite_quasiperiodic_extension_follows_from_moment_maps_alone"
        )
        is not False
    ):
        raise ValueError("finite-harmonic correction-class input drifted")


def _mode_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    evidence = _evidence(
        values,
        "polarized_state",
        "one_particle_krein",
        "positive_frequency_transform",
        "vacuum_cylinder_reduced_Bridge4",
        "Slavnov_preflight",
    )
    for chirality in (1, -1):
        for family in FAMILIES:
            minimum = BRANCH_MINIMUM[family]
            sign = FORM_SIGN[family]
            rows.append(
                _entry(
                    f"quantum.cylinder.mode_family.{family.lower()}.chirality_{'plus' if chirality > 0 else 'minus'}",
                    {
                        "theory": "free pure-Weyl BV-BFV gravity",
                        "background": "vacuum conformal cylinder R x S3",
                        "boundaries": "compact S3 Cauchy surface; selected positive-frequency boundary polarization",
                        "charge_sector": "ghost-number-zero one-particle reduced cylinder sector",
                        "carrier": f"normalized {family} energy-tower oscillator in chirality {chirality:+d}",
                        "degree": 0,
                        "parity": f"chirality {chirality:+d}; parity exchanges the opposite-chirality partner",
                        "ell": "NO_CERTIFIED_MAP: SO(4) irrep labels are not crosswalked to ell",
                        "m": "NO_CERTIFIED_MAP: magnetic index M is not crosswalked to one m convention",
                        "k": "NOT_APPLICABLE on S3",
                        "omega": f"positive cylinder energy n with n>={minimum}",
                    },
                    {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "CERTIFIED"},
                    {
                        "dispersion": _claim("CERTIFIED", f"positive cylinder energy n>={minimum}"),
                        "lee_wald": _claim("CERTIFIED", f"reduced Krein sign {sign:+d}"),
                        "taub_maps": _claim("NOT_APPLICABLE", "no second-order tangent-cone restriction is claimed for this all-energy family row"),
                        "resonance": _claim("OPEN", "the free spectral carrier is certified; nonlinear resonance disposition remains separate"),
                        "second_order": _second_order(
                            ("OPEN", "not classified for this mode family"),
                            ("OPEN", "not classified for this mode family"),
                            ("NO_CERTIFIED_MAP", "no same-background causal tangent-cone crosswalk"),
                        ),
                    },
                    _quantum_data(
                        "MODE_FAMILY",
                        ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
                        imported=("CERTIFIED", "YES: selected reduced E/A/L oscillator"),
                        cocycle=("CERTIFIED", "survives the selected polarized classical BRST retraction"),
                        exactness=("CERTIFIED", "nonexact in the selected reduced complex"),
                        pairing=("CERTIFIED", f"Krein sign {sign:+d}"),
                        complex_structure=("CERTIFIED", "J(q,p)=(-A^-1 p,Aq) on the same-background reduced Cauchy-Sobolev carrier"),
                        hadamard=("CERTIFIED", "global stationary reduced branch two-point distribution with C_plus wavefront; not a full-BV kernel"),
                        state_space=("CERTIFIED", "positive E sector and negative-Krein A/L sectors; total infinite-index Krein functional"),
                        qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME is obstructed at one loop"),
                        lifecycle=("CERTIFIED", "free reduced Bridge-4 carrier certified; strict interacting extension remains obstructed"),
                        particle=("CERTIFIED", "compact-cylinder reduced one-particle Krein excitation; not a positive graviton or scattering particle"),
                        crosswalk=("CERTIFIED", "real phase-space mode to selected positive-frequency oscillator"),
                    ),
                    evidence + _evidence(values, "regulated_Slavnov_breaking"),
                    "This REDUCED-MODE plus LORENTZIAN-CAUSAL row certifies the free vacuum-cylinder classical-to-quantum Bridge-4 carrier, compatible complex structure and Krein-Hadamard two-point distribution. It is not a full-BV BRST Hadamard state, positive graviton Hilbert space, interacting-QME theorem, or scattering-particle entry.",
                )
            )
    return rows


def _residual_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    evidence = _evidence(values, "curvature_CCR", "Slavnov_preflight", "regulated_Slavnov_breaking")
    for class_id, chirality in (("W_+^2", "+"), ("W_-^2", "-")):
        partner = "W_-^2" if chirality == "+" else "W_+^2"
        rows.append(
            _entry(
                f"quantum.cylinder.residual_deformation.{class_id.lower().replace('^', '_').replace('+', 'plus').replace('-', 'minus')}",
                {
                    "theory": "free pure-Weyl BV observable cohomology",
                    "background": "vacuum conformal cylinder R x S3",
                    "boundaries": "closed cylinder with all fifteen residual conformal generators gauged",
                    "charge_sector": "centered residual cohomology H4 at delta=0",
                    "carrier": class_id,
                    "degree": 4,
                    "parity": f"chiral {chirality}; parity partner is {partner}",
                    "ell": "NOT_APPLICABLE: two-particle ghost-dressed deformation class",
                    "m": "NOT_APPLICABLE: two-particle ghost-dressed deformation class",
                    "k": "NOT_APPLICABLE",
                    "omega": "NOT_APPLICABLE: not a one-particle frequency",
                },
                {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OBSTRUCTED"},
                {
                    "dispersion": _claim("NOT_APPLICABLE", "deformation class, not a one-particle shell"),
                    "lee_wald": _claim("CERTIFIED", "unit diagonal Gram entry in the final covariant H4 basis"),
                    "taub_maps": _claim("NOT_APPLICABLE", "not a first-order tangent mode"),
                    "resonance": _claim("NOT_APPLICABLE", "not a one-particle shell"),
                    "second_order": _second_order(
                        ("NOT_APPLICABLE", "not a tangent mode"),
                        ("NOT_APPLICABLE", "not a tangent mode"),
                        ("NOT_APPLICABLE", "not a tangent mode"),
                    ),
                },
                _quantum_data(
                    "NONPARTICLE_RESIDUAL_CLASS",
                    ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
                    imported=("CERTIFIED", "YES: non-particle residual class"),
                    cocycle=("CERTIFIED", "closed class in final covariant H4"),
                    exactness=("CERTIFIED", "nonexact H4 class"),
                    pairing=("CERTIFIED", "unit diagonal Gram entry"),
                    complex_structure=("NOT_APPLICABLE", "not a one-particle carrier"),
                    hadamard=("NOT_APPLICABLE", "not a one-particle carrier"),
                    state_space=("NOT_APPLICABLE", "deformation/vertex class"),
                    qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME fails before H3-H4-H5 transfer"),
                    lifecycle=("OBSTRUCTED", "classical deformation class remains certified; strict quantum survival is not defined"),
                    particle=("CERTIFIED", "NOT_A_PARTICLE"),
                    crosswalk=("CERTIFIED", "curvature graph image to final free BV cohomology"),
                ),
                evidence,
                "This is a deformation/vertex class, not a one-particle generator or particle Hilbert-space basis. Its free cohomology and Gram entry do not decide quantum survival.",
            )
        )
    return rows


def _berger_gap(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return _entry(
        "quantum.berger.carrier_gap.retained_26_stationary_modes",
        {
            "theory": "pure-Weyl gravity plus positive scalar clock at fixed coupling",
            "background": "compact positive Berger clock",
            "boundaries": "R x S3 with compact Cauchy surfaces",
            "charge_sector": "retained 26-row classical BV carrier",
            "carrier": "causal 26-row complex; stationary spectral mode basis not supplied",
            "degree": "all retained BV degrees",
            "parity": "NO_CERTIFIED_MAP",
            "ell": "NO_CERTIFIED_MAP",
            "m": "NO_CERTIFIED_MAP",
            "k": "NO_CERTIFIED_MAP",
            "omega": "NO_CERTIFIED_MAP: generalized-zero and nonzero spectrum not imported",
        },
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "OBSTRUCTED"},
        {
            "dispersion": _claim("NO_CERTIFIED_MAP", "no stationary physical mode basis"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "carrier pairing exists but has no modewise restriction"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no per-mode tangent-cone ledger"),
            "resonance": _claim("NO_CERTIFIED_MAP", "generalized zero and nonzero stationary spectrum not imported"),
            "second_order": _second_order(
                ("OPEN", "Berger finite-harmonic cone not classified"),
                ("OPEN", "Berger finite-harmonic cone not classified"),
                ("OPEN", "Berger causal carrier exists but its nonlinear tangent cone is not classified"),
            ),
        },
        _quantum_data(
            "CARRIER_IMPORT_GAP",
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            imported=("NO_CERTIFIED_MAP", "NO: causal carrier imported, no stationary mode crosswalk"),
            cocycle=("NO_CERTIFIED_MAP", "no per-mode cohomology ledger"),
            exactness=("NO_CERTIFIED_MAP", "no per-mode cohomology ledger"),
            pairing=("NO_CERTIFIED_MAP", "carrier pairing has no modewise restriction"),
            complex_structure=("OPEN", "not constructed on the 54-row distributional complex"),
            hadamard=("OPEN", "not constructed"),
            state_space=("OPEN", "reduced Krein evidence does not define a Berger physical state space"),
            qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME is obstructed"),
            lifecycle=("OBSTRUCTED", "classical causal import remains; strict interacting quantum lifecycle is blocked"),
            particle=("NO_CERTIFIED_MAP", "no mode basis or Hadamard state"),
            crosswalk=("NO_CERTIFIED_MAP", "retained 26 rows to stationary physical modes"),
        ),
        _evidence(values, "Berger_causal_chain", "Berger_Hadamard_gate", "Slavnov_preflight", "regulated_Slavnov_breaking"),
        "The 26/54-row causal carrier is imported, but it is not a stationary mode ledger. No physical mode, complex structure, Hadamard state, or particle is inferred.",
    )


def _tangent_crosswalk(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return _entry(
        "quantum.crosswalk.classical_tangent_cone_to_interacting_brst",
        {
            "theory": "classical finite-harmonic second-order theory to renormalized BV quantum theory",
            "background": "crosswalk only; every background requires its own certified carrier",
            "boundaries": "correction-class dependent",
            "charge_sector": "declared stabilizer moment-map zero sector",
            "carrier": "Z2^C classical tangent cone to a quantum BRST insertion",
            "degree": 2,
            "parity": "all declared finite-harmonic sectors",
            "ell": "finite declared block set",
            "m": "finite declared block set",
            "k": "finite declared block set",
            "omega": "bounded/quasiperiodic, smooth-secular, or causal/retarded",
        },
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
        {
            "dispersion": _claim("NOT_APPLICABLE", "abstract finite-block image/cokernel criterion"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "no universal quantum pairing follows from the classical criterion"),
            "taub_maps": _claim("CERTIFIED", "Z2^C={u: mu_X(u)=0 and R_j^C(u)=0}"),
            "resonance": _claim("CERTIFIED", "R_j^C depends on the correction class fixed before the cokernel"),
            "second_order": _second_order(
                ("OBSTRUCTED", "abstract criterion certified; opposite-momentum moment-map-only fixture fails on a nonempty resonance divisor"),
                ("CERTIFIED", "abstract criterion and fixed-(ell,|k|) smooth-secular fixture certified in declared scope"),
                ("NO_CERTIFIED_MAP", "abstract compatible-source retarded criterion certified, but no background-specific Green theorem is imported"),
            ),
        },
        _quantum_data(
            "CLASSICAL_TO_QUANTUM_CROSSWALK",
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            imported=("CERTIFIED", "abstract classical correction-class theorem imported by content hash"),
            cocycle=("NO_CERTIFIED_MAP", "no quantum BRST insertion constructed"),
            exactness=("NO_CERTIFIED_MAP", "no primitive or nonmembership witness constructed"),
            pairing=("NO_CERTIFIED_MAP", "no coefficient-bearing quantum pairing"),
            complex_structure=("NOT_APPLICABLE", "classical second-order solvability crosswalk"),
            hadamard=("NO_CERTIFIED_MAP", "no background-specific causal quantum state"),
            state_space=("NO_CERTIFIED_MAP", "no interacting quantum state space"),
            qme=("CERTIFIED", "strict one-loop local Euclidean QME is obstructed and the tau-adic compensator-extended one-loop local Euclidean QME is restored; the raw BoxR coefficient and scheme conversion remain fixed; generic triangle/contact incidence is exact, M14 is a nonzero Mellin-renormalized scale row, and the 33 finite contact rows are exact in the declared subtraction, while the triangle bulk, finite normalizations and complete Q1 remain underdetermined"),
            lifecycle=("NO_CERTIFIED_MAP", "the coefficient-bearing QME disposition, equal-box Mellin scale row, generic Volterra subtraction carrier and generic contact endpoint residues are complete, but the mixed-row incidence, generic primed Green/spectral carrier, repository form-factor functions and coefficients, parity-odd derivative manifest, finite normalizations, complete Q1, Bridge 2, and an extended same-background classical carrier map are absent"),
            particle=("NO_CERTIFIED_MAP", "classical obstruction is not ghost removal"),
            crosswalk=("NO_CERTIFIED_MAP", "classical obstruction to interacting BRST disappearance or quantum constraint"),
        ),
        _evidence(values, "general_tangent_cone", "finite_k0_cone", "smooth_secular_cone", "bounded_resonance_divisor", "Slavnov_preflight", "regulated_Slavnov_breaking", "WZ_compensator_preflight", "WZ_cotangent_lift", "WZ_extended_local_BV", "one_loop_Q1_disposition", "anomaly_induced_Gamma1", "flat_TT_log_Gamma1", "curvature_squared_log_Gamma1", "FV_conformized_C2_log_Gamma1", "FV_anomaly_action_Ricci_sector", "algebraic_cubic_Weyl_carriers", "third_curvature_Weyl_manifest", "CPT_universal_third_curvature_kernels", "generic_physical_hessian_linear_curvature", "generic_physical_hessian_n3_triangle_fixture", "generic_physical_hessian_n3_five_carrier_projection", "generic_physical_hessian_n3_integration_obstruction", "generic_physical_hessian_curvature_squared", "generic_physical_hessian_mixed_H1_H2_corner_fixture", "generic_physical_hessian_mellin_subtraction_scale_row", "generic_physical_hessian_covariant_Volterra_carrier", "generic_physical_hessian_H1_H2_contact_residue_projection", "generic_physical_hessian_symmetric_mixed_boundary_incidence", "generic_physical_hessian_triangle_corner_residues", "generic_physical_hessian_full_boundary_incidence", "generic_physical_hessian_H1_H2_contact_finite_rows", "generic_physical_hessian_triangle_master_completeness", "generic_physical_hessian_triangle_renormalized_master_values", "generic_background_ghost_CPT_obstruction", "generic_ghost_Endo_Duhamel_reduction", "generic_ghost_n1_n2_Hodge_resolvent_reduction", "generic_ghost_n1_n2_vector_CPT_projection", "generic_ghost_longitudinal_Schur_resummation", "generic_ghost_Schur_Schatten_split", "generic_ghost_Schur_Wodzicki_residue", "generic_ghost_Schur_weighted_trace_scale", "round_S4_ghost_Schur_finite_weighted_traces", "round_S4_ghost_Schur_zeta_factorization", "generic_ghost_Schur_weight_raised_zeta_factorization", "generic_ghost_n3_adiabatic_carrier", "generic_ghost_n3_triangle_kernel", "generic_ghost_n3_five_carrier_projection", "generic_ghost_n3_barycentric_factorization", "generic_ghost_n3_symmetric_point_simplex_integration", "scalar_flat_K_Ricci_crosswalk", "BoxR_scheme_conversion"),
        "Classical second-order obstruction does not imply BRST disappearance, a loop interaction, a quantum constraint, BRST exactness, or ghost removal. The coefficient-bearing QME disposition is complete—strict obstructed, tau-adic compensator extension restored locally at one Euclidean loop—and the exact FV anomaly action proves structural dependence of the Ricci-scalar sector. A generic covariant Volterra carrier joins the six physical triangle cells and three H1-H2 contact cells under the common Mellin boundary extension. The three generic triangle corner residues and all contact endpoint residues are exact rational five-carrier functions. Their full incidence is nonzero, so algebraic H2 cancellation is refuted generically and M14 is disposed as a nonzero Mellin-renormalized scale row. The 33 minimally-subtracted finite contact rows are also exact, with equal-box TT sum 3188/27. The renormalized triangle bulk, generic repository functions and coefficients, independent finite normalization, parity-odd derivative manifest, global Green data and complete Q1 remain open. Bridge 2 and a same-background extended classical carrier map are absent, so no interacting-BRST insertion crosswalk is certified.",
    )


def _guard_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        ("local_anomaly_class", "local ghost-number-one anomaly class such as omega C2 or omega E4", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("Slavnov_preflight", "regulated_Slavnov_breaking", "unitary_matter_no_go", "WZ_compensator_preflight", "WZ_cotangent_lift", "WZ_extended_local_BV", "one_loop_Q1_disposition", "anomaly_induced_Gamma1", "flat_TT_log_Gamma1")),
        ("euclidean_determinant_factor", "round-S4 TT or ghost determinant factor", ["EUCLIDEAN-SPECTRAL"], ("Slavnov_preflight", "Euclidean_elliptic_complex", "nonconformal_coefficient_match")),
        ("flat_tt_log_form_factor", "nonzero-momentum flat-TT logarithmic effective-action form factor", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("regulated_Slavnov_breaking", "one_loop_Q1_disposition", "flat_TT_log_Gamma1")),
        ("curvature_squared_covariant_log_form_factor", "covariant C log(Delta_C/mu^2) C effective-action form factor through curvature order two", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("regulated_Slavnov_breaking", "one_loop_Q1_disposition", "flat_TT_log_Gamma1", "curvature_squared_log_Gamma1")),
        ("fv_conformized_c2_log_form_factor", "FV scalar-flat Weyl-orbit completion of the selected C log(Delta_C/mu^2) C carrier plus the exact FV anomaly action and dependent Ricci sector", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("regulated_Slavnov_breaking", "one_loop_Q1_disposition", "flat_TT_log_Gamma1", "curvature_squared_log_Gamma1", "FV_conformized_C2_log_Gamma1", "FV_anomaly_action_Ricci_sector")),
        ("algebraic_cubic_weyl_carrier", "four-dimensional zero-derivative algebraic C3 carrier in its exact even/odd parity basis", ["LOCAL-ALGEBRAIC"], ("algebraic_cubic_Weyl_carriers",)),
        ("third_curvature_weyl_carrier_manifest", "five parity-even third-curvature conformal carrier labels modulo the exact four-dimensional symmetric functional relation", ["EUCLIDEAN-SPECTRAL"], ("third_curvature_Weyl_manifest",)),
        ("cpt_universal_third_curvature_kernel", "five exact universal CPT source kernels on the rank-one minimal scalar-Laplacian fixture; repository generic-background full-BV trace substitution open", ["EUCLIDEAN-SPECTRAL"], ("CPT_universal_third_curvature_kernels",)),
        ("generic_background_physical_hessian_n3_fixture", "same-gauge rank-nine physical H1/H2 blocks with formal-adjoint completion; three-H1 five-carrier projection and M14 corner obstruction certified; all generic triangle corner and contact endpoint residues are exact, their full incidence is nonzero, M14 is disposed as a Mellin-renormalized scale row, all 33 finite contact rows are exact, all eleven physical triangle rows lie in the exact rank-52 six-master span, and the M14 singlet plus standard-S3 pair have exact Mellin-renormalized values; the eleven physical master-coordinate functions remain open", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("generic_physical_hessian_linear_curvature", "generic_physical_hessian_n3_triangle_fixture", "generic_physical_hessian_n3_five_carrier_projection", "generic_physical_hessian_n3_integration_obstruction", "generic_physical_hessian_curvature_squared", "generic_physical_hessian_mixed_H1_H2_corner_fixture", "generic_physical_hessian_mellin_subtraction_scale_row", "generic_physical_hessian_covariant_Volterra_carrier", "generic_physical_hessian_H1_H2_contact_residue_projection", "generic_physical_hessian_symmetric_mixed_boundary_incidence", "generic_physical_hessian_triangle_corner_residues", "generic_physical_hessian_full_boundary_incidence", "generic_physical_hessian_H1_H2_contact_finite_rows", "generic_physical_hessian_triangle_master_completeness", "generic_physical_hessian_triangle_renormalized_master_values")),
        ("generic_background_diff_weyl_ghost_cpt_obstruction", "generic-background effective Diff-Weyl ghost determinant: direct minimal-CPT substitution obstructed; exact Endo-Duhamel reduction supplied; n=3 projected onto the scalar-flat ten-dimensional five-carrier quotient, with ten exact Delta cancellations, a unique direct I10 edge source and a pointwise I28 relation; all rows are integrated at the normalized symmetric point; the n=1+n=2 pure-vector CPT sum is exact and all longitudinal D_W towers are resummed into one normalized Schur kernel; its order-minus-two correction is in S_3, with exact Wres(K), Wres(K^2), Wres(log S_L), and the declared order-two weighted-trace pole/scale row; the round-S4 reference finite K/K2 rows, canonical det_3 tail and weighted modified determinant are complete; generic relative-IBP/corner-flux and edge-bubble data, physical Hessian and repository functions remain open", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("generic_background_ghost_CPT_obstruction", "generic_ghost_Endo_Duhamel_reduction", "generic_ghost_n1_n2_Hodge_resolvent_reduction", "generic_ghost_n1_n2_vector_CPT_projection", "generic_ghost_longitudinal_Schur_resummation", "generic_ghost_Schur_Schatten_split", "generic_ghost_Schur_Wodzicki_residue", "generic_ghost_Schur_weighted_trace_scale", "round_S4_ghost_Schur_finite_weighted_traces", "generic_ghost_Schur_weight_raised_zeta_factorization", "generic_ghost_n3_adiabatic_carrier", "generic_ghost_n3_triangle_kernel", "generic_ghost_n3_five_carrier_projection", "generic_ghost_n3_barycentric_factorization", "generic_ghost_n3_symmetric_point_simplex_integration", "scalar_flat_K_Ricci_crosswalk")),
        ("round_s4_schur_zeta_factorization", "round-unit-S4 primed scalar ghost Schur zeta factorization defect 5/3 and zeta determinant ratio; special-background non-particle spectral carrier", ["EUCLIDEAN-SPECTRAL"], ("round_S4_ghost_Schur_zeta_factorization",)),
        ("curvature_observable_generator", "support-local curvature-graph CCR generator", ["LORENTZIAN-CAUSAL"], ("curvature_CCR",)),
    ]
    rows = []
    for key, carrier, tags, evidence_names in specs:
        rows.append(
            _entry(
                f"quantum.crosswalk.{key}_to_particle",
                {
                    "theory": "pure-Weyl quantum programme",
                    "background": "carrier-specific; no cross-background identification",
                    "boundaries": "carrier-specific",
                    "charge_sector": "not a certified physical one-particle sector",
                    "carrier": carrier,
                    "degree": "carrier-specific",
                    "parity": "carrier-specific",
                    "ell": "NO_CERTIFIED_MAP",
                    "m": "NO_CERTIFIED_MAP",
                    "k": "NO_CERTIFIED_MAP",
                    "omega": "NO_CERTIFIED_MAP",
                },
                {axis: "NO_CERTIFIED_MAP" for axis in AXES},
                {
                    "dispersion": _claim("NO_CERTIFIED_MAP", "not a physical residual mode shell"),
                    "lee_wald": _claim("NO_CERTIFIED_MAP", "no particle pairing crosswalk"),
                    "taub_maps": _claim("NOT_APPLICABLE", "non-mode carrier guard"),
                    "resonance": _claim("NOT_APPLICABLE", "non-mode carrier guard"),
                    "second_order": _second_order(
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                    ),
                },
                _quantum_data(
                    "NON_MODE_PARTICLE_GUARD",
                    tags,
                    imported=("CERTIFIED", "carrier imported only in its declared non-particle role"),
                    cocycle=("NOT_APPLICABLE", "carrier-specific; no physical residual mode imported"),
                    exactness=("NOT_APPLICABLE", "carrier-specific; no physical residual mode imported"),
                    pairing=("NO_CERTIFIED_MAP", "no particle pairing crosswalk"),
                    complex_structure=("NO_CERTIFIED_MAP", "no particle complex structure crosswalk"),
                    hadamard=("NO_CERTIFIED_MAP", "no particle Hadamard crosswalk"),
                    state_space=("NO_CERTIFIED_MAP", "no particle state-space crosswalk"),
                    qme=(("CERTIFIED", "strict local Euclidean QME is obstructed; the tau-adic compensator-extended local Euclidean QME is restored at one loop, and this carrier's coefficient is bound to that disposition") if key in {"local_anomaly_class", "flat_tt_log_form_factor", "curvature_squared_covariant_log_form_factor", "fv_conformized_c2_log_form_factor"} else ("OPEN", "carrier retains its own anomaly/QME dependency")),
                    lifecycle=("NO_CERTIFIED_MAP", "not a particle lifecycle entry"),
                    particle=("NO_CERTIFIED_MAP", "forbidden without an explicit physical residual-mode crosswalk"),
                    crosswalk=("NO_CERTIFIED_MAP", "non-mode carrier to particle"),
                ),
                _evidence(values, *evidence_names),
                "This carrier remains valid in its local, spectral, or observable-algebra role, but no certified map turns it into a particle entry.",
            )
        )
    return rows


def entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return (
        _mode_entries(values)
        + _residual_entries(values)
        + [_berger_gap(values), _tangent_crosswalk(values)]
        + _guard_entries(values)
    )


def validate_fragment(value: dict[str, Any]) -> None:
    for schema_path in (SCHEMA, COMMON_SCHEMA):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    ids = [entry["id"] for entry in value["entries"]]
    if len(ids) != len(set(ids)) or len(ids) != 22:
        raise ValueError("quantum atlas entry count or uniqueness drifted")
    by_id = {entry["id"]: entry for entry in value["entries"]}
    residual = [entry for entry in value["entries"] if entry["quantum_data"]["entry_kind"] == "NONPARTICLE_RESIDUAL_CLASS"]
    if len(residual) != 2 or any(
        entry["quantum_data"]["particle_interpretation"]
        != _claim("CERTIFIED", "NOT_A_PARTICLE")
        for entry in residual
    ):
        raise ValueError("residual deformation class was promoted to a particle")
    berger = by_id["quantum.berger.carrier_gap.retained_26_stationary_modes"]
    if berger["quantum_data"]["classical_mode_imported"]["status"] != "NO_CERTIFIED_MAP":
        raise ValueError("Berger carrier was promoted to a spectral mode ledger")
    mode_rows = [
        entry
        for entry in value["entries"]
        if entry["quantum_data"]["entry_kind"] == "MODE_FAMILY"
    ]
    if len(mode_rows) != 6 or any(
        entry["quantum_data"]["compatible_complex_structure"]["status"]
        != "CERTIFIED"
        or entry["quantum_data"]["Hadamard_two_point_function"]["status"]
        != "CERTIFIED"
        or entry["quantum_data"]["lifecycle_state"]["status"] != "CERTIFIED"
        for entry in mode_rows
    ):
        raise ValueError("reduced vacuum-cylinder Bridge-4 mode row was dropped")
    tangent = by_id["quantum.crosswalk.classical_tangent_cone_to_interacting_brst"]
    if (
        tangent["quantum_data"]["carrier_crosswalk"]["status"] != "NO_CERTIFIED_MAP"
        or tangent["quantum_data"]["anomaly_QME_dependency"]["status"] != "CERTIFIED"
        or tangent["quantum_data"]["lifecycle_state"]["status"] != "NO_CERTIFIED_MAP"
    ):
        raise ValueError("classical tangent obstruction was promoted without the QME bridge")
    guards = [entry for entry in value["entries"] if entry["quantum_data"]["entry_kind"] == "NON_MODE_PARTICLE_GUARD"]
    if len(guards) != 12 or any(
        entry["quantum_data"]["particle_interpretation"]["status"] != "NO_CERTIFIED_MAP"
        for entry in guards
    ):
        raise ValueError("non-mode carrier was promoted to a particle")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_inputs(values)
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(values),
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m atlas.generate_quantum_atlas_fragment --check",
            "PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment",
            "PYTHONPATH=quantum-weyl python3 -m unittest atlas.tests.test_quantum_atlas_fragment",
            "python3 residual_atlas/validate_fragment.py quantum-weyl/atlas/quantum-atlas-fragment.json",
        ],
    }
    validate_fragment(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale quantum atlas fragment: {OUTPUT}")
    print("quantum residual-atlas fragment: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
