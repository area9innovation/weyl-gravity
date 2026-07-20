#!/usr/bin/env python3
"""Emit/check the first conformal gauge-carrier obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json

from .conformal_gauge_field_carrier_obstruction import HERE, build, validate


OUTPUT = (
    HERE
    / "certificates/FIRST_NEW_CONFORMAL_GAUGE_FIELD_CARRIER_OBSTRUCTION.json"
)
SOURCES = (
    "conformal_gauge_field_carrier_obstruction.py",
    "conformal_gauge_field_carrier_obstruction_certificate.py",
    "verify_conformal_gauge_field_carrier_obstruction.py",
    "schema/conformal-gauge-field-carrier-obstruction-v1.schema.json",
    "schema/conformal-gauge-field-carrier-receiver-v1.schema.json",
    "tests/test_conformal_gauge_field_carrier_obstruction.py",
    "../reports/conformal-gauge-field-carrier-obstruction.md",
)


def certificate() -> dict:
    value = build()
    value["provenance"] = {
        "proof_type": (
            "PRIMARY_SOURCE_IDENTITY_AUDIT_PLUS_STRICT_FAIL_CLOSED_RECEIVER"
        ),
        "primary_sources": [
            {
                "source_id": "KPR_2005_08657",
                "title": "New locally (super)conformal gauge models in Bach-flat backgrounds",
                "url": "https://arxiv.org/abs/2005.08657",
                "arxiv": "2005.08657v2",
                "source_tex_sha256": (
                    "fd20a3529929d3479384df35c499537ce15be771f5d3948a378cbf7ba97a99eb"
                ),
                "used_for": (
                    "explicit conformal-gravitino Bach variation and the "
                    "minimal-depth spin-3 spin-2 coupling requirement"
                ),
            },
            {
                "source_id": "BT_1702_00222",
                "title": "On induced action for conformal higher spins in curved background",
                "url": "https://arxiv.org/abs/1702.00222",
                "arxiv": "1702.00222v2",
                "source_tex_sha256": (
                    "3b782d81bed2f8d941cff864b12e8e8c4836d1ce9901a86b970d1855d0a10566"
                ),
                "used_for": (
                    "minimal-depth spin-1/spin-3 mixing and failure of the "
                    "pure sixth-order spin-3 block beyond first curvature order"
                ),
            },
            {
                "source_id": "KP_1912_00652",
                "title": "Generalised conformal higher-spin fields in curved backgrounds",
                "url": "https://arxiv.org/abs/1912.00652",
                "arxiv": "1912.00652v2",
                "source_tex_sha256": (
                    "b87fb876f3257226bae729f515f32d76050b2bf94d97b63695e02f12b0f2f841"
                ),
                "used_for": (
                    "separation of the complete maximal-depth scalar-ghost "
                    "model from the requested minimal-depth spin-3 carrier"
                ),
            },
            {
                "source_id": "KP_1902_08010",
                "title": "Conformal geometry and (super)conformal higher-spin gauge theories",
                "url": "https://arxiv.org/abs/1902.08010",
                "arxiv": "1902.08010v2",
                "source_tex_sha256": (
                    "16300f08f3beff4e50c27f4268595aef9b8edf6337ed0a8bb8cdb18fcdb7d076"
                ),
                "used_for": (
                    "arbitrary-curved Weyl covariance versus conformally-flat "
                    "higher-spin gauge invariance and Bach-flat exceptions"
                ),
            },
        ],
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
    }
    validate(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text
    ):
        raise SystemExit("stale conformal gauge-carrier obstruction certificate")
    print("FIRST NEW CONFORMAL GAUGE-FIELD CARRIER OBSTRUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
