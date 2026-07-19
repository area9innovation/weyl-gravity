#!/usr/bin/env python3
"""Independent consumer for the class-wide rank-310 causal lift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-rank310-causal-transfer-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for ref in value["dependency_refs"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drifted: {ref['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")
    if value["scope"]["degree_ranks"] != [15, 140, 140, 15]:
        raise AssertionError("rank-310 row coverage drifted")
    if value["transfer"]["formula"] != "Lambda310,+/-=H+I Lambda_metric,+/- pi":
        raise AssertionError("SDR lift formula drifted")
    if value["flags"]["PURE_PARENT_TO_METRIC_SDR"] is not False:
        raise AssertionError("pure parent crosswalk promoted")
    print("BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1: independently verified")


if __name__ == "__main__":
    verify()
