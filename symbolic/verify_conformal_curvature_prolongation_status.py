#!/usr/bin/env python3
"""Refresh the curvature-prolongation status after mapping-cylinder closure."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_prolongation_status import (
    CurvatureProlongationStatus,
)
from covariant_completion.curved_operator.null_symbol_quotient import (
    CurvedNullSymbolQuotient,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_curvature_prolongation_status.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a certificate object")
    return value


def _build(
    *,
    include_mapping_cylinder: bool,
    rees_override: dict[str, object] | None = None,
    core_chain_override: dict[str, object] | None = None,
    include_current: bool = True,
    current_override: dict[str, object] | None = None,
    include_promotion: bool = True,
    promotion_override: dict[str, object] | None = None,
    factorization_certificate: dict[str, object] | None = None,
    include_transport_recognition: bool = True,
    transport_recognition_override: dict[str, object] | None = None,
    include_SO42_recognition: bool = True,
    SO42_recognition_override: dict[str, object] | None = None,
    include_direct_tractor: bool = True,
    direct_tractor_override: dict[str, object] | None = None,
    curved_bgg_override: dict[str, object] | None = None,
    quotient: CurvedNullSymbolQuotient | None = None,
) -> CurvatureProlongationStatus:
    return CurvatureProlongationStatus.build(
        quotient=quotient,
        phase1_certificate=_load("curved_weyl_cotton_jet_comparison.json"),
        eal_certificate=_load("curved_EAL_spectrum_all_level.json"),
        hyperbolic_certificate=_load("curved_weyl_cotton_hyperbolic.json"),
        differential_ideal_certificate=_load(
            "curved_weyl_cotton_differential_ideal.json"
        ),
        formal_integrability_certificate=_load(
            "curved_weyl_cotton_formal_integrability.json"
        ),
        mapping_cylinder_certificate=(
            _load("curved_curvature_mapping_cylinder_substitution.json")
            if include_mapping_cylinder
            else None
        ),
        curved_core_chain_certificate=(
            core_chain_override
            if core_chain_override is not None
            else _load("curved_core_curvature_chain_map.json")
        ),
        rank14_full_cone_rees_certificate=(
            rees_override
            if rees_override is not None
            else _load("curved_rank14_full_cone_rees_gate.json")
        ),
        prolonged_current_certificate=(
            current_override
            if current_override is not None
            else _load("curved_prolonged_current_comparison.json")
            if include_current
            else None
        ),
        mixed_order_promotion_certificate=(
            promotion_override
            if promotion_override is not None
            else _load("curved_mixed_order_green_promotion.json")
            if include_promotion
            else None
        ),
        mixed_order_factorization_certificate=factorization_certificate,
        direct_tractor_causal_homotopy_certificate=(
            direct_tractor_override
            if direct_tractor_override is not None
            else _load("curved_full_prolonged_green_homotopy_assembly.json")
            if include_direct_tractor
            else None
        ),
        curved_bgg_pbw_certificate=(
            curved_bgg_override
            if curved_bgg_override is not None
            else _load("adjoint_tractor_bgg_curved_pbw.json")
            if include_direct_tractor
            else None
        ),
        causal_transport_recognition_certificate=(
            transport_recognition_override
            if transport_recognition_override is not None
            else _load("curved_causal_transport_recognition.json")
            if include_transport_recognition
            else None
        ),
        SO42_transport_recognition_certificate=(
            SO42_recognition_override
            if SO42_recognition_override is not None
            else _load("curved_SO42_causal_transport_recognition.json")
            if include_SO42_recognition
            else None
        ),
    )


def _valid_factorization_certificate() -> dict[str, object]:
    """Synthetic exact input used only to mutation-test dependency wiring."""

    return {
        "schema": "pure-weyl-mixed-order-factorization-v1",
        "exact_factorizations": {
            "D_P_equals_Lminus_Lplus": True,
            "P_D_equals_Rminus_Rplus": True,
            "global_coefficientwise": True,
        },
        "green_factors": {
            "Lminus_green_hyperbolic": True,
            "Lplus_green_hyperbolic": True,
            "Rminus_green_hyperbolic": True,
            "Rplus_green_hyperbolic": True,
        },
        "support": {
            "D_finite_order_differential": True,
            "all_factor_Green_operators_metric_causal": True,
        },
        "formal_adjoint_completion": {
            "all_bundle_pairings_nondegenerate": True,
            "factor_adjoint_relations_exact": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    status = _build(include_mapping_cylinder=True)
    certificate = status.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    promoted = (
        "curved_EB_equations",
        "curved_EB_first_order_closure",
        "curved_EB_symmetric_hyperbolicity",
        "curved_sourced_constraint_identity",
        "curved_constraint_propagation",
        "EAL_curvature_spectrum_match",
    )
    checks = {name: bool(certificate[name]) for name in promoted}
    checks["support_local_prolongation_retract_promoted"] = bool(
        certificate["support_local_prolongation_retract"]
    )
    checks["prolonged_BV_operator_identity_promoted"] = bool(
        certificate["prolonged_BV_operator_identity"]
    )
    checks["prolonged_current_promoted_from_corrected_core_provenance"] = bool(
        certificate["prolonged_current_comparison"]
    )
    fixed16 = certificate["fixed_temporal_16_diagnostic_flags"]
    checks["fixed_temporal_16_positive_no_go_recorded"] = (
        fixed16["fixed_temporal_16_family_complete"]
        and fixed16["intrinsic_sensitivity_matrix_zero"]
        and fixed16["parameter_uniform_Jordan_chain"]
        and not fixed16["strong_hyperbolicity_in_16_family"]
        and not fixed16["symmetric_hyperbolicity_in_16_family"]
        and fixed16["fixed_temporal_16_no_go"]
        and fixed16["aligned_physical_biwave_recursive_formula_exact"]
        and fixed16["aligned_physical_Jordan_extension_causal"]
        and fixed16["physical_biwave_block_green_hyperbolic"]
        and fixed16["physical_Jordan_extension_causal"]
        and fixed16["physical_green_flag_scope"]
        == "exact restricted TT plus shifted-auxiliary operator subcomplex"
        and fixed16["alternative_17_27_intrinsic_sensitivity_nonzero"]
        and not fixed16["alternative_17_27_minimal_regular_slices_semisimple"]
        and not fixed16["alternative_17_27_full_family_no_go"]
        and fixed16["alternative_minimal_sensitivity_family_complete"]
        and fixed16["alternative_minimal_family_zero_root_no_go"]
        and fixed16["rank34_presented_rank12_submodule_green"]
        and fixed16["rank34_rank8_constraint_quotient_hyperbolic"]
        and not fixed16["rank34_rank14_field_cokernel_green"]
        and fixed16["shifted_rank4_vector_block_contractible"]
        and fixed16["shifted_rank4_vector_replacement_Green_inverse"]
        and fixed16["shifted_rank4_vector_Green_homotopy"]
        and fixed16["all_row_Green_assembly_conditional_on_rank14"]
        and not fixed16["rank14_Weyl_Cotton_input_manifest_complete"]
        and fixed16["rank14_principal_projector_free_presentation"]
        and fixed16["rank14_principal_green_algebra"]
        and fixed16["direct_rank14_curvature_retraction_no_go"]
        and fixed16["rank14_equation_SDR_required"]
        and fixed16["rank14_raw_curvature_image_rank"] == 5
        and fixed16["rank14_raw_curvature_kernel_rank"] == 9
        and fixed16["rank14_compatible_source_kernel_rank"] == 12
        and not fixed16["rank14_raw_curvature_image_is_source_compatible"]
        and fixed16["rank14_generic_curvature_compatibility_defect_rank"] == 3
        and not fixed16["rank14_fake_V7_quotient_defined"]
        and not fixed16["rank14_equation_cone_exact"]
        and fixed16[
            "rank14_null_B3_H2_quotient_distinguished_from_constraint_kernel"
        ]
        and fixed16["rank14_witness_companion_cycle_gate_exact"]
        and fixed16["rank14_fake_state_SDR_rejected"]
        and fixed16["rank14_full_equation_cone_required"]
        and fixed16["rank14_ordinary_BV_Caux_layer_identified"]
        and not fixed16["rank14_curved_Caux_Rees_layer_unresolved"]
        and fixed16["rank14_mixed_symbol_cone_rejected"]
        and fixed16["rank14_common_Douglis_filtration_required"]
        and fixed16["rank14_common_Douglis_weight_constraints_feasible"]
        and not fixed16["rank14_full_symbol_cone_is_complex"]
        and not fixed16["rank14_full_symbol_cone_cohomology_computed"]
        and fixed16["rank14_full_Rees_final_square_defect_rank"] == 0
        and fixed16["rank14_stale_mixed_coordinate_Rees_defect_rank"] == 4
        and fixed16["rank14_fibre_identified_second_square_exact"]
        and not fixed16["rank14_identity_attachment_requires_repair"]
        and not fixed16["rank14_equation_SDR_constructed"]
        and not fixed16["rank14_green_operators_constructed"]
        and not fixed16["rank14_typed_incoming_map_ledger_complete"]
        and not fixed16["rank14_plain_state_kernel_quotient_is_target"]
        and not fixed16["rank14_principal_H7_contraction_certified"]
        and fixed16["rank14_corrected_equation_source_map_typed"]
        and fixed16["rank14_lower_order_PBW_may_resume"]
        and fixed16["rank14_stale_flat_Fourier_Rees_gate_superseded"]
        and fixed16["rank14_curved_core_projection_exact"]
        and fixed16["rank14_curved_attachment_chain_squares_exact"]
    )
    without_mapping = _build(
        include_mapping_cylinder=False, quotient=status.quotient
    )
    checks["retract_requires_mapping_certificate"] = not (
        without_mapping.support_local_prolongation_retract
    )
    checks["BV_identity_requires_mapping_certificate"] = not (
        without_mapping.prolonged_BV_operator_identity
    )
    without_current = _build(
        include_mapping_cylinder=True,
        include_current=False,
        quotient=status.quotient,
    )
    checks["current_requires_its_certificate"] = not (
        without_current.prolonged_current_comparison
    )
    if args.guards:
        inconsistent_rees = _load("curved_rank14_full_cone_rees_gate.json")
        inconsistent_rees["degree_zero_cone"]["is_complex"] = True
        try:
            _build(
                include_mapping_cylinder=True,
                rees_override=inconsistent_rees,
                quotient=status.quotient,
            )
        except AssertionError:
            checks["inconsistent_Rees_promotion_rejected"] = True
        else:
            checks["inconsistent_Rees_promotion_rejected"] = False
        broken_core = _load("curved_core_curvature_chain_map.json")
        broken_core["lifted_chain_squares"]["exact"] = False
        rejected_core = _build(
            include_mapping_cylinder=True,
            core_chain_override=broken_core,
            quotient=status.quotient,
        )
        checks["broken_curved_core_chain_blocks_mapping_promotion"] = not (
            rejected_core.support_local_prolongation_retract
            or rejected_core.prolonged_BV_operator_identity
        )
    checks["promotion_theorem_wired"] = status.mixed_order_promotion_theorem_exact
    checks["actual_factorization_absent"] = not status.mixed_order_factorization_exact
    checks["green_witness_remains_false"] = not status.prolonged_green_witness
    checks["causal_operators_remain_false"] = not (
        status.curvature_causal_green_operators
    )
    checks["direct_tractor_causal_homotopy_promoted"] = (
        status.direct_tractor_causal_homotopy
    )
    checks["direct_tractor_recognition_wired"] = (
        status.direct_tractor_causal_recognition_exact
    )
    checks["causal_homotopy_promoted_by_direct_tractor"] = (
        status.causal_green_homotopy
    )
    checks["transport_recognition_wired"] = (
        status.causal_transport_recognition_exact
    )
    checks["causal_quasi_promoted_by_direct_tractor"] = (
        status.causal_quasi_isomorphism
    )
    checks["endpoint_recovery_promoted_by_direct_tractor"] = (
        status.residual_endpoint_recovery
    )
    checks["SO42_recognition_wired"] = status.SO42_transport_recognition_exact
    checks["SO42_promoted_by_direct_tractor"] = (
        status.SO42_equivariant_transport
    )
    if args.guards:
        broken_current = _load("curved_prolonged_current_comparison.json")
        broken_current["all_row_ledger"]["silent_rows_dropped"] = 1
        rejected_current = _build(
            include_mapping_cylinder=True,
            current_override=broken_current,
            quotient=status.quotient,
        )
        checks["missing_current_row_blocks_promotion"] = not (
            rejected_current.prolonged_current_comparison
        )
        without_promotion = _build(
            include_mapping_cylinder=True,
            include_promotion=False,
            quotient=status.quotient,
        )
        checks["promotion_requires_theorem_certificate"] = not (
            without_promotion.mixed_order_promotion_theorem_exact
        )
        promotion = _load("curved_mixed_order_green_promotion.json")
        mutation_paths = (
            ("exact_formal_construction", "right_inverse_defect", 1),
            ("exact_formal_construction", "left_inverse_defect", 1),
            ("exact_formal_construction", "formula_equality_defect", 1),
            ("causal_support", "D_does_not_enlarge_support", False),
            ("formal_adjoint_handling", "operator_order_reversal_checked", False),
            (
                "sixteen_block_insertion",
                "conditional_all_16_blocks_two_sided_and_causal",
                False,
            ),
            ("homological_consequence_if_coefficients_pass", "QG_equals_GQ", False),
        )
        for section, key, value in mutation_paths:
            broken = deepcopy(promotion)
            broken[section][key] = value
            rejected = _build(
                include_mapping_cylinder=True,
                promotion_override=broken,
                include_direct_tractor=False,
                quotient=status.quotient,
            )
            checks[f"broken_{key}_blocks_promotion"] = not (
                rejected.mixed_order_promotion_theorem_exact
                or rejected.prolonged_green_witness
                or rejected.curvature_causal_green_operators
                or rejected.causal_green_homotopy
            )
        malformed_factorizations = (
            {},
            {"schema": "wrong"},
            {
                "schema": "pure-weyl-mixed-order-factorization-v1",
                "exact_factorizations": {},
                "green_factors": {},
                "support": {},
                "formal_adjoint_completion": {},
            },
        )
        for index, malformed in enumerate(malformed_factorizations):
            rejected = _build(
                include_mapping_cylinder=True,
                factorization_certificate=malformed,
                include_direct_tractor=False,
                quotient=status.quotient,
            )
            checks[f"malformed_factorization_{index}_blocks_promotion"] = not (
                rejected.mixed_order_factorization_exact
                or rejected.prolonged_green_witness
                or rejected.curvature_causal_green_operators
                or rejected.causal_green_homotopy
            )
        try:
            CurvatureProlongationStatus.build(
                mixed_order_factorization_certificate={}
            )
        except AssertionError:
            checks["factorization_without_theorem_rejected"] = True
        else:
            checks["factorization_without_theorem_rejected"] = False
        without_direct_tractor = _build(
            include_mapping_cylinder=True,
            include_direct_tractor=False,
            quotient=status.quotient,
        )
        checks["direct_tractor_certificate_required"] = not any(
            (
                without_direct_tractor.direct_tractor_causal_homotopy,
                without_direct_tractor.causal_green_homotopy,
                without_direct_tractor.causal_quasi_isomorphism,
                without_direct_tractor.residual_endpoint_recovery,
                without_direct_tractor.SO42_equivariant_transport,
            )
        )
        broken_direct = _load(
            "curved_full_prolonged_green_homotopy_assembly.json"
        )
        broken_direct["full_hybrid_assembly"][
            "algebraic_identity_exact_conditionally"
        ] = False
        rejected_direct = _build(
            include_mapping_cylinder=True,
            direct_tractor_override=broken_direct,
            quotient=status.quotient,
        )
        checks["broken_direct_tractor_certificate_blocks_transport"] = not any(
            (
                rejected_direct.direct_tractor_causal_homotopy,
                rejected_direct.causal_green_homotopy,
                rejected_direct.causal_quasi_isomorphism,
                rejected_direct.residual_endpoint_recovery,
                rejected_direct.SO42_equivariant_transport,
            )
        )
        without_transport_recognition = _build(
            include_mapping_cylinder=True,
            include_transport_recognition=False,
            factorization_certificate=_valid_factorization_certificate(),
            quotient=status.quotient,
        )
        checks["three_Green_flags_can_promote_in_synthetic_guard"] = all(
            (
                without_transport_recognition.prolonged_green_witness,
                without_transport_recognition.curvature_causal_green_operators,
                without_transport_recognition.causal_green_homotopy,
            )
        )
        checks["causal_quasi_requires_recognition_certificate"] = not (
            without_transport_recognition.causal_quasi_isomorphism
        )
        checks["endpoint_requires_recognition_certificate"] = not (
            without_transport_recognition.residual_endpoint_recovery
        )
        with_transport_recognition = _build(
            include_mapping_cylinder=True,
            factorization_certificate=_valid_factorization_certificate(),
            quotient=status.quotient,
        )
        checks["causal_quasi_promotes_only_after_all_inputs"] = (
            with_transport_recognition.causal_quasi_isomorphism
        )
        checks["endpoint_promotes_only_after_all_inputs"] = (
            with_transport_recognition.residual_endpoint_recovery
        )
        checks["SO42_promotes_only_after_all_inputs"] = (
            with_transport_recognition.SO42_equivariant_transport
        )
        recognition = _load("curved_causal_transport_recognition.json")
        broken_recognition = deepcopy(recognition)
        broken_recognition["causal_quasi_isomorphism"][
            "right_cohomology_inverse"
        ] = False
        rejected_transport = _build(
            include_mapping_cylinder=True,
            factorization_certificate=_valid_factorization_certificate(),
            transport_recognition_override=broken_recognition,
            quotient=status.quotient,
        )
        checks["broken_transport_recognition_blocks_causal_quasi"] = not (
            rejected_transport.causal_quasi_isomorphism
        )
        checks["broken_transport_recognition_blocks_endpoint"] = not (
            rejected_transport.residual_endpoint_recovery
        )
        checks["broken_transport_recognition_blocks_SO42"] = not (
            rejected_transport.SO42_equivariant_transport
        )

        without_SO42_recognition = _build(
            include_mapping_cylinder=True,
            factorization_certificate=_valid_factorization_certificate(),
            include_SO42_recognition=False,
            quotient=status.quotient,
        )
        checks["SO42_requires_its_recognition_certificate"] = not (
            without_SO42_recognition.SO42_equivariant_transport
        )
        so42_recognition = _load("curved_SO42_causal_transport_recognition.json")
        broken_so42 = deepcopy(so42_recognition)
        broken_so42["cutoff_homotopy"]["formal_defect"] = 1
        rejected_so42 = _build(
            include_mapping_cylinder=True,
            factorization_certificate=_valid_factorization_certificate(),
            SO42_recognition_override=broken_so42,
            quotient=status.quotient,
        )
        checks["broken_SO42_recognition_blocks_promotion"] = not (
            rejected_so42.SO42_equivariant_transport
        )
        for name, passed in checks.items():
            if not passed:
                raise AssertionError(f"curvature status promotion failed: {name}")
        print(
            "CURVATURE PROLONGATION STATUS GUARDS: "
            f"{len(checks)}/{len(checks)} PASS"
        )
    print(
        "CURVATURE PROLONGATION STATUS: PDE AND LOCAL PROLONGATION FLAGS TRUE; "
        "DIRECT-TRACTOR GREEN/CURRENT/TRANSPORT FLAGS TRUE; "
        "CANONICAL ENDPOINT FLAGS FALSE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
