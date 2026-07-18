"""Independent verifier for the nonconformal coefficient receiver readiness."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from .nonconformal_coefficient_match_readiness import (
    DEPENDENCIES,
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(checked)
    if checked != build():
        raise ValueError("nonconformal coefficient readiness does not reproduce")
    if checked["dependency_hashes"] != {
        name: _sha256(path) for name, path in DEPENDENCIES.items()
    }:
        raise ValueError("nonconformal coefficient dependency hash drifted")
    if any(
        row["C2_visible"]
        and row["repository_operator"]
        and row["Euclidean_elliptic_full_BV"]
        and row["measure_and_regulator"]
        and row["coefficient_vector"]
        for row in checked["current_candidate_audit"]
    ):
        raise ValueError("an eligible current C2 carrier was incorrectly rejected")
    for path, digest in checked["provenance"]["source_sha256"].items():
        if _sha256(ROOT / path) != digest:
            raise ValueError(f"nonconformal coefficient source drifted: {path}")
    return checked


if __name__ == "__main__":
    verify()
    print("independent nonconformal coefficient readiness verifier: PASS")
