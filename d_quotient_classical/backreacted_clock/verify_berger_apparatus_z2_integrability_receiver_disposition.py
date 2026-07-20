#!/usr/bin/env python3
"""Method-distinct replay of the Berger apparatus Z2 receiver disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / (
    "d_quotient_classical/certificates/"
    "BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1.json"
)
SCHEMA = ROOT / (
    "d_quotient_classical/schema/"
    "berger-apparatus-z2-integrability-receiver-disposition-v1.schema.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    records = {}
    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
        record = json.loads(path.read_text())
        if record.get("result_id", record.get("schema")) != ref["artifact_id"]:
            raise ValueError(f"dependency identity drifted: {name}")
        records[name] = record
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source hash drifted: {relative}")

    # This priority replay is intentionally not imported from the producer.
    combined_obstructed = (
        records["combined_q1_crosswalk_obstruction"]["claim_status"]
        == "OBSTRUCTED_NO_BACKGROUND_PRESERVING_LINEAR_K_ON_DECLARED_COMBINED_CARRIER"
    )
    combined_exact = records["combined_q1_crosswalk_obstruction"][
        "exact_obstruction"
    ]
    q2_obstructed = records["arity_two_obstruction"]["flags"][
        "COMPLETE_108_ROW_ARITY_TWO_OBSTRUCTED"
    ]
    k_background_open = not records["apparatus_K_gate"]["flags"][
        "K_BERGER_BACKGROUND_PRESERVING_ON_APPARATUS"
    ]
    preparations_exist = records["detector_selected_preparations"]["flags"][
        "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED"
    ]
    pairing_exists = records["component_and_pairing_contract"]["flags"][
        "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED"
    ]
    if not (
        combined_obstructed
        and combined_exact["global_rod_closure"]["current_real_rod_span_rank"]
        == 6
        and combined_exact["global_rod_closure"][
            "time_translation_closure_rank"
        ]
        == 8
        and combined_exact[
            "parent_material_rows_cannot_supply_missing_directions"
        ]["constant_mixing_nullity"]
        == 0
        and q2_obstructed
        and k_background_open
        and preparations_exist
        and pairing_exists
    ):
        raise ValueError("independent gate vector changed")
    if value["ordered_gate_disposition"][0]["object"] != (
        "combined_q1_pairing_real_K_carrier"
    ):
        raise ValueError("first missing operator is not the earliest gate")
    if value["ordered_gate_disposition"][0]["status"] != "OBSTRUCTED":
        raise ValueError("terminal combined-q1 obstruction was not imported")
    if value["combined_q1_crosswalk_obstruction"]["global_no_go"] is not False:
        raise ValueError("scoped obstruction was globalized")
    if value["strict_receiver_contract"]["quadratic_pairs"] != [
        "(u_0,u_0)",
        "(u_0,u_1)",
        "(u_1,u_1)",
    ]:
        raise ValueError("mixed preparation source was dropped")
    if any(
        row != "NO_CERTIFIED_MAP"
        for row in value["strict_receiver_contract"]["required_outputs"].values()
    ):
        raise ValueError("undefined receiver output was promoted")
    if value["downstream_disposition"] != {
        "Z2_Berger": "NO_CERTIFIED_MAP",
        "nonlinear_detector_rank": "NO_CERTIFIED_MAP",
        "particle": "NO_CERTIFIED_MAP",
        "q3": "NO_CERTIFIED_MAP",
        "quantum": "NO_CERTIFIED_MAP",
        "redshift": "NO_CERTIFIED_MAP",
        "relational_memory": "NO_CERTIFIED_MAP",
    }:
        raise ValueError("downstream fail-closed ledger drifted")
    print(
        "BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1 "
        "independent verification: PASS"
    )
    return value


if __name__ == "__main__":
    verify()
