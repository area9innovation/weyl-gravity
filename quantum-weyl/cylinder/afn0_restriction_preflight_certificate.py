"""Emit the AFN0 cylinder structural restriction preflight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_bv.algebra import canonical_sha256

from .afn0_restriction_preflight import afn0_restriction_preflight


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "AFN0_CYLINDER_RESTRICTION_PREFLIGHT.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_cylinder_restriction_preflight.schema.json"


def build_certificate() -> dict[str, object]:
    payload = afn0_restriction_preflight()
    implementation = {
        "preflight": "quantum-weyl/cylinder/afn0_restriction_preflight.py",
        "emitter": "quantum-weyl/cylinder/afn0_restriction_preflight_certificate.py",
        "schema": "quantum-weyl/cylinder/schema/afn0_cylinder_restriction_preflight.schema.json",
    }
    certificate = {
        **payload,
        "preflight_hash": canonical_sha256(payload),
        "provenance": implementation,
    }
    return {**certificate, "certificate_hash": canonical_sha256(certificate)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"AFN0 cylinder preflight is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("AFN0 CYLINDER PREFLIGHT: STRUCTURE VERIFIED, PROJECTION BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
