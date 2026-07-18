from closed_universe_observers.generate_berger_recoil_stream_executable_readiness_audit import build


def test_symbolic_word_is_not_promoted_to_an_interval_backend():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["rows"]}
    assert rows["complete_symbolic_operator_word"] == "CERTIFIED"
    assert rows["shell_interval_evaluator"] == "CERTIFIED"
    assert rows["tail_aware_aggregate_stop_loop"] == "OBSTRUCTED"
    assert value["atlas_status"] == "OBSTRUCTED"


def test_external_specialization_is_deferred_until_backend_exists():
    value = build()
    assert value["readiness"]["internal_executable_stream_ready"] is False
    assert value["readiness"]["external_specialization_deferred"] is True
    assert value["flags"]["NUMERICAL_SPECIALIZATION_INPUT_SCHEMA_EXPORTED"] is True
    assert value["flags"]["NUMERICAL_SPECIALIZATION_VALUES_DECLARED"] is False


def test_shell_aggregation_closes_but_three_execution_capabilities_remain_fail_closed():
    rows = build()["readiness"]["rows"][1:]
    assert len(rows) == 4
    assert [row["status"] for row in rows].count("CERTIFIED") == 1
    assert [row["status"] for row in rows].count("OBSTRUCTED") == 3
