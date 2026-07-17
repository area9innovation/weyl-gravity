#!/usr/bin/env python3
"""Independent replay of the V2 receiver obstruction."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json"
SCHEMA = ROOT / "d_quotient_classical/schema/classical-minimal-bv-antifield-export-v2-receiver-obstruction-v1.schema.json"


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    sys.path.insert(0, str(ROOT / "quantum-weyl"))
    from classical_import.verify_antifield_export_v2 import AntifieldExportV2Error, validate_export_v2
    from d_quotient_classical.minimal_bv_antifield.classical_minimal_bv_antifield_export_v2 import build_export

    candidate = build_export(payload["classical_commit"])
    try:
        validate_export_v2(candidate)
    except AntifieldExportV2Error as exc:
        if str(exc) != payload["receiver_witness"]["failure"]:
            raise AssertionError("receiver failure drifted") from exc
    else:
        raise AssertionError("receiver unexpectedly accepted the untruncated tower")

    prefix = payload["receiver_witness"]["tower_prefix"]
    for expected, row in enumerate(prefix):
        if row["n"] != expected or row["ghost_number"] != 2 * expected:
            raise AssertionError("tower grading witness drifted")
        if row["monomial"] != ["g", *("Lie_omega" for _ in range(expected))]:
            raise AssertionError("tower monomial witness drifted")
    if payload["flags"]["CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2"] is not False:
        raise AssertionError("blocked export was promoted")
    print("CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2 receiver obstruction: PASS")


if __name__ == "__main__":
    verify()
