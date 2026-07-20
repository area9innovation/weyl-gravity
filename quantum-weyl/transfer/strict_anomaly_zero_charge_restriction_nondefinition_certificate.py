#!/usr/bin/env python3
"""Emit/check the strict-anomaly zero-charge restriction nondefinition."""

from __future__ import annotations

import argparse
import hashlib
import json

from .strict_anomaly_zero_charge_restriction_nondefinition import (
    HERE,
    build,
    validate,
)


OUTPUT = (
    HERE
    / "certificates/STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION.json"
)
SOURCES = (
    "strict_anomaly_zero_charge_restriction_nondefinition.py",
    "strict_anomaly_zero_charge_restriction_nondefinition_certificate.py",
    "verify_strict_anomaly_zero_charge_restriction_nondefinition.py",
    "schema/strict-anomaly-zero-charge-restriction-nondefinition-v1.schema.json",
    "schema/strict-anomaly-sector-restriction-map-v1.schema.json",
    "tests/test_strict_anomaly_zero_charge_restriction_nondefinition.py",
    "../reports/strict-anomaly-zero-charge-restriction-nondefinition.md",
)


def certificate() -> dict:
    value = build()
    value["provenance"] = {
        "proof_type": "PINNED_MISSING_CHAIN_MAP_THEOREM_WITH_TYPED_RECEIVER",
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
        raise SystemExit("stale strict-anomaly sector restriction certificate")
    print("STRICT ANOMALY ZERO-CHARGE RESTRICTION NONDEFINITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
