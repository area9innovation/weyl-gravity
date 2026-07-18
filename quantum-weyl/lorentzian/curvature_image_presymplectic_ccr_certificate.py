#!/usr/bin/env python3
"""Emit or check the curvature-image presymplectic CCR certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .curvature_image_presymplectic_ccr import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate().copy()
    paths = (
        "curvature_image_presymplectic_ccr.py",
        "curvature_image_presymplectic_ccr_certificate.py",
        "verify_curvature_image_presymplectic_ccr.py",
        "schema/curvature-image-presymplectic-ccr-v1.schema.json",
        "tests/test_curvature_image_presymplectic_ccr.py",
        "../reports/curvature-image-presymplectic-ccr.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = build_certificate()
    if args.emit:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {OUTPUT}")
        return 0
    if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != result:
        raise SystemExit(f"stale curvature-image CCR certificate: {OUTPUT}")
    print("CURVATURE IMAGE PRESYMPLECTIC CCR certificate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
