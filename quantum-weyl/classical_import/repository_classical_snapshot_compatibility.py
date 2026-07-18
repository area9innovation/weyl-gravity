"""Emit the physical cross-commit classical-snapshot compatibility bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .classical_snapshot_compatibility_receiver import (
    REQUIRED_ROLES,
    SCHEMA,
    validate_classical_snapshot_compatibility,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL_IMPORT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
ATTRIBUTION = HERE / "certificates/ANALYTIC_OPERATOR_CLASSICAL_SNAPSHOT_ATTESTATION.json"
OUTPUT = HERE / "certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path) -> dict[str, str]:
    return {
        "format": "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    local = json.loads(LOCAL_IMPORT.read_text())
    attribution = json.loads(ATTRIBUTION.read_text())
    local_commit = local["classical_commit"]
    analytic_commit = attribution["analytic_producer_commit"]
    hashes = local["independent_replay"]["canonical_hashes"]
    value = {
        "schema": "quantum-weyl-classical-snapshot-compatibility-input-v1",
        "result_id": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
        "result_state": "LOCAL_BV_CONTENT_HASHES_EQUAL_ACROSS_DISTINCT_COMMITS",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "local_BV_snapshot": {
            "classical_commit": local_commit,
            "canonical_hashes": hashes,
        },
        "analytic_operator_snapshot": {
            "classical_commit": analytic_commit,
            "canonical_hashes": hashes,
        },
        "matched_roles": REQUIRED_ROLES,
        "compatibility": {
            "status": "CONTENT_HASH_COMPATIBLE",
            "all_declared_hashes_equal": True,
            "semantic_receiver_replayed": True,
        },
        "proof_artifacts": [_artifact(LOCAL_IMPORT), _artifact(ATTRIBUTION)],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC compatibility bridge proves that the accepted "
            "analytic producer commit and frozen local-BV quotient use identical "
            "minimal generator, local atom, classical differential, dependency, "
            "grading, and locality content. The analytic side is established by "
            "exact Git-tree attribution of the producer to the frozen classical "
            "export. It does not compute a C2 coefficient, regulated Slavnov "
            "breaking, QME disposition, residual transfer, or Lorentzian theory."
        ),
    }
    validate_classical_snapshot_compatibility(
        value,
        repository_root=ROOT,
        expected_local_commit=local_commit,
        expected_local_hashes=hashes,
        expected_analytic_commit=analytic_commit,
    )
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale physical snapshot compatibility bridge: {OUTPUT}")
    print("repository classical snapshot compatibility: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
