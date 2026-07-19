#!/usr/bin/env python3
"""Verify the complete reality-folded Berger ``two_j=6`` feedback shell."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING.json"
SCHEMA = PACKAGE / "schema/berger-recoil-two-j6-reality-folded-binding-v1.schema.json"


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in list(value["dependency_refs"].values()) + value["provenance"]["source_manifest"]:
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise SystemExit(f"content hash drift: {ref['path']}")
    summary = value["coverage_summary"]
    if (summary["total_channel_column_count"], summary["direct_backend_count"], summary["exact_reality_derived_count"]) != (56, 32, 24):
        raise SystemExit("two_j=6 direct/derived coverage drifted")
    if len(value["two_j6_real_channel_sums"]) != 8:
        raise SystemExit("two_j=6 real channel sums are incomplete")
    print("BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
