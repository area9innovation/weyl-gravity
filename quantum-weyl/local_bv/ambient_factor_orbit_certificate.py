"""Emit the AFN0 degree-three/four signed factor-orbit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .ambient_factor_orbits import ambient_factor_orbit_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "AFN0_AMBIENT_FACTOR_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_ambient_factor_orbit.schema.json"
BUNDLE_SCHEMA_PATH = (
    PACKAGE_ROOT / "schema" / "afn0_ambient_factor_orbit_bundle.schema.json"
)
BUNDLE_DIRECTORY = PACKAGE_ROOT / "certificates" / "ambient_factor_orbit_manifests"


def _source_manifest() -> dict[str, str]:
    paths = (
        "ambient_factor_orbits.py",
        "ambient_factor_orbit_certificate.py",
        "schema/afn0_ambient_factor_orbit.schema.json",
        "schema/afn0_ambient_factor_orbit_bundle.schema.json",
        "tests/test_ambient_factor_orbits.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    analysis, bundle = ambient_factor_orbit_analysis()
    payload = {
        **analysis,
        "factor_orbit_bundle": {
            **analysis["factor_orbit_bundle"],
            "path": f"ambient_factor_orbit_manifests/{bundle['bundle_sha256']}.json",
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
            "analysis_sha256": analysis["analysis_sha256"],
            "bundle_sha256": bundle["bundle_sha256"],
        },
    }
    return {**payload, "certificate_sha256": canonical_sha256(payload)}, bundle


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, bundle = build_artifacts()
    bundle_path = BUNDLE_DIRECTORY / f"{bundle['bundle_sha256']}.json"
    certificate_content = _render(certificate)
    bundle_content = _render(bundle)
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        BUNDLE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(certificate_content, encoding="utf-8")
        bundle_path.write_text(bundle_content, encoding="utf-8")
    if args.check:
        if OUTPUT_PATH.read_text(encoding="utf-8") != certificate_content:
            raise SystemExit(f"ambient factor-orbit certificate is stale: {OUTPUT_PATH}")
        if bundle_path.read_text(encoding="utf-8") != bundle_content:
            raise SystemExit(f"ambient factor-orbit bundle is stale: {bundle_path}")
    if not args.emit and not args.check:
        print(certificate_content, end="")
    else:
        print("AFN0 FACTOR ORBITS: DEGREES 3-4 COMPLETE, IDENTITY QUOTIENT OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
