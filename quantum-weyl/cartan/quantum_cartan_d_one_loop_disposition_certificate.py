#!/usr/bin/env python3
"""Emit or check the one-loop quantum D-Cartan disposition certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .quantum_cartan_d_one_loop_disposition import evaluate
except ImportError:
    from quantum_cartan_d_one_loop_disposition import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION.json"
SOURCE_PATHS = (
    "quantum_cartan_d_one_loop_disposition.py",
    "quantum_cartan_d_one_loop_disposition_certificate.py",
    "verify_quantum_cartan_d_one_loop_disposition.py",
    "schema/quantum-cartan-d-one-loop-disposition-v1.schema.json",
    "tests/test_quantum_cartan_d_one_loop_disposition.py",
    "../reports/quantum-cartan-d-one-loop-disposition.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    value = evaluate()
    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    value["provenance"] = {
        "proof_type": "EXACT_MULTI_ARTIFACT_MISSING_CARRIER_DISPOSITION",
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest(),
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale Cartan disposition: {OUTPUT}")
    print("QUANTUM CARTAN D ONE-LOOP DISPOSITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
