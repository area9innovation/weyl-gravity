"""Emit the AFN0 degree-three/four intrinsic signed-orbit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .ambient_intrinsic_orbits import ambient_intrinsic_orbit_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "AFN0_AMBIENT_INTRINSIC_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_ambient_intrinsic_orbit.schema.json"
BUNDLE_SCHEMA_PATH = (
    PACKAGE_ROOT / "schema" / "afn0_ambient_intrinsic_orbit_bundle.schema.json"
)
BUNDLE_DIRECTORY = PACKAGE_ROOT / "certificates" / "ambient_intrinsic_orbit_manifests"
PREDECESSOR_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "AFN0_AMBIENT_FACTOR_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json"
)


def _source_manifest() -> dict[str, str]:
    paths = (
        "ambient_intrinsic_orbits.py",
        "ambient_intrinsic_orbit_certificate.py",
        "schema/afn0_ambient_intrinsic_orbit.schema.json",
        "schema/afn0_ambient_intrinsic_orbit_bundle.schema.json",
        "tests/test_ambient_intrinsic_orbits.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _predecessor_source() -> dict[str, object]:
    predecessor = json.loads(PREDECESSOR_PATH.read_text(encoding="utf-8"))
    payload = {
        key: value
        for key, value in predecessor.items()
        if key != "certificate_sha256"
    }
    if canonical_sha256(payload) != predecessor["certificate_sha256"]:
        raise AssertionError("predecessor factor-orbit certificate hash mismatch")
    if predecessor["totals"]["raw_graph_count"] != 388_011:
        raise AssertionError("predecessor raw graph scope drifted")
    return {
        "result_id": predecessor["result_id"],
        "analysis_sha256": predecessor["analysis_sha256"],
        "certificate_sha256": predecessor["certificate_sha256"],
        "bundle_sha256": predecessor["factor_orbit_bundle"]["bundle_sha256"],
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    analysis, bundle = ambient_intrinsic_orbit_analysis()
    payload = {
        **analysis,
        "predecessor_factor_orbit_source": _predecessor_source(),
        "checks": {
            **analysis["checks"],
            "predecessor_certificate_hash_and_scope": "VERIFIED",
        },
        "intrinsic_orbit_bundle": {
            **analysis["intrinsic_orbit_bundle"],
            "path": f"ambient_intrinsic_orbit_manifests/{bundle['bundle_sha256']}.json",
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
            "analysis_sha256": analysis["analysis_sha256"],
            "bundle_sha256": bundle["bundle_sha256"],
            "predecessor_source_sha256": canonical_sha256(_predecessor_source()),
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
            raise SystemExit(f"ambient intrinsic-orbit certificate is stale: {OUTPUT_PATH}")
        if bundle_path.read_text(encoding="utf-8") != bundle_content:
            raise SystemExit(f"ambient intrinsic-orbit bundle is stale: {bundle_path}")
    if not args.emit and not args.check:
        print(certificate_content, end="")
    else:
        print("AFN0 INTRINSIC ORBITS: DEGREES 3-4 COMPLETE, LINEAR RELATIONS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
