#!/usr/bin/env python3
"""Independent replay for the Nariai curvature-to-metric disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-metric-bridge-disposition-v1.schema.json"


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
        if payload["result_id"] != record["artifact_id"]:
            raise ValueError(f"dependency identity drifted: {name}")
        records[name] = payload
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")

    mismatch = records["parent_reducibility_mismatch"]["obstruction"]
    if mismatch["metric_H_minus_1_lower_bound"] - mismatch["parent_H_minus_1_upper_bound"] != 5:
        raise ValueError("normalized reducibility witness drifted")
    if records["rank_288_sdr_obstruction"]["obstruction"]["extra_prolonged_degree_zero_symbol_cohomology_lower_bound"] != 15:
        raise ValueError("rank-288 symbol obstruction drifted")
    if records["rank_310_mapping_cone_repair"]["carrier"]["added_rank_over_obstructed_carrier"] != 22:
        raise ValueError("rank-310 repair size drifted")
    if not records["rank_310_green_transfer"]["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"]:
        raise ValueError("rank-310 causal transfer disappeared")
    if value["bridge_disposition"]["direct_incidence_cylinder_to_metric_map"] != "NO_CERTIFIED_MAP":
        raise ValueError("a nonexistent direct map was promoted")
    if value["bridge_disposition"]["rank_310_replacement"] != "CERTIFIED":
        raise ValueError("rank-310 replacement was demoted")
    print("NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
