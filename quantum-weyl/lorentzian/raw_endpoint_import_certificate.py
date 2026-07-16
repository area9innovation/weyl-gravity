#!/usr/bin/env python3
"""Emit/check the pinned corrected raw Berger endpoint import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from local_bv.schema_validation import validate_instance

from .raw_endpoint_import import (
    CLASSICAL_COMMIT,
    LORENTZIAN_ROOT,
    SETTING_ID,
    evaluate_raw_endpoint,
    fast_receipt,
    source_artifacts,
)


OUTPUT = (
    LORENTZIAN_ROOT
    / "certificates"
    / "BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"
)
SCHEMA = (
    LORENTZIAN_ROOT / "schema" / "berger-raw-endpoint-import-v1.schema.json"
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _scientific_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "independent_exact_checks": {
            "source_schemas_strict_and_valid": True,
            "artifact_file_and_internal_hashes_match": True,
            "F12_C12_and_C12_F12_equal_identity": True,
            "full_34_row_coordinate_roundtrip_exact": True,
            "coordinate_transport_BV_canonical": True,
            "transported_q34_reproduces_dressed_unary_complex": True,
            "raw_q34_squared_zero": True,
            "raw_q34_cyclic": True,
            "raw_W34_cyclic": True,
            "raw_P34_equals_q34W34_plus_W34q34": True,
            "raw_pairing34_nondegenerate": True,
            "four_principal_identity_blocks_exact": True,
            "clock_order_four_diagonal_zero": True,
            "metric_to_clock_order_four_rank_one": True,
            "clock_full_diagonal_equals_I2": True,
            "Schur_correction_nonzero_order_six": True,
            "Schur_correction_wave_divisible": True,
            "wave_divided_Schur_symbol_rank_one": True,
        },
        "coordinate_hashes": result["coordinate_hashes"],
        "operator_hashes": result["operator_hashes"],
        "raw_principal_audit": {
            "comparison_covector": [1, 0, 0, 0],
            "ghost_block": "I5",
            "metric_block": "I10",
            "metric_antifield_block": "I10",
            "identity_block": "I5",
            "clock_diagonal_order_four_rank": 0,
            "metric_to_clock_order_four_rank": 1,
        },
        "filtered_endpoint_preflight": {
            "layout": "raw_metric_10 plus contractible_clock_2",
            "differential_orders": result["orders"],
            "order_six_polynomial_gcd": result["schur_gcd"],
            "rank_fixtures": result["schur_ranks"],
            "interpretation": "rank-one wave-divisible gauge/clock extension",
        },
    }


def _validate_scientific_payload(payload: object, receipt: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != {
        "independent_exact_checks",
        "coordinate_hashes",
        "operator_hashes",
        "raw_principal_audit",
        "filtered_endpoint_preflight",
    }:
        raise ValueError("raw endpoint scientific replay fields drifted")
    checks = payload["independent_exact_checks"]
    if not isinstance(checks, dict) or len(checks) != 18 or not all(
        value is True for value in checks.values()
    ):
        raise ValueError("raw endpoint scientific checks were weakened")
    if payload["coordinate_hashes"] != receipt["coordinate_hashes"]:
        raise ValueError("raw endpoint coordinate hashes drifted")
    if payload["operator_hashes"] != receipt["operator_hashes"]:
        raise ValueError("raw endpoint operator hashes drifted")
    if payload["raw_principal_audit"] != {
        "comparison_covector": [1, 0, 0, 0],
        "ghost_block": "I5",
        "metric_block": "I10",
        "metric_antifield_block": "I10",
        "identity_block": "I5",
        "clock_diagonal_order_four_rank": 0,
        "metric_to_clock_order_four_rank": 1,
    }:
        raise ValueError("raw endpoint principal audit drifted")
    filtered = payload["filtered_endpoint_preflight"]
    if (
        filtered.get("layout") != "raw_metric_10 plus contractible_clock_2"
        or filtered.get("differential_orders")
        != {
            "A_metric": 4,
            "B_clock_to_metric": 2,
            "C_metric_to_clock": 4,
            "D_clock": 0,
            "BC_schur_correction": 6,
        }
        or filtered.get("rank_fixtures")
        != {"timelike": 1, "spacelike": 1, "null": 0, "generic": 1}
        or filtered.get("interpretation")
        != "rank-one wave-divisible gauge/clock extension"
    ):
        raise ValueError("raw endpoint filtered preflight drifted")
    return payload


def _manifest() -> dict[str, str]:
    paths = (
        "raw_endpoint_import.py",
        "raw_endpoint_import_certificate.py",
        "schema/berger-raw-endpoint-import-v1.schema.json",
        "tests/test_raw_endpoint_import.py",
        "../reports/berger-raw-endpoint-import.md",
        "README.md",
        "../README.md",
    )
    return {path: _hash(LORENTZIAN_ROOT / path) for path in paths}


def build_certificate(
    scientific_replay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    receipt = fast_receipt()
    if scientific_replay is None:
        if not OUTPUT.exists():
            raise ValueError("raw endpoint certificate absent; run --emit")
        scientific_replay = json.loads(OUTPUT.read_text())["scientific_replay"]
    replay = _validate_scientific_payload(scientific_replay, receipt)
    manifest = _manifest()
    return {
        "schema": "quantum-weyl-berger-raw-endpoint-import-v1",
        "result_id": "BERGER_RAW_ENDPOINT_INPUT_IMPORT",
        "result_state": "RAW_ENDPOINT_IMPORTED_EXACT_REPLAY_FILTERED_GREEN_EXTENSION_OPEN",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "coverage": {
            "total_rows": 34,
            "degree_ranks": [5, 12, 12, 5],
            "coordinate_presentation": "RAW_CLOCK_REATTACHED",
            "coefficient_domain": "EXACT_Q(alpha_B,u,v)_PBW",
        },
        "scientific_replay": replay,
        "input_gate_update": {
            "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT": "IMPORTED_AND_EXACTLY_REPLAYED",
            "BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT": "IMPORTED_AND_EXACTLY_REPLAYED",
            "BERGER_RAW_ENDPOINT_FILTERED_GREEN_EXTENSION": "NOT_CONSTRUCTED",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": "NOT_CONSTRUCTED",
            "BERGER_HADAMARD_DATA": "NOT_CONSTRUCTED",
        },
        "principal_compatibility_certified": True,
        "filtered_extension_preflight_certified": True,
        "green_execution_authorized": False,
        "quantum_execution_authorized": False,
        "next_gate": "CONSTRUCT_RANK_ONE_WAVE_FILTERED_GREEN_EXTENSION_FOR_RAW_ENDPOINT",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "artifacts": source_artifacts(),
        },
        "consumer_provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
            "fast_check_command": (
                "PYTHONPATH=quantum-weyl python3 -m "
                "lorentzian.raw_endpoint_import_certificate --check"
            ),
            "scientific_replay_command": (
                "PYTHONPATH=quantum-weyl python3 -m "
                "lorentzian.raw_endpoint_import_certificate --replay-check"
            ),
        },
        "claim_boundary": (
            "Pins and independently replays the corrected raw 34-row Berger "
            "endpoint, its exact cyclic witness identities, BV-canonical "
            "coordinate transport, principal identity blocks, and the rank-one "
            "wave-divisible Schur preflight. The LORENTZIAN-CAUSAL tag records "
            "the target support category only. No filtered Green extension, "
            "advanced/retarded inverse, causal support theorem, retained 26-row "
            "Green homotopy, Hadamard state, QME, or quantum claim is constructed."
        ),
    }


def _validate_schema(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"raw endpoint import failed strict schema: {errors}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--replay-check", action="store_true")
    args = parser.parse_args()
    if sum((args.emit, args.refresh, args.check, args.replay_check)) > 1:
        raise SystemExit("choose at most one mode")
    if args.emit or args.replay_check:
        scientific = _scientific_payload(evaluate_raw_endpoint())
    else:
        scientific = None
    payload = build_certificate(scientific)
    _validate_schema(payload)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.emit or args.refresh:
        OUTPUT.write_text(content, encoding="utf-8")
    if (args.check or args.replay_check) and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale raw endpoint import certificate: {OUTPUT}")
    if not args.emit and not args.refresh and not args.check and not args.replay_check:
        print(content, end="")
    else:
        mode = (
            "SCIENTIFIC REPLAY"
            if args.emit or args.replay_check
            else "FAST RECEIPT REFRESH"
            if args.refresh
            else "FAST RECEIPT"
        )
        print(f"BERGER RAW ENDPOINT IMPORT: {mode} PASS; GREEN EXTENSION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
