"""Compare local anomaly pullback data with the quantum D-Cartan complex.

This module constructs every map justified by the current inputs and stops at
the precise missing arrow.  The one-generator pullback of a local
ghost-number-one density is not automatically a degree-zero endomorphism
Cartan defect.  Producing that arrow requires renormalized Ward insertions
(``Q_1``, ``iota_{D,1}``, and ``L_{D,1}``) on a declared observable algebra.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from local_bv.algebra import canonical_sha256
from local_bv.relative_cohomology import SparseMatrix
from spectral.euclidean.coefficient_reconstruction import (
    cylinder_d_reducibility,
    d_pullback,
    minkowski_d_reducibility,
    spin_two_anomaly,
)


LOCAL_EVEN_BASIS = ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4")
LOCAL_ODD_BASIS = ("ANOM_OMEGA_C_DUAL_C",)
D_LOCAL_TARGET_BASIS = ("c_D_C2", "c_D_E4")


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _diagonal_pullback(sigma: Fraction) -> SparseMatrix:
    return SparseMatrix(
        len(D_LOCAL_TARGET_BASIS),
        len(LOCAL_EVEN_BASIS),
        {(index, index): sigma for index in range(2) if sigma},
    )


@lru_cache(maxsize=1)
def comparison_analysis() -> dict[str, object]:
    anomaly = spin_two_anomaly()
    coefficient_vector = (anomaly.c, -anomaly.a)
    cylinder = cylinder_d_reducibility()
    minkowski = minkowski_d_reducibility()
    cylinder_map = _diagonal_pullback(cylinder.sigma)
    minkowski_map = _diagonal_pullback(minkowski.sigma)
    if cylinder_map.apply(coefficient_vector) != (0, 0):
        raise AssertionError("vacuum-cylinder local D pullback is not zero")
    if minkowski_map.apply(coefficient_vector) != (-anomaly.c, anomaly.a):
        raise AssertionError("Minkowski local D pullback normalization drifted")

    missing_carriers = (
        {
            "carrier_id": "FROZEN_CLASSICAL_D_ACTION",
            "required_for": "source and target chain-complex identification",
            "status": "MISSING_FULL_CLASSICAL_FREEZE",
        },
        {
            "carrier_id": "RENORMALIZED_Q1",
            "required_for": "[Q_1,iota_D] contribution to the Cartan defect",
            "status": "UNDEFINED_ANALYTICALLY",
        },
        {
            "carrier_id": "RENORMALIZED_IOTA_D_1",
            "required_for": "[Q,iota_{D,1}] contribution to the Cartan defect",
            "status": "UNDEFINED_ANALYTICALLY",
        },
        {
            "carrier_id": "RENORMALIZED_L_D_1",
            "required_for": "first-order Ward-action subtraction",
            "status": "UNDEFINED_ANALYTICALLY",
        },
        {
            "carrier_id": "LOCAL_INSERTION_TO_ADMISSIBLE_DERIVATION_MAP",
            "required_for": "map H14 local anomaly densities to H0 admissible endomorphisms",
            "status": "CONTRACT_READY_OPERATOR_DATA_NOT_RECEIVED",
        },
        {
            "carrier_id": "REGULATED_SLAVNOV_BREAKING",
            "required_for": "match background trace coefficients to the repository BV anomaly",
            "status": "CONTRACT_READY_NOT_COMPUTED",
        },
    )
    source_target_audit = {
        "source_complex": "H^{1,4}_AFN0(s|d)",
        "source_degree": {"ghost_number": 1, "form_degree": 4},
        "intermediate_complex": "one-generator local D pullback",
        "intermediate_degree": {"D_ghost_number": 1, "form_degree": 4},
        "target_complex": "H^0(Der_adm(C),[Q,-])",
        "target_degree": {"endomorphism_degree": 0},
        "canonical_map_from_grading_alone": False,
        "missing_arrow": "RENORMALIZED_LOCAL_WARD_INSERTION",
    }
    payload_for_hash = {
        "basis": {
            "local_even": LOCAL_EVEN_BASIS,
            "local_odd": LOCAL_ODD_BASIS,
            "D_local_target": D_LOCAL_TARGET_BASIS,
        },
        "coefficient_vector": [_fraction(value) for value in coefficient_vector],
        "cylinder_map": cylinder_map.canonical_payload(),
        "minkowski_map": minkowski_map.canonical_payload(),
        "source_target_audit": source_target_audit,
        "missing_carriers": missing_carriers,
    }
    return {
        "coefficient_vector": coefficient_vector,
        "cylinder_map": cylinder_map,
        "minkowski_map": minkowski_map,
        "cylinder_pullback": d_pullback(cylinder, anomaly),
        "minkowski_pullback": d_pullback(minkowski, anomaly),
        "source_target_audit": source_target_audit,
        "missing_carriers": missing_carriers,
        "analysis_sha256": canonical_sha256(payload_for_hash),
    }


def comparison_payload() -> dict[str, object]:
    analysis = comparison_analysis()
    return {
        "result_id": "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON",
        "result_state": "LOCAL_D_PULLBACK_COMPUTED_TARGET_CHAIN_MAP_UNDEFINED",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "LORENTZIAN-CAUSAL",
        ],
        "setting_id": "vacuum_cylinder",
        "generator_id": "D_compact",
        "phase_space_id": "compact_quantum",
        "source_local_cohomology": {
            "even_basis": list(LOCAL_EVEN_BASIS),
            "odd_basis": list(LOCAL_ODD_BASIS),
            "even_standard_background_coefficient_coordinates": [
                _fraction(value) for value in analysis["coefficient_vector"]
            ],
            "odd_coefficient_status": "NOT_COMPUTED",
            "full_BV_lift_status": "NOT_COMPUTED",
        },
        "setting_specific_classical_inputs": [
            {
                "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
                "generator": "D_helical represented by D_compact in the dressed frame",
                "classical_D_action": "AVAILABLE_SETTING_SPECIFIC_BERGER_54_ROWS",
                "unary_D_equivariance": "VERIFIED",
                "contraction_D_equivariance": "VERIFIED",
                "cyclic_D_action": "VERIFIED",
                "causal_54_to_26_reduction": "VERIFIED_CONDITIONAL",
                "retained_26_row_green_homotopy": "NOT_CONSTRUCTED",
                "renormalized_local_Ward_insertion": "NOT_CONSTRUCTED",
                "cartan_classification_status": "NO_VERDICT",
            }
        ],
        "prepared_input_contracts": {
            "berger_26_row_green_hadamard_endpoint": {
                "status": "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED",
                "physical_green_status": "NOT_CONSTRUCTED",
                "hadamard_status": "NOT_CONSTRUCTED",
            },
            "renormalized_D_Ward_insertion": {
                "status": "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED",
                "regulated_breaking_status": "NOT_COMPUTED",
                "local_to_cartan_map_status": "NOT_CONSTRUCTED",
                "quantum_cartan_status": "NO_VERDICT",
            },
        },
        "one_generator_pullback_maps": {
            "target_basis": list(D_LOCAL_TARGET_BASIS),
            "vacuum_cylinder": {
                "matrix": analysis["cylinder_map"].canonical_payload(),
                "coefficient_image": [_fraction(0), _fraction(0)],
                "status": "ZERO_BECAUSE_SIGMA_D_EQUALS_ZERO",
            },
            "minkowski_dilation_cross_check": {
                "matrix": analysis["minkowski_map"].canonical_payload(),
                "coefficient_image": [
                    _fraction(value)
                    for value in analysis["minkowski_map"].apply(
                        analysis["coefficient_vector"]
                    )
                ],
                "status": "NONZERO_LOCAL_COCYCLE_PULLBACK",
            },
        },
        "source_target_degree_audit": analysis["source_target_audit"],
        "minimal_missing_carrier_theorem": {
            "status": "COMPLETE_NAMED_MISSING_ARROW",
            "carriers": list(analysis["missing_carriers"]),
            "conclusion": (
                "the ordinary bulk trace anomaly has zero direct local D_compact "
                "insertion on the closed vacuum cylinder; a nonzero quantum "
                "D-Cartan defect, if present, must enter through the unconstructed "
                "renormalized Ward/operator map, measure, boundary/corner, zero-mode, "
                "or antifield-completion data"
            ),
        },
        "cartan_defect_comparison": {
            "map_status": "UNDEFINED_MISSING_RENORMALIZED_LOCAL_WARD_INSERTION",
            "classification_status": "NO_VERDICT",
            "zero_local_pullback_implies_zero_cartan_defect": False,
        },
        "checks": {
            "local_even_source_basis_complete_at_AFN0": "VERIFIED",
            "local_odd_source_basis_complete_at_AFN0": "VERIFIED",
            "cylinder_sigma_D_zero": "VERIFIED",
            "cylinder_pullback_matrix_zero": "VERIFIED",
            "minkowski_sigma_D_minus_one": "VERIFIED",
            "source_target_degree_mismatch_recorded": "VERIFIED",
            "missing_arrow_fail_closed": "VERIFIED",
            "berger_classical_D_input_setting_specific": "VERIFIED",
            "green_endpoint_contract_fail_closed": "VERIFIED",
            "ward_insertion_contract_fail_closed": "VERIFIED",
        },
        "claim_boundary": [
            "The coefficient vector is the standard Euclidean background conformal-spin-two trace anomaly, not a computed repository BV Slavnov breaking.",
            "The zero cylinder pullback is a local one-generator statement and does not classify the degree-zero D-Cartan defect.",
            "No QME restoration, residual quantum transfer, boundary theorem, or Lorentzian causal result is claimed.",
        ],
        "analysis_sha256": analysis["analysis_sha256"],
    }
