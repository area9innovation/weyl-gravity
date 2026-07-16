#!/usr/bin/env python3
"""Emit or check the Berger base-wave Hadamard-parametrix certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_base_wave_hadamard_parametrix import (
    ARTIFACT_PATHS, HERE, evaluate, theorem_instantiation_payloads,
)


OUTPUT = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_certificate() -> tuple[dict, dict[str, dict]]:
    result = evaluate().copy()
    artifacts = theorem_instantiation_payloads()
    sources = (
        "README.md",
        "berger_base_wave_hadamard_parametrix.py",
        "berger_base_wave_hadamard_parametrix_certificate.py",
        "verify_berger_base_wave_hadamard_parametrix.py",
        "schema/berger-base-wave-hadamard-parametrix-v1.schema.json",
        "tests/test_berger_base_wave_hadamard_parametrix.py",
        "../reports/berger-base-wave-hadamard-parametrix.md",
    )
    manifest = {path: _sha256(HERE / path) for path in sources}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result, artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, artifacts = build_certificate()
    if args.emit:
        for name, payload in artifacts.items():
            path = ARTIFACT_PATHS[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_text(payload))
        OUTPUT.write_text(_text(result))
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != _text(result):
            raise SystemExit(f"stale base-wave certificate: {OUTPUT}")
        for name, payload in artifacts.items():
            if ARTIFACT_PATHS[name].read_text() != _text(payload):
                raise SystemExit(f"stale theorem-instantiation artifact: {name}")
    print("BERGER BASE-WAVE HADAMARD PARAMETRIX: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
