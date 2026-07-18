#!/usr/bin/env python3
"""Independent verifier for the active quantum-frontier certificate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

try:
    from .active_frontier import DEPENDENCIES, validate
    from .active_frontier_certificate import HERE, OUTPUT, build_certificate
except ImportError:
    from active_frontier import DEPENDENCIES, validate
    from active_frontier_certificate import HERE, OUTPUT, build_certificate


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads((HERE / "schema/active-frontier-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if certificate != build_certificate():
        raise ValueError("active frontier does not reproduce")
    for name, path in DEPENDENCIES.items():
        reference = certificate["dependency_refs"][name]
        if reference["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"active frontier dependency drifted: {name}")
    for key in (
        "GLOBAL_BRST_HADAMARD_STATE",
        "HADAMARD_EXISTENCE_THEOREM_APPLIES",
        "RANK_46_IS_QUANTUM_PREREQUISITE",
        "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED",
        "FULL_EXTENDED_BV_QME_RESTORED",
        "FINITE_C2_NORMALIZATION_FIXED",
        "FINITE_R2_NORMALIZATION_FIXED",
        "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED",
        "PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE",
        "REPOSITORY_GENERIC_BACKGROUND_CPT_TRACE_SUBSTITUTION_SUPPLIED",
        "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED",
        "GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED",
        "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED",
        "GENERIC_GHOST_LONGITUDINAL_DW_CARRIERS_EVALUATED",
        "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED",
        "RENORMALIZED_R_K_COMPUTED",
        "FINITE_PART_R_K2_COMPUTED",
        "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED",
        "ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED",
        "ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED",
        "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED",
        "FV_AND_WZ_DRESSED_METRICS_IDENTIFIED",
        "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
        "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
        "A_L_BRANCHES_POSITIVE",
        "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED",
        "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED",
        "BERGER_BRIDGE4_CERTIFIED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"active frontier overclaim accepted: {key}")
    for key in (
        "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED",
        "REPOSITORY_C2_COEFFICIENT_COMPUTED",
        "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_OBSTRUCTED_STRICT_FIELD_CONTENT",
        "STANDARD_UNITARY_FREE_MATTER_CANCELLATION_OBSTRUCTED",
        "WZ_AFN0_PRIMITIVE_CERTIFIED",
        "WZ_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED",
        "WZ_TAU_ADIC_EXTENDED_H04_H14_COMPLETE",
        "TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED",
        "WZ_LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED",
        "FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO",
        "FLAT_TT_UNIVERSAL_LOG_GAMMA1_FORM_FACTOR_FIXED",
        "CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED",
        "FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE",
        "FV_CONFORMIZED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED",
        "FV_ANOMALY_ACTION_FIXED",
        "RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED",
        "ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE",
        "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE",
        "FIVE_UNIVERSAL_CPT_THIRD_CURVATURE_KERNELS_IMPORTED",
        "GENERIC_BACKGROUND_GHOST_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED",
        "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED",
        "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED",
        "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED",
        "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED",
        "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED",
        "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION",
        "SCHUR_CORRECTION_S3_CLASS_PROVED",
        "CANONICAL_DET3_TAIL_DEFINED",
        "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED",
        "WODZICKI_RESIDUE_K_COMPUTED",
        "WODZICKI_RESIDUE_LOG_S_COMPUTED",
        "ZETA_SCALE_COEFFICIENT_COMPUTED",
        "GENERIC_GHOST_N3_ADIABATIC_ANGULAR_CARRIER_COMPUTED",
        "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED",
        "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED",
        "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED",
        "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE",
        "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED",
        "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED",
        "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED",
        "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED",
        "VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED",
        "REDUCED_COMPATIBLE_COMPLEX_STRUCTURE_CERTIFIED",
        "REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED",
        "E_BRANCH_POSITIVE_HADAMARD_STATE_CERTIFIED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = False
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"active frontier certified result dropped: {key}")
    return certificate


def main() -> int:
    verify()
    print("QUANTUM WEYL ACTIVE FRONTIER independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
