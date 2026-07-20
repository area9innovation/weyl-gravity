#!/usr/bin/env python3
"""Independent replay of the renormalized D-Ward non-definition theorem.

This verifier imports neither the producer nor its certificate emitter.  It
reconstructs the decisive classical-import, rank, analytic-domain and
lifecycle checks directly from the pinned source certificates.
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
OUTPUT = (
    HERE
    / "certificates/RENORMALIZED_D_WARD_INSERTION_NONDEFINITION.json"
)
SCHEMA = (
    HERE
    / "schema/renormalized-d-ward-insertion-nondefinition-v1.schema.json"
)
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
SOURCE_PATHS = (
    "renormalized_d_ward_insertion_nondefinition.py",
    "renormalized_d_ward_insertion_nondefinition_certificate.py",
    "verify_renormalized_d_ward_insertion_nondefinition.py",
    "schema/renormalized-d-ward-insertion-nondefinition-v1.schema.json",
    "tests/test_renormalized_d_ward_insertion_nondefinition.py",
    "../reports/renormalized-d-ward-insertion-nondefinition.md",
)
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


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"Ward non-definition schema failed: {errors}")

    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        ref = value["dependency_refs"][name]
        if (
            ref["path"] != path.relative_to(ROOT).as_posix()
            or ref["result_id"] != dependencies[name]["result_id"]
            or ref["sha256"] != _sha256(path)
        ):
            raise ValueError(f"dependency drift: {name}")

    classical = dependencies["classical_wz_d_cartan"]
    if (
        classical["generator"]["generator_id"] != "D_compact"
        or classical["generator"]["is_K_Berger"]
        or not classical["claim_flags"][
            "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION"
        ]
        or classical["claim_flags"]["MINKOWSKI_DILATION_CONTRACTION_EXPORTED"]
    ):
        raise ValueError("independent classical Cartan import replay failed")

    q1 = dependencies["q1_disposition"]
    full = q1["finite_counterterm_ambiguity"][
        "bulk_quadratic_response_matrix"
    ]
    reduced = [
        [_fraction(full[0][0]), _fraction(full[0][2])],
        [_fraction(full[1][0]), _fraction(full[1][2])],
    ]
    determinant = reduced[0][0] * reduced[1][1] - reduced[0][1] * reduced[1][0]
    if reduced != [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(9)]]:
        raise ValueError("independent finite-scheme matrix replay failed")
    if determinant != 9 or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR":
        raise ValueError("independent rank/Q1 replay failed")

    anomaly = dependencies["anomaly_induced_gamma1"]
    curved = dependencies["curvature_squared_gamma1"]
    fv = dependencies["fv_conformized_gamma1"]
    if (
        anomaly["green_operator_contract"]["existence_status"]
        != "CONDITIONAL_ON_DECLARED_EUCLIDEAN_GENERALIZED_INVERSE"
        or anomaly["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or curved["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"]
        or curved["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"]
        or fv["claim_flags"]["NONLOCAL_R2_FORM_FACTOR_COMPUTED"]
        or fv["claim_flags"][
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
        ]
    ):
        raise ValueError("independent analytic shortfall replay failed")

    branch = value["analytic_branches"]["same_background_lorentzian"]
    if (
        branch["status"] != "FIRST_DISTRIBUTION_EXTENSION_UNDEFINED"
        or branch["first_missing_operator"] != "T2_ren_tau_adic_BV"
        or branch["off_diagonal_domain"] != "M^2 minus Diag_2"
        or "EPSTEIN_GLASER_T2_EXTENSION_ACROSS_DIAG2"
        not in branch["missing_prerequisites"]
    ):
        raise ValueError("first distribution extension drifted")

    ledger = value["operator_ledger"]
    if (
        ledger["Q0"] != "CERTIFIED"
        or ledger["iota_D0"] != "CERTIFIED"
        or ledger["L_D0"] != "CERTIFIED"
        or ledger["Q1_complete"] != "NOT_DEFINED"
        or ledger["iota_D1"] != "NOT_DEFINED"
        or ledger["L_D1"] != "NOT_DEFINED"
        or ledger["A_D1"] != "UNDEFINED_ANALYTICALLY"
    ):
        raise ValueError("operator ledger crossed its boundary")

    flags = value["claim_flags"]
    if (
        not flags["CLASSICAL_SAME_BACKGROUND_D_CARTAN_IMPORTED"]
        or flags["FINITE_NORMALIZATION_CANONICAL"]
        or flags["RENORMALIZED_T2_EXTENSION_SUPPLIED"]
        or flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"]
        or flags["QUANTUM_CARTAN_CLASS_CLASSIFIED"]
        or flags["RESIDUAL_TRANSFER_AUTHORIZED"]
        or flags["LORENTZIAN_QME_CERTIFIED"]
    ):
        raise ValueError("claim flags crossed the non-definition boundary")

    request = value["producer_request"]
    event = _load(REQUEST_EVENT)
    payload = event["body"]["payload"]
    if (
        request["request_id"] != REQUEST_ID
        or request["event_path"] != REQUEST_EVENT.relative_to(ROOT).as_posix()
        or request["event_sha256"] != _sha256(REQUEST_EVENT)
        or payload["request_id"] != REQUEST_ID
        or payload["to_stream"] != "quantum-qme"
        or payload["typed"] != "coefficient-bearing-operator"
        or not payload["need"].startswith(request["need_id"] + ":")
    ):
        raise ValueError("producer request replay failed")

    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("source manifest drifted")
    return value


if __name__ == "__main__":
    verify()
    print("RENORMALIZED D-WARD independent non-definition replay: PASS")
