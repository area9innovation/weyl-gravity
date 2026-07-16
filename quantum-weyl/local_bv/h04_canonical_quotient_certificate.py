"""Emit the complete AFN0 ghost-zero covariant candidate quotient."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .algebra import canonical_sha256
from .h04_canonical_quotient import canonical_quotient_payload


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "AFN0_H04_CANONICAL_QUOTIENT.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_h04_canonical_quotient.schema.json"

DEPENDENCIES = (
    "quantum-weyl/local_bv/certificates/BASIS_GAP_REPORT_AFN0.json",
    "quantum-weyl/local_bv/certificates/LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json",
    "quantum-weyl/local_bv/certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json",
    "quantum-weyl/local_bv/certificates/TRIVIALITY_CERTIFICATE.json",
    "quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    payload = canonical_quotient_payload()
    sources = {path: _sha256(REPOSITORY_ROOT / path) for path in DEPENDENCIES}
    certificate = {
        **payload,
        "provenance": {
            "source_sha256": sources,
            "source_manifest_sha256": canonical_sha256(sources),
            "implementation": "quantum-weyl/local_bv/h04_canonical_quotient.py",
            "schema": "quantum-weyl/local_bv/schema/afn0_h04_canonical_quotient.schema.json",
        },
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
            raise SystemExit(f"H04 canonical quotient certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("AFN0 H04 COVARIANT QUOTIENT: EVEN 2, ODD 1, LOCAL-ALGEBRAIC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
