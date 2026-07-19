#!/usr/bin/env python3
"""Independently verify the 108-row apparatus scalarization obstruction."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_apparatus_q2_q3_scalarization_obstruction import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    coordinate_jet_nonuniqueness,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    witness = coordinate_jet_nonuniqueness()
    assert value["exact_nonuniqueness_witness"] == witness
    assert witness["exact_replay"]["unary_difference_count"] == 0
    assert witness["exact_replay"]["q2_difference_nonzero"] is True
    assert witness["exact_replay"]["q3_difference_nonzero"] is True
    assert value["atlas_status"] == "NO_CERTIFIED_MAP"
    assert not any(
        value["activation_disposition"][key]
        for key in value["activation_disposition"]
        if key != "physical_branch_bridge_activated"
    )
    print("BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
