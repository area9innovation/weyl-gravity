#!/usr/bin/env python3
"""Emit/check the tau-adic DR/MS QAP obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json

from .tau_adic_dr_ms_qap_obstruction import HERE, build, validate


OUTPUT = HERE / "certificates/TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json"
SOURCES = (
    "tau_adic_dr_ms_qap_obstruction.py",
    "tau_adic_dr_ms_qap_obstruction_certificate.py",
    "verify_tau_adic_dr_ms_qap_obstruction.py",
    "schema/tau-adic-dr-ms-qap-obstruction-v1.schema.json",
    "tests/test_tau_adic_dr_ms_qap_obstruction.py",
    "../reports/tau-adic-dr-ms-qap-obstruction.md",
)


def certificate() -> dict:
    value = build()
    value["provenance"] = {
        "proof_type": "EXACT_POLE_TIMES_EVANESCENT_NONCOMMUTATION",
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
        raise SystemExit("stale tau-adic DR/MS QAP obstruction")
    print("TAU-ADIC DR/MS QAP: EVANESCENT CLOSURE OBSTRUCTION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
