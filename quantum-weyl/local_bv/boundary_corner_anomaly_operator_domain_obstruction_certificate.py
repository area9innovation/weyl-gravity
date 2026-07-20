#!/usr/bin/env python3
"""Emit/check the boundary/corner anomaly operator-domain obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .boundary_corner_anomaly_operator_domain_obstruction import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/BOUNDARY_CORNER_ANOMALY_OPERATOR_DOMAIN_OBSTRUCTION.json"
SOURCES = (
    "boundary_corner_anomaly_operator_domain_obstruction.py",
    "boundary_corner_anomaly_operator_domain_obstruction_certificate.py",
    "verify_boundary_corner_anomaly_operator_domain_obstruction.py",
    "schema/boundary-corner-anomaly-operator-domain-obstruction-v1.schema.json",
    "tests/test_boundary_corner_anomaly_operator_domain_obstruction.py",
    "../reports/boundary-corner-anomaly-operator-domain-obstruction.md",
)


def build() -> dict:
    value = evaluate()
    value["provenance"] = {
        "proof_type": (
            "EXACT_IMPORTED_SCOPE_AUDIT_AND_BOUNDARY_GAUGE_BRANCH_OBSTRUCTION"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text)
    if args.check and OUTPUT.read_text() != text:
        raise SystemExit("stale boundary/corner obstruction certificate")
    print("BOUNDARY CORNER ANOMALY OPERATOR-DOMAIN OBSTRUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
