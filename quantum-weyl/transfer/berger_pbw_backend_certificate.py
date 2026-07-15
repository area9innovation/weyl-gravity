#!/usr/bin/env python3
"""Emit or check the registered Berger PBW operator-backend certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_pbw_backend import (
        BACKEND_ID,
        EXPRESSION_SCHEMA_VERSION,
        build_operator_backend_registry,
    )
except ImportError:
    from berger_pbw_backend import (
        BACKEND_ID,
        EXPRESSION_SCHEMA_VERSION,
        build_operator_backend_registry,
    )


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
INPUT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_RETAINED_MINIMAL_Q1_IMPORT.json"
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_PBW_OPERATOR_BACKEND.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "operator_backend_registry.py",
        "berger_pbw_backend.py",
        "berger_pbw_backend_certificate.py",
        "schema/berger-pbw-operator-backend-v1.schema.json",
        "tests/test_berger_pbw_backend.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    registry = build_operator_backend_registry(repository_root=ROOT)
    descriptor = registry.descriptor(BACKEND_ID)
    verified = registry.validate(
        BACKEND_ID,
        EXPRESSION_SCHEMA_VERSION,
        payload,
        required_arity=1,
    )
    manifest = _source_manifest()
    return {
        "schema": "quantum-weyl-berger-pbw-operator-backend-v1",
        "result_id": "BERGER_PBW_OPERATOR_BACKEND",
        "result_state": "ARITY_ONE_OPERATOR_BACKEND_READY_ND2_ASSEMBLY_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "descriptor": descriptor.to_payload(),
        "verified_import": {
            "path": "quantum-weyl/transfer/certificates/BERGER_RETAINED_MINIMAL_Q1_IMPORT.json",
            "sha256": _sha256(INPUT_PATH),
            "result_id": verified.result_id,
            "retained_rows": verified.retained_rows,
            "block_hashes": dict(verified.block_hashes),
            "pbw_term_count": verified.pbw_term_count,
            "maximum_differential_order": verified.maximum_differential_order,
        },
        "nd2_compatibility": {
            "operator_backend_registered": True,
            "supported_arities": [1],
            "finite_cartan_evaluator_registered": False,
            "assembly_adapter_registered": False,
            "physical_execution_authorized": False,
            "blocker": "COEFFICIENT_DOMAIN_AND_ARITY_MISMATCH",
            "reason": (
                "The retained q1 is PBW-operator-valued over Q[alpha_B,u,v], while "
                "the current ND2 finite Cartan engine is Fraction-valued and also "
                "requires q2, D, contraction, and admissibility inputs."
            ),
            "allowed_routes": [
                "extend ND2 to a declared PBW-module-valued Cartan complex",
                "provide an exact finite specialization tagged REDUCED-MODE",
            ],
        },
        "provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
            "schema": "quantum-weyl/transfer/schema/berger-pbw-operator-backend-v1.schema.json",
        },
        "claim_boundary": (
            "This certificate registers an exact arity-one LOCAL-ALGEBRAIC operator "
            "backend for the imported retained Berger q1. It does not register a "
            "Fraction-valued physical evaluator or assembly adapter, does not supply "
            "q2, D, contraction, or admissibility data, and authorizes no ND2 run."
        ),
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"Berger PBW operator-backend certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER PBW BACKEND: ARITY ONE READY, ND2 ASSEMBLY BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
