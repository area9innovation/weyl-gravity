#!/usr/bin/env python3
"""Emit/check the exact matter anomaly-cancellation lattice."""

from __future__ import annotations

import argparse
import hashlib
import json

from .matter_content_anomaly_cancellation_lattice import (
    HERE,
    build as classify,
    validate,
)


OUTPUT = HERE / "certificates/MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE.json"
SOURCES = (
    "matter_content_anomaly_cancellation_lattice.py",
    "matter_content_anomaly_cancellation_lattice_certificate.py",
    "verify_matter_content_anomaly_cancellation_lattice.py",
    "schema/matter-content-anomaly-cancellation-lattice-v1.schema.json",
    "tests/test_matter_content_anomaly_cancellation_lattice.py",
    "../reports/matter-content-anomaly-cancellation-lattice.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "TWO_METHOD_EXACT_COEFFICIENT_REPLAY_DUAL_CONE_SEPARATION_"
            "AND_SMITH_AFFINE_LATTICE"
        ),
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
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text
    ):
        raise SystemExit("stale matter anomaly-cancellation lattice")
    print("MATTER CONTENT ANOMALY CANCELLATION LATTICE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
