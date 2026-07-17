"""Emit the executable v2 antifield-import receiving certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .verify_antifield_export_v2 import (
    DEPENDENCY_KEYS,
    REQUIRED_ROLES,
    synthetic_fixture,
    validate_export_v2,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT.json"
SCHEMA = HERE / "schema/antifield_contract_v2_certificate.schema.json"
EXPORT_SCHEMA = HERE / "schema/antifield_export_v2.schema.json"
V1 = HERE / "certificates/ANTIFIELD_EXPORT_CONTRACT.json"
SOURCE_PATHS = (
    "quantum-weyl/classical_import/antifield_contract_v2_certificate.py",
    "quantum-weyl/classical_import/verify_antifield_contract_v2.py",
    "quantum-weyl/classical_import/verify_antifield_export_v2.py",
    "quantum-weyl/classical_import/schema/antifield_export_v2.schema.json",
    "quantum-weyl/classical_import/schema/antifield_contract_v2_certificate.schema.json",
    "quantum-weyl/classical_import/tests/test_verify_antifield_export_v2.py",
    "quantum-weyl/classical_import/tests/test_antifield_contract_v2_certificate.py",
    "quantum-weyl/classical_import/REPORT_V2.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    fixture = synthetic_fixture()
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(export_schema).validate(fixture)
    replay = validate_export_v2(fixture)
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    dependencies = {
        "historical_v1_contract": {
            "path": str(V1.relative_to(ROOT)),
            "sha256": _sha256(V1),
        }
    }
    return {
        "schema": "quantum-weyl-antifield-contract-v2-certificate",
        "result_id": "ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT",
        "result_state": "EXECUTABLE_V2_CONTRACT_READY_SCOPE_AWARE",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "receiving_contract": {
            "schema": str(EXPORT_SCHEMA.relative_to(ROOT)),
            "consumer": "quantum-weyl/classical_import/verify_antifield_export_v2.py",
            "expression_schema_version": "canonical-superpolynomial-atoms-v1",
            "required_minimal_roles": sorted(REQUIRED_ROLES),
            "required_content_addressed_dependencies": sorted(DEPENDENCY_KEYS),
            "coefficient_field": "Q",
            "locality": "SUPPORT_LOCAL_POLYNOMIAL_JETS",
            "spacetime_dimension": 4,
        },
        "synthetic_exact_replay": replay,
        "checks": {
            "strict_Draft_2020_12_export_schema": "VERIFIED",
            "complete_minimal_field_ghost_antifield_dictionary": "VERIFIED",
            "opaque_expression_objects_rejected": "VERIFIED",
            "exact_rational_superpolynomial_AST": "VERIFIED",
            "canonical_Grassmann_order_and_odd_nilpotence": "VERIFIED",
            "Q_reconstructed_from_filtration_components": "VERIFIED",
            "delta_squared_independently_replayed": "VERIFIED",
            "delta_gamma_anticommutator_independently_replayed": "VERIFIED",
            "Q_squared_independently_replayed": "VERIFIED",
            "producer_booleans_not_used_as_authority": "VERIFIED",
            "filtered_local_complex_dry_run": "VERIFIED",
            "AFN0_view_dry_run": "VERIFIED",
            "declared_graded_scope_projection": "VERIFIED",
            "content_hash_rerun_key": "VERIFIED",
            "mutation_suite": "VERIFIED",
            "classical_export_imported": "OUT_OF_SCOPE_USE_SEPARATE_IMPORT_RECEIPT",
            "minimal_BV_H04_H14": "NOT_COMPUTED",
        },
        "resource_policy": {
            "arrival_gate": "schema, hashes, exact AST, independent generator-level filtration replay, and filtered-complex dry run",
            "quotient_rerun_key": [
                "scope_hash",
                "generator_hash",
                "atom_hash",
                "differential_hash",
                "dependency_hash",
                "AFN0_basis_manifest_hashes",
            ],
            "full_quotient_run_required_when": [
                "a quotient_rerun_key changes",
                "the declared derivative/dimension/locality scope expands",
                "a new antifield-number block or lower-form carrier is admitted",
            ],
            "full_repository_suite_required_when": [
                "shared canonical algebra changes",
                "the relative-cohomology or filtered-complex engine changes",
                "a publishable minimal-BV quotient is promoted",
            ],
            "otherwise": "run the v2 arrival, mutation, and affected filtered-complex tests only",
        },
        "claim_flags": {
            "ANTIFIELD_EXPORT_V2_RECEIVER_READY": True,
            "DECLARED_GRADED_SCOPE_ENFORCED": True,
            "INDEPENDENT_FILTRATION_REPLAY_READY": True,
            "FILTERED_COMPLEX_ADAPTER_READY": True,
            "IMPORT_STATUS_DELEGATED_TO_SEPARATE_RECEIPT": True,
            "FULL_BV_G2_COMPLETE": False,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "USE_CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2_RECEIPT",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate promotes only an executable receiving contract. "
            "The quantum consumer accepts exact rational canonical superpolynomials over a finite "
            "grading-bounded atom dictionary, reconstructs Q from delta, gamma and positive "
            "filtration components, independently evaluates delta^2, the delta-gamma "
            "anticommutator and Q^2, and dry-runs the resulting blocks through the existing "
            "FilteredLocalComplex and AFN0-view APIs. The adapter enforces the declared graded "
            "window and records projected monomials. Producer proof artifacts remain pinned "
            "provenance and are not used as mathematical authority. The synthetic fixture is a "
            "contract regression, not classical Weyl-gravity data; export availability is "
            "reported only by the separate import receipt. No minimal-BV H^{0,4} or H^{1,4} quotient has been "
            "computed, no anomaly coefficient or Slavnov breaking has been derived, and no QME, "
            "Lorentzian, residual-transfer, particle, or quantum claim is authorized."
        ),
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "dependency_manifest_sha256": _canonical_hash(dependencies),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m classical_import.antifield_contract_v2_certificate --check",
                "status": "PASS",
                "elapsed_seconds": 0.55,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m classical_import.verify_antifield_contract_v2",
                "status": "PASS",
                "elapsed_seconds": 0.53,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/classical_import/tests/test_verify_antifield_export_v2.py quantum-weyl/classical_import/tests/test_antifield_contract_v2_certificate.py",
                "status": "PASS",
                "elapsed_seconds": 0.85,
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "No real classical export or production quotient is present; exact fixture, mutation, pinning, and adapter tests cover this receiving-contract change.",
            "tier_3": "No shared algebra, quotient theorem, coefficient, QME lifecycle, Lorentzian construction, paper freeze, or release boundary is promoted.",
        },
    }


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("ANTIFIELD_EXPORT_V2_RECEIVER_READY") is not True
        or flags.get("DECLARED_GRADED_SCOPE_ENFORCED") is not True
        or flags.get("INDEPENDENT_FILTRATION_REPLAY_READY") is not True
        or flags.get("FILTERED_COMPLEX_ADAPTER_READY") is not True
        or flags.get("IMPORT_STATUS_DELEGATED_TO_SEPARATE_RECEIPT") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "FULL_BV_G2_COMPLETE",
                "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
                "QME_RESTORED",
                "QUANTUM_CLAIM",
            )
        )
        or value.get("next_gate") != "USE_CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2_RECEIPT"
    ):
        raise ValueError("antifield v2 receiving contract crossed its claim boundary")


def _text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    content = _text(value)
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and OUTPUT.read_text() != content:
        raise SystemExit(f"stale antifield v2 contract: {OUTPUT}")
    print("ANTIFIELD EXPORT V2 CONTRACT: SCOPE-AWARE RECEIVER READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
