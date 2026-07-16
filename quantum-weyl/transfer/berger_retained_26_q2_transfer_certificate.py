#!/usr/bin/env python3
"""Emit or validate the exact retained 26-row Berger q2 transfer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .berger_retained_26_q2_transfer import compute_retained_q2


ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "certificates" / "BERGER_RETAINED_26_Q2_TRANSFER.json"
PAYLOAD = ROOT / "certificates" / "BERGER_RETAINED_26_Q2_PAYLOAD.json"
Q2_REPLAY = ROOT / "certificates" / "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"
GAUGE_IMPORT = ROOT / "certificates" / "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"
OBSTRUCTION_IMPORT = (
    ROOT / "certificates" / "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION_IMPORT.json"
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "berger_retained_26_q2_transfer.py",
        "berger_retained_26_q2_transfer_certificate.py",
        "schema/berger-retained-26-q2-transfer-v1.schema.json",
        "schema/berger-retained-26-q2-payload-v1.schema.json",
        "tests/test_berger_retained_26_q2_transfer.py",
        "../reports/berger-retained-26-q2-transfer.md",
        "README.md",
    )
    return {path: _hash(ROOT / path) for path in paths}


def build_certificate() -> tuple[dict[str, Any], dict[str, Any]]:
    q2_replay = json.loads(Q2_REPLAY.read_text(encoding="utf-8"))
    gauge = json.loads(GAUGE_IMPORT.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION_IMPORT.read_text(encoding="utf-8"))
    if (
        q2_replay.get("replay", {}).get("all_identities_pass") is not True
        or gauge.get("coverage", {}).get("retained_rows") != 26
        or obstruction.get("claim_flags", {}).get(
            "BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"
        )
        is not True
    ):
        raise ValueError("retained q2 transfer prerequisites drifted")
    payload, transfer = compute_retained_q2()
    manifest = _source_manifest()
    certificate = {
        "schema": "quantum-weyl-berger-retained-26-q2-transfer-v1",
        "result_id": "BERGER_RETAINED_26_Q2_TRANSFER",
        "result_state": "RETAINED_26_ROW_Q2_TRANSFERRED_IDENTITIES_VERIFIED_FURTHER_RESIDUAL_TRANSFER_PENDING",
        "lifecycle_layer": "CLASSICAL_BV_TRANSFER",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "input_certificates": {
            str(Q2_REPLAY.relative_to(REPOSITORY_ROOT)): _hash(Q2_REPLAY),
            str(GAUGE_IMPORT.relative_to(REPOSITORY_ROOT)): _hash(GAUGE_IMPORT),
            str(OBSTRUCTION_IMPORT.relative_to(REPOSITORY_ROOT)): _hash(
                OBSTRUCTION_IMPORT
            ),
        },
        "payload": {
            "path": str(PAYLOAD.relative_to(REPOSITORY_ROOT)),
            "file_sha256": "PENDING_FILE_HASH",
            "canonical_sha256": payload["canonical_sha256"],
        },
        "transfer": transfer,
        "claim_flags": {
            "CLASSICAL_RETAINED_26_Q2_TRANSFERRED": True,
            "RETAINED_Q1_Q2_IDENTITIES_VERIFIED": True,
            "MINIMAL_RESIDUAL_ELL2_COMPUTED": False,
            "BARE_D_CARTAN_RESTORED": False,
            "RESIDUAL_BFV_EXTENSION_COMPUTED": False,
            "LORENTZIAN_CAUSAL_EXTENSION_COMPUTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gates": [
            "CHARACTERISTIC_SYMBOL_COHOMOLOGY_MODULE",
            "RESIDUAL_BFV_OR_LORENTZIAN_CAUSAL_EXTENSION",
        ],
        "consumer_provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC result transfers the complete classical 54-row "
            "Berger q2 through the exact 54-to-26 SDR and verifies the retained "
            "q1/q2 and odd-Darboux cyclic identities over Q(sqrt(10)). The output "
            "q2_26 is an operation on the retained complex, not yet a minimal "
            "residual/cohomology ell2. It does not bypass the bare unary D-Cartan "
            "obstruction, construct a BFV or causal extension, restore a QME, or "
            "make a quantum claim."
        ),
    }
    return payload, certificate


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _render_payload(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def emit() -> None:
    payload, certificate = build_certificate()
    PAYLOAD.write_text(_render_payload(payload), encoding="utf-8")
    certificate["payload"]["file_sha256"] = _hash(PAYLOAD)
    OUTPUT.write_text(_render(certificate), encoding="utf-8")


def validate_checked_receipt() -> dict[str, Any]:
    if not OUTPUT.exists() or not PAYLOAD.exists():
        raise ValueError("missing retained q2_26 transfer receipt")
    certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    manifest = _source_manifest()
    if (
        certificate.get("result_state")
        != "RETAINED_26_ROW_Q2_TRANSFERRED_IDENTITIES_VERIFIED_FURTHER_RESIDUAL_TRANSFER_PENDING"
        or certificate.get("payload", {}).get("file_sha256") != _hash(PAYLOAD)
        or certificate.get("payload", {}).get("canonical_sha256")
        != payload.get("canonical_sha256")
        or payload.get("canonical_sha256")
        != _canonical_hash({key: value for key, value in payload.items() if key != "canonical_sha256"})
        or certificate.get("consumer_provenance", {}).get("source_manifest")
        != manifest
        or certificate.get("consumer_provenance", {}).get("source_manifest_sha256")
        != _canonical_hash(manifest)
        or any(
            certificate.get("input_certificates", {}).get(
                str(path.relative_to(REPOSITORY_ROOT))
            )
            != _hash(path)
            for path in (Q2_REPLAY, GAUGE_IMPORT, OBSTRUCTION_IMPORT)
        )
        or not all(certificate.get("transfer", {}).get("exact_checks", {}).values())
    ):
        raise ValueError("retained q2_26 transfer receipt drifted")
    return certificate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--replay-check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit()
    if args.check:
        validate_checked_receipt()
    if args.replay_check:
        payload, certificate = build_certificate()
        expected_payload = _render_payload(payload)
        if PAYLOAD.read_text(encoding="utf-8") != expected_payload:
            raise SystemExit("stale retained q2_26 payload")
        certificate["payload"]["file_sha256"] = hashlib.sha256(
            expected_payload.encode()
        ).hexdigest()
        if OUTPUT.read_text(encoding="utf-8") != _render(certificate):
            raise SystemExit("stale retained q2_26 certificate")
    if not args.emit and not args.check and not args.replay_check:
        print(_render(validate_checked_receipt()), end="")
    else:
        print("BERGER RETAINED q2_26: EXACT TRANSFER PASS; FURTHER RESIDUAL TRANSFER OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
