from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from closed_universe_observers.berger_recoil_numerical_input_contract import (
    DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS,
    serialize_runtime_kwargs,
    translate_numerical_specialization,
)
from closed_universe_observers.generate_berger_recoil_numerical_input_contract import (
    build,
    mutation_audit,
    validation_declarations,
)


ROOT = Path(__file__).resolve().parents[2]


def test_all_four_runtime_goals_translate_without_activation():
    translated = [translate_numerical_specialization(value) for value in validation_declarations()]
    assert {row["runtime_kwargs"]["goal"]["type"] for row in translated} == {
        "entry_tolerance", "entry_nonzero", "entry_sign", "rank_two"
    }
    assert all(row["physical_activation_eligible"] is False for row in translated)


def test_mass_representation_is_squared_exactly():
    runtime = translate_numerical_specialization(validation_declarations()[0])["runtime_kwargs"]
    assert runtime["mass_squared_intervals"][0].serialize() == {
        "lower": "1", "upper": "9/4", "width": "5/4"
    }
    assert runtime["mass_squared_intervals"][1].serialize() == {
        "lower": "4", "upper": "25/4", "width": "9/4"
    }


def test_mass_squared_representation_is_not_squared_again():
    declaration = validation_declarations()[0]
    declaration["mass_domain"]["representation"] = "mass_squared"
    runtime = translate_numerical_specialization(declaration)["runtime_kwargs"]
    assert runtime["mass_squared_intervals"][0].serialize()["upper"] == "3/2"


def test_translation_covers_exact_runtime_argument_contract():
    runtime = translate_numerical_specialization(validation_declarations()[0])["runtime_kwargs"]
    assert tuple(runtime) == DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS
    assert serialize_runtime_kwargs(runtime)["initial_partial_intervals"] is None


def test_shell_and_tail_maps_are_exact():
    runtime = translate_numerical_specialization(validation_declarations()[0])["runtime_kwargs"]
    assert runtime["two_js"] == [7, 8]
    assert set(runtime["tail_radii_by_two_j"]) == {7, 8}
    assert set(runtime["tail_radii_by_two_j"][7]) == {(0, 0), (0, 1), (1, 0), (1, 1)}


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.__setitem__("two_js", [7, 7]),
        lambda d: d.__setitem__("two_js", [7, 9]),
        lambda d: d["tail_radii_by_two_j"][0]["radii"].pop("10"),
        lambda d: d["couplings"].__setitem__("0", "0"),
        lambda d: d.pop("provenance"),
    ],
)
def test_fail_closed_mutations(mutation):
    declaration = validation_declarations()[0]
    mutation(declaration)
    with pytest.raises((ValidationError, ValueError)):
        translate_numerical_specialization(declaration)


def test_complete_mutation_audit_detects_every_required_failure():
    rows = mutation_audit(validation_declarations()[0])
    assert len(rows) == 11
    assert all(row["detected"] for row in rows)


def test_certificate_keeps_physical_claims_false():
    value = build()
    assert value["legacy_v1_audit"]["status"] == "OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH"
    assert value["flags"]["EXACT_NUMERICAL_INPUT_CONTRACT_V2_EXPORTED"] is True
    assert value["flags"]["PHYSICAL_SPECIALIZATION_VALUES_DECLARED"] is False
    assert value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"] is False
    assert value["flags"]["RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED"] is False


def test_fixture_is_explicitly_validation_only():
    fixture = json.loads((ROOT / "closed_universe_observers/fixtures/berger_recoil_numerical_input_contract_validation.json").read_text())
    assert fixture["fixture_status"] == "VALIDATION_ONLY_NOT_PHYSICAL_DATA"
    assert fixture["base_declaration"]["declaration_status"] == "VALIDATION_ONLY"
