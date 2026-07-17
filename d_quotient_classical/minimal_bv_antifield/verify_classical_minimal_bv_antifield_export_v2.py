#!/usr/bin/env python3
"""Independent replay of the classical V2 export and historical obstruction."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json"
EXPORT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
SCHEMA = ROOT / "d_quotient_classical/schema/classical-minimal-bv-antifield-export-v2-receiver-obstruction-v1.schema.json"
EXPORT_SCHEMA = ROOT / "quantum-weyl/classical_import/schema/antifield_export_v2.schema.json"

# Keep direct-file and ``python -m`` execution equivalent.
sys.path.insert(0, str(ROOT))


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    sys.path.insert(0, str(ROOT / "quantum-weyl"))
    from classical_import.verify_antifield_export_v2 import validate_export_v2
    from d_quotient_classical.minimal_bv_antifield.classical_minimal_bv_antifield_export_v2 import build_export, build_receiver_obstruction

    if payload != build_receiver_obstruction(payload["classical_commit"]):
        raise AssertionError("historical receiver obstruction drifted")
    exported = json.loads(EXPORT.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(export_schema).validate(exported)
    if exported != build_export(payload["classical_commit"]):
        raise AssertionError("official classical V2 export drifted")
    replay = validate_export_v2(exported, repository_root=ROOT)
    if replay["filtered_complex_adapter"]["scope_projection"]["status"] != "DECLARED_GRADED_WINDOW_ENFORCED":
        raise AssertionError("scope-aware receiver repair is absent")

    prefix = payload["receiver_witness"]["tower_prefix"]
    for expected, row in enumerate(prefix):
        if row["n"] != expected or row["ghost_number"] != 2 * expected:
            raise AssertionError("tower grading witness drifted")
        if row["monomial"] != ["g", *("Lie_omega" for _ in range(expected))]:
            raise AssertionError("tower monomial witness drifted")
    if payload["flags"]["CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2"] is not False:
        raise AssertionError("blocked export was promoted")
    print("CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2 export and historical obstruction: PASS")


if __name__ == "__main__":
    verify()
