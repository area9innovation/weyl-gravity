#!/usr/bin/env python3
import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_charge_block_companion_closure_gate import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    derive,
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
    derived = derive(dependencies)
    for key in ("charge_blocks", "missing_on_support_real_form_entries", "missing_scalar_rows", "coverage"):
        assert value[key] == derived[key]
    statuses = {
        component["status"]
        for block in value["charge_blocks"]
        for member in block["members"]
        for component in member["real_components"]
    }
    assert statuses == {"SELECTED", "MISSING_ON_SUPPORT", "STRUCTURAL_ZERO"}
    assert value["direct_promotion_mutation"]["incorrect_zero_count"] == 33
    assert value["direct_promotion_mutation"]["detected"] is True
    assert value["flags"]["SELECTED_INPUT_RAIL_CHARGE_BLOCK_CLOSED"] is False
    assert value["flags"]["DIRECT_SELECTED_RAIL_TEMPORAL_PROMOTION_OBSTRUCTED"] is True
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected charge-block companion closure gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
