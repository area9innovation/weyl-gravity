#!/usr/bin/env python3
"""Emit or check the quantum relative Einstein--Weyl readiness certificate."""

from __future__ import annotations

import argparse
import hashlib
import json

from .einstein_weyl_qme_readiness import HERE, build


OUTPUT = HERE / "certificates/QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json"


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    result = build()
    sources = (
        "einstein_weyl_qme_readiness.py",
        "einstein_weyl_qme_readiness_certificate.py",
        "verify_einstein_weyl_qme_readiness.py",
        "schema/einstein-weyl-qme-readiness-v1.schema.json",
        "tests/test_einstein_weyl_qme_readiness.py",
        "../reports/quantum-relative-einstein-weyl-qme-readiness.md",
    )
    manifest = {path: _sha256(HERE / path) for path in sources}
    result = result.copy()
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _text(build_certificate())
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale quantum relative readiness certificate: {OUTPUT}")
    print("QUANTUM RELATIVE EINSTEIN-WEYL: G0 LEDGER READY, ANALYTIC FRAMEWORK MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
