#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import _mul
from closed_universe_observers.generate_berger_selected_clock_power_polarized_form_rail import (
    CERTIFICATE,
    DEPENDENCIES,
    POWERS,
    ROOT,
    SCHEMA,
    _axis,
    _moment_lookup,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    assert dependencies["p0_form"]["flags"]["SELECTED_INTERVALS_UNIFORM_OVER_NORMALIZED_CLOCK_SUPPORT"] is True
    assert dependencies["clock_moments"]["flags"]["VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED"] is True
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["result_id"] == dependencies[name]["result_id"]
        assert reference["sha256"] == _sha256(path)
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == _sha256(ROOT / source["path"])
    moments = _moment_lookup(dependencies["clock_moments"])
    source_rows = dependencies["p0_form"]["polarized_form_rows"]
    rows = value["selected_form_rows"]
    assert len(source_rows) == len(rows) == 18
    maxima = {power: Fraction(0) for power in POWERS}
    metadata = ("anchor", "detector_id", "coframe_component", "coordinate", "form_two_j", "form_row", "form_column")
    for source, row in zip(source_rows, rows):
        assert all(row[name] == source[name] for name in metadata)
        assert len(row["clock_power_intervals"]) == len(POWERS)
        for power, interval in zip(POWERS, row["clock_power_intervals"]):
            assert interval["clock_power"] == power
            real = _mul(moments[power], _axis(source, "real"))
            imaginary = _mul(moments[power], _axis(source, "imaginary"))
            assert Fraction(interval["normalized_even_clock_moment"]["lower"]) == moments[power][0]
            assert Fraction(interval["normalized_even_clock_moment"]["upper"]) == moments[power][1]
            assert Fraction(interval["normalized_even_clock_moment"]["width"]) == moments[power][1] - moments[power][0]
            assert Fraction(interval["real"]["lower"]) == real[0]
            assert Fraction(interval["real"]["upper"]) == real[1]
            assert Fraction(interval["real"]["width"]) == real[1] - real[0]
            assert Fraction(interval["imaginary"]["lower"]) == imaginary[0]
            assert Fraction(interval["imaginary"]["upper"]) == imaginary[1]
            assert Fraction(interval["imaginary"]["width"]) == imaginary[1] - imaginary[0]
            width = max(real[1] - real[0], imaginary[1] - imaginary[0])
            assert Fraction(interval["maximum_axis_width"]) == width
            assert width < Fraction(1, 10)
            maxima[power] = max(maxima[power], width)
    assert value["coverage"]["complex_interval_count"] == 270
    assert value["coverage"]["p0_exact_reproduction_defect_count"] == 0
    assert value["coverage"]["canonical_selected_clock_power_rail_sha256"] == hashlib.sha256(
        json.dumps(rows, sort_keys=True).encode()
    ).hexdigest()
    assert {
        int(power): Fraction(width)
        for power, width in value["maximum_axis_width_by_clock_power"].items()
    } == maxima
    assert value["joint_clock_weighting"]["independence_assumption"] is False
    assert value["clock_power_coverage_mutation"] == {
        "name": "drop_clock_power_p28",
        "expected_clock_power_count": len(POWERS),
        "mutated_clock_power_count": len(POWERS) - 1,
        "detected": True,
    }
    assert value["flags"]["SELECTED_POLARIZED_FORM_CLOCK_POWERS_P0_TO_P28_EXPORTED"] is True
    assert value["flags"]["ALL_270_SELECTED_COMPLEX_INTERVALS_EXPORTED"] is True
    assert value["flags"]["P0_SOURCE_ROWS_REPRODUCED_EXACTLY"] is True
    assert value["flags"]["NO_CLOCK_SPATIAL_INDEPENDENCE_ASSUMED"] is True
    assert value["flags"]["ALL_SELECTED_CLOCK_POWER_WIDTHS_BELOW_ONE_TENTH"] is True
    assert value["flags"]["CLOCK_POWER_COVERAGE_MUTATION_REJECTED"] is True
    assert value["flags"]["COMPLETE_FORM_RAIL_EVALUATED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected clock-power polarized form rail verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
