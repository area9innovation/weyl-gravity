#!/usr/bin/env python3
"""Independent dependency replay for the Berger Bridge-1 disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-bridge1-admissible-carrier-disposition-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    records = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha(path) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
        payload = json.loads(path.read_text())
        if payload.get("result_id", payload.get("schema")) != record["artifact_id"]:
            raise ValueError(f"dependency identity drifted: {name}")
        records[name] = payload
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")

    if records["retained_36_cyclic_carrier"]["flags"]["BERGER_TYPED_64_TO_36_CYCLIC_SDR"] is not True:
        raise ValueError("retained 36-row cyclic carrier disappeared")
    if records["retained_54_causal_homotopy"]["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise ValueError("retained 54-row causal homotopy disappeared")
    if records["rank_36_projector_obstruction"]["flags"]["BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR_OBSTRUCTION"] is not True:
        raise ValueError("rank-36 obstruction disappeared")
    if records["rank_46_graph_carrier"]["flags"]["CYCLIC_GRAPH_SDR_46_TO_36"] is not True:
        raise ValueError("rank-46 graph SDR disappeared")
    if records["rank_46_subprincipal_obstruction"]["claim_flags"]["RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED"] is not True:
        raise ValueError("rank-46 subprincipal obstruction disappeared")
    if value["bridge_disposition"]["atlas_status"] != "NO_CERTIFIED_MAP":
        raise ValueError("atlas disposition drifted")
    if any(value["flags"][name] for name in (
        "BERGER_BRIDGE1_ACTIVATED",
        "BERGER_RETAINED_BRANCH_CROSSWALK",
        "ELL3_BRANCH_MIXING_AUTHORIZED",
        "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
        "QUANTUM_CLAIM",
    )):
        raise ValueError("claim boundary crossed")
    print("BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
