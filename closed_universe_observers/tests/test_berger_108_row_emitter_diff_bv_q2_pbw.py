from closed_universe_observers.generate_berger_108_row_emitter_diff_bv_q2_pbw import (
    build,
    cartan_audit,
    emitter_tensor,
    graded_symmetry_defects,
    payload_document,
    scalar_template_audit,
)


def test_two_form_lie_derivative_is_cartan_formula():
    assert cartan_audit()["Cartan_formula_defect_count"] == 0


def test_cotangent_engine_recovers_certified_scalar_template():
    assert scalar_template_audit()["scalar_BV_template_recovery_defect_count"] == 0


def test_emitter_diff_tensor_is_graded_symmetric():
    tensor, _ = emitter_tensor()
    assert graded_symmetry_defects(tensor) == 0


def test_complete_emitter_but_not_complete_scalar_q2():
    value = build()
    assert value["activation_disposition"]["complete_emitter_q2_exported"] is True
    assert value["activation_disposition"]["complete_scalar_q2_payload_assembled"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False


def test_payload_covers_field_cotangent_and_ghost_cotangent_rows():
    rows = set(payload_document()["nonzero_output_rows"])
    assert set(range(84, 108)) <= rows
    assert {49, 50, 51, 52} <= rows
