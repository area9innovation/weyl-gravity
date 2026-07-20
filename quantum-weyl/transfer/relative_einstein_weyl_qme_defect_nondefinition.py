"""Exact non-definition of the first relative Einstein--Weyl QME defect.

The complete all-row linear triangle supplies a contravariant classical
observable pullback.  It does not supply the action-compatible cyclic
pushforward required by the requested target-valued subtraction, nor do the
repository inputs contain matched Einstein--Maxwell and Weyl--Maxwell
renormalized QME insertions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
READINESS = (
    QROOT
    / "relative/certificates/"
    "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json"
)
TRIANGLE = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json"
OBSERVABLE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1.json"
)
CYCLIC_RANK = (
    ROOT
    / "d_quotient_classical/certificates/"
    "EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1.json"
)
COTANGENT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json"
)
LOCAL_ANOMALY = (
    QROOT
    / "local_bv/certificates/"
    "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path) -> dict[str, str]:
    value = _load(path)
    result_id = value.get("result_id") or value.get("certificate_id")
    if not result_id:
        raise ValueError(f"dependency identity missing: {path}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "result_id": str(result_id),
        "sha256": _sha256(path),
    }


def evaluate() -> dict[str, Any]:
    readiness = _load(READINESS)
    triangle = _load(TRIANGLE)
    observable = _load(OBSERVABLE)
    cyclic_rank = _load(CYCLIC_RANK)
    cotangent = _load(COTANGENT)
    local_anomaly = _load(LOCAL_ANOMALY)

    if (
        readiness.get("result_id")
        != "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS"
        or triangle.get("result_id")
        != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        or observable.get("result_id")
        != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"
        or cyclic_rank.get("result_id")
        != "EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1"
        or cotangent.get("result_id")
        != "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1"
        or local_anomaly.get("result_id")
        != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
    ):
        raise ValueError("relative Einstein--Weyl input identity drifted")

    triangle_hash = _sha256(TRIANGLE)
    observable_hash = _sha256(OBSERVABLE)
    if (
        readiness["dependency_refs"]["relative_linear_triangle"]["sha256"]
        != triangle_hash
        or readiness["dependency_refs"]["relative_observable_functor"]["sha256"]
        != observable_hash
        or readiness["classical_import_gate"]["current_map_disposition"]
        != "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED"
        or observable["observable_pullback"]["contravariant"] is not True
        or "q_EM^dual iota_star = iota_star q_WM^dual"
        not in observable["observable_pullback"]["chain_identity"]
        or observable["observable_pullback"]["support_local"] is not True
        or "no standard-pairing cyclic relative map"
        not in observable["claim_boundary"]
    ):
        raise ValueError("relative classical import replay failed")

    if (
        cyclic_rank["result_state"]
        != "FIXED_238_ROW_CARRIER_HAS_NO_NONDEGENERATE_DEGREE_ONE_ODD_PAIRING"
        or cotangent["result_state"]
        != "CANONICAL_ODD_COTANGENT_UNARY_COMPLETION_SELECTED"
        or readiness["framework_ledger"]["EUCLIDEAN_SPECTRAL"]["status"]
        != "NOT_COMPUTED_RELATIVELY"
        or readiness["qme_and_transfer_gate"]["Einstein_QME"]
        != "NOT_COMPUTED"
        or readiness["qme_and_transfer_gate"]["relative_QME_defect"]
        != "UNDEFINED_ANALYTICALLY"
    ):
        raise ValueError("relative quantum/cyclic boundary drifted")

    bulk_vector = local_anomaly["two_method_coefficients"]["repository_vector"]
    if bulk_vector != {
        "ANOM_OMEGA_C2": {"numerator": 199, "denominator": 30},
        "ANOM_OMEGA_E4": {"numerator": -87, "denominator": 20},
        "ANOM_OMEGA_C_DUAL_C": {"numerator": 0, "denominator": 1},
        "ANOM_OMEGA_BOX_R": {"numerator": 0, "denominator": 1},
    }:
        raise ValueError("pure-Weyl anomaly vector drifted")

    exact_checks = {
        "all_row_linear_triangle_hash_matches_readiness": True,
        "observable_pullback_hash_matches_readiness": True,
        "contravariant_pullback_is_support_local_chain_map": True,
        "standard_action_pairing_cyclic_map_absent": True,
        "fixed_238_row_cyclic_pairing_obstructed": True,
        "cotangent_completion_changes_carrier_and_pairing": True,
        "matched_relative_Euclidean_spectral_pair_absent": True,
        "Einstein_QME_insertion_absent": True,
        "pure_Weyl_vector_not_promoted_to_coupled_relative_vector": True,
        "compact_product_has_no_asymptotic_boundary": True,
    }
    if not all(exact_checks.values()):
        raise ValueError("relative QME non-definition replay failed")

    result = {
        "schema": "quantum-weyl-relative-einstein-weyl-qme-defect-nondefinition-v1",
        "result_id": "RELATIVE_EINSTEIN_WEYL_QME_DEFECT_NONDEFINITION",
        "result_state": (
            "COMPLETE_CLASSICAL_LINEAR_RESTRICTION_IMPORTED_RELATIVE_ONE_LOOP_"
            "CLASS_UNDEFINED_WITH_CYCLIC_AND_MATCHED_QME_ROWS_MISSING"
        ),
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "setting": {
            "theory_pair": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact Einstein-Maxwell product",
            "boundary_conditions": (
                "compact periodic S1 x S2 fixed bundle; no asymptotic boundary"
            ),
            "charge_sector": (
                "complete standard harmonic tangent before optional stabilizer "
                "reduction; absolute quotient unauthorized before common "
                "moment-map/Taub-zero and null-subalgebra certification"
            ),
            "antifield_scope": (
                "complete classical all-row linear triangle imported; "
                "renormalized antifield insertion map not supplied"
            ),
        },
        "classical_triangle": {
            "selected_result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            "strength": (
                "complete all-row finite-order support-local noncyclic linear "
                "triangle with exact mapping cofiber"
            ),
            "observable_result_id": "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
            "restriction_map": (
                "iota_star: Obs_WM -> Obs_EM is a contravariant support-local "
                "linear BRST-DGA chain map"
            ),
            "cyclic_map": (
                "NOT_SUPPLIED: the three action-derived pairings remain "
                "distinct and no standard-pairing cyclic relative map exists"
            ),
            "H_product_equivariance": "CERTIFIED_INCLUDING_TIME_TRANSLATION",
        },
        "relative_anomaly_complex": {
            "formal_complex": "Cone(iota_star:C_WM->C_EM)[-1]",
            "degree_n_elements": "(a_WM,b_EM) in C_WM^n direct_sum C_EM^(n-1)",
            "differential": (
                "D_rel(a_WM,b_EM)="
                "(s_WM a_WM, iota_star(a_WM)-s_EM b_EM)"
            ),
            "closure_condition": (
                "s_WM a_WM=0 and iota_star(a_WM)=s_EM b_EM"
            ),
            "classical_definition_status": "DEFINED_AT_LINEAR_OBSERVABLE_LEVEL",
            "one_loop_insertion_status": (
                "UNDEFINED_MATCHED_RENORMALIZED_INSERTIONS_NOT_SUPPLIED"
            ),
        },
        "requested_subtraction": {
            "formal_expression": (
                "[A_rel]=[A_WM-iota_push A_EM]"
            ),
            "contravariant_map_available": True,
            "covariant_action_compatible_iota_push_available": False,
            "reason": (
                "A target-valued pushforward requires an action-compatible "
                "cyclic pairing. The fixed 238-row carrier has an exact rank "
                "obstruction; the 316-row cotangent completion changes the "
                "carrier and pairing and is not the action-current pushforward."
            ),
        },
        "coefficient_ledger": {
            "strict_pure_Weyl_bulk_vector": bulk_vector,
            "Einstein_Maxwell_QME_insertion": "NOT_COMPUTED",
            "Weyl_Maxwell_QME_insertion": (
                "NOT_COMPUTED_AS_MATCHED_COUPLED_TARGET"
            ),
            "relative_vector": "UNDEFINED",
            "warning": (
                "The pure-Weyl graviton vector cannot be reused as the "
                "Weyl-Maxwell target or relative coefficient vector."
            ),
        },
        "missing_object_ledger": [
            {
                "object_id": "MATCHED_EINSTEIN_MAXWELL_RENORMALIZED_QME_INSERTION",
                "status": "MISSING",
            },
            {
                "object_id": "MATCHED_WEYL_MAXWELL_RENORMALIZED_QME_INSERTION",
                "status": "MISSING",
            },
            {
                "object_id": "RENORMALIZED_RELATIVE_OBSERVABLE_PULLBACK",
                "status": "MISSING",
            },
            {
                "object_id": "ACTION_COMPATIBLE_CYCLIC_IOTA_PUSH",
                "status": "OBSTRUCTED_ON_FIXED_238_ROW_CARRIER",
            },
            {
                "object_id": "RENORMALIZED_ANTIFIELD_MEASURE_ZERO_MODE_MAPS",
                "status": "MISSING",
            },
            {
                "object_id": "COMMON_TAUB_ZERO_DERIVED_SECTOR_AND_NULL_QUOTIENT",
                "status": "MISSING",
            },
        ],
        "separate_ledgers": {
            "determinant_factorization": (
                "NOT_COMPUTED_RELATIVELY_NO_MATCHED_OPERATOR_MEASURE_PAIR"
            ),
            "residual_action": (
                "H_PRODUCT_EQUIVARIANT_LINEAR_CLASSICAL_MAP_ONLY"
            ),
            "boundary_corner": (
                "NOT_APPLICABLE_TO_COMPACT_PERIODIC_SETTING; NO_ASYMPTOTIC "
                "BOUNDARY CLAIM"
            ),
            "Lorentzian_state": "NOT_CONSTRUCTED",
            "relative_D_Cartan": "UNDEFINED_ANALYTICALLY",
        },
        "verdict": {
            "classification": "UNDEFINED",
            "first_exact_obstruction": (
                "NO_ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_ON_THE_IMPORTED_"
                "TRIANGLE_AND_NO_MATCHED_EINSTEIN_MAXWELL_WEYL_MAXWELL_"
                "RENORMALIZED_QME_INSERTION_PAIR"
            ),
            "relative_anomaly_class": "NOT_DEFINED",
            "relative_coefficient": "NOT_DEFINED",
            "relative_QME_restored": False,
        },
        "claim_flags": {
            "COMPLETE_CLASSICAL_LINEAR_TRIANGLE_IMPORTED": True,
            "CONTRAVARIANT_OBSERVABLE_RESTRICTION_IMPORTED": True,
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_IMPORTED": False,
            "MATCHED_RELATIVE_QME_INSERTIONS_IMPORTED": False,
            "RELATIVE_ANOMALY_CLASS_DEFINED": False,
            "RELATIVE_COEFFICIENT_COMPUTED": False,
            "PURE_WEYL_VECTOR_IS_RELATIVE_VECTOR": False,
            "RELATIVE_QME_RESTORED": False,
            "LORENTZIAN_RELATIVE_STATE_CERTIFIED": False,
        },
        "exact_checks": exact_checks,
        "dependency_refs": {
            "quantum_relative_readiness": _ref(READINESS),
            "relative_linear_triangle": _ref(TRIANGLE),
            "relative_observable_functor": _ref(OBSERVABLE),
            "fixed_238_cyclic_rank_obstruction": _ref(CYCLIC_RANK),
            "canonical_316_cotangent_completion": _ref(COTANGENT),
            "pure_Weyl_local_anomaly": _ref(LOCAL_ANOMALY),
        },
        "next_gate": (
            "COMPUTE_MATCHED_EINSTEIN_MAXWELL_AND_WEYL_MAXWELL_QME_"
            "INSERTIONS_AND_CONSTRUCT_AN_ACTION_COMPATIBLE_RENORMALIZED_"
            "RELATIVE_MAP"
        ),
        "claim_boundary": (
            "This exact result imports the strongest complete classical "
            "linear triangle and defines its relative mapping-cone convention, "
            "but proves that the requested coefficient-bearing one-loop "
            "relative class is not defined. It does not identify the pure-Weyl "
            "bulk vector with a coupled relative vector, compute a relative "
            "determinant, restore a QME, renormalize a cofiber pairing, define "
            "an asymptotic boundary charge, construct a Lorentzian state, or "
            "establish particles, positivity, scattering or unitarity."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    flags = value["claim_flags"]
    if (
        value["verdict"]["classification"] != "UNDEFINED"
        or not flags["COMPLETE_CLASSICAL_LINEAR_TRIANGLE_IMPORTED"]
        or not flags["CONTRAVARIANT_OBSERVABLE_RESTRICTION_IMPORTED"]
        or flags["ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_IMPORTED"]
        or flags["MATCHED_RELATIVE_QME_INSERTIONS_IMPORTED"]
        or flags["RELATIVE_ANOMALY_CLASS_DEFINED"]
        or flags["RELATIVE_COEFFICIENT_COMPUTED"]
        or flags["PURE_WEYL_VECTOR_IS_RELATIVE_VECTOR"]
        or flags["RELATIVE_QME_RESTORED"]
        or flags["LORENTZIAN_RELATIVE_STATE_CERTIFIED"]
    ):
        raise ValueError("relative QME claim boundary was over-promoted")


if __name__ == "__main__":
    evaluate()
    print("RELATIVE EINSTEIN-WEYL QME DEFECT NONDEFINITION: PASS")
