"""Fail-closed disposition of the complete renormalized D-Ward insertion.

The classical same-background Wess--Zumino compensator contraction is now
available.  This module therefore removes that historical blocker, declares
an explicit (non-canonical) reference finite-counterterm scheme, and identifies
the first analytic operators that are still not defined on the target
vacuum-cylinder tau-adic BV observable complex.

No absence claim is inferred from a filename search.  Every negative status is
read from a content-addressed producer certificate whose own claim boundary
states that the corresponding operator or domain is not supplied.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

DEPENDENCIES = {
    "classical_wz_d_cartan": (
        ROOT
        / "d_quotient_classical/certificates/"
        "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json"
    ),
    "local_anomaly_audit": (
        ROOT
        / "quantum-weyl/local_bv/certificates/"
        "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
    ),
    "q1_disposition": (
        ROOT
        / "quantum-weyl/transfer/certificates/"
        "ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json"
    ),
    "anomaly_induced_gamma1": (
        ROOT
        / "quantum-weyl/transfer/certificates/"
        "ANOMALY_INDUCED_NONLOCAL_GAMMA1.json"
    ),
    "curvature_squared_gamma1": (
        ROOT
        / "quantum-weyl/transfer/certificates/"
        "CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json"
    ),
    "fv_conformized_gamma1": (
        ROOT
        / "quantum-weyl/transfer/certificates/"
        "FV_CONFORMIZED_C2_LOG_GAMMA1.json"
    ),
    "ward_contract": (
        HERE / "certificates/RENORMALIZED_D_WARD_INSERTION_CONTRACT.json"
    ),
    "cartan_disposition": (
        HERE / "certificates/QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION.json"
    ),
}

EXPECTED_IDS = {
    "classical_wz_d_cartan": "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1",
    "local_anomaly_audit": "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT",
    "q1_disposition": "ONE_LOOP_SLAVNOV_Q1_DISPOSITION",
    "anomaly_induced_gamma1": "ANOMALY_INDUCED_NONLOCAL_GAMMA1",
    "curvature_squared_gamma1": "CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1",
    "fv_conformized_gamma1": "FV_CONFORMIZED_C2_LOG_GAMMA1",
    "ward_contract": "RENORMALIZED_D_WARD_INSERTION_CONTRACT",
    "cartan_disposition": "QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION",
}

REQUEST_EVENT = (
    ROOT
    / "planning/events/"
    "quantum-complete-renormalized-d-ward-insertion-REQUEST-1190fa5df53e8659.json"
)
REQUEST_ID = (
    "sf:program/request/"
    "quantum-complete-renormalized-d-ward-insertion-to-quantum-qme-"
    "1190fa5df53e8659"
)
REQUEST_NEED_ID = (
    "FULL_TAU_ADIC_BV_HADAMARD_FEYNMAN_KERNEL_AND_RENORMALIZED_"
    "T2_EXTENSION_ON_VACUUM_CYLINDER"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _require_inputs(values: dict[str, dict[str, Any]]) -> None:
    for name, value in values.items():
        if value.get("result_id") != EXPECTED_IDS[name]:
            raise ValueError(f"dependency identity drifted: {name}")

    classical = values["classical_wz_d_cartan"]
    flags = classical["claim_flags"]
    if (
        classical["background"]["setting_id"]
        != "vacuum_cylinder_regular_Bach_chart"
        or classical["generator"]["generator_id"] != "D_compact"
        or not flags["SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION"]
        or not flags["RAW_D_COMPACT_USED"]
        or flags["RAW_D_REPLACED_BY_K_BERGER"]
        or flags["WZ_TAU_IDENTIFIED_WITH_BERGER_CLOCK"]
        or flags["QUANTUM_D_CARTAN_DEFECT_CLASSIFIED"]
    ):
        raise ValueError("classical same-background Cartan export drifted")

    audit = values["local_anomaly_audit"]
    if (
        audit["QME_lifecycles"]["tau_adic_compensator_extended"]
        != "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
        or audit["QME_lifecycles"]["Lorentzian"] != "OPEN"
        or audit["claim_flags"]["LORENTZIAN_QME_CERTIFIED"]
    ):
        raise ValueError("local QME lifecycle drifted")

    q1 = values["q1_disposition"]
    if (
        q1["finite_counterterm_ambiguity"]["bulk_response_rank"] != 2
        or q1["finite_counterterm_ambiguity"]["bulk_quadratic_response_matrix"]
        != [
            [_q(1), _q(0), _q(0), _q(0)],
            [_q(0), _q(0), _q(9), _q(0)],
        ]
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
        or q1["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or q1["claim_flags"]["RESIDUAL_TRANSFER_AUTHORIZED"]
    ):
        raise ValueError("Q1 non-uniqueness disposition drifted")

    anomaly = values["anomaly_induced_gamma1"]
    if (
        not anomaly["claim_flags"]["ANOMALY_INDUCED_REPRESENTATIVE_SUPPLIED"]
        or anomaly["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or anomaly["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or anomaly["green_operator_contract"]["existence_status"]
        != "CONDITIONAL_ON_DECLARED_EUCLIDEAN_GENERALIZED_INVERSE"
    ):
        raise ValueError("conditional anomaly-induced Gamma1 scope drifted")

    curved = values["curvature_squared_gamma1"]
    if (
        not curved["claim_flags"]["CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED"]
        or curved["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or curved["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"]
        or curved["claim_flags"]["FINITE_R2_NORMALIZATION_FIXED"]
    ):
        raise ValueError("curvature-squared Gamma1 scope drifted")

    fv = values["fv_conformized_gamma1"]
    if (
        not fv["claim_flags"]["SELECTED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED"]
        or fv["claim_flags"]["NONLOCAL_R2_FORM_FACTOR_COMPUTED"]
        or fv["claim_flags"]["INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"]
        or fv["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
    ):
        raise ValueError("FV conformized Gamma1 scope drifted")

    ward = values["ward_contract"]
    if (
        ward["accepted_export_schema"]
        != "quantum-weyl-renormalized-D-ward-insertion-export-v1"
        or ward["physical_input_status"] != "NOT_RECEIVED"
        or ward["local_to_cartan_map_status"] != "NOT_CONSTRUCTED"
        or ward["quantum_cartan_status"] != "NO_VERDICT"
    ):
        raise ValueError("Ward insertion contract drifted")

    cartan = values["cartan_disposition"]
    if (
        cartan["claim_flags"]["EXTENDED_CARTAN_CLASS_CLASSIFIED"]
        or cartan["claim_flags"]["RESIDUAL_TRANSFER_AUTHORIZED"]
    ):
        raise ValueError("prior Cartan disposition was over-promoted")


def _request_row() -> dict[str, str]:
    event = _load(REQUEST_EVENT)
    payload = event.get("body", {}).get("payload", {})
    if (
        event.get("body", {}).get("event_kind") != "REQUEST"
        or payload.get("request_id") != REQUEST_ID
        or payload.get("from_item")
        != "sf:program/work/quantum-complete-renormalized-d-ward-insertion"
        or payload.get("to_stream") != "quantum-qme"
        or payload.get("typed") != "coefficient-bearing-operator"
        or not str(payload.get("need", "")).startswith(REQUEST_NEED_ID + ":")
    ):
        raise ValueError("next analytic producer request drifted")
    return {
        "request_id": REQUEST_ID,
        "to_stream": "quantum-qme",
        "typed": "coefficient-bearing-operator",
        "need_id": REQUEST_NEED_ID,
        "status": "FILED_APPEND_ONLY",
        "event_path": _relative(REQUEST_EVENT),
        "event_sha256": _sha256(REQUEST_EVENT),
    }


def evaluate() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _require_inputs(values)
    q1 = values["q1_disposition"]
    classical = values["classical_wz_d_cartan"]

    result = {
        "schema": "quantum-weyl-renormalized-d-ward-insertion-nondefinition-v1",
        "result_id": "RENORMALIZED_D_WARD_INSERTION_NONDEFINITION",
        "result_state": (
            "REFERENCE_FINITE_NORMALIZATION_DECLARED_CLASSICAL_CARTAN_"
            "IMPORTED_FIRST_ANALYTIC_OPERATOR_UNDEFINED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "setting": {
            "theory_id": "TAU_ADIC_WESS_ZUMINO_EXTENDED_WEYL",
            "background_id": "vacuum_cylinder_regular_Bach_chart",
            "metric": "g_bar=-dt^2+dOmega_3^2",
            "boundaries": "closed compact Cauchy surface S3; no spatial boundary",
            "phase_space_id": "P_der",
            "generator_id": "D_compact",
            "signature_target": "LORENTZIAN_SAME_BACKGROUND",
        },
        "classical_import": {
            "status": "CERTIFIED",
            "available_operators": [
                "Q0",
                "iota_D0",
                "L_D0",
                "inclusion",
                "projection",
                "homotopy",
                "pairing",
            ],
            "operator_sha256": classical["content_hashes"]["operators_sha256"],
            "formal_algebra_sha256": classical["content_hashes"][
                "formal_algebra_sha256"
            ],
            "cartan_identity": "[Q0,iota_D0]_+=L_D0",
            "sdr_identity": "Q0 S+S Q0=1-inclusion projection",
        },
        "finite_normalization": {
            "scheme_id": "DECLARED_REFERENCE_ZERO_FINITE_BULK_SCHEME",
            "reference_scale": "mu_star>0",
            "conditions": [
                "z_C(mu_star)=0",
                "z_Rhat2(mu_star)=0",
            ],
            "status": "DECLARED_CONVENTION_NOT_CANONICAL_PHYSICAL_NORMALIZATION",
            "reason": (
                "the anomaly fixes scale response but no external finite "
                "renormalization observable selects the additive constants"
            ),
            "scheme_change": {
                "parameters": ["alpha_C", "alpha_R"],
                "delta_Gamma1": (
                    "alpha_C integral C(g_hat)^2+"
                    "alpha_R integral R(g_hat)^2"
                ),
                "delta_Q1": "(delta_Gamma1,-)_BV",
                "bulk_response_basis": ["TT", "CONFORMAL"],
                "bulk_response_matrix": [[_q(1), _q(0)], [_q(0), _q(9)]],
                "rank": 2,
            },
        },
        "analytic_branches": {
            "same_background_lorentzian": {
                "status": "FIRST_DISTRIBUTION_EXTENSION_UNDEFINED",
                "first_missing_operator": "T2_ren_tau_adic_BV",
                "domain": (
                    "F_loc(E_ext) tensor F_loc(E_ext) on "
                    "M=R_t x S3, E_ext=tau-adic minimal BV bundle"
                ),
                "off_diagonal_domain": "M^2 minus Diag_2",
                "required_extension": (
                    "extend the graded time-ordered contraction kernels from "
                    "M^2\\Diag_2 across Diag_2 with local covariance, causal "
                    "factorization, scaling-degree bounds, cyclicity, and the "
                    "Q0 Ward identity"
                ),
                "missing_prerequisites": [
                    "FULL_TAU_ADIC_BV_BRST_COMPATIBLE_HADAMARD_FEYNMAN_KERNEL",
                    "EPSTEIN_GLASER_T2_EXTENSION_ACROSS_DIAG2",
                    "RENORMALIZED_COINCIDENT_BV_CONTRACTION_DELTA_REN",
                    "COMMON_OPERATOR_DOMAIN_AND_ZERO_MODE_POLICY",
                ],
                "consequence": (
                    "the same-background renormalized BV Laplacian/time-"
                    "ordered product and hence complete Q1 are not defined"
                ),
            },
            "euclidean_coefficient_route": {
                "status": "CONDITIONAL_REPRESENTATIVES_NOT_COMPLETE_GAMMA1",
                "first_missing_domain": (
                    "self-adjoint Paneitz/Delta_C boundary domain with kernel "
                    "projector and source-compatibility policy on a declared "
                    "Euclidean background"
                ),
                "additional_missing_functional_data": [
                    "WEYL_INVARIANT_NONLOCAL_REMAINDER",
                    "INDEPENDENT_NONLOCAL_RHAT2_FORM_FACTOR",
                    "INDEPENDENT_CUBIC_AND_HIGHER_WEYL_FORM_FACTORS",
                ],
                "signature_bridge_status": (
                    "NO_CERTIFIED_EUCLIDEAN_TO_LORENTZIAN_WARD_OPERATOR_MAP"
                ),
            },
        },
        "operator_ledger": {
            "Q0": "CERTIFIED",
            "iota_D0": "CERTIFIED",
            "L_D0": "CERTIFIED",
            "Gamma1_anomaly_induced": "CONDITIONAL_EUCLIDEAN_REPRESENTATIVE",
            "Gamma1_complete": "NOT_DEFINED",
            "T2_ren": "NOT_DEFINED",
            "Delta_ren": "NOT_DEFINED",
            "Q1_complete": "NOT_DEFINED",
            "iota_D1": "NOT_DEFINED",
            "L_D1": "NOT_DEFINED",
            "local_to_Cartan_map": "NOT_CONSTRUCTED",
            "A_D1": "UNDEFINED_ANALYTICALLY",
        },
        "defect_target": {
            "formula": "A_D^(1)=[Q0,iota_D1]+[Q1,iota_D0]-L_D1",
            "sourced_identity": (
                "[Q0,A_D^(1)]=[[Q0,Q1],iota_D0]-"
                "([Q0,L_D1]+[Q1,L_D0])"
            ),
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "three order-one operators and their local-to-Cartan map do "
                "not exist on one common admissible observable complex"
            ),
        },
        "scheme_invariance_disposition": {
            "verified": (
                "all finite local scheme shifts lie in the exact rank-two "
                "Hamiltonian family displayed above"
            ),
            "not_verified": (
                "the Cartan class cannot be compared across schemes before "
                "T2_ren, Q1, iota_D1, L_D1, and the map are defined"
            ),
        },
        "dependency_refs": {
            name: {
                "path": _relative(path),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "producer_request": _request_row(),
        "exact_checks": {
            "same_background_classical_contraction_imported": True,
            "raw_D_compact_not_K_Berger": True,
            "WZ_tau_not_Berger_clock": True,
            "reference_finite_scheme_declared": True,
            "reference_scheme_not_called_canonical": True,
            "finite_bulk_scheme_rank_two": (
                q1["finite_counterterm_ambiguity"]["bulk_response_rank"] == 2
            ),
            "extended_local_euclidean_QME_restored": True,
            "Lorentzian_QME_remains_open": True,
            "conditional_Euclidean_domains_retained": True,
            "same_background_T2_extension_absent": True,
            "complete_Q1_absent": True,
            "order_one_D_operators_absent": True,
            "local_to_Cartan_map_absent": True,
            "Cartan_class_not_promoted": True,
            "residual_transfer_forbidden": True,
        },
        "claim_flags": {
            "CLASSICAL_SAME_BACKGROUND_D_CARTAN_IMPORTED": True,
            "FINITE_C2_NORMALIZATION_DECLARED": True,
            "FINITE_RHAT2_NORMALIZATION_DECLARED": True,
            "FINITE_NORMALIZATION_CANONICAL": False,
            "RENORMALIZED_T2_EXTENSION_SUPPLIED": False,
            "RENORMALIZED_BV_LAPLACIAN_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "IOTA_D1_SUPPLIED": False,
            "L_D1_SUPPLIED": False,
            "LOCAL_TO_CARTAN_MAP_SUPPLIED": False,
            "QUANTUM_CARTAN_CLASS_CLASSIFIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "next_gate": (
            "FULL_TAU_ADIC_BV_HADAMARD_FEYNMAN_KERNEL_AND_RENORMALIZED_"
            "T2_EXTENSION_ON_VACUUM_CYLINDER"
        ),
        "science_forge": {
            "work_item": (
                "sf:program/work/quantum-complete-renormalized-d-ward-insertion"
            ),
            "stop_condition_disposition": (
                "PRECISE_NONDEFINITION_THEOREM_FIRST_DISTRIBUTION_"
                "EXTENSION_AND_OPERATOR_DOMAIN_NAMED"
            ),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate imports "
            "the exact same-background vacuum-cylinder Wess-Zumino "
            "compensator D_compact contraction, declares the non-canonical "
            "reference conditions z_C(mu_star)=z_Rhat2(mu_star)=0, and proves "
            "from pinned producer boundaries that the first same-background "
            "analytic Ward operator remains undefined: no BRST-compatible "
            "full tau-adic BV Hadamard/Feynman kernel and no renormalized T2 "
            "extension across Diag_2 have been supplied. Conditional "
            "Euclidean anomaly-induced and curvature-squared representatives "
            "do not define that Lorentzian operator and do not supply complete "
            "Gamma1. Consequently complete Q1, iota_D1, L_D1, the "
            "local-to-Cartan map, A_D^(1), and residual transfer remain "
            "undefined. This is not a nonexistence theorem for such "
            "extensions, a Lorentzian QME, a Hadamard state, positivity, "
            "particle, scattering, or unitarity result."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if value.get("result_id") != "RENORMALIZED_D_WARD_INSERTION_NONDEFINITION":
        raise ValueError("result identity drifted")
    if value.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]:
        raise ValueError("dependency boundary drifted")
    if value["finite_normalization"][
        "status"
    ] != "DECLARED_CONVENTION_NOT_CANONICAL_PHYSICAL_NORMALIZATION":
        raise ValueError("finite normalization was over-promoted")
    if value["finite_normalization"]["scheme_change"]["rank"] != 2:
        raise ValueError("finite scheme rank drifted")
    if value["analytic_branches"]["same_background_lorentzian"][
        "first_missing_operator"
    ] != "T2_ren_tau_adic_BV":
        raise ValueError("first missing distribution extension drifted")
    if value["defect_target"]["classification"] != "UNDEFINED_ANALYTICALLY":
        raise ValueError("Cartan defect was over-promoted")
    if value["producer_request"]["need_id"] != REQUEST_NEED_ID:
        raise ValueError("next analytic producer request drifted")
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact check failed")
    expected_flags = {
        "CLASSICAL_SAME_BACKGROUND_D_CARTAN_IMPORTED": True,
        "FINITE_C2_NORMALIZATION_DECLARED": True,
        "FINITE_RHAT2_NORMALIZATION_DECLARED": True,
        "FINITE_NORMALIZATION_CANONICAL": False,
        "RENORMALIZED_T2_EXTENSION_SUPPLIED": False,
        "RENORMALIZED_BV_LAPLACIAN_SUPPLIED": False,
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
        "IOTA_D1_SUPPLIED": False,
        "L_D1_SUPPLIED": False,
        "LOCAL_TO_CARTAN_MAP_SUPPLIED": False,
        "QUANTUM_CARTAN_CLASS_CLASSIFIED": False,
        "RESIDUAL_TRANSFER_AUTHORIZED": False,
        "LORENTZIAN_QME_CERTIFIED": False,
    }
    if value["claim_flags"] != expected_flags:
        raise ValueError("claim flags crossed the non-definition boundary")
