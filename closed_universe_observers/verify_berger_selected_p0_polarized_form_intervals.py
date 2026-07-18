#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_p0_polarized_form_intervals import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    _scalar_lookup,
    apply_external_clock_factor,
    polarized_interval,
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
    lookup = _scalar_lookup(dependencies["closure"])
    entries = dependencies["closure"]["form_selection"]["entries"]
    rows = value["polarized_form_rows"]
    assert len(entries) == len(rows) == 18
    total_terms = 0
    for entry, row in zip(entries, rows):
        spatial_interval, applications = polarized_interval(entry, lookup)
        interval = apply_external_clock_factor(spatial_interval)
        assert row["recurrence_term_count"] == len(applications)
        assert row["term_applications"] == applications
        assert Fraction(row["spatial_recurrence_interval_before_external_clock_factor"]["real"]["lower"]) == spatial_interval[0][0]
        assert Fraction(row["spatial_recurrence_interval_before_external_clock_factor"]["real"]["upper"]) == spatial_interval[0][1]
        assert Fraction(row["spatial_recurrence_interval_before_external_clock_factor"]["imaginary"]["lower"]) == spatial_interval[1][0]
        assert Fraction(row["spatial_recurrence_interval_before_external_clock_factor"]["imaginary"]["upper"]) == spatial_interval[1][1]
        assert Fraction(row["polarized_interval"]["real"]["lower"]) == interval[0][0]
        assert Fraction(row["polarized_interval"]["real"]["upper"]) == interval[0][1]
        assert Fraction(row["polarized_interval"]["imaginary"]["lower"]) == interval[1][0]
        assert Fraction(row["polarized_interval"]["imaginary"]["upper"]) == interval[1][1]
        assert Fraction(row["polarized_interval"]["maximum_axis_width"]) < Fraction(1, 10)
        total_terms += len(applications)
    assert total_terms == value["selection"]["scalar_term_application_count"] == 54
    assert Fraction(value["maximum_selected_axis_width"]) < Fraction(99, 1000)
    assert value["term_coverage_mutation"]["detected"] is True
    assert value["external_clock_factor_mutation"]["detected"] is True
    assert value["flags"]["EXTERNAL_DETECTOR_CLOCK_FACTOR_APPLIED"] is True
    assert value["flags"]["ALL_CLOCK_POWERS_AND_COMPLETE_FORM_RAIL_EVALUATED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected p0 polarized form interval verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
