#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_two_j138_exact_t_input_tail_obstruction import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["result_id"] == json.loads(path.read_text())["result_id"]
        assert reference["sha256"] == _sha256(path)
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == _sha256(ROOT / source["path"])
    audit = value["cutoff_audit"]
    assert audit["retained_form_two_j_maximum"] + 1 == audit["first_omitted_form_two_j"]
    witness = audit["witness"]
    assert Fraction(witness["selected_spatial_absolute_lower"]) > Fraction(4, 5)
    assert Fraction(witness["temporal_absolute_lower"]) > Fraction(4, 5)
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["flags"]["TWO_J138_UNIFORM_SMALL_INPUT_TAIL_CERTIFIED"] is False
    assert value["flags"]["INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("two_j138 exact-T input-tail obstruction verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
