import json

from jsonschema import Draft202012Validator

from closed_universe_observers import (
    generate_berger_recoil_reality_folded_shell_stream_adapter as generator,
)


def test_emitted_adapter_certificate_is_schema_valid_and_fail_closed():
    value = json.loads(generator.CERTIFICATE.read_text())
    schema = json.loads(generator.SCHEMA.read_text())
    Draft202012Validator(schema).validate(value)
    replay = value["two_j6_validation_replay"]
    assert replay["representative_columns_called"] == [0, 1, 2, 3]
    assert replay["completed_columns_exact_match"] is True
    assert replay["stop_evaluation"]["lifecycle_status"] == "OPEN"
    assert len(replay["aggregate_rows"]) == 4
    assert all(row["detected"] for row in value["mutation_results"])
    assert value["flags"]["PHYSICAL_MASS_COUPLING_SPECIALIZATION_EXPORTED"] is False
    assert value["flags"]["RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED"] is False
