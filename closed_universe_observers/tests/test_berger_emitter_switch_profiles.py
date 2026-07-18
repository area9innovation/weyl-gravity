import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_emitter_switch_profiles import (
    INPUT,
    INPUT_SCHEMA,
    build,
    bump_audit,
    switch_audit,
)


def test_switch_supports_have_exact_causal_margins() -> None:
    audit = switch_audit(json.loads(INPUT.read_text()))
    assert audit["strict_causal_order"] is True
    assert audit["causal_margins_physical_time"] == ["1/24"] * 3
    assert audit["causal_margins_clock_phase"] == ["1/32"] * 3


def test_physical_time_to_clock_phase_conversion_is_exact() -> None:
    switches = switch_audit(json.loads(INPUT.read_text()))["switches"]
    assert switches[0]["support_clock_phase"] == ["7/64", "9/64"]
    assert switches[1]["support_clock_phase"] == ["15/64", "21/64"]
    assert all(item["clock_conversion_defect_count"] == 0 for item in switches)


def test_flat_bump_has_unit_clock_integral() -> None:
    audit = bump_audit()
    assert audit["C_infinity_compact_support"] is True
    assert audit["unit_clock_integral"] is True
    assert audit["clock_integral_after_change_of_variable"] == "1"


def test_switch_mutations_fail() -> None:
    data = json.loads(INPUT.read_text())
    assert switch_audit(data, mutation="move_h1_before_D0")["strict_causal_order"] is False
    assert bump_audit(omit_radius_normalization=True)["unit_clock_integral"] is False
    assert bump_audit(use_nonflat_polynomial=True)["C_infinity_compact_support"] is False


def test_input_schema_rejects_duplicate_or_reordered_switch_identity() -> None:
    data = json.loads(INPUT.read_text())
    data["switches"][1]["id"] = "h_0"
    validator = Draft202012Validator(json.loads(INPUT_SCHEMA.read_text()))
    assert list(validator.iter_errors(data))


def test_profiles_and_green_images_remain_open() -> None:
    flags = build()["flags"]
    assert flags["EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED"] is True
    assert flags["COMPACT_EMITTER_CAUCHY_PROFILES_SERIALIZED"] is False
    assert flags["MASSIVE_TWO_FORM_GREEN_IMAGES_EVALUATED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert flags["QUANTUM_CLAIM"] is False
