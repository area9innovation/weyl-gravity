#!/usr/bin/env python3
"""Independent topology and receiver replay for global-anomaly preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from ci.standalone_provenance import read_attached_blob


OUTPUT = HERE / "certificates/COMPLEX_COMPENSATOR_GLOBAL_ANOMALY_CARRIER_NONDEFINITION.json"
SCHEMA = HERE / "schema/complex-compensator-global-anomaly-carrier-preflight-v1.schema.json"
RECEIVER = HERE / "schema/complex-compensator-global-anomaly-audit-input-v1.schema.json"
FIXTURE = HERE / "fixtures/complex_compensator_global_anomaly_audit_input_accept.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"global-anomaly carrier schema failed: {errors}")

    for pin in value["input_pins"].values():
        read_attached_blob(
            pin["source_commit"],
            pin["path"],
            pin["sha256"],
        )

    # Independent cellular replay: S1 has cells in degrees 0,1 and S3 in
    # degrees 0,3. Their product has one cell in degrees 0,1,3,4 and zero
    # cellular boundaries.
    cells = [1, 1, 0, 1, 1]
    boundaries = [0, 0, 0, 0, 0]
    homology_ranks = [
        cells[i] - boundaries[i] - (boundaries[i + 1] if i < 4 else 0)
        for i in range(5)
    ]
    if (
        homology_ranks != value["finite_index_ledger"]["betti_numbers_S1xS3"]
        or homology_ranks[1] != 1
        or homology_ranks[2] != 0
    ):
        raise ValueError("independent S1 x S3 cellular replay failed")

    fixture_errors = validate_instance(_load(FIXTURE), _load(RECEIVER))
    if fixture_errors:
        raise ValueError(f"global-anomaly receiver fixture failed: {fixture_errors}")

    diff_rows = [
        row for row in value["group_component_ledger"]
        if row.get("factor") == "Diff"
    ]
    if (
        value["imported_theory"]["internal_phase_symmetry"]
        != "GLOBAL_U1_NOT_GAUGED"
        or value["bundle_and_winding_ledger"]["Berger_magnetic_bundle"]
        != "NOT_IMPORTED_DIFFERENT_WEYL_MAXWELL_CARRIER"
        or value["finite_index_ledger"]["global_anomaly_verdict"] != "UNDEFINED"
        or len(diff_rows) != 1
        or diff_rows[0].get("disconnected_components")
        != "UNDEFINED_ALLOWED_MAPPING_CLASS_SUBGROUP_NOT_EXPORTED"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("global-anomaly non-definition boundary crossed")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Complex-compensator global-anomaly independent topology/receiver replay: PASS")
    return value


if __name__ == "__main__":
    verify()
