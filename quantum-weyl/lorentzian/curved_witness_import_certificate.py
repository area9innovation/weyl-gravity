#!/usr/bin/env python3
"""Emit the pinned exact import of the Berger 34-row curved witness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from local_bv.schema_validation import validate_instance

from .curved_witness_adapter import (
    EXPORT_SCHEMA_ID,
    ROOT,
    evaluate_curved_witness_export,
)


LORENTZIAN_ROOT = Path(__file__).resolve().parent
OUTPUT = (
    LORENTZIAN_ROOT
    / "certificates"
    / "BERGER_CURVED_CLOCK_REATTACHED_WITNESS_IMPORT.json"
)
SCHEMA = (
    LORENTZIAN_ROOT
    / "schema"
    / "berger-curved-witness-import-v1.schema.json"
)
EXPORT_COMMIT = "96c28b554f1d1eb548edb2b12def0a9ff853473b"
EXPORT_CERTIFICATE = (
    "d_quotient_classical/certificates/"
    "BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json"
)
EXPORT_ARTIFACTS = (
    EXPORT_CERTIFICATE,
    "d_quotient_classical/generated/berger_curved_clock_reattached_witness/W34.json",
    "d_quotient_classical/generated/berger_curved_clock_reattached_witness/P34.json",
    "d_quotient_classical/generated/berger_curved_clock_reattached_witness/pairing34.json",
    "d_quotient_classical/backreacted_clock/berger_curved_witness_export.py",
    "d_quotient_classical/reports/berger-curved-clock-reattached-witness.md",
)


def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{EXPORT_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"missing pinned curved-witness export artifact: {relative}")
    return result.stdout


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": EXPORT_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_import() -> dict[str, Any]:
    payload = json.loads(_git_blob(EXPORT_CERTIFICATE))
    export_schema = json.loads(
        (LORENTZIAN_ROOT / "schema" / "berger-curved-witness-export-v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    errors = validate_instance(payload, export_schema)
    if errors:
        raise ValueError(f"pinned curved-witness export failed schema validation: {errors}")
    if payload.get("schema") != EXPORT_SCHEMA_ID:
        raise ValueError("pinned curved-witness export schema identity drifted")

    with tempfile.TemporaryDirectory() as directory:
        repository_root = Path(directory)
        for artifact in payload["operators"].values():
            relative = artifact["path"]
            destination = repository_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_git_blob(relative))
        verdict = evaluate_curved_witness_export(
            payload,
            repository_root=repository_root,
        )

    if verdict["verdict"] != "ADMISSIBLE_EXACT_CURVED_WITNESS":
        raise ValueError(f"curved-witness import did not pass: {verdict['verdict']}")
    if not verdict["curved_witness_certified"] or verdict["green_execution_authorized"]:
        raise ValueError("curved-witness lifecycle boundary drifted")

    return {
        "schema": "quantum-weyl-berger-curved-witness-import-v1",
        "result_id": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS_IMPORT",
        "result_state": "CURVED_34_ROW_WITNESS_IMPORTED_AND_EXACTLY_REPLAYED_GREEN_OPEN",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": verdict["setting_id"],
        "coverage": {
            "total_rows": 34,
            "degree_ranks": [5, 12, 12, 5],
            "coefficient_domain": "EXACT_RATIONAL_PBW",
        },
        "independent_exact_checks": {
            "export_schema_valid": True,
            "coordinate_transport_hashes_match": True,
            "q34_nilpotent": True,
            "pairing34_nondegenerate": True,
            "q34_cyclic": True,
            "q34_W34_plus_W34_q34_equals_P34": True,
            "W34_cyclic": True,
        },
        "exact_primitive": verdict["exact_primitive"],
        "obstruction_witness": None,
        "input_gate_update": {
            "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": "IMPORTED_AND_EXACTLY_REPLAYED",
            "BERGER_CAUSAL_GREEN_HOMOTOPY": "NOT_CONSTRUCTED",
            "BERGER_HADAMARD_DATA": "NOT_CONSTRUCTED",
        },
        "curved_witness_certified": True,
        "green_execution_authorized": False,
        "quantum_execution_authorized": False,
        "next_gate": "CONSTRUCT_ADVANCED_RETARDED_GREEN_OPERATORS_FOR_P34_WITH_CAUSAL_SUPPORT_AND_CYCLIC_ADJOINTNESS",
        "provenance": {
            "export_commit": EXPORT_COMMIT,
            "generator_classical_commit": payload["classical_commit"],
            "artifacts": [_artifact(path) for path in EXPORT_ARTIFACTS],
        },
        "claim_boundary": (
            "Pins and independently replays the authoritative 34-row curved BV "
            "witness, including the nondegenerate pairing and cyclic q34/W34 "
            "identities. The LORENTZIAN-CAUSAL tag records the geometric target, "
            "not a causal theorem: no advanced or retarded inverse, support "
            "property, Hadamard state, time-ordered product, or Lorentzian QME is "
            "constructed."
        ),
    }


def build_certificate() -> dict[str, Any]:
    result = build_import()
    paths = (
        "curved_witness_adapter.py",
        "curved_witness_import_certificate.py",
        "schema/berger-curved-witness-export-v1.schema.json",
        "schema/berger-curved-witness-import-v1.schema.json",
        "tests/test_curved_witness_import.py",
        "../reports/berger-curved-witness-adapter.md",
        "README.md",
    )
    manifest = {path: _hash(LORENTZIAN_ROOT / path) for path in paths}
    result["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale curved-witness import certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CURVED WITNESS IMPORTED AND EXACTLY REPLAYED; GREEN GATE OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
