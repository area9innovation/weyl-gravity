#!/usr/bin/env python3
"""Independent fail-closed verifier for the cyclicity-defect atlas."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_coupled_cyclicity_defect_atlas import HERE, PAYLOAD_PATH
from .berger_coupled_cyclicity_defect_atlas_certificate import OUTPUT, build_certificate


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rejects_overclaim(value: dict) -> None:
    flags = value["claim_flags"]
    scaling = {
        row["convention"]: row
        for row in value["convention_sweep"]["output_scaling_cases"]
    }
    if (
        flags["PAIRING_SIGN_ONLY_REPAIR_FOUND"]
        or flags["UNIFORM_MAXWELL_OUTPUT_X2_COMPLETE_REPAIR"]
        or flags["COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND"]
        or flags["MIXED_Q3_TRANSFERRED"]
        or flags["QUANTUM_CLAIM"]
        or scaling["uniform_Maxwell_output_x2"]["retained_cyclicity_defect_count"] != 15
        or scaling["uniform_Maxwell_output_x2"]["retained_q1_q2_defect_count"] != 0
    ):
        raise ValueError("cyclicity atlas was over-promoted or its partial repair drifted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    payload = json.loads(PAYLOAD_PATH.read_text())
    certificate_schema = json.loads(
        (HERE / "schema/berger-coupled-cyclicity-defect-atlas-v1.schema.json").read_text()
    )
    payload_schema = json.loads(
        (HERE / "schema/berger-coupled-retained-cyclicity-defect-payload-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, certificate_schema) + validate_instance(
        payload, payload_schema
    )
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    expected_certificate, expected_payload = build_certificate()
    if certificate != expected_certificate or payload != expected_payload:
        raise ValueError("cyclicity atlas does not reproduce")
    body = {key: payload[key] for key in payload if key != "canonical_sha256"}
    if (
        payload["canonical_sha256"] != _canonical_hash(body)
        or certificate["defect_payload"]["file_sha256"]
        != hashlib.sha256(PAYLOAD_PATH.read_bytes()).hexdigest()
    ):
        raise ValueError("defect payload hash drifted")
    _rejects_overclaim(certificate)
    for key in (
        "PAIRING_SIGN_ONLY_REPAIR_FOUND",
        "UNIFORM_MAXWELL_OUTPUT_X2_COMPLETE_REPAIR",
        "COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND",
        "MIXED_Q3_TRANSFERRED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            _rejects_overclaim(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"atlas overclaim mutation accepted: {key}")
    mutant_payload = deepcopy(payload)
    mutant_payload["entries"][0][5]["rational"] = 0
    mutant_body = {
        key: mutant_payload[key]
        for key in mutant_payload
        if key != "canonical_sha256"
    }
    if mutant_payload["canonical_sha256"] == _canonical_hash(mutant_body):
        raise ValueError("defect coefficient mutation escaped canonical hash")
    return certificate


def main() -> int:
    verify()
    print("BERGER COUPLED CYCLICITY ATLAS independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
