"""Exact first one-loop disposition of the quantum D-Cartan gate.

The calculation deliberately keeps three logically different inputs apart:

* the anomalous strict pure-Weyl local BV theory;
* the formally restored tau-adic Wess--Zumino extension; and
* the positive-Berger gravity--clock carrier, whose stationary generator is
  ``K_Berger`` rather than the affine raw cylinder translation ``D``.

The current evidence determines the coefficient-bearing local source and its
one-generator pullbacks, but it does not provide the operator data required to
turn those local classes into a degree-zero Cartan cocycle.  The result is
therefore an exact missing-carrier theorem, not a zero-defect theorem.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]

DEPENDENCIES = {
    "local_anomaly_audit": (
        REPOSITORY_ROOT
        / "quantum-weyl/local_bv/certificates/"
        "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
    ),
    "q1_disposition": (
        REPOSITORY_ROOT
        / "quantum-weyl/transfer/certificates/"
        "ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json"
    ),
    "anomaly_induced_gamma1": (
        REPOSITORY_ROOT
        / "quantum-weyl/transfer/certificates/"
        "ANOMALY_INDUCED_NONLOCAL_GAMMA1.json"
    ),
    "local_D_comparison": (
        HERE / "certificates/LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
    ),
    "ward_insertion_contract": (
        HERE / "certificates/RENORMALIZED_D_WARD_INSERTION_CONTRACT.json"
    ),
    "berger_local_D_action": (
        REPOSITORY_ROOT
        / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
    ),
    "berger_generator_audit": (
        REPOSITORY_ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_GENERATOR_CONJUGATION_AUDIT.json"
    ),
    "berger_K_cartan": (
        REPOSITORY_ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json"
    ),
}

EXPECTED_RESULT_IDS = {
    "local_anomaly_audit": "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT",
    "q1_disposition": "ONE_LOOP_SLAVNOV_Q1_DISPOSITION",
    "anomaly_induced_gamma1": "ANOMALY_INDUCED_NONLOCAL_GAMMA1",
    "local_D_comparison": "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON",
    "ward_insertion_contract": "RENORMALIZED_D_WARD_INSERTION_CONTRACT",
    "berger_local_D_action": "BERGER_54_ROW_LOCAL_D_ACTION",
    "berger_generator_audit": "BERGER_GENERATOR_CONJUGATION_AUDIT",
    "berger_K_cartan": "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE",
}

EXPECTED_VECTOR = {
    "ANOM_OMEGA_C2": Fraction(199, 30),
    "ANOM_OMEGA_E4": Fraction(-87, 20),
    "ANOM_OMEGA_C_DUAL_C": Fraction(0),
    "ANOM_OMEGA_BOX_R": Fraction(0),
}

CLASSIFICATIONS = {
    "ZERO",
    "EXACT_REMOVABLE",
    "NONTRIVIAL_ANOMALY",
    "UNDEFINED_ANALYTICALLY",
}

REQUESTS = (
    {
        "request_id": (
            "sf:program/request/"
            "quantum-cartan-d-one-loop-obstruction-to-classical-0ffe79fd2ff547a0"
        ),
        "to_stream": "classical",
        "typed": "dependency-artifact",
        "need_id": "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION",
        "status": "FILED_APPEND_ONLY",
        "event_path": (
            "planning/events/"
            "quantum-cartan-d-one-loop-obstruction-REQUEST-0ffe79fd2ff547a0.json"
        ),
    },
    {
        "request_id": (
            "sf:program/request/"
            "quantum-cartan-d-one-loop-obstruction-to-quantum-qme-709f817c881265e8"
        ),
        "to_stream": "quantum-qme",
        "typed": "coefficient-bearing-operator",
        "need_id": "COMPLETE_RENORMALIZED_D_WARD_INSERTION",
        "status": "FILED_APPEND_ONLY",
        "event_path": (
            "planning/events/"
            "quantum-cartan-d-one-loop-obstruction-REQUEST-709f817c881265e8.json"
        ),
    },
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: str | dict[str, int]) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _relative(path: Path) -> str:
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def _require_inputs(values: dict[str, dict[str, Any]]) -> None:
    for name, value in values.items():
        if value.get("result_id") != EXPECTED_RESULT_IDS[name]:
            raise ValueError(f"{name} result identity drifted")

    audit = values["local_anomaly_audit"]
    if (
        audit["regularity_scope"] != "REGULAR_BACH_LOCUS"
        or not audit["claim_flags"]["FULL_LOCAL_BV_ANOMALY_COHOMOLOGY_COMPLETE"]
        or not audit["claim_flags"]["STRICT_LOCAL_EUCLIDEAN_QME_OBSTRUCTED"]
        or not audit["claim_flags"][
            "TAU_ADIC_EXTENDED_LOCAL_EUCLIDEAN_QME_RESTORED"
        ]
    ):
        raise ValueError("local anomaly/QME audit is not complete")
    vector = {
        key: _fraction(value)
        for key, value in audit["two_method_coefficients"][
            "repository_vector"
        ].items()
    }
    if vector != EXPECTED_VECTOR:
        raise ValueError("coefficient vector drifted")

    q1 = values["q1_disposition"]
    if (
        q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
        or q1["finite_counterterm_ambiguity"]["bulk_response_rank"] != 2
        or q1["claim_flags"]["EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED"]
        or q1["claim_flags"]["RESIDUAL_TRANSFER_AUTHORIZED"]
    ):
        raise ValueError("Q1 missing-object disposition drifted")
    gamma1 = values["anomaly_induced_gamma1"]
    if (
        gamma1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
        or not gamma1["claim_flags"]["ANOMALY_VECTOR_REPRODUCED"]
        or gamma1["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
    ):
        raise ValueError("conditional Gamma1 scope drifted")

    comparison = values["local_D_comparison"]
    maps = comparison["one_generator_pullback_maps"]
    cylinder = [
        _fraction(value)
        for value in maps["vacuum_cylinder"]["coefficient_image"]
    ]
    minkowski = [
        _fraction(value)
        for value in maps["minkowski_dilation_cross_check"]["coefficient_image"]
    ]
    if cylinder != [Fraction(0), Fraction(0)]:
        raise ValueError("vacuum-cylinder direct pullback drifted")
    if minkowski != [Fraction(-199, 30), Fraction(87, 20)]:
        raise ValueError("Minkowski dilation pullback drifted")
    if comparison["cartan_defect_comparison"]["classification_status"] != "NO_VERDICT":
        raise ValueError("historical comparison was over-promoted")

    ward = values["ward_insertion_contract"]
    if (
        ward["defect_formula"]
        != "A_D^(1)=[Q0,iota_D1]+[Q1,iota_D0]-L_D1"
        or ward["local_to_cartan_map_status"] != "NOT_CONSTRUCTED"
        or ward["physical_input_status"] != "NOT_RECEIVED"
    ):
        raise ValueError("Ward insertion contract drifted")

    local_d = values["berger_local_D_action"]
    if (
        local_d["claim_status"]
        != "CERTIFIED_COMPLETE_LOCAL_D_ACTION_UNARY_EQUIVARIANCE"
        or not all(local_d["exact_checks"].values())
    ):
        raise ValueError("Berger unary local action drifted")
    generator = values["berger_generator_audit"]
    if (
        not generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"]
        or generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]
        or not generator["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"]
    ):
        raise ValueError("raw-D/K_Berger distinction drifted")
    k_cartan = values["berger_K_cartan"]
    if (
        not k_cartan["flags"]["BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"]
        or k_cartan["flags"]["BERGER_RAW_D_AFFINE_CARTAN"]
        or k_cartan["flags"]["QME_RESTORED"]
        or k_cartan["flags"]["QUANTUM_CLAIM"]
    ):
        raise ValueError("Berger K-Cartan boundary drifted")


def _request_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for expected in REQUESTS:
        path = REPOSITORY_ROOT / expected["event_path"]
        event = _load(path)
        payload = event.get("body", {}).get("payload", {})
        if (
            event.get("kind") != "event"
            or event.get("body", {}).get("event_kind") != "REQUEST"
            or payload.get("request_id") != expected["request_id"]
            or payload.get("from_item")
            != "sf:program/work/quantum-cartan-d-one-loop-obstruction"
            or payload.get("to_stream") != expected["to_stream"]
            or payload.get("typed") != expected["typed"]
            or not str(payload.get("need", "")).startswith(
                expected["need_id"] + ":"
            )
        ):
            raise ValueError(
                f"typed request event drifted: {expected['need_id']}"
            )
        rows.append(
            {
                **expected,
                "event_sha256": _sha256(path),
            }
        )
    return rows


def evaluate() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _require_inputs(values)

    audit = values["local_anomaly_audit"]
    comparison = values["local_D_comparison"]
    q1 = values["q1_disposition"]
    vector = audit["two_method_coefficients"]["repository_vector"]
    pullbacks = comparison["one_generator_pullback_maps"]

    bulk_candidates = [
        {
            "representative_id": "ANOM_OMEGA_C2",
            "parity": "even",
            "coefficient": vector["ANOM_OMEGA_C2"],
            "strict_relative_status": "NONTRIVIAL",
            "extended_relative_status": "EXACT_BY_WESS_ZUMINO_PRIMITIVE",
            "cartan_operator_image_status": "NOT_CONSTRUCTED",
        },
        {
            "representative_id": "ANOM_OMEGA_E4",
            "parity": "even",
            "coefficient": vector["ANOM_OMEGA_E4"],
            "strict_relative_status": "NONTRIVIAL",
            "extended_relative_status": "EXACT_BY_WESS_ZUMINO_PRIMITIVE",
            "cartan_operator_image_status": "NOT_CONSTRUCTED",
        },
        {
            "representative_id": "ANOM_OMEGA_C_DUAL_C",
            "parity": "odd",
            "coefficient": vector["ANOM_OMEGA_C_DUAL_C"],
            "strict_relative_status": "NONTRIVIAL_ZERO_COEFFICIENT",
            "extended_relative_status": "EXACT_IN_EXTENDED_H14_ZERO",
            "cartan_operator_image_status": "NOT_CONSTRUCTED",
        },
        {
            "representative_id": "ANOM_OMEGA_BOX_R",
            "parity": "even",
            "coefficient": vector["ANOM_OMEGA_BOX_R"],
            "strict_relative_status": "EXACT_WITH_STORED_PRIMITIVE",
            "extended_relative_status": "EXACT",
            "cartan_operator_image_status": "NOT_APPLICABLE_ZERO_EXACT_ROW",
        },
    ]

    dispositions = [
        {
            "row_id": "strict_vacuum_cylinder_D_compact",
            "theory_id": "STRICT_PURE_WEYL",
            "setting_id": "VACUUM_CYLINDER_REGULAR_BACH_LOCUS",
            "generator_id": "D_COMPACT",
            "classical_generator_status": "SETTING_SPECIFIC_CLASSICAL_INPUT_ONLY",
            "qme_status": "OBSTRUCTED_NONZERO_LOCAL_SOURCE",
            "q1_status": "NO_NILPOTENT_RENORMALIZED_Q1_IN_STRICT_FIELD_CONTENT",
            "direct_bulk_pullback": pullbacks["vacuum_cylinder"][
                "coefficient_image"
            ],
            "defect_closure_status": "SOURCED_NOT_A_CLOSED_H0_CLASS",
            "local_to_cartan_map_status": "NOT_CONSTRUCTED",
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "sigma_D=0 kills only the direct local bulk pullback; the "
                "strict one-loop Slavnov source is nonzero and the "
                "renormalized Ward insertion is absent"
            ),
        },
        {
            "row_id": "strict_minkowski_raw_dilation_cross_check",
            "theory_id": "STRICT_PURE_WEYL",
            "setting_id": "MINKOWSKI_DILATION_CROSS_CHECK",
            "generator_id": "RAW_DILATION",
            "classical_generator_status": "ONE_GENERATOR_LOCAL_PULLBACK_ONLY",
            "qme_status": "OBSTRUCTED_NONZERO_LOCAL_SOURCE",
            "q1_status": "NO_NILPOTENT_RENORMALIZED_Q1_IN_STRICT_FIELD_CONTENT",
            "direct_bulk_pullback": pullbacks["minkowski_dilation_cross_check"][
                "coefficient_image"
            ],
            "defect_closure_status": "SOURCED_NOT_A_CLOSED_H0_CLASS",
            "local_to_cartan_map_status": "NOT_CONSTRUCTED",
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "the nonzero local pullback remains a ghost-number-one "
                "relative density; no grading-only map turns it into the "
                "degree-zero Cartan defect"
            ),
        },
        {
            "row_id": "tau_adic_extended_regular_bach_raw_D",
            "theory_id": "TAU_ADIC_WESS_ZUMINO_EXTENDED_WEYL",
            "setting_id": "FORMAL_LOCAL_REGULAR_BACH_LOCUS",
            "generator_id": "RAW_D",
            "classical_generator_status": (
                "SAME_BACKGROUND_EXTENDED_CONTRACTION_NOT_SUPPLIED"
            ),
            "qme_status": "RESTORED_ONE_LOOP_LOCAL_EUCLIDEAN",
            "q1_status": (
                "WZ_HAMILTONIAN_PIECE_FIXED_COMPLETE_Q1_UNDERDETERMINED"
            ),
            "direct_bulk_pullback": None,
            "defect_closure_status": "NOT_EVALUABLE_OPERATORS_INCOMPLETE",
            "local_to_cartan_map_status": "NOT_CONSTRUCTED",
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "the local QME source is removed, but the rank-two finite "
                "bulk ambiguity, missing finite/nonlocal Gamma1 and "
                "renormalized-product data, missing iota_D1/L_D1, and missing "
                "extended contraction prevent assembly of A_D^(1)"
            ),
        },
        {
            "row_id": "positive_berger_clock_K_Berger",
            "theory_id": "POSITIVE_BERGER_GRAVITY_CLOCK_MAXWELL",
            "setting_id": "COMPACT_POSITIVE_BERGER_CLOCK_FIXED_COUPLING",
            "generator_id": "K_BERGER",
            "classical_generator_status": (
                "CERTIFIED_CAUSAL_CYCLIC_CARTAN_THROUGH_ARITY_THREE"
            ),
            "qme_status": "NO_QME_DATA_ON_THIS_QUANTUM_CARRIER",
            "q1_status": "NO_COEFFICIENT_BEARING_Q1_ON_THIS_CARRIER",
            "direct_bulk_pullback": None,
            "defect_closure_status": "NOT_EVALUABLE_QUANTUM_OPERATOR_ABSENT",
            "local_to_cartan_map_status": "NO_CERTIFIED_MAP",
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "the Berger clock field is not the Wess-Zumino compensator; "
                "the pure-Weyl anomaly vector cannot be imported by matching "
                "the symbol tau or the word Cartan"
            ),
        },
        {
            "row_id": "positive_berger_clock_raw_D",
            "theory_id": "POSITIVE_BERGER_GRAVITY_CLOCK_MAXWELL",
            "setting_id": "COMPACT_POSITIVE_BERGER_CLOCK_FIXED_COUPLING",
            "generator_id": "RAW_D",
            "classical_generator_status": (
                "AFFINE_NONZERO_ARITY_ZERO_NO_CARTAN_CONTRACTION"
            ),
            "qme_status": "NO_QME_DATA_ON_THIS_QUANTUM_CARRIER",
            "q1_status": "NO_COEFFICIENT_BEARING_Q1_ON_THIS_CARRIER",
            "direct_bulk_pullback": None,
            "defect_closure_status": "CLASSICAL_CARTAN_INPUT_ABSENT",
            "local_to_cartan_map_status": "NO_CERTIFIED_MAP",
            "classification": "UNDEFINED_ANALYTICALLY",
            "reason": (
                "the frozen e0 generator is K_Berger=D-omega R; raw D does "
                "not fix the rotating background and has a nonzero arity-zero "
                "component"
            ),
        },
    ]

    dependency_refs = {
        name: {
            "path": _relative(path),
            "result_id": values[name]["result_id"],
            "sha256": _sha256(path),
        }
        for name, path in DEPENDENCIES.items()
    }

    result = {
        "schema": "quantum-weyl-quantum-cartan-d-one-loop-disposition-v1",
        "result_id": "QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION",
        "result_state": (
            "COEFFICIENT_SOURCE_DISPOSED_ALL_DECLARED_CARTAN_ROWS_"
            "UNDEFINED_ANALYTICALLY_TYPED_REQUESTS_FILED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "regularity_scope": "REGULAR_BACH_LOCUS_FOR_LOCAL_BV_QUOTIENT",
        "dependency_refs": dependency_refs,
        "operator_target": {
            "defect": "A_D^(1)=[Q0,iota_D1]+[Q1,iota_D0]-L_D1",
            "cohomology": "H^0(Der_adm(C),[Q0,-])",
            "sourced_identity": (
                "[Q0,A_D^(1)]=[[Q0,Q1],iota_D0]"
                "-([Q0,L_D1]+[Q1,L_D0])"
            ),
            "classification_domain_requirement": (
                "QME_SOURCE_ZERO_AND_COMPLETE_ADMISSIBLE_WARD_OPERATORS"
            ),
        },
        "bulk_candidate_ledger": bulk_candidates,
        "direct_pullback_ledger": {
            "vacuum_cylinder_D_compact": {
                "sigma_D": _q(0),
                "coefficient_image": pullbacks["vacuum_cylinder"][
                    "coefficient_image"
                ],
                "status": "ZERO_DIRECT_LOCAL_BULK_PULLBACK_ONLY",
            },
            "minkowski_raw_dilation_cross_check": {
                "sigma_D": _q(-1),
                "coefficient_image": pullbacks[
                    "minkowski_dilation_cross_check"
                ]["coefficient_image"],
                "status": "NONZERO_LOCAL_RELATIVE_PULLBACK_NO_CARTAN_MAP",
            },
        },
        "finite_counterterm_ambiguity": {
            "basis": q1["finite_counterterm_ambiguity"]["H04_basis"],
            "bulk_response_rank": q1["finite_counterterm_ambiguity"][
                "bulk_response_rank"
            ],
            "independent_bulk_directions": ["C(g_hat)^2", "R(g_hat)^2"],
            "bulk_kernel_directions": q1["finite_counterterm_ambiguity"][
                "bulk_kernel"
            ],
            "cartan_effect_status": "NOT_COMPUTABLE_WITHOUT_COMPLETE_WARD_OPERATORS",
        },
        "theory_setting_dispositions": dispositions,
        "missing_carrier_theorem": {
            "strict_theory": (
                "NONZERO_QME_SOURCE_PREVENTS_UNSOURCED_CARTAN_H0_CLASSIFICATION"
            ),
            "extended_theory": [
                "COMPLETE_NORMALIZED_RENORMALIZED_GAMMA1_AND_Q1",
                "RENORMALIZED_BV_LAPLACIAN_OR_TIME_ORDERED_PRODUCTS",
                "IOTA_D1_AND_L_D1",
                "SAME_BACKGROUND_TAU_ADIC_EXTENDED_CLASSICAL_D_CONTRACTION",
                "ADMISSIBLE_OBSERVABLE_COMPLEX_AND_LOCAL_TO_CARTAN_MAP",
            ],
            "berger_theory": [
                "COEFFICIENT_BEARING_Q1_ON_THE_SAME_CLOCK_CARRIER",
                "EXPLICIT_BRIDGE_FROM_THE_CHOSEN_QUANTUM_THEORY_TO_K_BERGER",
            ],
            "minimal_conclusion": (
                "no declared row currently supplies a closed, assembled "
                "coefficient-bearing A_D^(1); ZERO, EXACT_REMOVABLE, and "
                "NONTRIVIAL_ANOMALY are therefore all forbidden promotions"
            ),
        },
        "producer_requests": _request_rows(),
        "exact_checks": {
            "complete_local_H14_imported": True,
            "strict_even_coefficients_nonzero": True,
            "strict_QME_source_nonzero": True,
            "extended_local_QME_restored": True,
            "complete_Q1_absent": True,
            "finite_bulk_Q1_ambiguity_rank_two": True,
            "vacuum_direct_pullback_zero": True,
            "minkowski_direct_pullback_exact": True,
            "local_to_cartan_map_absent": True,
            "all_declared_rows_fail_closed": True,
            "raw_D_and_K_Berger_distinct": True,
            "WZ_tau_and_Berger_clock_distinct": True,
            "typed_producer_requests_filed": True,
            "residual_transfer_forbidden": True,
        },
        "claim_flags": {
            "COEFFICIENT_BEARING_LOCAL_SOURCE_COMPUTED": True,
            "STRICT_CARTAN_CLASS_CLASSIFIED": False,
            "EXTENDED_CARTAN_CLASS_CLASSIFIED": False,
            "BERGER_QUANTUM_CARTAN_CLASS_CLASSIFIED": False,
            "RAW_D_IDENTIFIED_WITH_K_BERGER": False,
            "WZ_COMPENSATOR_IDENTIFIED_WITH_BERGER_CLOCK": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "science_forge": {
            "work_item": (
                "sf:program/work/quantum-cartan-d-one-loop-obstruction"
            ),
            "stop_condition_disposition": (
                "PRECISE_MISSING_OBJECT_THEOREM_AND_TYPED_REQUESTS"
            ),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result computes the "
            "complete coefficient-bearing bulk candidate ledger and exact "
            "one-generator pullbacks supported by current evidence. It proves "
            "that the strict sourced theory, the formally restored tau-adic "
            "extension, Berger K_Berger, and affine raw Berger D do not yet "
            "define a coefficient-bearing closed Cartan defect. It does not "
            "classify any of those rows as ZERO, EXACT_REMOVABLE, or "
            "NONTRIVIAL_ANOMALY; identify the distinct theories or generators; "
            "authorize residual transfer; or establish a Lorentzian QME, "
            "Hadamard state, positivity, particle, scattering, or unitarity."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if value.get("result_id") != "QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION":
        raise ValueError("result identity drifted")
    if value.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]:
        raise ValueError("dependency-tag boundary drifted")
    rows = value.get("theory_setting_dispositions")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("theory/setting disposition ledger is incomplete")
    if any(row.get("classification") not in CLASSIFICATIONS for row in rows):
        raise ValueError("unknown Cartan classification")
    if any(
        row.get("classification") != "UNDEFINED_ANALYTICALLY" for row in rows
    ):
        raise ValueError("Cartan class was over-promoted")
    if value["claim_flags"] != {
        "COEFFICIENT_BEARING_LOCAL_SOURCE_COMPUTED": True,
        "STRICT_CARTAN_CLASS_CLASSIFIED": False,
        "EXTENDED_CARTAN_CLASS_CLASSIFIED": False,
        "BERGER_QUANTUM_CARTAN_CLASS_CLASSIFIED": False,
        "RAW_D_IDENTIFIED_WITH_K_BERGER": False,
        "WZ_COMPENSATOR_IDENTIFIED_WITH_BERGER_CLOCK": False,
        "RESIDUAL_TRANSFER_AUTHORIZED": False,
        "LORENTZIAN_QME_CERTIFIED": False,
    }:
        raise ValueError("claim flags over-promoted")
    checks = value.get("exact_checks")
    if not isinstance(checks, dict) or not checks or not all(checks.values()):
        raise ValueError("an exact check failed")
    if value["finite_counterterm_ambiguity"]["bulk_response_rank"] != 2:
        raise ValueError("finite counterterm ambiguity rank drifted")
    if len(value.get("producer_requests", [])) != 2:
        raise ValueError("typed producer-request ledger is incomplete")
    if {
        row["need_id"] for row in value["producer_requests"]
    } != {
        "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION",
        "COMPLETE_RENORMALIZED_D_WARD_INSERTION",
    }:
        raise ValueError("typed producer-request identity drifted")
