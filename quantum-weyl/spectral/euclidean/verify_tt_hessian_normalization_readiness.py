"""Independent verifier for the repository TT Hessian readiness audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json"
SCHEMA = HERE / "schema/repository-tt-hessian-normalization-readiness-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    identity = value["repository_action_normalization"]["curvature_identity"]
    if identity["residual_coordinates"] != ["0", "0", "0"] or identity["verified"] is not True:
        raise ValueError("repository curvature identity drifted")
    mutant = value["negative_control"]["mutated_identity"]
    if mutant["verified"] is not False or mutant["residual_coordinates"] == ["0", "0", "0"]:
        raise ValueError("R-squared coefficient mutation was not exposed")

    eligibility = {row["artifact"]: row["eligibility"] for row in value["evidence_eligibility_ledger"]}
    if eligibility != {
        "repository reduced Weyl action": "ACCEPTED_ACTION_NORMALIZATION_INPUT",
        "pure-weyl-tt-local-factorization-v1": "ACCEPTED_CYLINDER_OPERATOR_INPUT",
        "STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH": "ACCEPTED_TARGET_NOT_REPOSITORY_IDENTIFICATION",
        "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1": "REJECTED_AS_ROUND_S4_OPERATOR_DICTIONARY_BACKGROUND_MISMATCH",
    }:
        raise ValueError("evidence eligibility ledger drifted")

    missing = value["minimal_missing_carrier_theorem"]
    if (
        missing["missing_artifact"] != "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
        or "exact scalar kappa including sign" not in missing["required_exact_fields"]
        or value["target_operator"]["repository_identity_status"] != "NOT_COMPUTED_ON_ROUND_S4"
    ):
        raise ValueError("minimal missing carrier theorem drifted")

    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"TT Hessian readiness source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent repository TT Hessian readiness verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
