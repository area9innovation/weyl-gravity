#!/usr/bin/env python3
"""Independent replay of the one-loop quantum D-Cartan disposition.

This verifier intentionally imports neither the producer nor its certificate
emitter.  It reconstructs the decisive coefficient, lifecycle, generator, and
source/target checks directly from the pinned dependencies.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION.json"
SCHEMA = (
    HERE / "schema/quantum-cartan-d-one-loop-disposition-v1.schema.json"
)
DEPENDENCIES = {
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
    "local_D_comparison": (
        HERE / "certificates/LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
    ),
    "ward_insertion_contract": (
        HERE / "certificates/RENORMALIZED_D_WARD_INSERTION_CONTRACT.json"
    ),
    "berger_local_D_action": (
        ROOT
        / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
    ),
    "berger_generator_audit": (
        ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_GENERATOR_CONJUGATION_AUDIT.json"
    ),
    "berger_K_cartan": (
        ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json"
    ),
}
SOURCE_PATHS = (
    "quantum_cartan_d_one_loop_disposition.py",
    "quantum_cartan_d_one_loop_disposition_certificate.py",
    "verify_quantum_cartan_d_one_loop_disposition.py",
    "schema/quantum-cartan-d-one-loop-disposition-v1.schema.json",
    "tests/test_quantum_cartan_d_one_loop_disposition.py",
    "../reports/quantum-cartan-d-one-loop-disposition.md",
)
REQUEST_EVENT_PATHS = {
    "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION": (
        ROOT
        / "planning/events/"
        "quantum-cartan-d-one-loop-obstruction-REQUEST-0ffe79fd2ff547a0.json"
    ),
    "COMPLETE_RENORMALIZED_D_WARD_INSERTION": (
        ROOT
        / "planning/events/"
        "quantum-cartan-d-one-loop-obstruction-REQUEST-709f817c881265e8.json"
    ),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | dict[str, int]) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"Cartan disposition schema failed: {errors}")

    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        ref = value["dependency_refs"][name]
        if (
            ref["path"] != path.relative_to(ROOT).as_posix()
            or ref["result_id"] != dependencies[name]["result_id"]
            or ref["sha256"] != _sha256(path)
        ):
            raise ValueError(f"dependency drift: {name}")

    audit = dependencies["local_anomaly_audit"]
    vector = {
        key: _q(coefficient)
        for key, coefficient in audit["two_method_coefficients"][
            "repository_vector"
        ].items()
    }
    if vector != {
        "ANOM_OMEGA_C2": Fraction(199, 30),
        "ANOM_OMEGA_E4": Fraction(-87, 20),
        "ANOM_OMEGA_C_DUAL_C": Fraction(0),
        "ANOM_OMEGA_BOX_R": Fraction(0),
    }:
        raise ValueError("independent coefficient replay failed")
    if (
        audit["QME_lifecycles"]["strict_fixed_field_content"]
        != "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
        or audit["QME_lifecycles"]["tau_adic_compensator_extended"]
        != "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
    ):
        raise ValueError("strict/extended lifecycle replay failed")

    q1 = dependencies["q1_disposition"]
    if (
        q1["finite_counterterm_ambiguity"]["bulk_response_rank"] != 2
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
        or q1["missing_operator_data"]["extended_classical_residual_contraction"]
        != "NOT_SUPPLIED"
    ):
        raise ValueError("independent Q1 shortfall replay failed")

    comparison = dependencies["local_D_comparison"][
        "one_generator_pullback_maps"
    ]
    if [
        _q(item)
        for item in comparison["vacuum_cylinder"]["coefficient_image"]
    ] != [0, 0]:
        raise ValueError("vacuum pullback is not zero")
    if [
        _q(item)
        for item in comparison["minkowski_dilation_cross_check"][
            "coefficient_image"
        ]
    ] != [Fraction(-199, 30), Fraction(87, 20)]:
        raise ValueError("Minkowski pullback replay failed")

    ward = dependencies["ward_insertion_contract"]
    if (
        ward["local_to_cartan_map_status"] != "NOT_CONSTRUCTED"
        or ward["physical_input_status"] != "NOT_RECEIVED"
    ):
        raise ValueError("Ward insertion unexpectedly exists")

    generator = dependencies["berger_generator_audit"]
    k_cartan = dependencies["berger_K_cartan"]
    if (
        not generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"]
        or generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]
        or not generator["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"]
        or not k_cartan["flags"][
            "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"
        ]
        or k_cartan["flags"]["BERGER_RAW_D_AFFINE_CARTAN"]
        or k_cartan["flags"]["QME_RESTORED"]
    ):
        raise ValueError("raw-D/K_Berger replay failed")

    rows = value["theory_setting_dispositions"]
    if (
        len(rows) != 5
        or {row["classification"] for row in rows}
        != {"UNDEFINED_ANALYTICALLY"}
        or {
            row["generator_id"] for row in rows
        }
        != {"D_COMPACT", "RAW_DILATION", "RAW_D", "K_BERGER"}
    ):
        raise ValueError("fail-closed disposition ledger drifted")
    if value["claim_flags"]["RESIDUAL_TRANSFER_AUTHORIZED"]:
        raise ValueError("residual transfer was over-promoted")
    if value["claim_flags"]["RAW_D_IDENTIFIED_WITH_K_BERGER"]:
        raise ValueError("raw D was identified with K_Berger")
    if value["claim_flags"]["WZ_COMPENSATOR_IDENTIFIED_WITH_BERGER_CLOCK"]:
        raise ValueError("the two tau fields were identified")

    request_rows = {
        row["need_id"]: row for row in value["producer_requests"]
    }
    if set(request_rows) != set(REQUEST_EVENT_PATHS):
        raise ValueError("request ledger is incomplete")
    for need_id, path in REQUEST_EVENT_PATHS.items():
        row = request_rows[need_id]
        event = _load(path)
        payload = event["body"]["payload"]
        if (
            row["event_path"] != path.relative_to(ROOT).as_posix()
            or row["event_sha256"] != _sha256(path)
            or payload["request_id"] != row["request_id"]
            or payload["to_stream"] != row["to_stream"]
            or payload["typed"] != row["typed"]
            or not payload["need"].startswith(need_id + ":")
        ):
            raise ValueError(f"request event replay failed: {need_id}")

    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("source manifest drifted")
    return value


if __name__ == "__main__":
    verify()
    print("QUANTUM CARTAN D ONE-LOOP independent verification: PASS")
