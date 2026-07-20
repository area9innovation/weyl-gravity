#!/usr/bin/env python3
"""Emit/check the relative changed-theory QME disposition and its two rails."""

from __future__ import annotations

import argparse
import hashlib
import json

from .relative_changed_theory_qme_disposition import HERE, build as classify, validate


OUTPUT = HERE / "certificates/RELATIVE_CHANGED_THEORY_QME_NONDEFINITION.json"
FINITE_OUTPUT = (
    HERE
    / "certificates/RELATIVE_CHANGED_THEORY_FINITE_CARRIER_COMPATIBILITY.json"
)
LOCAL_OUTPUT = (
    HERE
    / "certificates/RELATIVE_CHANGED_THEORY_LOCAL_COHOMOLOGY_NONDEFINITION.json"
)
SOURCES = (
    "relative_changed_theory_qme_disposition.py",
    "relative_changed_theory_qme_disposition_certificate.py",
    "verify_relative_changed_theory_qme_disposition.py",
    "schema/relative-changed-theory-qme-disposition-v1.schema.json",
    "tests/test_relative_changed_theory_qme_disposition.py",
    "../reports/relative-changed-theory-qme-disposition.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "EXACT_REPAIR_ORBIT_READINESS_AND_TYPED_QME_DATA_"
            "NONDEFINITION_AUDIT"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
    }
    validate(value)
    return value


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {
        OUTPUT: value,
        FINITE_OUTPUT: value["finite_carrier_rail"],
        LOCAL_OUTPUT: value["local_cohomology_rail"],
    }
    if args.emit:
        for path, payload in outputs.items():
            path.write_text(_render(payload), encoding="utf-8")
    if args.check:
        for path, payload in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != _render(payload):
                raise SystemExit(f"stale relative QME disposition artifact: {path}")
    print("RELATIVE CHANGED-THEORY QME DISPOSITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
