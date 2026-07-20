#!/usr/bin/env python3
"""Independent verifier of the strict-anomaly restriction nondefinition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
OUTPUT = (
    HERE
    / "certificates/STRICT_ANOMALY_ZERO_CHARGE_RESTRICTION_NONDEFINITION.json"
)
SCHEMA = (
    HERE
    / "schema/strict-anomaly-zero-charge-restriction-nondefinition-v1.schema.json"
)
RECEIVER = (
    HERE / "schema/strict-anomaly-sector-restriction-map-v1.schema.json"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_receiver(payload: dict[str, Any]) -> None:
    errors = validate_instance(payload, _load(RECEIVER))
    if errors:
        raise ValueError(f"restriction receiver schema failed: {errors}")
    if payload["sector_id"] == "Berger_fixed_coupling":
        if payload["Cartan_generator"] != "K_Berger=D-omega R":
            raise ValueError("Berger receiver substituted raw D")
    elif payload["Cartan_generator"] != "raw_D":
        raise ValueError("cylinder receiver substituted K_Berger")


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"restriction schema failed: {errors}")
    for pin in value["input_pins"].values():
        path = ROOT / pin["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError("restriction dependency hash failed")
    local_pin = value["input_pins"]["local_anomaly_audit"]
    historical = subprocess.run(
        [
            "git",
            "show",
            f"{local_pin['source_commit']}:physics/symplectic-reconstruction/"
            f"{local_pin['path']}",
        ],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(historical).hexdigest() != local_pin["sha256"]:
        raise ValueError("requested local anomaly commit pin failed")
    rows = {
        (row["sector_id"], row["class_id"]): row
        for row in value["pullback_dispositions"]
    }
    expected_orders = {
        ("cylinder_Taub_zero", "ANOM_OMEGA_C2"): 2,
        ("cylinder_Taub_zero", "ANOM_OMEGA_E4"): 1,
        ("cylinder_Taub_zero", "ANOM_OMEGA_C_DUAL_C"): 2,
        ("Berger_fixed_coupling", "ANOM_OMEGA_C2"): 0,
        ("Berger_fixed_coupling", "ANOM_OMEGA_E4"): 1,
        ("Berger_fixed_coupling", "ANOM_OMEGA_C_DUAL_C"): 1,
    }
    if set(rows) != set(expected_orders):
        raise ValueError("restriction row set failed")
    for key, order in expected_orders.items():
        row = rows[key]
        if (
            row["status"] != "UNDEFINED_MISSING_CHAIN_MAP"
            or row["background_evaluation_used_as_pullback"]
            or row["onset_ledger"]["first_possible_h_order"] != order
        ):
            raise ValueError("background evaluation/pullback distinction failed")
    cartan = value["Cartan_obstruction_dispositions"]
    if (
        cartan[0]["generator"] != "raw_D"
        or cartan[1]["generator"] != "K_Berger=D-omega R"
        or cartan[2]["status"]
        != "NOT_APPLICABLE_AFFINE_GENERATOR_NOT_CERTIFIED_CARTAN"
    ):
        raise ValueError("raw-D/K_Berger independent replay failed")
    if any(value["claim_flags"].values()):
        raise ValueError("restriction claim boundary over-promoted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Strict-anomaly restriction nondefinition independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
