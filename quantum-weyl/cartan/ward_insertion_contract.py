"""Portable contract for a coefficient-bearing renormalized D-Ward insertion.

The exact finite Cartan engine already implements the defect, its sourced
consistency identity, admissible quotient, and scheme covariance.  This
module defines the physical operator payload that must be supplied before
that engine can be used for a quantum verdict.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any, Iterable

from .defect_complex import (
    ExactMatrix,
    FiniteGradedComplex,
    FirstOrderCartanData,
    HomogeneousOperator,
    classify_closed_defect,
)


SCHEMA_ID = "quantum-weyl-renormalized-D-ward-insertion-export-v1"
OPERATOR_DEGREES = {
    "L_D0": 0,
    "L_D1": 0,
    "Q0": 1,
    "Q1": 1,
    "iota_D0": -1,
    "iota_D1": -1,
}
CONSISTENCY_CHECKS = (
    "Q0_squared_zero",
    "classical_Cartan_identity",
    "defect_consistency_Q_closed",
    "first_order_QME_linearization",
    "first_order_Ward_compatibility",
    "sourced_consistency_identity",
)
ALLOWED_TAGS = {
    "EUCLIDEAN-SPECTRAL",
    "LOCAL-ALGEBRAIC",
    "LORENTZIAN-CAUSAL",
    "REDUCED-MODE",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_fields(value: object, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label} fields drifted")
    return value


def _artifact(value: object, *, repository_root: Path, label: str) -> dict[str, str]:
    row = _require_fields(value, ("format", "path", "sha256"), label)
    if row["format"] not in {
        "JSON_ADMISSIBILITY_POLICY",
        "JSON_DUAL_WITNESS",
        "JSON_LOCAL_OPERATOR",
        "JSON_OBSERVABLE_COMPLEX",
        "JSON_PROOF_CERTIFICATE",
        "TEXT_PROOF_CERTIFICATE",
    }:
        raise ValueError(f"{label} has an unknown artifact format")
    path = (repository_root / row["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes the repository root") from exc
    if not path.is_file() or _sha256(path) != row["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    return row


def _optional_artifact(value: object, *, repository_root: Path, label: str) -> None:
    if value is not None:
        _artifact(value, repository_root=repository_root, label=label)


def validate_ward_insertion_export(
    payload: object,
    *,
    repository_root: Path,
) -> dict[str, Any]:
    """Validate a physical Ward-insertion payload without guessing semantics."""

    record = _require_fields(
        payload,
        (
            "schema",
            "result_id",
            "result_state",
            "dependency_tags",
            "setting_id",
            "generator_id",
            "phase_space_id",
            "renormalization",
            "observable_complex",
            "operators",
            "slavnov",
            "consistency_checks",
            "cartan_defect",
            "local_to_cartan_map",
            "claim_boundary",
        ),
        "Ward insertion export",
    )
    if (
        record["schema"] != SCHEMA_ID
        or record["result_id"] != "RENORMALIZED_D_WARD_INSERTION"
        or record["result_state"]
        not in {
            "REGULATED_BREAKING_COMPUTED_QME_OPEN",
            "QME_RESTORED_CARTAN_CLASSIFIED",
        }
        or record["generator_id"] != "D_compact"
    ):
        raise ValueError("Ward insertion identity or lifecycle drifted")
    tags = record["dependency_tags"]
    if (
        not isinstance(tags, list)
        or not tags
        or len(tags) != len(set(tags))
        or any(tag not in ALLOWED_TAGS for tag in tags)
        or "LOCAL-ALGEBRAIC" not in tags
    ):
        raise ValueError("Ward insertion dependency tags drifted")
    for key in ("setting_id", "phase_space_id", "claim_boundary"):
        if not isinstance(record[key], str) or not record[key]:
            raise ValueError(f"Ward insertion {key} is missing")

    renormalization = _require_fields(
        record["renormalization"],
        (
            "boundary_conditions",
            "gauge",
            "regularization",
            "scheme",
            "signature",
            "zero_mode_policy",
        ),
        "renormalization",
    )
    if any(not isinstance(value, str) or not value for value in renormalization.values()):
        raise ValueError("renormalization provenance is incomplete")

    observable = _require_fields(
        record["observable_complex"],
        (
            "admissibility_policy_artifact",
            "algebra_id",
            "grading_convention",
            "representation_artifact",
        ),
        "observable_complex",
    )
    for key in ("algebra_id", "grading_convention"):
        if not isinstance(observable[key], str) or not observable[key]:
            raise ValueError("observable complex identity is incomplete")
    _artifact(
        observable["representation_artifact"],
        repository_root=repository_root,
        label="observable_complex.representation_artifact",
    )
    _artifact(
        observable["admissibility_policy_artifact"],
        repository_root=repository_root,
        label="observable_complex.admissibility_policy_artifact",
    )

    operators = _require_fields(record["operators"], OPERATOR_DEGREES, "operators")
    for operator_id, degree in OPERATOR_DEGREES.items():
        operator = _require_fields(
            operators[operator_id],
            ("artifact", "degree", "evaluator_id", "expression_schema_version"),
            f"operators.{operator_id}",
        )
        if operator["degree"] != degree:
            raise ValueError(f"operators.{operator_id} has the wrong degree")
        if any(
            not isinstance(operator[key], str) or not operator[key]
            for key in ("evaluator_id", "expression_schema_version")
        ):
            raise ValueError(f"operators.{operator_id} evaluator identity is incomplete")
        _artifact(
            operator["artifact"],
            repository_root=repository_root,
            label=f"operators.{operator_id}.artifact",
        )

    slavnov = _require_fields(
        record["slavnov"],
        ("qme_source", "qme_status", "regulated_breaking"),
        "slavnov",
    )
    _artifact(
        slavnov["regulated_breaking"],
        repository_root=repository_root,
        label="slavnov.regulated_breaking",
    )
    _optional_artifact(
        slavnov["qme_source"],
        repository_root=repository_root,
        label="slavnov.qme_source",
    )

    checks = _require_fields(record["consistency_checks"], CONSISTENCY_CHECKS, "consistency_checks")
    allowed_check_statuses = {
        "Q0_squared_zero": {"VERIFIED_ZERO"},
        "classical_Cartan_identity": {"VERIFIED"},
        "defect_consistency_Q_closed": {"VERIFIED_ZERO", "SOURCED_NONZERO"},
        "first_order_QME_linearization": {"VERIFIED_ZERO", "COMPUTED_NONZERO"},
        "first_order_Ward_compatibility": {"VERIFIED_ZERO", "COMPUTED_NONZERO"},
        "sourced_consistency_identity": {"VERIFIED"},
    }
    for check_id in CONSISTENCY_CHECKS:
        check = _require_fields(
            checks[check_id], ("proof_artifact", "status"), f"consistency_checks.{check_id}"
        )
        _artifact(
            check["proof_artifact"],
            repository_root=repository_root,
            label=f"consistency_checks.{check_id}.proof_artifact",
        )
        if check["status"] not in allowed_check_statuses[check_id]:
            raise ValueError(f"consistency_checks.{check_id} has an invalid status")

    defect = _require_fields(
        record["cartan_defect"],
        ("artifact", "dual_witness", "primitive", "status"),
        "cartan_defect",
    )
    if defect["status"] not in {
        "ZERO",
        "EXACT_REMOVABLE",
        "NONTRIVIAL_ANOMALY",
        "UNDEFINED_ANALYTICALLY",
    }:
        raise ValueError("unknown Cartan defect status")
    _artifact(defect["artifact"], repository_root=repository_root, label="cartan_defect.artifact")
    _optional_artifact(defect["primitive"], repository_root=repository_root, label="cartan_defect.primitive")
    _optional_artifact(defect["dual_witness"], repository_root=repository_root, label="cartan_defect.dual_witness")
    if defect["status"] == "ZERO" and (defect["primitive"] is not None or defect["dual_witness"] is not None):
        raise ValueError("zero Cartan defect carries an invalid witness")
    if defect["status"] == "EXACT_REMOVABLE" and (defect["primitive"] is None or defect["dual_witness"] is not None):
        raise ValueError("exact Cartan defect lacks its unique witness type")
    if defect["status"] == "NONTRIVIAL_ANOMALY" and (defect["primitive"] is not None or defect["dual_witness"] is None):
        raise ValueError("nontrivial Cartan defect lacks its unique witness type")
    if defect["status"] == "UNDEFINED_ANALYTICALLY" and (defect["primitive"] is not None or defect["dual_witness"] is not None):
        raise ValueError("undefined Cartan defect carries a premature witness")

    map_row = _require_fields(record["local_to_cartan_map"], ("artifact", "status"), "local_to_cartan_map")
    _optional_artifact(map_row["artifact"], repository_root=repository_root, label="local_to_cartan_map.artifact")

    restored = record["result_state"] == "QME_RESTORED_CARTAN_CLASSIFIED"
    if restored:
        if (
            slavnov["qme_status"] != "RESTORED"
            or slavnov["qme_source"] is not None
            or checks["first_order_QME_linearization"]["status"] != "VERIFIED_ZERO"
            or checks["first_order_Ward_compatibility"]["status"] != "VERIFIED_ZERO"
            or checks["defect_consistency_Q_closed"]["status"] != "VERIFIED_ZERO"
            or checks["Q0_squared_zero"]["status"] != "VERIFIED_ZERO"
            or checks["classical_Cartan_identity"]["status"] != "VERIFIED"
            or checks["sourced_consistency_identity"]["status"] != "VERIFIED"
            or defect["status"] == "UNDEFINED_ANALYTICALLY"
            or map_row["status"] != "CONSTRUCTED"
            or map_row["artifact"] is None
        ):
            raise ValueError("restored Ward insertion is missing a required closure gate")
    else:
        if (
            slavnov["qme_status"] != "NOT_RESTORED_SOURCE_RETAINED"
            or slavnov["qme_source"] is None
            or checks["first_order_QME_linearization"]["status"] != "COMPUTED_NONZERO"
            or checks["defect_consistency_Q_closed"]["status"] != "SOURCED_NONZERO"
            or checks["sourced_consistency_identity"]["status"] != "VERIFIED"
            or defect["status"] != "UNDEFINED_ANALYTICALLY"
            or map_row != {"status": "NOT_CONSTRUCTED", "artifact": None}
        ):
            raise ValueError("sourced Ward insertion crossed the QME gate")
    return {
        "result_state": record["result_state"],
        "qme_status": slavnov["qme_status"],
        "cartan_status": defect["status"],
        "map_status": map_row["status"],
        "operator_hashes": {
            key: operators[key]["artifact"]["sha256"] for key in sorted(operators)
        },
    }


def _zero_fixture() -> FirstOrderCartanData:
    q = HomogeneousOperator("Q", 1, ExactMatrix.from_rows(((0, 0), (1, 0))))
    complex_ = FiniteGradedComplex((0, 1), q)
    iota = HomogeneousOperator("iota_D", -1, ExactMatrix.from_rows(((0, 1), (0, 0))))
    return FirstOrderCartanData(
        complex=complex_,
        iota_0=iota,
        lie_0=HomogeneousOperator("L_D", 0, ExactMatrix.identity(2)),
        q_1=HomogeneousOperator("Q_1", 1, ExactMatrix.zero(2, 2)),
        iota_1=HomogeneousOperator("iota_1", -1, ExactMatrix.zero(2, 2)),
        lie_1=HomogeneousOperator("L_D_1", 0, ExactMatrix.zero(2, 2)),
    )


def ward_mechanics_fixture() -> dict[str, Any]:
    data = _zero_fixture()
    checks = data.checks()
    classification = classify_closed_defect(data.complex, data.defect())
    if not all(checks.values()) or classification.status != "ZERO":
        raise AssertionError("Ward mechanics fixture failed")
    sourced_q = HomogeneousOperator(
        "Q", 1, ExactMatrix.from_rows(((0, 0, 0), (1, 0, 0), (0, 0, 0)))
    )
    sourced = FirstOrderCartanData(
        complex=FiniteGradedComplex((0, 1, 2), sourced_q),
        iota_0=HomogeneousOperator(
            "iota_D", -1, ExactMatrix.from_rows(((0, 0, 0), (0, 0, 1), (0, 0, 0)))
        ),
        lie_0=HomogeneousOperator("L_D", 0, ExactMatrix.zero(3, 3)),
        q_1=HomogeneousOperator(
            "Q_1", 1, ExactMatrix.from_rows(((0, 0, 0), (0, 0, 0), (0, 1, 0)))
        ),
        iota_1=HomogeneousOperator("iota_1", -1, ExactMatrix.zero(3, 3)),
        lie_1=HomogeneousOperator("L_D_1", 0, ExactMatrix.zero(3, 3)),
    )
    sourced_checks = sourced.checks()
    if (
        sourced_checks["first_order_QME_linearization"]
        or sourced_checks["defect_consistency_Q_closed"]
        or not sourced_checks["sourced_consistency_identity"]
    ):
        raise AssertionError("sourced Ward fixture failed")
    return {
        "fixture_id": "first_order_D_Ward_interface_mechanics",
        "scope": "FINITE_EXACT_MECHANICS_FIXTURE_ONLY",
        "closed_branch": {
            "classification": classification.status,
            "all_consistency_checks": "VERIFIED",
        },
        "sourced_branch": {
            "qme_source": "NONZERO",
            "defect_closure": "SOURCED_NONZERO",
            "sourced_consistency_identity": "VERIFIED",
            "classification": "UNDEFINED_ANALYTICALLY",
        },
    }


def build_contract_receipt() -> dict[str, Any]:
    return deepcopy(
        {
            "schema": "quantum-weyl-renormalized-D-ward-insertion-contract-v1",
            "result_id": "RENORMALIZED_D_WARD_INSERTION_CONTRACT",
            "result_state": "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "accepted_export_schema": SCHEMA_ID,
            "operator_degrees": OPERATOR_DEGREES,
            "required_consistency_checks": list(CONSISTENCY_CHECKS),
            "defect_formula": "A_D^(1)=[Q0,iota_D1]+[Q1,iota_D0]-L_D1",
            "sourced_identity": "[Q0,A_D^(1)]=[[Q0,Q1],iota_D0]-([Q0,L_D1]+[Q1,L_D0])",
            "mechanics_fixture": ward_mechanics_fixture(),
            "physical_input_status": "NOT_RECEIVED",
            "qme_status": "NOT_COMPUTED",
            "local_to_cartan_map_status": "NOT_CONSTRUCTED",
            "quantum_cartan_status": "NO_VERDICT",
            "next_gate": "IMPORT_REGULATED_SLAVNOV_BREAKING_AND_RENORMALIZED_WARD_OPERATORS",
            "claim_boundary": (
                "The content-addressed Ward-operator socket and its sourced/restored "
                "lifecycle rules are ready. The finite fixture verifies mechanics only. "
                "No regulated Slavnov breaking, physical Q1, restored QME, local-to-Cartan "
                "map, coefficient, or quantum D verdict is supplied."
            ),
        }
    )
