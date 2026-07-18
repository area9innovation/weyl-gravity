"""Independent verifier for classical snapshot compatibility readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "certificates/CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS.json"
SCHEMA = HERE / "schema/classical-snapshot-compatibility-readiness-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify(value: dict | None = None) -> dict:
    if value is None:
        value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    receipt = value["receiver_mechanics"]["synthetic_receipt"]
    if (
        receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED"
        or receipt["matched_hash_count"] != 5
        or receipt["local_BV_commit"] == receipt["analytic_operator_commit"]
    ):
        raise ValueError("snapshot compatibility synthetic receipt drifted")
    mutations = value["receiver_mechanics"]["mutation_receipts"]
    if (
        {row["mutation"] for row in mutations}
        != {
            "analytic_differential_hash",
            "analytic_generator_hash",
            "wrong_local_commit",
            "bad_proof_hash",
        }
        or not all(row["rejected"] for row in mutations)
    ):
        raise ValueError("snapshot compatibility mutation battery drifted")
    dependency_hashes = value["dependency_hashes"]
    frozen_import = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
    input_schema = HERE / "schema/classical-snapshot-compatibility-input-v1.schema.json"
    if dependency_hashes != {
        "frozen_minimal_BV_import": _sha256(frozen_import),
        "input_schema": _sha256(input_schema),
    }:
        raise ValueError("snapshot compatibility readiness dependency drifted")
    proof_payload = {
        "frozen_import": _sha256(frozen_import),
        "input_schema": _sha256(input_schema),
        "contract": value["accepted_contract"],
        "receipt": receipt,
        "mutations": mutations,
    }
    if value["proof_sha256"] != _canonical_hash(proof_payload):
        raise ValueError("snapshot compatibility readiness proof digest drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"snapshot compatibility source drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent classical snapshot compatibility readiness verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
