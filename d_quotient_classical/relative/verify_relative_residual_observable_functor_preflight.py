#!/usr/bin/env python3
"""Independent schema and claim-boundary check for the relative preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-residual-observable-functor-preflight-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    for item in certificate["dependency_refs"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {item['path']}")
    imported = certificate["required_import"]["status"] == "IMPORTED"
    expected_row = {
        "O2": "PARTIAL_FIXTURES_ONLY",
        "cofiber": "IMPORTED_MAPPING_COFIBER" if imported else "BLOCKED_OFFSHELL_TRIANGLE_MISSING",
        "map_iota": "IMPORTED_OFFSHELL_TRIANGLE" if imported else "ONSHELL_MAP_ONLY",
        "observable_map": "BLOCKED_OFFSHELL_PULLBACK_MISSING",
        "quantum_lift": "NOT_APPLICABLE_TO_CLASSICAL_PREFLIGHT",
        "relative_pairing": "CLASSICAL_REDUCED_MODE_PULLBACK_ONLY",
        "residual_action": "BLOCKED_OFFSHELL_EQUIVARIANCE_MISSING",
    }
    if certificate["shared_relative_row"] != expected_row:
        raise AssertionError("shared relative row drifted")
    expected_true = 2 if imported else 1
    if sum(bool(v) for v in certificate["flags"].values()) != expected_true:
        raise AssertionError("a downstream relative flag was promoted")
    print("relative residual/observable preflight independent audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
