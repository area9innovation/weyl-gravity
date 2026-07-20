#!/usr/bin/env python3
"""Emit/check the conditional tau-adic all-loop local-QME theorem."""

from __future__ import annotations

import argparse
import hashlib
import json

from .tau_adic_all_loop_qme_stability import HERE, build, validate


OUTPUT = HERE / "certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json"
SOURCES = (
    "tau_adic_all_loop_qme_stability.py",
    "tau_adic_all_loop_qme_stability_certificate.py",
    "verify_tau_adic_all_loop_qme_stability.py",
    "schema/tau-adic-all-loop-local-qme-stability-v1.schema.json",
    "tests/test_tau_adic_all_loop_qme_stability.py",
    "../reports/tau-adic-all-loop-local-qme-stability.md",
)


def certificate() -> dict:
    value = build()
    value["provenance"] = {
        "proof_type": (
            "EXACT_COHOMOLOGY_MODULE_AND_FILTERED_ALGEBRAIC_RENORMALIZATION_INDUCTION"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
        "primary_references": [
            "https://arxiv.org/abs/hep-th/0002245",
            "https://arxiv.org/abs/hep-th/9405109",
            "https://arxiv.org/abs/hep-th/9505173",
        ],
    }
    validate(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists()
        or OUTPUT.read_text(encoding="utf-8") != rendered
    ):
        raise SystemExit("stale tau-adic all-loop QME certificate")
    print("TAU-ADIC ALL-LOOP LOCAL QME: CONDITIONAL FORMAL INDUCTION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
