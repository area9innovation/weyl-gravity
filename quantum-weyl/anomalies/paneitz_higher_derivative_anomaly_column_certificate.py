#!/usr/bin/env python3
"""Emit/check the exact Paneitz higher-derivative anomaly column."""

from __future__ import annotations

import argparse
import hashlib
import json

from .paneitz_higher_derivative_anomaly_column import (
    HERE,
    build as classify,
    validate,
)


OUTPUT = HERE / "certificates/PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json"
SOURCES = (
    "paneitz_higher_derivative_anomaly_column.py",
    "paneitz_higher_derivative_anomaly_column_certificate.py",
    "verify_paneitz_higher_derivative_anomaly_column.py",
    "schema/paneitz-higher-derivative-anomaly-column-v1.schema.json",
    "tests/test_paneitz_higher_derivative_anomaly_column.py",
    "../reports/paneitz-higher-derivative-anomaly-column.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "TWO_ROUTE_HIGHER_ORDER_HEAT_AND_IMPROVED_SPECTRAL_"
            "COEFFICIENT_REPLAY_WITH_EXACT_LATTICE_WITNESSES"
        ),
        "primary_sources": [
            {
                "title": (
                    "Holographic Weyl anomaly for GJMS operators: "
                    "one Laplacian to rule them all"
                ),
                "url": "https://arxiv.org/abs/1811.10380",
                "arxiv": "1811.10380v2",
                "source_tex_sha256": (
                    "7f5d97b1ff07be99fad0a7c0b739f7a72047d338efc1174a981b5bbf6c0f96ae"
                ),
                "used_for": "Einstein factorization and exact a,c-a route",
            },
            {
                "title": (
                    "On heat coefficients, multiplicative anomaly and "
                    "4D Casimir energy for GJMS operators"
                ),
                "url": "https://arxiv.org/abs/2501.17828",
                "arxiv": "2501.17828v2",
                "source_tex_sha256": (
                    "f5809824dd9c37b198d99bdbd272349787496bf3611d28f1ccc1450e0f11d80c"
                ),
                "used_for": (
                    "local Paneitz total derivative and independent "
                    "multiplicative-anomaly-improved Casimir route"
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
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text
    ):
        raise SystemExit("stale Paneitz higher-derivative anomaly column")
    print("PANEITZ HIGHER-DERIVATIVE ANOMALY COLUMN: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
