#!/usr/bin/env python3
"""Independent audit of the Berger clock one-loop nondefinition theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from ci.standalone_provenance import read_attached_blob


OUTPUT = HERE / "certificates/BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-complex-clock-one-loop-breaking-nondefinition-v1.schema.json"
RECEIVER_SCHEMA = HERE / "schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json"
REQUEST = ROOT / "planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/positive-berger-complex-clock-one-loop-nondefinition-fragment-v1.json"
ATLAS_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _historical(pin: dict[str, str]) -> dict[str, Any]:
    _, data = read_attached_blob(
        pin["source_commit"],
        pin["path"],
        pin["sha256"],
    )
    return json.loads(data)


def verify_payload(value: dict[str, Any]) -> None:
    Draft202012Validator(_load(SCHEMA)).validate(value)
    inputs = {name: _historical(pin) for name, pin in value["input_pins"].items()}

    anomaly = inputs["local_anomaly_complex"]
    action = inputs["matter_coupled_master_action"]
    unary = inputs["berger_classical_gauge_fixed_unary"]
    multiplicity = inputs["loop_multiplicity_receiver"]
    regulator = inputs["conditional_covariant_regulator_receiver"]

    # Independent ordered-gate audit.  The action and classical gauge fixing
    # pass; the very next quantum integration datum does not.
    ordered = [
        ("master_action", action["claim_flags"]["LOCAL_ACTION_CERTIFIED"]),
        ("minimal_nonminimal_BV", action["claim_flags"]["MINIMAL_AND_NONMINIMAL_BV_CERTIFIED"]),
        (
            "classical_gauge_fixed_unary",
            unary["exact_checks"]["gauge_fixed_classical_unary_q1_squared_zero"],
        ),
        (
            "Euclidean_gauge_fixed_Lagrangian_integration_slice",
            multiplicity["claim_flags"]["REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED"],
        ),
        (
            "selected_Hessian",
            regulator["claim_flags"]["SELECTED_HESSIAN_IMPORTED"],
        ),
    ]
    first_failure = next(name for name, passed in ordered if not passed)
    if first_failure != "Euclidean_gauge_fixed_Lagrangian_integration_slice":
        raise ValueError("independent first-missing-datum order changed")

    boundary = multiplicity["claim_boundary"]
    if (
        "explicitly rejected as loop multiplicity authority" not in boundary
        or "No Euclidean Lagrangian integration slice" not in boundary
        or anomaly["coefficient_and_qme_status"]["coefficient_status"]
        != "NOT_COMPUTED_FOR_GRAVITY_CLOCK_THEORY"
        or value["first_missing_input"]["id"]
        != "POSITIVE_BERGER_COMPLEX_CLOCK_EUCLIDEAN_BV_INTEGRATION_SLICE_V1"
        or value["quotient_disposition"]["strict_199_over_30_minus_87_over_20_import"]
        != "FORBIDDEN_CHANGED_THEORY_NO_ACTION_COMPLEX_MAP"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("independent one-loop nondefinition boundary crossed")

    rows = {row["class_id"]: row for row in value["coefficient_ledger"]}
    if set(rows) != {
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_C_DUAL_C",
        "ANOM_OMEGA_BOX_R",
    } or any(row["prequotient_coefficient"] != "NONDEFINED" for row in rows.values()):
        raise ValueError("coefficient nondefinition ledger is incomplete")

    Draft202012Validator.check_schema(_load(RECEIVER_SCHEMA))
    request = _load(REQUEST)
    if (
        request["id"]
        != "sf:forge-request/positive-berger-complex-clock-euclidean-bv-integration-slice"
        or request["body"]["state"] not in {"REQUESTED", "ACCEPTED", "LANDED"}
        or "quantum-berger-matter-coupled-one-loop-breaking-coefficients"
        not in request["body"]["depends_on"][0]
        or "54-row BRST matrix" not in request["body"]["forbid"]
    ):
        raise ValueError("typed producer request drifted")

    atlas = _load(ATLAS_OUTPUT)
    Draft202012Validator(_load(ATLAS_SCHEMA)).validate(atlas)
    if len(atlas["entries"]) != 1:
        raise ValueError("Berger one-loop atlas fragment must have one row")
    row = atlas["entries"][0]
    if (
        row["quantum_data"]["entry_kind"] != "NON_MODE_PARTICLE_GUARD"
        or row["quantum_data"]["anomaly_QME_dependency"]["status"] != "OPEN"
        or row["quantum_data"]["particle_interpretation"]["status"]
        != "NOT_APPLICABLE"
        or row["quantum_data"]["carrier_crosswalk"]["status"]
        != "NO_CERTIFIED_MAP"
        or row["evidence"][0]["sha256"]
        != hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    ):
        raise ValueError("fail-closed Berger one-loop atlas row drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Berger complex-clock one-loop first-missing-datum independent audit: PASS")
    return value


if __name__ == "__main__":
    verify()
