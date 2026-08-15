#!/usr/bin/env python3
"""Schema, report, provenance, and no-promotion verifier for the Bach benchmark."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json"
SCHEMA = HERE / "schema/strict-polarized-bach-kernel-benchmark-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.md"
sys.path.insert(0, str(HERE))
from check_strict_polarized_bach_benchmark import check  # noqa: E402


def verify(value: dict[str, object], report: str) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend(check(value))
    required_report_tokens = (
        "BENCHMARK_CONTRACT_CERTIFIED_GENERAL_KERNEL_ABSENT",
        "ten symmetric contravariant density outputs",
        "no hidden factor of `1/2`",
        "PPWAVE_ARBITRARY_PROFILE_ZERO_SLICE",
        "CYLINDER_HT1B_NONZERO_MODE_CHANNELS",
        "NARIAI_TRANSVERSE_HESSIAN_VARIATION",
        "two unary cross terms",
        "NOT_RUN_NO_GENERAL_EVALUATOR",
    )
    for token in required_report_tokens:
        if token not in report:
            errors.append(f"human report missing boundary token: {token}")
    if value.get("repository_base_commit") != "99d4020850ef9cd394a5cfd9e1001228f430e2e2":
        errors.append("repository base commit drift")
    if len(value.get("does_not_establish", [])) < 7:
        errors.append("does_not_establish ledger shortened")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"input hash drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - Draft 2020-12 schema, source replay, report and provenance agree")
        print("  - all 10 general-evaluator gates remain explicitly unrun")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
