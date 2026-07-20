#!/usr/bin/env python3
"""Emit/check the complex-compensator global-anomaly carrier preflight."""

from __future__ import annotations

import argparse
import hashlib
import json

from .complex_compensator_global_anomaly_carrier_preflight import HERE, build, validate


OUTPUT = HERE / "certificates/COMPLEX_COMPENSATOR_GLOBAL_ANOMALY_CARRIER_NONDEFINITION.json"
SOURCES = (
    "complex_compensator_global_anomaly_carrier_preflight.py",
    "complex_compensator_global_anomaly_carrier_preflight_certificate.py",
    "verify_complex_compensator_global_anomaly_carrier_preflight.py",
    "schema/complex-compensator-global-anomaly-carrier-preflight-v1.schema.json",
    "schema/complex-compensator-global-anomaly-audit-input-v1.schema.json",
    "fixtures/complex_compensator_global_anomaly_audit_input_accept.json",
    "tests/test_complex_compensator_global_anomaly_carrier_preflight.py",
    "../reports/complex-compensator-global-anomaly-carrier-preflight.md",
)


def certificate() -> dict:
    value = build()
    value["provenance"] = {
        "proof_type": "EXACT_KUNNETH_PLUS_TYPED_GLOBAL_CARRIER_NONDEFINITION",
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
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != text):
        raise SystemExit("stale complex-compensator global-anomaly preflight")
    print("COMPLEX COMPENSATOR GLOBAL-ANOMALY CARRIER: NONDEFINITION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
