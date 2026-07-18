#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_charge_block_form_companion_clock_rail import (
    CERTIFICATE,
    DEPENDENCIES,
    POWERS,
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
    companions = value["form_companion_rows"]
    expected = {
        (row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"])
        for row in dependencies["closure_gate"]["missing_on_support_real_form_entries"]
    }
    actual = {(row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"]) for row in companions}
    assert actual == expected and len(companions) == 33
    assert sum(row["recurrence_term_count"] for row in companions) == 84
    for row in companions:
        assert tuple(power["clock_power"] for power in row["clock_power_intervals"]) == POWERS
        assert all(Fraction(power["maximum_axis_width"]) < Fraction(1, 10) for power in row["clock_power_intervals"])
    blocks = value["completed_charge_block_inputs"]
    assert len(blocks) == 18
    assert all(tuple(row["clock_power"] for row in block["clock_power_helicity_vectors"]) == POWERS for block in blocks)
    assert all(len(row["helicity_input_vector"]) == 3 for block in blocks for row in block["clock_power_helicity_vectors"])
    assert value["coverage"]["form_companion_complex_interval_count"] == 495
    assert value["coverage"]["clock_power_helicity_vector_count"] == 270
    digest = hashlib.sha256(json.dumps({"companions": companions, "block_vectors": blocks}, sort_keys=True).encode()).hexdigest()
    assert value["coverage"]["canonical_completed_charge_block_input_sha256"] == digest
    assert value["deleted_companion_mutation"]["detected"] is True
    assert value["flags"]["ALL_18_SELECTED_CHARGE_BLOCK_INPUTS_CLOSED"] is True
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected charge-block form companion clock rail verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
