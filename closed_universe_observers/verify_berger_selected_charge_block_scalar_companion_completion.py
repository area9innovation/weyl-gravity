#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_charge_block_scalar_companion_completion import (
    CERTIFICATE,
    DEPENDENCIES,
    EXPECTED_MISSING,
    ROOT,
    SCHEMA,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["result_id"] == dependencies[name]["result_id"]
        assert reference["sha256"] == _sha256(path)
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == _sha256(ROOT / source["path"])
    new_rows = value["newly_evaluated_scalar_rows"]
    assert tuple((row["two_j"], row["basis_index"]) for row in new_rows) == EXPECTED_MISSING
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in new_rows)
    assert [row["radial_subdivisions"] for row in new_rows] == [64, 64, 128, 64, 64, 128]
    complete = value["complete_scalar_input_rows"]
    required = {
        tuple(scalar_row)
        for entry in dependencies["closure_gate"]["missing_on_support_real_form_entries"]
        for scalar_row in entry["required_scalar_rows"]
    }
    assert {(row["two_j"], row["basis_index"]) for row in complete} == required
    assert len(complete) == 18
    digest = hashlib.sha256(json.dumps(new_rows, sort_keys=True).encode()).hexdigest()
    assert value["coverage"]["canonical_new_scalar_companion_sha256"] == digest
    assert Fraction(value["coverage"]["maximum_new_scalar_interval_width"]) == max(
        Fraction(row["interval"]["width"]) for row in new_rows
    )
    assert value["deleted_row_mutation"]["detected"] is True
    assert value["flags"]["ALL_18_CHARGE_BLOCK_FORM_SCALAR_INPUT_ROWS_PRESENT"] is True
    assert value["flags"]["THIRTY_THREE_ON_SUPPORT_FORM_COMPANIONS_EVALUATED"] is False
    assert value["flags"]["SELECTED_INPUT_RAIL_CHARGE_BLOCK_CLOSED"] is False
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected charge-block scalar companion completion verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
