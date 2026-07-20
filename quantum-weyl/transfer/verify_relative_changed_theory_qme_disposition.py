#!/usr/bin/env python3
"""Independent verifier for the changed-theory relative QME non-definition."""

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
OUTPUT = HERE / "certificates/RELATIVE_CHANGED_THEORY_QME_NONDEFINITION.json"
FINITE_OUTPUT = (
    HERE / "certificates/RELATIVE_CHANGED_THEORY_FINITE_CARRIER_COMPATIBILITY.json"
)
LOCAL_OUTPUT = (
    HERE / "certificates/RELATIVE_CHANGED_THEORY_LOCAL_COHOMOLOGY_NONDEFINITION.json"
)
SCHEMA = HERE / "schema/relative-changed-theory-qme-disposition-v1.schema.json"
SOURCES = (
    "relative_changed_theory_qme_disposition.py",
    "relative_changed_theory_qme_disposition_certificate.py",
    "verify_relative_changed_theory_qme_disposition.py",
    "schema/relative-changed-theory-qme-disposition-v1.schema.json",
    "tests/test_relative_changed_theory_qme_disposition.py",
    "../reports/relative-changed-theory-qme-disposition.md",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _verify_pin(value: dict[str, Any]) -> dict[str, Any]:
    pin = value["input_pins"]["terminal_repair"]
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    blob = subprocess.check_output(
        ["git", "show", f"{pin['commit']}:{prefix}{pin['path']}"],
        cwd=ROOT,
    )
    repair = json.loads(blob)
    if (
        hashlib.sha256(blob).hexdigest() != pin["sha256"]
        or repair["result_id"]
        != "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION"
    ):
        raise ValueError("independent repair pin failed")
    sectors = repair["sector_classification"]
    if (
        len(sectors) != 2
        or any(row["minimal_target_pairing_repair"]["rank"] != 1 for row in sectors)
        or any(
            not row["minimal_target_pairing_repair"]["identity_verified"]
            for row in sectors
        )
        or repair["claim_flags"]["FULL_OFF_SHELL_CHANGED_ACTION_COMPLEX_CONSTRUCTED"]
        is not False
    ):
        raise ValueError("independent inertia-repair replay failed")
    return repair


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"relative changed-theory schema failed: {errors}")
    _verify_pin(value)
    local_pin = value["input_pins"]["strict_local_anomaly"]
    local_path = ROOT / local_pin["path"]
    local = _load(local_path)
    if (
        hashlib.sha256(local_path.read_bytes()).hexdigest() != local_pin["sha256"]
        or local["result_id"] != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
        or local["two_method_coefficients"]["repository_vector"]
        != value["coefficient_ledger"]["strict_pure_Weyl_reference_vector"]
    ):
        raise ValueError("independent strict anomaly reference failed")
    orbits = value["repair_orbit_dispositions"]
    if [row["repair_orbit"] for row in orbits] != [
        "pairing_deformation",
        "quadratic_action_deformation",
        "physical_auxiliary_extension",
    ]:
        raise ValueError("repair orbit census failed")
    if any(
        row["reduced_cyclic_map"] != "EXISTS"
        or row["off_shell_chain_lift"] != "NOT_SUPPLIED"
        or row["common_regulator_domain"] != "NOT_SUPPLIED"
        or row["relative_one_loop_defect"] != "UNDEFINED"
        for row in orbits
    ):
        raise ValueError("relative QME data-state mutation detected")
    if any(
        value["coefficient_ledger"][key] != "UNDEFINED"
        for key in (
            "changed_pairing_relative_vector",
            "changed_action_relative_vector",
            "physical_auxiliary_relative_vector",
        )
    ):
        raise ValueError("relative anomaly coefficient mutation detected")
    if _load(FINITE_OUTPUT) != value["finite_carrier_rail"]:
        raise ValueError("finite-carrier rail drifted")
    if _load(LOCAL_OUTPUT) != value["local_cohomology_rail"]:
        raise ValueError("local-cohomology rail drifted")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("relative QME source manifest drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("relative changed-theory QME disposition independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
