#!/usr/bin/env python3
"""Verify the Berger complex-channel to real-shell extraction certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_REAL_SHELL_EXTRACTION.json"
SCHEMA = PACKAGE / "schema/berger-recoil-real-shell-extraction-v1.schema.json"


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in list(value["dependency_refs"].values()) + value["provenance"]["source_manifest"]:
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise SystemExit(f"content hash drift: {ref['path']}")
    if len(value["two_j5_real_channel_sums"]) != 8:
        raise SystemExit("two_j=5 real channel coverage is incomplete")
    if any(any(row[key]) for row in value["algebra_audits"] for key in (
        "de_rham_reality_defect_counts_by_degree_0_1_2",
        "laplacian_reality_defect_counts_by_degree_0_1_2_3",
    )):
        raise SystemExit("operator reality defect")
    if any(row["representation_reality_defect_count"] for row in value["algebra_audits"]):
        raise SystemExit("representation reality defect")
    print("BERGER_RECOIL_REAL_SHELL_EXTRACTION verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
