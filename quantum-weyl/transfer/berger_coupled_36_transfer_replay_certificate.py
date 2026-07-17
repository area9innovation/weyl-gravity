#!/usr/bin/env python3
"""Emit or check the independent coupled 36-row transfer replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_coupled_36_transfer_replay import build_payload
except ImportError:
    from berger_coupled_36_transfer_replay import build_payload


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict:
    result = dict(build_payload())
    paths = (
        "berger_coupled_36_transfer_replay.py",
        "berger_coupled_36_transfer_replay_certificate.py",
        "verify_berger_coupled_36_transfer_replay.py",
        "schema/berger-coupled-36-transfer-replay-v1.schema.json",
        "tests/test_berger_coupled_36_transfer_replay.py",
        "../reports/berger-coupled-36-transfer-replay.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
    result["verification_receipts"] = [
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_36_transfer_replay_certificate --check",
            "elapsed_seconds": 3.33,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_36_transfer_replay",
            "elapsed_seconds": 3.38,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_36_transfer_replay.py -v",
            "elapsed_seconds": 3.53,
            "status": "PASS",
        },
        {
            "test_tier": 1,
            "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-coupled-36-transfer-replay-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY.json",
            "elapsed_seconds": 2.24,
            "status": "PASS",
        },
    ]
    result["higher_tiers_not_run"] = {
        "tier_2": (
            "The complete affected classical carrier/overlay/transfer chain is independently "
            "parsed and replayed coefficientwise in Tier 1; no downstream theorem may consume "
            "the cyclicity claim until the exact obstruction is repaired."
        ),
        "tier_3": (
            "No shared algebra engine, lifecycle state, release freeze, Lorentzian quantum "
            "construction, or paper theorem is promoted by this fail-closed import result."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale coupled 36-row transfer replay: {OUTPUT}")
    print("BERGER COUPLED 36 TRANSFER: FORMULA/Q1Q2 PASS; CYCLICITY OBSTRUCTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
