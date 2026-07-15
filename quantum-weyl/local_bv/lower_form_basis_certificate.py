"""Emit the AFN0 lower-form candidate-carrier precertificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .lower_form_basis import lower_form_carrier_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "AFN0_LOWER_FORM_CARRIER_PRECERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_lower_form_carrier_precertificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "lower_form_basis.py",
        "lower_form_basis_certificate.py",
        "schema/afn0_lower_form_carrier_precertificate.schema.json",
        "tests/test_lower_form_basis.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    analysis = lower_form_carrier_analysis()
    payload = {
        **analysis,
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
            "analysis_sha256": analysis["analysis_sha256"],
        },
    }
    return {**payload, "certificate_sha256": canonical_sha256(payload)}


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"AFN0 lower-form carrier artifact is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("AFN0 LOWER-FORM CARRIERS: DECLARED SECTOR COMPLETE, AMBIENT BASIS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
