"""Emit the machine contract for a future classical antifield export."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


IMPORT_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = IMPORT_ROOT / "certificates" / "ANTIFIELD_EXPORT_CONTRACT.json"


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "antifield_contract_certificate.py",
        "verify_antifield_export.py",
        "schema/antifield_export.schema.json",
        "tests/test_antifield_contract_certificate.py",
        "tests/test_verify_antifield_export.py",
    )
    return {
        path: hashlib.sha256((IMPORT_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    required_generator_fields = [
        "symbol",
        "tensor_type",
        "ghost_number",
        "antifield_number",
        "form_degree",
        "Grassmann_parity",
        "mass_dimension",
        "Weyl_weight",
        "Q_image",
        "canonical_index_symmetry",
        "equation_or_identity_row",
    ]
    source_manifest = _source_manifest()
    return {
        "result_id": "ANTIFIELD_EXPORT_CONTRACT",
        "result_state": "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "schema": "quantum-weyl/classical_import/schema/antifield_export.schema.json",
        "preflight": "quantum-weyl/classical_import/verify_antifield_export.py",
        "required_minimal_roles": [
            "metric_antifield",
            "diffeomorphism_ghost_antifield",
            "weyl_ghost_antifield",
        ],
        "required_generator_fields": required_generator_fields,
        "required_filtration_rows": {
            "delta": {"antifield_number_shift": -1},
            "gamma": {"antifield_number_shift": 0},
            "Q_gt0": {
                "component_count": "ZERO_OR_MORE",
                "minimum_antifield_number_shift": 1,
                "distinct_shifts_required": True,
            },
        },
        "required_filtration_checks": [
            "delta_squared_zero",
            "delta_gamma_anticommutator_zero",
            "Q_decomposition_sums_to_Q_image",
            "Q_squared_zero",
        ],
        "checks": {
            "exact_required_field_set": "ENFORCED",
            "minimal_antifield_metadata": "ENFORCED",
            "no_floating_point_payloads": "ENFORCED",
            "filtration_degree_rows": "ENFORCED",
            "proof_artifact_inventory": "ENFORCED",
            "pinned_proof_artifact_integrity": "ENFORCED_WHEN_REPOSITORY_ROOT_SUPPLIED",
            "canonical_hash_reproduction": "ENFORCED",
            "classical_export_imported": "NOT_AVAILABLE",
            "filtration_identities_independently_reverified": "NOT_COMPUTED",
        },
        "canonical_hashes": {
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "required_generator_fields_sha256": _canonical_hash(required_generator_fields),
        },
        "assumptions": [
            "This is a format and exactness preflight, not an independent proof of the exported Q rows.",
            "Gate A remains fail-closed until a pinned classical export passes this preflight and the quantum repository independently evaluates the filtration identities.",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"antifield export contract is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ANTIFIELD EXPORT CONTRACT: EXACT PREFLIGHT READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
