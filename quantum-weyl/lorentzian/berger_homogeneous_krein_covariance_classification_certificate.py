#!/usr/bin/env python3
"""Emit or freshness-check the homogeneous Berger covariance classification."""

from __future__ import annotations

import argparse
import hashlib
import json

from .berger_homogeneous_krein_covariance_classification import (
    GENERATED,
    HERE,
    build as classify,
)


OUTPUT = (
    HERE
    / "certificates/BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION.json"
)
SOURCES = (
    "berger_homogeneous_krein_covariance_classification.py",
    "berger_homogeneous_krein_covariance_classification_certificate.py",
    "verify_berger_homogeneous_krein_covariance_classification.py",
    "schema/berger-homogeneous-krein-covariance-classification-v1.schema.json",
    "tests/test_berger_homogeneous_krein_covariance_classification.py",
    "../reports/berger-homogeneous-krein-covariance-classification.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "EXACT_ACTION_LAGRANGE_IDENTITY_PRIMARY_JORDAN_"
            "LYAPUNOV_AND_CCR_RADICAL_OBSTRUCTION"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
        "generated_summary": (
            "quantum-weyl/lorentzian/generated/"
            "berger_homogeneous_krein_covariance_classification/"
            "classification_summary.json"
        ),
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text)
        GENERATED.mkdir(parents=True, exist_ok=True)
        summary = {
            key: value[key]
            for key in (
                "result_id",
                "input_commit",
                "action_pairing",
                "homogeneous_spectral_classification",
                "stationary_covariance_classification",
                "nonstationary_alternative",
            )
        }
        (GENERATED / "classification_summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != text:
            raise SystemExit("stale homogeneous Berger covariance classification")
        summary_path = GENERATED / "classification_summary.json"
        expected_summary = {
            key: value[key]
            for key in (
                "result_id",
                "input_commit",
                "action_pairing",
                "homogeneous_spectral_classification",
                "stationary_covariance_classification",
                "nonstationary_alternative",
            )
        }
        if (
            not summary_path.exists()
            or json.loads(summary_path.read_text()) != expected_summary
        ):
            raise SystemExit("stale homogeneous covariance summary")
    print("BERGER HOMOGENEOUS KREIN COVARIANCE CLASSIFICATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
