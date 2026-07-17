#!/usr/bin/env python3
"""Emit or check the globally indexed partial Berger A104 assembly."""

from __future__ import annotations

import argparse
import hashlib
import json

from .berger_a104_global_partial_assembly import GENERATED, build


HERE = GENERATED.parent.parent
OUTPUT = HERE / "certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json"


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_certificate() -> tuple[dict, dict[str, dict]]:
    result, artifacts = build()
    result = result.copy()
    sources = (
        "berger_a104_global_partial_assembly.py",
        "berger_a104_global_partial_assembly_certificate.py",
        "verify_berger_a104_global_partial_assembly.py",
        "schema/berger-a104-global-partial-assembly-v1.schema.json",
        "schema/berger-endpoint-a24-cauchy-export-v1.schema.json",
        "tests/test_berger_a104_global_partial_assembly.py",
        "../reports/berger-a104-global-partial-assembly.md",
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
        GENERATED.mkdir(parents=True, exist_ok=True)
        for name, payload in artifacts.items():
            (GENERATED / f"{name}.json").write_text(_text(payload))
        OUTPUT.write_text(_text(result))
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != _text(result):
            raise SystemExit(f"stale global partial A104 certificate: {OUTPUT}")
        for name, payload in artifacts.items():
            path = GENERATED / f"{name}.json"
            if not path.exists() or path.read_text() != _text(payload):
                raise SystemExit(f"stale global partial A104 artifact: {name}")
    print("BERGER GLOBAL PARTIAL A104: 10528/10816 COORDINATES EXACT, TWO A12 SLOTS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
