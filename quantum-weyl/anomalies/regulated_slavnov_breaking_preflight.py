"""Bind the complete local BV anomaly quotient to analytic coefficient input.

This preflight performs every exact reduction that is justified before a
repository regulator and BV Slavnov functional are supplied.  It deliberately
does not identify a standard background heat-kernel vector with the
repository breaking.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from classical_import.classical_snapshot_compatibility_receiver import (
    HASH_KEYS as SNAPSHOT_HASH_KEYS,
    validate_classical_snapshot_compatibility,
)
from spectral.euclidean.multiplicity_export_receiver import (
    validate_repository_multiplicity_export,
)
from spectral.euclidean.tt_hessian_dictionary_receiver import (
    validate_tt_hessian_dictionary,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json"
SCHEMA = HERE / "schema/regulated-slavnov-breaking-assembly-preflight-v1.schema.json"
EXPORT_SCHEMA = HERE / "schema/regulated-slavnov-breaking-export-v2.schema.json"
EXPORT_SCHEMA_ID = "quantum-weyl-regulated-slavnov-breaking-export-v2"

DEPENDENCIES = {
    "full_local_BV_G2": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "gauge_fixed_H14": ROOT / "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
    "BoxR_triviality": ROOT / "quantum-weyl/local_bv/certificates/TRIVIALITY_CERTIFICATE.json",
    "standard_background_coefficients": ROOT / "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "standard_auxiliary_fourth_order_match": ROOT / "quantum-weyl/spectral/euclidean/certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json",
    "full_BV_multiplicity_preflight": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json",
    "full_BV_ledger_composer": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_LEDGER_COMPOSER_READINESS.json",
    "physical_TT_dictionary": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json",
    "physical_full_BV_multiplicity_ledger": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "repository_round_S4_Euler_coefficient": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json",
    "nonconformal_coefficient_match_receiver": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_NONCONFORMAL_COEFFICIENT_MATCH_READINESS.json",
    "classical_snapshot_compatibility_receiver": ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS.json",
    "physical_classical_snapshot_compatibility": ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json",
    "Ward_insertion_contract": ROOT / "quantum-weyl/cartan/certificates/RENORMALIZED_D_WARD_INSERTION_CONTRACT.json",
}

SOURCE_PATHS = (
    "quantum-weyl/anomalies/regulated_slavnov_breaking_preflight.py",
    "quantum-weyl/anomalies/verify_regulated_slavnov_breaking_preflight.py",
    "quantum-weyl/anomalies/schema/regulated-slavnov-breaking-assembly-preflight-v1.schema.json",
    "quantum-weyl/anomalies/schema/regulated-slavnov-breaking-export-v2.schema.json",
    "quantum-weyl/anomalies/tests/test_regulated_slavnov_breaking_preflight.py",
    "quantum-weyl/reports/regulated-slavnov-breaking-assembly-preflight.md",
)

RAW_BASIS = (
    "ANOM_OMEGA_C2",
    "ANOM_OMEGA_E4",
    "ANOM_OMEGA_C_DUAL_C",
    "ANOM_OMEGA_BOX_R",
)
QUOTIENT_BASIS = RAW_BASIS[:3]
PROOF_RESULT_IDS = {
    "complete_complex_EUCLIDEAN_ELLIPTIC": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
    "complete_complex_LORENTZIAN_CAUSAL": "REPOSITORY_LORENTZIAN_CAUSAL_RENORMALIZED_PRODUCTS",
    "multiplicity": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
    "auxiliary_fourth_order_match": "REPOSITORY_AUXILIARY_FOURTH_ORDER_MATCH",
    "zero_mode_ledger": "REPOSITORY_ZERO_MODE_LEDGER",
    "measure_contour": "REPOSITORY_MEASURE_CONTOUR_LEDGER",
    "wess_zumino": "REGULATED_SLAVNOV_WESS_ZUMINO_CONSISTENCY",
    "parity_ward_zero": "REPOSITORY_PARITY_WARD_IDENTITY",
    "parity_coefficient": "REPOSITORY_PARITY_ODD_COEFFICIENT",
    "qme_disposition": "REGULATED_SLAVNOV_QME_DISPOSITION",
    "exact_counterterm": "REGULATED_SLAVNOV_EXACT_COUNTERTERM",
    "snapshot_compatibility": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
    "slavnov_action": "REGULATED_BV_SLAVNOV_ACTION",
    "total_derivative": "REGULATED_SLAVNOV_TOTAL_DERIVATIVE",
    "gauge_dependence": "REGULATED_SLAVNOV_GAUGE_PARAMETER_DEPENDENCE",
    "regularization_dependence": "REGULATED_SLAVNOV_REGULARIZATION_DEPENDENCE",
    "antifield_completion": "REGULATED_SLAVNOV_ANTIFIELD_COMPLETION",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _load_inputs() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _artifact(value: object, *, repository_root: Path, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"{label} artifact fields drifted")
    if value["format"] not in {"JSON_DATA", "JSON_PROOF", "TEXT_PROOF"}:
        raise ValueError(f"{label} artifact format drifted")
    path = (repository_root / value["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != value["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    return value


def _require_json_result_id(
    artifact: dict[str, str],
    *,
    repository_root: Path,
    label: str,
    expected_result_id: str,
) -> None:
    if artifact["format"] not in {"JSON_DATA", "JSON_PROOF"}:
        raise ValueError(f"{label} must be a machine-readable JSON artifact")
    value = json.loads((repository_root / artifact["path"]).read_text())
    if value.get("result_id") != expected_result_id:
        raise ValueError(
            f"{label} has result_id {value.get('result_id')!r}, expected {expected_result_id!r}"
        )


def _require_bound_breaking_proof(
    artifact: dict[str, str],
    *,
    repository_root: Path,
    label: str,
    expected_result_id: str,
    classical_commit: str,
    analytic_route: str,
    coefficient_basis: list[str],
    coefficients: dict[str, object],
) -> None:
    """Require a role proof to bind the exact breaking it is certifying."""

    if artifact["format"] not in {"JSON_DATA", "JSON_PROOF"}:
        raise ValueError(f"{label} must be a machine-readable bound proof")
    value = json.loads((repository_root / artifact["path"]).read_text())
    expected = {
        "result_id": expected_result_id,
        "classical_commit": classical_commit,
        "analytic_route": analytic_route,
        "coefficient_basis": coefficient_basis,
        "coefficients_sha256": _canonical_hash(coefficients),
    }
    actual = {key: value.get(key) for key in expected}
    if actual != expected:
        raise ValueError(f"{label} breaking binding drifted")


def _rational_value(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, dict)
        or set(value) != {"numerator", "denominator"}
        or not isinstance(value["numerator"], int)
        or not isinstance(value["denominator"], int)
        or value["denominator"] <= 0
    ):
        raise ValueError(f"{label} is not an exact rational")
    return Fraction(value["numerator"], value["denominator"])


def validate_regulated_breaking_export(
    payload: object, *, repository_root: Path, allow_synthetic_fixture: bool = False
) -> dict[str, Any]:
    """Validate and classify a physical regulator/Slavnov handoff."""

    required = {
        "schema",
        "result_id",
        "dependency_tags",
        "classical_commit",
        "analytic_route",
        "classical_snapshot_compatibility",
        "normalization",
        "operator_and_measure",
        "coefficient_basis",
        "coefficients",
        "insertion_decomposition",
        "consistency",
        "classification",
        "qme_disposition",
        "claim_boundary",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("regulated-breaking export fields drifted")
    if (
        payload["schema"] != EXPORT_SCHEMA_ID
        or payload["result_id"] != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
        or payload["analytic_route"] not in {"EUCLIDEAN_ELLIPTIC", "LORENTZIAN_CAUSAL"}
        or not isinstance(payload["classical_commit"], str)
        or len(payload["classical_commit"]) != 40
    ):
        raise ValueError("regulated-breaking export identity drifted")
    frozen_g2 = json.loads(
        (
            repository_root
            / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
        ).read_text()
    )
    compatibility = payload["classical_snapshot_compatibility"]
    if not isinstance(compatibility, dict) or set(compatibility) != {
        "local_BV_commit",
        "analytic_operator_commit",
        "status",
        "proof_artifact",
    }:
        raise ValueError("classical snapshot compatibility fields drifted")
    local_commit = compatibility["local_BV_commit"]
    analytic_commit = compatibility["analytic_operator_commit"]
    if analytic_commit != payload["classical_commit"]:
        raise ValueError("analytic operator commit does not match export commit")
    if allow_synthetic_fixture:
        if (
            payload["classical_commit"] != "0" * 40
            or local_commit != "0" * 40
            or compatibility["status"] != "IDENTICAL_COMMIT"
            or compatibility["proof_artifact"] is not None
        ):
            raise ValueError("synthetic receiver fixture must use the null commit")
    else:
        if local_commit != frozen_g2.get("classical_commit"):
            raise ValueError("local BV commit does not match frozen G2")
        if analytic_commit == local_commit:
            if (
                compatibility["status"] != "IDENTICAL_COMMIT"
                or compatibility["proof_artifact"] is not None
            ):
                raise ValueError("identical classical commits have a spurious bridge")
        else:
            if compatibility["status"] != "CONTENT_HASH_COMPATIBLE":
                raise ValueError("distinct classical commits lack compatibility status")
            compatibility_artifact = _artifact(
                compatibility["proof_artifact"],
                repository_root=repository_root,
                label="classical_snapshot_compatibility.proof_artifact",
            )
            _require_json_result_id(
                compatibility_artifact,
                repository_root=repository_root,
                label="classical_snapshot_compatibility.proof_artifact",
                expected_result_id=PROOF_RESULT_IDS["snapshot_compatibility"],
            )
            compatibility_payload = json.loads(
                (repository_root / compatibility_artifact["path"]).read_text()
            )
            frozen_import = json.loads(
                (
                    repository_root
                    / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
                ).read_text()
            )
            canonical_hashes = frozen_import.get("independent_replay", {}).get(
                "canonical_hashes", {}
            )
            if set(canonical_hashes) != set(SNAPSHOT_HASH_KEYS):
                raise ValueError("frozen classical snapshot canonical hashes drifted")
            try:
                validate_classical_snapshot_compatibility(
                    compatibility_payload,
                    repository_root=repository_root,
                    expected_local_commit=local_commit,
                    expected_local_hashes=canonical_hashes,
                    expected_analytic_commit=analytic_commit,
                )
            except Exception as exc:
                raise ValueError(
                    "classical snapshot compatibility semantic replay failed"
                ) from exc
    tags = payload["dependency_tags"]
    expected_analytic_tag = (
        "EUCLIDEAN-SPECTRAL"
        if payload["analytic_route"] == "EUCLIDEAN_ELLIPTIC"
        else "LORENTZIAN-CAUSAL"
    )
    if (
        not isinstance(tags, list)
        or "LOCAL-ALGEBRAIC" not in tags
        or expected_analytic_tag not in tags
        or len(tags) != len(set(tags))
    ):
        raise ValueError("regulated-breaking dependency tags drifted")
    normalization = payload["normalization"]
    if not isinstance(normalization, dict) or set(normalization) != {
        "action",
        "alpha_C",
        "signature",
        "gauge",
        "regularization",
        "scheme",
        "boundary_conditions",
    } or any(not isinstance(value, str) or not value for value in normalization.values()):
        raise ValueError("regulated-breaking normalization is incomplete")
    operator = payload["operator_and_measure"]
    always_artifact_fields = {
        "complete_complex_artifact",
        "multiplicity_artifact",
        "zero_mode_ledger_artifact",
        "measure_contour_artifact",
    }
    always_status_fields = {
        "complete_complex_status",
        "multiplicity_status",
        "zero_mode_ledger_status",
        "measure_contour_status",
    }
    required_operator_fields = (
        always_artifact_fields
        | always_status_fields
        | {
            "formulation",
            "auxiliary_fourth_order_match_artifact",
            "auxiliary_fourth_order_match_status",
        }
    )
    if not isinstance(operator, dict) or set(operator) != required_operator_fields:
        raise ValueError("regulated-breaking operator/measure fields drifted")
    if operator["formulation"] not in {
        "FOURTH_ORDER_METRIC",
        "SECOND_ORDER_AUXILIARY",
    }:
        raise ValueError("regulated-breaking formulation drifted")
    if any(operator[key] != "VERIFIED" for key in always_status_fields):
        raise ValueError("regulated-breaking operator/measure proof status is incomplete")
    if operator["formulation"] == "FOURTH_ORDER_METRIC":
        if (
            operator["auxiliary_fourth_order_match_status"]
            != "NOT_APPLICABLE_FOURTH_ORDER_METRIC"
            or operator["auxiliary_fourth_order_match_artifact"] is not None
        ):
            raise ValueError("fourth-order route imported an auxiliary-only proof gate")
    elif (
        operator["auxiliary_fourth_order_match_status"] != "VERIFIED"
        or operator["auxiliary_fourth_order_match_artifact"] is None
    ):
        raise ValueError("auxiliary route is missing its formulation-equivalence proof")
    role_result_ids = {
        "complete_complex_artifact": (
            PROOF_RESULT_IDS["complete_complex_EUCLIDEAN_ELLIPTIC"]
            if payload["analytic_route"] == "EUCLIDEAN_ELLIPTIC"
            else PROOF_RESULT_IDS["complete_complex_LORENTZIAN_CAUSAL"]
        ),
        "multiplicity_artifact": PROOF_RESULT_IDS["multiplicity"],
        "auxiliary_fourth_order_match_artifact": PROOF_RESULT_IDS[
            "auxiliary_fourth_order_match"
        ],
        "zero_mode_ledger_artifact": PROOF_RESULT_IDS["zero_mode_ledger"],
        "measure_contour_artifact": PROOF_RESULT_IDS["measure_contour"],
    }
    active_artifact_fields = set(always_artifact_fields)
    if operator["formulation"] == "SECOND_ORDER_AUXILIARY":
        active_artifact_fields.add("auxiliary_fourth_order_match_artifact")
    for key in sorted(active_artifact_fields):
        artifact = _artifact(operator[key], repository_root=repository_root, label=key)
        if not allow_synthetic_fixture:
            _require_json_result_id(
                artifact,
                repository_root=repository_root,
                label=key,
                expected_result_id=role_result_ids[key],
            )
            if key == "multiplicity_artifact":
                validate_repository_multiplicity_export(
                    json.loads((repository_root / artifact["path"]).read_text()),
                    repository_root=repository_root,
                    expected_classical_commit=payload["classical_commit"],
                    expected_analytic_route=payload["analytic_route"],
                )
    if payload["coefficient_basis"] != list(RAW_BASIS):
        raise ValueError("regulated-breaking coefficient basis drifted")
    coefficients = payload["coefficients"]
    if not isinstance(coefficients, dict) or set(coefficients) != set(RAW_BASIS):
        raise ValueError("regulated-breaking coefficient fields drifted")
    values = tuple(_rational_value(coefficients[key], key) for key in RAW_BASIS)
    insertion = payload["insertion_decomposition"]
    insertion_fields = {
        "regulated_slavnov_action_status",
        "regulated_slavnov_action_artifact",
        "cohomology_reduction_status",
        "total_derivative_status",
        "total_derivative_artifact",
        "gauge_parameter_dependence_status",
        "gauge_parameter_dependence_artifact",
        "regularization_dependence_status",
        "regularization_dependence_artifact",
        "antifield_completion_status",
        "antifield_completion_artifact",
    }
    if not isinstance(insertion, dict) or set(insertion) != insertion_fields:
        raise ValueError("regulated BV insertion-decomposition fields drifted")
    if (
        insertion["regulated_slavnov_action_status"] != "COMPUTED"
        or insertion["cohomology_reduction_status"]
        != "VERIFIED_AGAINST_COMPLETE_GAUGE_FIXED_H14"
        or insertion["total_derivative_status"] != "EXPLICIT_INCLUDING_ZERO"
        or insertion["gauge_parameter_dependence_status"]
        not in {"INDEPENDENT_VERIFIED", "DEPENDENT_DECOMPOSED"}
        or insertion["regularization_dependence_status"]
        not in {"INDEPENDENT_VERIFIED", "DEPENDENT_DECOMPOSED"}
        or insertion["antifield_completion_status"]
        != "COMPLETE_INCLUDING_ZERO"
    ):
        raise ValueError("regulated BV insertion decomposition is incomplete")
    insertion_roles = {
        "regulated_slavnov_action_artifact": PROOF_RESULT_IDS["slavnov_action"],
        "total_derivative_artifact": PROOF_RESULT_IDS["total_derivative"],
        "gauge_parameter_dependence_artifact": PROOF_RESULT_IDS[
            "gauge_dependence"
        ],
        "regularization_dependence_artifact": PROOF_RESULT_IDS[
            "regularization_dependence"
        ],
        "antifield_completion_artifact": PROOF_RESULT_IDS[
            "antifield_completion"
        ],
    }
    for key, result_id in insertion_roles.items():
        artifact = _artifact(insertion[key], repository_root=repository_root, label=key)
        if not allow_synthetic_fixture:
            _require_bound_breaking_proof(
                artifact,
                repository_root=repository_root,
                label=key,
                expected_result_id=result_id,
                classical_commit=payload["classical_commit"],
                analytic_route=payload["analytic_route"],
                coefficient_basis=payload["coefficient_basis"],
                coefficients=coefficients,
            )
    consistency = payload["consistency"]
    if not isinstance(consistency, dict) or set(consistency) != {
        "wess_zumino_status",
        "wess_zumino_proof",
        "parity_status",
        "parity_proof",
    }:
        raise ValueError("regulated-breaking consistency fields drifted")
    if (
        consistency["wess_zumino_status"] != "VERIFIED"
        or consistency["parity_status"]
        not in {"COEFFICIENT_COMPUTED", "WARD_VERIFIED_ZERO"}
    ):
        raise ValueError("regulated-breaking consistency is incomplete")
    wess_zumino_artifact = _artifact(
        consistency["wess_zumino_proof"],
        repository_root=repository_root,
        label="wess_zumino_proof",
    )
    parity_artifact = _artifact(
        consistency["parity_proof"],
        repository_root=repository_root,
        label="parity_proof",
    )
    if not allow_synthetic_fixture:
        _require_bound_breaking_proof(
            wess_zumino_artifact,
            repository_root=repository_root,
            label="wess_zumino_proof",
            expected_result_id=PROOF_RESULT_IDS["wess_zumino"],
            classical_commit=payload["classical_commit"],
            analytic_route=payload["analytic_route"],
            coefficient_basis=payload["coefficient_basis"],
            coefficients=coefficients,
        )
        _require_bound_breaking_proof(
            parity_artifact,
            repository_root=repository_root,
            label="parity_proof",
            expected_result_id=(
                PROOF_RESULT_IDS["parity_ward_zero"]
                if consistency["parity_status"] == "WARD_VERIFIED_ZERO"
                else PROOF_RESULT_IDS["parity_coefficient"]
            ),
            classical_commit=payload["classical_commit"],
            analytic_route=payload["analytic_route"],
            coefficient_basis=payload["coefficient_basis"],
            coefficients=coefficients,
        )
    classification = payload["classification"]
    if not isinstance(classification, dict) or set(classification) != {
        "status",
        "exact_counterterm",
    }:
        raise ValueError("regulated-breaking classification fields drifted")
    disposition = payload["qme_disposition"]
    if not isinstance(disposition, dict) or set(disposition) != {"status", "proof_artifact"}:
        raise ValueError("regulated-breaking QME disposition fields drifted")
    disposition_artifact = _artifact(
        disposition["proof_artifact"],
        repository_root=repository_root,
        label="qme_disposition.proof_artifact",
    )
    if not allow_synthetic_fixture:
        _require_bound_breaking_proof(
            disposition_artifact,
            repository_root=repository_root,
            label="qme_disposition.proof_artifact",
            expected_result_id=PROOF_RESULT_IDS["qme_disposition"],
            classical_commit=payload["classical_commit"],
            analytic_route=payload["analytic_route"],
            coefficient_basis=payload["coefficient_basis"],
            coefficients=coefficients,
        )
    nontrivial = any(values[:3])
    if nontrivial:
        if (
            classification != {"status": "NONTRIVIAL", "exact_counterterm": None}
            or disposition["status"] != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        ):
            raise ValueError("nontrivial breaking has an invalid QME disposition")
    else:
        counterterm = classification["exact_counterterm"]
        if (
            classification["status"] != "TRIVIAL_OR_ZERO"
            or disposition["status"] != "RESTORABLE_BY_LOCAL_COUNTERTERM"
            or (values[3] and counterterm is None)
        ):
            raise ValueError("trivial breaking has an invalid QME disposition")
        if counterterm is not None:
            counterterm_artifact = _artifact(
                counterterm, repository_root=repository_root, label="exact_counterterm"
            )
            if not allow_synthetic_fixture:
                _require_bound_breaking_proof(
                    counterterm_artifact,
                    repository_root=repository_root,
                    label="exact_counterterm",
                    expected_result_id=PROOF_RESULT_IDS["exact_counterterm"],
                    classical_commit=payload["classical_commit"],
                    analytic_route=payload["analytic_route"],
                    coefficient_basis=payload["coefficient_basis"],
                    coefficients=coefficients,
                )
    if not isinstance(payload["claim_boundary"], str) or not payload["claim_boundary"]:
        raise ValueError("regulated-breaking claim boundary is missing")
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(export_schema).validate(payload)
    return {
        "cohomology_coordinates": [_fraction(value) for value in values[:3]],
        "exact_coordinate": _fraction(values[3]),
        "classification": classification["status"],
        "qme_disposition": disposition["status"],
        "insertion_decomposition": "COMPLETE_RECEIVER_INPUT",
    }


def receiver_fixture_payload(
    coefficients: tuple[Fraction, Fraction, Fraction, Fraction],
    *,
    nontrivial: bool,
    formulation: str = "SECOND_ORDER_AUXILIARY",
) -> dict[str, Any]:
    """Build a content-addressed exact mechanics fixture for receiver tests."""

    proof_path = "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
    artifact = {
        "format": "JSON_PROOF",
        "path": proof_path,
        "sha256": _sha256(ROOT / proof_path),
    }
    return {
        "schema": EXPORT_SCHEMA_ID,
        "result_id": "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": "0" * 40,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "classical_snapshot_compatibility": {
            "local_BV_commit": "0" * 40,
            "analytic_operator_commit": "0" * 40,
            "status": "IDENTICAL_COMMIT",
            "proof_artifact": None,
        },
        "normalization": {
            "action": "S_W=alpha_C integral sqrt(g) C^2",
            "alpha_C": "1",
            "signature": "Euclidean",
            "gauge": "fixture",
            "regularization": "exact fixture",
            "scheme": "fixture",
            "boundary_conditions": "closed",
        },
        "operator_and_measure": {
            "formulation": formulation,
            **{
                key: artifact
                for key in (
                    "complete_complex_artifact",
                    "multiplicity_artifact",
                    "zero_mode_ledger_artifact",
                    "measure_contour_artifact",
                )
            },
            **{
                key: "VERIFIED"
                for key in (
                    "complete_complex_status",
                    "multiplicity_status",
                    "zero_mode_ledger_status",
                    "measure_contour_status",
                )
            },
            "auxiliary_fourth_order_match_status": (
                "VERIFIED"
                if formulation == "SECOND_ORDER_AUXILIARY"
                else "NOT_APPLICABLE_FOURTH_ORDER_METRIC"
            ),
            "auxiliary_fourth_order_match_artifact": (
                artifact if formulation == "SECOND_ORDER_AUXILIARY" else None
            ),
        },
        "coefficient_basis": list(RAW_BASIS),
        "coefficients": {
            key: _fraction(value) for key, value in zip(RAW_BASIS, coefficients)
        },
        "insertion_decomposition": {
            "regulated_slavnov_action_status": "COMPUTED",
            "regulated_slavnov_action_artifact": artifact,
            "cohomology_reduction_status": "VERIFIED_AGAINST_COMPLETE_GAUGE_FIXED_H14",
            "total_derivative_status": "EXPLICIT_INCLUDING_ZERO",
            "total_derivative_artifact": artifact,
            "gauge_parameter_dependence_status": "INDEPENDENT_VERIFIED",
            "gauge_parameter_dependence_artifact": artifact,
            "regularization_dependence_status": "DEPENDENT_DECOMPOSED",
            "regularization_dependence_artifact": artifact,
            "antifield_completion_status": "COMPLETE_INCLUDING_ZERO",
            "antifield_completion_artifact": artifact,
        },
        "consistency": {
            "wess_zumino_status": "VERIFIED",
            "wess_zumino_proof": artifact,
            "parity_status": "WARD_VERIFIED_ZERO",
            "parity_proof": artifact,
        },
        "classification": {
            "status": "NONTRIVIAL" if nontrivial else "TRIVIAL_OR_ZERO",
            "exact_counterterm": None if nontrivial else artifact,
        },
        "qme_disposition": {
            "status": (
                "OBSTRUCTED_STRICT_FIELD_CONTENT"
                if nontrivial
                else "RESTORABLE_BY_LOCAL_COUNTERTERM"
            ),
            "proof_artifact": artifact,
        },
        "claim_boundary": "mechanics fixture only",
    }


def _receiver_fixture() -> dict[str, Any]:

    obstructed = validate_regulated_breaking_export(
        receiver_fixture_payload(
            (Fraction(199, 30), Fraction(-87, 20), Fraction(0), Fraction(0)),
            nontrivial=True,
        ),
        repository_root=ROOT,
        allow_synthetic_fixture=True,
    )
    restorable = validate_regulated_breaking_export(
        receiver_fixture_payload(
            (Fraction(0), Fraction(0), Fraction(0), Fraction(1)), nontrivial=False
        ),
        repository_root=ROOT,
        allow_synthetic_fixture=True,
    )
    return {
        "scope": "SYNTHETIC_EXACT_RECEIVER_MECHANICS_ONLY",
        "nontrivial_branch": obstructed,
        "trivial_branch": restorable,
    }


def _validate_inputs(values: dict[str, dict[str, Any]]) -> None:
    g2 = values["full_local_BV_G2"]
    h14 = values["gauge_fixed_H14"]
    triviality = values["BoxR_triviality"]
    coefficients = values["standard_background_coefficients"]
    auxiliary = values["standard_auxiliary_fourth_order_match"]
    multiplicity = values["full_BV_multiplicity_preflight"]
    composer = values["full_BV_ledger_composer"]
    physical_tt = values["physical_TT_dictionary"]
    physical_ledger = values["physical_full_BV_multiplicity_ledger"]
    repository_euler = values["repository_round_S4_Euler_coefficient"]
    nonconformal_receiver = values["nonconformal_coefficient_match_receiver"]
    compatibility = values["classical_snapshot_compatibility_receiver"]
    physical_compatibility = values["physical_classical_snapshot_compatibility"]
    ward = values["Ward_insertion_contract"]
    if (
        g2.get("result_state")
        != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or g2.get("claim_flags", {}).get("FULL_BV_G2_COMPLETE") is not True
        or g2.get("claim_flags", {}).get("REGULATED_SLAVNOV_BREAKING_COMPUTED")
        is not False
    ):
        raise ValueError("full local BV G2 dependency drifted")
    if (
        h14.get("result_state") != "GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE"
        or h14.get("parity_dimensions") != {"even": 2, "odd": 1}
        or [row.get("representative_id") for row in h14.get("classes", [])]
        != list(QUOTIENT_BASIS)
        or h14.get("exact_rows") != ["ANOM_OMEGA_BOX_R"]
    ):
        raise ValueError("gauge-fixed H14 dependency drifted")
    box_r = triviality.get("trivializations", {}).get("ANOM_OMEGA_BOX_R", {})
    if (
        triviality.get("result_state") != "EXACT_PRIMITIVES_VERIFIED"
        or box_r.get("class_status") != "EXACT"
        or box_r.get("primitive") != "R^2"
        or box_r.get("primitive_coefficient")
        != {"numerator": -1, "denominator": 12}
    ):
        raise ValueError("omega BoxR trivialization drifted")
    flags = coefficients.get("claim_flags", {})
    if (
        coefficients.get("result_state")
        != "STANDARD_SPIN2_BACKGROUND_COEFFICIENTS_COMPUTED_D_PULLBACK_CERTIFIED"
        or flags.get("STANDARD_BACKGROUND_A_AND_C_COMPUTED") is not True
        or flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or flags.get("FULL_GAUGE_FIXED_BV_ANOMALY_BASIS_AVAILABLE") is not True
        or flags.get("REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED") is not False
        or coefficients.get("coefficient_calculation", {}).get("anomaly_coordinates")
        != {"C2": "199/30", "CdualC": "0", "E4": "-87/20"}
    ):
        raise ValueError("standard coefficient dependency drifted")
    if (
        auxiliary.get("result_state")
        != "STANDARD_PHYSICAL_TT_SCHUR_AND_LOCAL_JACOBIAN_IDENTITY_VERIFIED_REPOSITORY_MATCH_OPEN"
        or auxiliary.get("claim_flags", {}).get(
            "STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY"
        )
        is not True
        or auxiliary.get("claim_flags", {}).get(
            "STANDARD_LOCAL_FIELD_DEPENDENT_JACOBIAN_ZERO"
        )
        is not True
        or auxiliary.get("claim_flags", {}).get("REPOSITORY_AUXILIARY_MEASURE_MATCH")
        is not False
    ):
        raise ValueError("standard auxiliary/fourth-order dependency drifted")
    multiplicity_flags = multiplicity.get("claim_flags", {})
    if (
        multiplicity.get("result_state")
        != "STANDARD_FACTOR_AND_COVARIANT_FIELD_RANKS_MATCHED_SCALAR_GHOST_AND_ANALYTIC_ROW_MAP_OPEN"
        or multiplicity.get("classical_commit") != g2.get("classical_commit")
        or multiplicity_flags.get("STANDARD_FACTOR_MULTIPLICITIES_COMPLETE") is not True
        or multiplicity_flags.get("COVARIANT_MINIMAL_COMPONENT_RANKS_COMPLETE")
        is not True
        or multiplicity_flags.get("SCALAR_GHOST_GAP_LOCALIZED_TO_RANK_ONE")
        is not True
        or multiplicity_flags.get("MULTIPLICITY_EXPORT_SEMANTIC_RECEIVER_READY")
        is not True
        or multiplicity_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
    ):
        raise ValueError("full-BV multiplicity preflight dependency drifted")
    composer_flags = composer.get("claim_flags", {})
    composer_contract = composer.get("accepted_contract", {})
    if (
        composer.get("result_state")
        != "ALL_STANDARD_ROWS_BOUND_COMPOSER_READY_PHYSICAL_TT_INPUT_NOT_SUPPLIED"
        or composer_flags.get("FULL_BV_LEDGER_COMPOSER_READY") is not True
        or composer_flags.get("ALL_NON_TT_STANDARD_ROWS_BOUND") is not True
        or composer_flags.get(
            "COMPOSER_EXACT_EXPONENT_AND_ZERO_MODE_POLICY_ENFORCED"
        )
        is not True
        or composer_flags.get("PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED") is not False
        or composer_flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not False
        or composer_contract.get("required_input_result_id")
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
    ):
        raise ValueError("full-BV ledger composer dependency drifted")
    physical_commit = physical_tt.get("classical_commit")
    if not isinstance(physical_commit, str) or len(physical_commit) != 40:
        raise ValueError("physical TT dictionary classical commit drifted")
    validate_tt_hessian_dictionary(
        physical_tt,
        repository_root=ROOT,
        expected_classical_commit=physical_commit,
    )
    physical_tt_flags = physical_tt.get("claim_flags", {})
    if (
        physical_tt.get("result_state")
        != "REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED"
        or physical_tt_flags.get(
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_SUPPLIED"
        )
        is not True
        or physical_tt_flags.get("REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED")
        is not True
        or physical_tt_flags.get("REPOSITORY_ELLIPTIC_TT_BLOCK_CERTIFIED")
        is not True
        or physical_tt_flags.get("REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED")
        is not False
    ):
        raise ValueError("physical TT dictionary dependency drifted")
    validate_repository_multiplicity_export(
        physical_ledger,
        repository_root=ROOT,
        expected_classical_commit=physical_commit,
        expected_analytic_route="EUCLIDEAN_ELLIPTIC",
    )
    if (
        physical_ledger.get("result_state")
        != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
        or [row.get("operator") for row in physical_ledger.get("repository_factors", [])]
        != [
            "Delta_2_perp(4)",
            "Delta_0(-4)",
            "Delta_2_perp(2)",
            "Delta_1_perp(-3)",
        ]
        or physical_ledger.get("cancellations", {}).get("factor_coverage_status")
        != "VERIFIED"
        or physical_ledger.get("cancellations", {}).get(
            "integration_row_coverage_status"
        )
        != "VERIFIED"
    ):
        raise ValueError("physical full-BV multiplicity ledger dependency drifted")
    repository_euler_flags = repository_euler.get("claim_flags", {})
    if (
        repository_euler.get("result_state")
        != "REPOSITORY_EUCLIDEAN_S4_EULER_COEFFICIENT_MATCHED_C_COEFFICIENT_OPEN"
        or repository_euler.get("classical_commit") != physical_commit
        or repository_euler.get("coefficient_result", {}).get("a") != "87/20"
        or repository_euler.get("coefficient_result", {}).get("E4_coordinate")
        != "-87/20"
        or repository_euler.get("coefficient_result", {}).get("c")
        != "NOT_DETERMINED_ON_ROUND_S4"
        or repository_euler_flags.get(
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED"
        )
        is not True
        or repository_euler_flags.get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not False
        or repository_euler_flags.get(
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED"
        )
        is not False
    ):
        raise ValueError("repository round-S4 Euler coefficient dependency drifted")
    nonconformal_flags = nonconformal_receiver.get("claim_flags", {})
    if (
        nonconformal_receiver.get("result_state")
        != "RECEIVER_READY_CURRENT_CANDIDATES_FAIL_COMPLEMENTARY_GATES"
        or nonconformal_flags.get("NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY")
        is not True
        or nonconformal_flags.get("CURRENT_CANDIDATES_AUDITED") is not True
        or nonconformal_flags.get("PHYSICAL_C2_CARRIER_SUPPLIED") is not False
        or nonconformal_flags.get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not False
        or nonconformal_receiver.get("accepted_contract", {}).get(
            "required_result_id"
        )
        != "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH"
    ):
        raise ValueError("nonconformal coefficient receiver dependency drifted")
    compatibility_flags = compatibility.get("claim_flags", {})
    if (
        compatibility.get("result_state")
        != "CONTENT_HASH_COMPATIBILITY_RECEIVER_READY_PHYSICAL_BRIDGE_NOT_SUPPLIED"
        or compatibility_flags.get(
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY"
        )
        is not True
        or compatibility_flags.get("DISTINCT_COMMITS_REQUIRE_CONTENT_PROOF")
        is not True
        or compatibility_flags.get("PHYSICAL_COMPATIBILITY_BRIDGE_SUPPLIED")
        is not False
    ):
        raise ValueError("classical snapshot compatibility dependency drifted")
    frozen_import = json.loads(
        (
            ROOT
            / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
        ).read_text()
    )
    physical_compatibility_receipt = validate_classical_snapshot_compatibility(
        physical_compatibility,
        repository_root=ROOT,
        expected_local_commit=g2["classical_commit"],
        expected_local_hashes=frozen_import["independent_replay"]["canonical_hashes"],
        expected_analytic_commit=physical_commit,
    )
    if (
        physical_compatibility.get("result_state")
        != "LOCAL_BV_CONTENT_HASHES_EQUAL_ACROSS_DISTINCT_COMMITS"
        or physical_compatibility_receipt.get("status")
        != "SEMANTIC_RECEIVER_ACCEPTED"
        or physical_compatibility_receipt.get("matched_hash_count") != 5
    ):
        raise ValueError("physical classical snapshot compatibility drifted")
    if (
        ward.get("result_state") != "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED"
        or ward.get("physical_input_status") != "NOT_RECEIVED"
        or ward.get("qme_status") != "NOT_COMPUTED"
    ):
        raise ValueError("Ward insertion contract crossed its input boundary")


def analysis() -> dict[str, Any]:
    values = _load_inputs()
    _validate_inputs(values)
    even = (Fraction(199, 30), Fraction(-87, 20))
    reduction_entries = [
        {"row": index, "column": index, "coefficient": _fraction(1)}
        for index in range(3)
    ]
    quotient_image = (*even, Fraction(0))
    if not quotient_image[0] or not quotient_image[1]:
        raise AssertionError("standard even background vector lost a nonzero coordinate")
    witness_rows = [
        {
            "witness_id": f"lambda_{basis}",
            "coordinates_on_quotient_basis": [
                _fraction(1 if row == column else 0) for column in range(3)
            ],
            "standard_background_evaluation": _fraction(quotient_image[row]),
            "status": "TRANSPORTED_COMPLETE_QUOTIENT_COORDINATE_DUAL",
        }
        for row, basis in enumerate(QUOTIENT_BASIS)
    ]
    dependency_hashes = {name: _sha256(path) for name, path in DEPENDENCIES.items()}
    proof_payload = {
        "raw_basis": RAW_BASIS,
        "quotient_basis": QUOTIENT_BASIS,
        "reduction_entries": reduction_entries,
        "even": [_fraction(value) for value in even],
        "standard_quotient_vector": [_fraction(value) for value in quotient_image],
        "dependency_hashes": dependency_hashes,
        "repository_physical_input": {
            "classical_commit": values["physical_TT_dictionary"]["classical_commit"],
            "round_S4_Euler_a": "87/20",
            "round_S4_C2_status": "NOT_DETERMINED_ON_ROUND_S4",
        },
    }
    return {
        "dependency_hashes": dependency_hashes,
        "raw_basis": list(RAW_BASIS),
        "quotient_basis": list(QUOTIENT_BASIS),
        "reduction_entries": reduction_entries,
        "standard_even_vector": [_fraction(value) for value in even],
        "standard_quotient_vector": [_fraction(value) for value in quotient_image],
        "witness_rows": witness_rows,
        "repository_physical_input": proof_payload["repository_physical_input"],
        "proof_sha256": _canonical_hash(proof_payload),
    }


def build() -> dict[str, Any]:
    result = analysis()
    certificate = {
        "schema": "quantum-weyl-regulated-slavnov-breaking-assembly-preflight-v1",
        "result_id": "REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT",
        "result_state": "FULL_BV_QUOTIENT_PHYSICAL_ROUND_S4_LEDGER_EULER_AND_SNAPSHOT_COMPATIBILITY_BOUND_REGULATED_BV_INSERTION_OPEN",
        "result_stage": "CLASSIFIED_AND_BACKGROUND_VECTOR_BOUND",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "regularity_scope": "REGULAR_BACH_LOCUS_FOR_LOCAL_BV_COHOMOLOGY",
        "dependency_hashes": result["dependency_hashes"],
        "accepted_export_schema": EXPORT_SCHEMA_ID,
        "accepted_proof_result_ids": PROOF_RESULT_IDS,
        "receiver_mechanics": _receiver_fixture(),
        "cohomology_reduction": {
            "raw_candidate_basis": result["raw_basis"],
            "quotient_basis": result["quotient_basis"],
            "matrix_shape": [3, 4],
            "matrix_entries": result["reduction_entries"],
            "kernel": ["ANOM_OMEGA_BOX_R"],
            "kernel_primitive": "-(1/12) R^2 modulo d_h current",
            "pure_Diff_dimension": 0,
            "independent_mixed_Diff_Weyl_dimension": 0,
            "positive_antifield_extra_dimension": 0,
            "nonminimal_extra_dimension": 0,
        },
        "standard_background_input": {
            "scope": "STANDARD_ISOLATED_FOUR_DIMENSIONAL_CONFORMAL_SPIN_TWO_BACKGROUND_ANOMALY",
            "convention": "(4 pi)^(-2) [c omega C2-a omega E4] modulo exact omega BoxR",
            "known_even_coordinates": result["standard_even_vector"],
            "quotient_coordinates": result["standard_quotient_vector"],
            "parity_odd_status": "WARD_VERIFIED_ZERO_FOR_STANDARD_PARITY_EVEN_REGULATOR",
            "BoxR_status": "SCHEME_DEPENDENT_EXACT_REMOVABLE",
            "repository_matching_status": "E4_MATCHED_ON_ROUND_S4_C2_REPOSITORY_MATCH_OPEN",
        },
        "repository_physical_input": {
            "classical_commit": result["repository_physical_input"]["classical_commit"],
            "analytic_route": "EUCLIDEAN_ELLIPTIC",
            "TT_dictionary_status": "SEMANTIC_RECEIVER_ACCEPTED",
            "full_BV_multiplicity_ledger_status": "SEMANTIC_RECEIVER_ACCEPTED",
            "round_S4_Euler_coefficient": {
                "a": {"numerator": 87, "denominator": 20},
                "E4_coordinate": {"numerator": -87, "denominator": 20},
            },
            "round_S4_C2_status": result["repository_physical_input"][
                "round_S4_C2_status"
            ],
            "repository_BV_anomaly_vector_status": "NOT_COMPUTED",
        },
        "complete_dual_witness_binding": {
            "basis_status": "COMPLETE_GAUGE_FIXED_BV_QUOTIENT_ON_REGULAR_BACH_LOCUS",
            "witnesses": result["witness_rows"],
            "known_even_vector_nonzero": True,
            "proof_source": "GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION",
        },
        "conditional_obstruction_theorem": {
            "status": "PROVED_CONDITIONAL_NOT_ACTIVATED",
            "antecedents": [
                "repository regulator and measure match the standard spin-two nontrivial even coordinates",
                "regulated Slavnov breaking satisfies the Wess-Zumino consistency equation in the certified local BV complex",
                "field content is strict pure Weyl gravity with no compensating Wess-Zumino sector",
            ],
            "conclusion": "the one-loop breaking has a nonzero H14 class and the strict fixed-field-content QME is obstructed",
            "reason": "both certified even quotient coordinates 199/30 and -87/20 are nonzero",
            "activated": False,
        },
        "analytic_matching_ledger": {
            "discharged": [
                "complete minimal/nonminimal/gauge-fixed local H14 quotient",
                "pure-Diff and independent mixed Diff-Weyl exclusion",
                "explicit omega BoxR primitive",
                "exact standard background even coefficient reconstruction",
                "standard parity-even determinant Ward identity fixing the odd coordinate to zero",
                "standard physical TT auxiliary/fourth-order Schur and local Jacobian identity",
                "standard determinant bundle ranks and covariant BV component ranks",
                "exact rank-two-to-rank-one scalar Diff-Weyl ghost reduction",
                "York/Hodge measure and nonminimal quartet Berezinian cancellation",
                "round-S4 standard zero-mode and priming ledger",
                "mutation-tested full-BV local multiplicity composer for all non-TT rows",
                "semantically replayed physical round-S4 TT Hessian dictionary",
                "semantically replayed physical round-S4 full-BV multiplicity ledger",
                "repository round-S4 Euler coefficient a=87/20 (E4 coordinate -87/20)",
                "mutation-tested C2-visible full-BV coefficient-match receiver and current-candidate audit",
                "semantic cross-commit classical snapshot compatibility receiver",
                "physical cross-commit classical snapshot compatibility bridge",
                "versioned regulated BV insertion-decomposition output contract",
                "portable renormalized Ward-insertion input contract",
            ],
            "missing": [
                {
                    "carrier_id": "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH",
                    "required_output": "supply the executable receiver input on an eligible C2-visible Euclidean background, including the repository elliptic BV complex, measure, regulator and exact factor coefficient sum",
                },
                {
                    "carrier_id": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
                    "required_output": "bind the composed factors to a complete gauge-fixed elliptic complex, action normalization and declared fourth-order or auxiliary formulation",
                },
                {
                    "carrier_id": "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER",
                    "required_output": "content-address the regulator, priming, determinant measure and any formulation-specific contour or global phase policy",
                },
                {
                    "carrier_id": "REGULATED_BV_SLAVNOV_ACTION",
                    "required_output": "compute the regularized BV antibracket insertion, Wess-Zumino consistency, parity disposition and cohomology coordinates",
                },
            ],
        },
        "minimal_missing_carrier_theorem": {
            "status": "EXACT_REGULATED_BV_INSERTION_GAP",
            "algebraic_basis_gap": False,
            "coefficient_arithmetic_gap": False,
            "standard_parity_gap": False,
            "standard_physical_TT_auxiliary_identity_gap": False,
            "standard_factor_rank_gap": False,
            "scalar_ghost_gap_rank": 0,
            "full_BV_ledger_composer_ready": True,
            "physical_TT_dictionary_accepted": True,
            "physical_full_BV_multiplicity_ledger_accepted": True,
            "repository_round_S4_Euler_coefficient_computed": True,
            "repository_C2_coefficient_gap": True,
            "nonconformal_coefficient_match_receiver_ready": True,
            "classical_snapshot_compatibility_bridge_gap": False,
            "physical_classical_snapshot_compatibility_accepted": True,
            "regulated_BV_insertion_v2_receiver_ready": True,
            "remaining_decision_gap": "the round-S4 physical ledger fixes a=87/20 but cannot see C2; a non-conformally-flat or Ricci-flat full-BV coefficient carrier, a cross-snapshot compatibility proof, and a regulated BV Slavnov insertion with Wess-Zumino and parity proofs remain required; determinant coefficients alone do not decide the QME",
            "no_further_local_graph_expansion_required": True,
        },
        "claim_flags": {
            "FULL_GAUGE_FIXED_BV_H14_BOUND": True,
            "STANDARD_BACKGROUND_EVEN_VECTOR_REDUCED": True,
            "STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED": True,
            "STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND": True,
            "FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND": True,
            "FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_BOUND": True,
            "FULL_BV_LEDGER_COMPOSER_READY": True,
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED": True,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": True,
            "REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED": True,
            "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED": True,
            "NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY": True,
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND": True,
            "REGULATED_BV_INSERTION_V2_RECEIVER_READY": True,
            "CONDITIONAL_NONZERO_QME_CLASS_THEOREM": True,
            "ANALYTIC_SLAVNOV_EXPORT_RECEIVER_READY": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_OBSTRUCTED": False,
            "QME_RESTORED": False,
            "D_CARTAN_CLASSIFIED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "proof_sha256": result["proof_sha256"],
        "next_gate": "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL preflight binds the complete local gauge-fixed BV H14 quotient on the regular Bach locus to the exact standard conformal-spin-two background vector (199/30,-87/20,0). It proves the quotient reduction, removes omega BoxR with its explicit primitive, and imports an exact parity Ward zero for the declared standard parity-even determinant regulator. The rank-two scalar Diff-Weyl ghost reduction, York/Hodge measure, nonminimal Berezinian, standard zero modes, determinant exponents, and all local multiplicity rows are exact. The physical round-S4 TT Hessian dictionary and full-BV multiplicity ledger pass their semantic receivers, and the physical round-S4 ledger fixes a=87/20, equivalently E4 coordinate -87/20. Because round S4 is conformally flat, it cannot determine c: 199/30 remains a standard Euclidean cross-check rather than a repository promotion. Although the analytic producer and local-BV commits differ, exact Git-tree attribution and equality of all five canonical classical hashes now supply the required physical compatibility bridge. This still does not compute a BV Slavnov breaking: a non-conformally-flat or Ricci-flat C2 carrier, complete elliptic realization, regulator and measure policy, regularized antibracket insertion, Wess-Zumino proof, and repository parity disposition remain required. The versioned v2 export receiver requires the regulated action, total-derivative remainder, gauge-parameter dependence, regularization dependence, and antifield completion explicitly, including certified zero rows. Every insertion-side proof binds the exact commit, analytic route, basis, and coefficient hash. It permits a genuinely fourth-order metric route without inventing an auxiliary-row proof, while retaining the equivalence proof on an auxiliary route. Distinct analytic and local-BV commits require a full semantic replay of the five canonical classical snapshot hashes and the role-specific nested proofs; a matching result_id alone is rejected. It proves only the conditional implication that a physical regulated breaking with a nonzero quotient coordinate would obstruct the strict fixed-field-content QME. Therefore it does not promote a complete repository anomaly vector, activate the obstruction theorem, restore or obstruct the QME, classify the D-Cartan defect, transfer to residual cohomology, or establish Lorentzian quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(certificate)
    return certificate


def validate_claim_boundary(certificate: dict[str, Any]) -> None:
    flags = certificate.get("claim_flags", {})
    if (
        flags.get("FULL_GAUGE_FIXED_BV_H14_BOUND") is not True
        or flags.get("STANDARD_BACKGROUND_EVEN_VECTOR_REDUCED") is not True
        or flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or flags.get("STANDARD_PHYSICAL_TT_AUXILIARY_IDENTITY_BOUND") is not True
        or flags.get("FULL_BV_MULTIPLICITY_PREFLIGHT_BOUND") is not True
        or flags.get("FULL_BV_MULTIPLICITY_SEMANTIC_RECEIVER_BOUND") is not True
        or flags.get("FULL_BV_LEDGER_COMPOSER_READY") is not True
        or flags.get("REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_ACCEPTED")
        is not True
        or flags.get("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED")
        is not True
        or flags.get("REPOSITORY_ROUND_S4_EULER_COEFFICIENT_COMPUTED")
        is not True
        or flags.get("REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_ACCEPTED")
        is not True
        or flags.get("NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY") is not True
        or flags.get("CLASSICAL_SNAPSHOT_COMPATIBILITY_SEMANTIC_RECEIVER_BOUND")
        is not True
        or flags.get("REGULATED_BV_INSERTION_V2_RECEIVER_READY") is not True
        or flags.get("CONDITIONAL_NONZERO_QME_CLASS_THEOREM") is not True
        or flags.get("ANALYTIC_SLAVNOV_EXPORT_RECEIVER_READY") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
                "REGULATED_SLAVNOV_BREAKING_COMPUTED",
                "QME_OBSTRUCTED",
                "QME_RESTORED",
                "D_CARTAN_CLASSIFIED",
                "LORENTZIAN_QUANTUM_THEORY",
            )
        )
        or certificate.get("conditional_obstruction_theorem", {}).get("activated")
        is not False
        or certificate.get("next_gate")
        != "SUPPLY_REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH_AND_REGULATED_SLAVNOV_INSERTION"
    ):
        raise ValueError("Slavnov-breaking preflight crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(schema).validate(value)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale regulated Slavnov-breaking preflight: {OUTPUT}")
    print("SLAVNOV BREAKING ASSEMBLY: FULL BV BASIS BOUND; ANALYTIC MATCHING OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
