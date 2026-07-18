#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_polarization_recurrence_scalar_closure import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    _closure,
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
    entries = value["form_selection"]["entries"]
    assert len(entries) == 18
    closure = _closure(entries)
    assert [list(row) for row in closure] == value["scalar_closure"]["required_rows"]
    assert len(closure) == 12
    imported = value["scalar_closure"]["imported_rows"]
    new = value["scalar_closure"]["newly_evaluated_rows"]
    assert len(imported) == 3 and len(new) == 9
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in imported + new)
    assert [row["radial_subdivisions"] for row in new if row["basis_index"] >= 383] == [128, 128, 128]
    mutation = value["same_index_only_mutation"]
    assert mutation["omitted_required_row_count"] == 6
    assert mutation["detected"] is True
    assert value["flags"]["SELECTED_POLARIZED_FORM_INTERVALS_EVALUATED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("polarization recurrence scalar closure verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
