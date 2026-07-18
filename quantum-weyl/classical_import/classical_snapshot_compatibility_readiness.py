"""Readiness certificate for cross-commit classical snapshot compatibility."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

try:
    from .classical_snapshot_compatibility_receiver import (
        HASH_KEYS,
        SCHEMA as INPUT_SCHEMA,
        synthetic_payload,
        validate_classical_snapshot_compatibility,
    )
except ImportError:
    from classical_snapshot_compatibility_receiver import (
        HASH_KEYS,
        SCHEMA as INPUT_SCHEMA,
        synthetic_payload,
        validate_classical_snapshot_compatibility,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN_IMPORT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
OUTPUT = HERE / "certificates/CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS.json"
SCHEMA = HERE / "schema/classical-snapshot-compatibility-readiness-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/classical_import/classical_snapshot_compatibility_receiver.py",
    "quantum-weyl/classical_import/classical_snapshot_compatibility_readiness.py",
    "quantum-weyl/classical_import/verify_classical_snapshot_compatibility_readiness.py",
    "quantum-weyl/classical_import/schema/classical-snapshot-compatibility-input-v1.schema.json",
    "quantum-weyl/classical_import/schema/classical-snapshot-compatibility-readiness-v1.schema.json",
    "quantum-weyl/classical_import/tests/test_classical_snapshot_compatibility.py",
    "quantum-weyl/reports/classical-snapshot-compatibility-receiver-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _frozen_snapshot() -> tuple[str, dict[str, str]]:
    value = json.loads(FROZEN_IMPORT.read_text())
    hashes = value.get("independent_replay", {}).get("canonical_hashes", {})
    if set(hashes) != set(HASH_KEYS):
        raise ValueError("frozen minimal-BV canonical hashes drifted")
    return value["classical_commit"], hashes


def _rejects(
    payload: dict[str, Any], local_commit: str, hashes: dict[str, str]
) -> bool:
    try:
        validate_classical_snapshot_compatibility(
            payload,
            repository_root=ROOT,
            expected_local_commit=local_commit,
            expected_local_hashes=hashes,
            expected_analytic_commit="1" * 40,
            allow_synthetic_fixture=True,
        )
    except Exception:
        return True
    return False


def mutation_receipts(
    payload: dict[str, Any], local_commit: str, hashes: dict[str, str]
) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
        (
            "analytic_differential_hash",
            lambda row: row["analytic_operator_snapshot"]["canonical_hashes"].update(
                differential_hash="0" * 64
            ),
        ),
        (
            "analytic_generator_hash",
            lambda row: row["analytic_operator_snapshot"]["canonical_hashes"].update(
                generator_hash="0" * 64
            ),
        ),
        (
            "wrong_local_commit",
            lambda row: row["local_BV_snapshot"].update(classical_commit="2" * 40),
        ),
        (
            "bad_proof_hash",
            lambda row: row["proof_artifacts"][0].update(sha256="0" * 64),
        ),
    )
    receipts = []
    for name, mutate in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        receipts.append(
            {"mutation": name, "rejected": _rejects(mutant, local_commit, hashes)}
        )
    return receipts


def build() -> dict[str, Any]:
    local_commit, hashes = _frozen_snapshot()
    analytic_commit = "1" * 40
    fixture = synthetic_payload(
        local_commit=local_commit,
        analytic_commit=analytic_commit,
        canonical_hashes=hashes,
    )
    receipt = validate_classical_snapshot_compatibility(
        fixture,
        repository_root=ROOT,
        expected_local_commit=local_commit,
        expected_local_hashes=hashes,
        expected_analytic_commit=analytic_commit,
        allow_synthetic_fixture=True,
    )
    mutations = mutation_receipts(fixture, local_commit, hashes)
    if (
        receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED"
        or not all(row["rejected"] for row in mutations)
    ):
        raise AssertionError("snapshot compatibility receiver mutation battery failed")
    contract = {
        "required_result_id": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
        "input_schema_path": str(INPUT_SCHEMA.relative_to(ROOT)),
        "frozen_local_BV_commit": local_commit,
        "required_canonical_hash_keys": list(HASH_KEYS),
        "required_physical_proof_roles": [
            "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
            "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
        ],
        "physical_input_status": "NOT_SUPPLIED",
    }
    proof_payload = {
        "frozen_import": _sha256(FROZEN_IMPORT),
        "input_schema": _sha256(INPUT_SCHEMA),
        "contract": contract,
        "receipt": receipt,
        "mutations": mutations,
    }
    value = {
        "schema": "quantum-weyl-classical-snapshot-compatibility-readiness-v1",
        "result_id": "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READINESS",
        "result_state": "CONTENT_HASH_COMPATIBILITY_RECEIVER_READY_PHYSICAL_BRIDGE_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": local_commit,
        "frozen_canonical_hashes": hashes,
        "dependency_hashes": {
            "frozen_minimal_BV_import": _sha256(FROZEN_IMPORT),
            "input_schema": _sha256(INPUT_SCHEMA),
        },
        "accepted_contract": contract,
        "receiver_mechanics": {
            "scope": "SYNTHETIC_DISTINCT_COMMIT_EQUAL_HASH_MECHANICS_ONLY",
            "synthetic_receipt": receipt,
            "mutation_receipts": mutations,
        },
        "claim_flags": {
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY": True,
            "GENERATOR_ATOM_DIFFERENTIAL_DEPENDENCY_SCOPE_HASHES_ENFORCED": True,
            "DISTINCT_COMMITS_REQUIRE_CONTENT_PROOF": True,
            "PHYSICAL_COMPATIBILITY_BRIDGE_SUPPLIED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY_IF_ANALYTIC_COMMIT_DIFFERS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC readiness artifact supplies a strict semantic "
            "receiver for cross-commit compatibility between the frozen local-BV "
            "snapshot and a later analytic-operator snapshot. It enforces exact "
            "equality of generator, atom, differential, dependency, and scope "
            "hashes and requires role-specific content-addressed import and export "
            "proofs on the physical path. The synthetic distinct-commit fixture "
            "tests mechanics only and does not certify an absent analytic producer. "
            "No physical compatibility bridge, multiplicity ledger, Slavnov "
            "breaking, QME disposition, residual transfer, or Lorentzian quantum "
            "theory is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(
        flags.get(name) is True
        for name in (
            "CLASSICAL_SNAPSHOT_COMPATIBILITY_RECEIVER_READY",
            "GENERATOR_ATOM_DIFFERENTIAL_DEPENDENCY_SCOPE_HASHES_ENFORCED",
            "DISTINCT_COMMITS_REQUIRE_CONTENT_PROOF",
        )
    ) or any(
        flags.get(name) is not False
        for name in (
            "PHYSICAL_COMPATIBILITY_BRIDGE_SUPPLIED",
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
            "REGULATED_SLAVNOV_BREAKING_COMPUTED",
            "QME_DISPOSITION",
        )
    ):
        raise ValueError("snapshot compatibility readiness crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale snapshot compatibility readiness: {OUTPUT}")
    print("classical snapshot compatibility receiver readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
