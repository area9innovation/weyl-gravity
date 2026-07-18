"""Independent verifier for repository elliptic-complex readiness."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .elliptic_complex_readiness import DEPENDENCIES, OUTPUT, ROOT, SCHEMA, build


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(checked)
    if checked != build():
        raise ValueError("elliptic-complex readiness does not reproduce")
    if checked["dependency_hashes"] != {
        name: _sha256(path) for name, path in DEPENDENCIES.items()
    }:
        raise ValueError("elliptic-complex readiness dependency drifted")
    if any(
        row["Euclidean"]
        and row["full_BV_rows"]
        and row["principal_symbol_exactness"]
        and row["gauge_fixed_ellipticity"]
        for row in checked["current_candidate_audit"]
    ):
        raise ValueError("eligible elliptic complex was incorrectly rejected")
    for path, digest in checked["provenance"]["source_sha256"].items():
        if _sha256(ROOT / path) != digest:
            raise ValueError(f"elliptic-complex readiness source drifted: {path}")
    return checked


if __name__ == "__main__":
    verify()
    print("independent repository elliptic-complex readiness verifier: PASS")
