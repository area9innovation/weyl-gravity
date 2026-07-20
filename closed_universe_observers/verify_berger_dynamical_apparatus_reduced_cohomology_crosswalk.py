#!/usr/bin/env python3
"""Independent audit of the apparatus combined-q1 crosswalk shortfall."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json"
X = P / "certificates/BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT.json"
SCHEMA = (
    P
    / "schema/berger-dynamical-apparatus-reduced-cohomology-crosswalk-v1.schema.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, contract = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["contract_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    parent = json.loads(
        (P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json").read_text()
    )
    independently_absent = {
        "row_level_q1_entries": "q1_entries" not in parent,
        "combined_carrier_embedding": "combined_carrier" not in parent,
        "row_level_pairing_entries": "odd_pairing_entries" not in parent["carrier"],
        "row_level_K_action": "K_Berger_matrix" not in parent,
        "cohomological_degrees": "cohomological_degrees" not in parent["carrier"],
        "real_structure_matrix": "real_structure_matrix" not in parent,
        "smearing_to_Maxwell_chain_map": "smearing_to_Maxwell_chain_map" not in parent,
        "zero_mode_support_category": "zero_mode_support_category" not in parent,
    }
    assert independently_absent == contract["current_absence_audit"]
    assert all(independently_absent.values())
    assert contract["base_carrier_choice"]["status"] == "UNRESOLVED"
    assert len(contract["required_row_table_columns"]) == 10
    assert len(contract["required_verification"]) == 10
    assert cert["capability_audit"]["verdict"] == (
        "CROSSWALK_REQUIRED_BEFORE_REDUCTION"
    )
    assert all(
        value == "NO_CERTIFIED_MAP"
        for value in cert["downstream_disposition"].values()
    )
    assert "no exact combined kernel" in cert["claim_boundary"]
    print(
        "BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
