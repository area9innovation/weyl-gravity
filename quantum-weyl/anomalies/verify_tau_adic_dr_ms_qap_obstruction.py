#!/usr/bin/env python3
"""Independent verifier for the tau-adic DR/MS QAP obstruction."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
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


OUTPUT = HERE / "certificates/TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json"
SCHEMA = HERE / "schema/tau-adic-dr-ms-qap-obstruction-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"tau-adic DR/MS obstruction schema failed: {errors}")

    for pin in value["historical_input_pins"].values():
        read_attached_blob(
            pin["source_commit"],
            pin["path"],
            pin["sha256"],
        )

    residue = value["first_incompatibility"]["nonzero_Euler_residue"]
    a = Fraction(residue["numerator"], residue["denominator"])
    finite = value["first_incompatibility"]["finite_evanescent_coefficient"]
    if (
        a == 0
        or a != Fraction(finite["numerator"], finite["denominator"])
        or value["first_incompatibility"]["status"]
        != "EXACT_EVANESCENT_CONTINUATION_DEPENDENCE"
    ):
        raise ValueError("independent pole-times-evanescent replay failed")

    failures = [
        row for row in value["qap_hypothesis_ledger"]
        if row["status"].startswith("FAILED")
    ]
    if (
        failures
        != [{
            "hypothesis": "subtraction continuous and closed in declared algebra",
            "status": "FAILED_EVANESCENT_EXTENSION_REQUIRED",
        }]
        or value["receiver_status"]
        != "REJECT_UNCONDITIONAL_ALL_LOOP_PROMOTION"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("obstruction receiver boundary crossed")

    architecture = value["declared_architecture"]
    required = ("measure", "variables", "tau_topology", "zero_modes")
    if any(not architecture.get(field) for field in required):
        raise ValueError("declared architecture is incomplete")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Tau-adic DR/MS independent evanescent-closure replay: PASS")
    return value


if __name__ == "__main__":
    verify()
