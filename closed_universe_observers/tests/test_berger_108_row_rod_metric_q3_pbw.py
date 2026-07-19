import json

from closed_universe_observers.generate_berger_108_row_rod_metric_q3_pbw import (
    CERTIFICATE,
    PAYLOAD,
    density_derivative,
)


def documents():
    return json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())


def test_fourth_density_jet_has_independent_exact_checks():
    certificate, _ = documents()
    audit = certificate["action_and_cyclicity_audit"]
    assert audit["lower_order_density_component_defect_count"] == 0
    assert audit["direct_fourth_metric_variation_defect_count"] == 0
    assert audit["fourth_frechet_permutation_defect_count"] == 0
    assert density_derivative((0, 1, 2, 3)) == density_derivative((3, 1, 0, 2))


def test_all_five_quartic_rod_action_orbits_are_nonempty():
    _, payload = documents()
    blocks = payload["orbit_blocks"]
    assert set(blocks) == {"hhrr_metric_output", "hhhr_metric_output", "hhhh_metric_output", "hhr_rod_output", "hhh_rod_output"}
    assert all(block["operator_key_count"] > 0 for block in blocks.values())


def test_rod_q3_is_graded_symmetric_and_cyclic():
    certificate, _ = documents()
    audit = certificate["action_and_cyclicity_audit"]
    assert audit["graded_symmetry_defect_count"] == 0
    assert audit["hhrr_to_hhr_formal_transpose_defect_count"] == 0
    assert audit["hhhr_to_hhh_formal_transpose_defect_count"] == 0


def test_payload_has_exact_metric_and_rod_cotangent_support():
    _, payload = documents()
    assert payload["nonzero_output_rows"] == list(range(27, 37)) + list(range(74, 80))
    assert payload["operator_key_count"] > 0
    assert payload["serialized_term_count"] >= payload["operator_key_count"]


def test_subblock_remains_fail_closed_downstream():
    certificate, _ = documents()
    disposition = certificate["activation_disposition"]
    assert disposition["rod_metric_q3_subblock_exported"] is True
    assert disposition["complete_scalar_q3_exported"] is False
    assert disposition["arity_replay_certified"] is False
    assert disposition["K_Berger_equivariance_certified"] is False
    assert disposition["observer_morphism_stability_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
