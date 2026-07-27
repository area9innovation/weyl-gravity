#!/usr/bin/env python3
"""Independent verifier for the conformal gauge-carrier obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
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


OUTPUT = (
    HERE
    / "certificates/FIRST_NEW_CONFORMAL_GAUGE_FIELD_CARRIER_OBSTRUCTION.json"
)
SCHEMA = (
    HERE
    / "schema/conformal-gauge-field-carrier-obstruction-v1.schema.json"
)
RECEIVER_SCHEMA = (
    HERE / "schema/conformal-gauge-field-carrier-receiver-v1.schema.json"
)
PANEITZ_PATH = (
    "physics/symplectic-reconstruction/quantum-weyl/anomalies/certificates/"
    "PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json"
)
PANEITZ_SHA = (
    "cb6d708fb081d6a93fc64ab988f267cdd4a0c92651d872aaed5b59e3ecc3cb3c"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_receiver(payload: dict[str, Any]) -> None:
    errors = validate_instance(payload, _load(RECEIVER_SCHEMA))
    if errors:
        raise ValueError(f"carrier receiver schema failed: {errors}")
    fields = {row["field_id"] for row in payload["fields"]}
    determinant_fields = {
        row["field_id"] for row in payload["determinant_ledger"]
    }
    if not determinant_fields.issubset(fields):
        raise ValueError("determinant ledger contains undeclared field")
    if payload["reality_structure"] == "COMPLEX_WITH_CONJUGATE" and set(
        payload["chiral_components"]
    ) != {"UNDOTTED", "DOTTED_CONJUGATE"}:
        raise ValueError("wrong chirality completion")
    if len(payload["coefficient_routes"]) != 2:
        raise ValueError("exactly two coefficient routes required")
    if (
        payload["coefficient_routes"][0]["raw_column"]
        != payload["coefficient_routes"][1]["raw_column"]
    ):
        raise ValueError("coefficient routes disagree")
    if payload["lattice_action"] != "APPEND_NEW_COLUMN":
        raise ValueError("complete carrier must append its verified column")


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"carrier obstruction schema failed: {errors}")
    pin = value["input_pins"]["Paneitz_predecessor"]
    current = ROOT / pin["path"]
    if hashlib.sha256(current.read_bytes()).hexdigest() != PANEITZ_SHA:
        raise ValueError("current Paneitz input hash failed")
    read_attached_blob(
        pin["source_commit"],
        PANEITZ_PATH,
        PANEITZ_SHA,
    )

    audits = {row["candidate_id"]: row for row in value["candidate_audits"]}
    gravitino = audits[
        "complex_conformal_gravitino_minimal_depth_3_over_2"
    ]
    spin3 = audits["bosonic_conformal_spin_3_minimal_depth"]
    if (
        gravitino["gate_status"]["exact_generic_background_Noether_identity"]
        != "FAILED_EXACT_IDENTITY"
        or "Bach insertion" not in gravitino["exact_obstruction"]
        or gravitino["required_chiral_components"]
        != ["(2,1)_complex_field", "(1,2)_complex_conjugate"]
    ):
        raise ValueError("gravitino identity/chirality audit failed")
    if (
        spin3["gate_status"]["no_omitted_mixed_spin_carrier"]
        != "FAILED_EXACT_IDENTITY"
        or "spin-1/spin-3" not in spin3["first_missing_carrier"]
        or "spin-2 sector indicated" not in spin3["first_missing_carrier"]
        or "maximal-depth" not in spin3["first_missing_carrier"]
    ):
        raise ValueError("spin-3 missing-carrier audit failed")
    if (
        value["determinant_ledger"]["status"] != "NOT_ASSEMBLED"
        or value["determinant_ledger"]["rows"]
        or value["coefficient_routes"]["status"] != "NOT_RUN"
        or value["coefficient_routes"]["routes"]
        or value["anomaly_lattice"]["new_column_appended"]
    ):
        raise ValueError("incomplete determinant/coefficient gate failed")
    if any(value["claim_flags"].values()):
        raise ValueError("claim boundary over-promoted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Conformal gauge-field carrier obstruction independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
