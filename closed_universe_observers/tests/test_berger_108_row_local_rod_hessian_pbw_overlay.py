from fractions import Fraction

from closed_universe_observers.generate_berger_108_row_local_rod_hessian_pbw_overlay import (
    action_hessian_audit,
    build,
    connection_audit,
    levi_civita,
    mixed_wave_audit,
    payload_document,
)


def test_berger_levi_civita_table_is_exact_and_nonholonomic():
    connection = levi_civita()
    assert connection[3, 1, 2] == (Fraction(0), Fraction(3, 40))
    assert connection[2, 3, 1] == (Fraction(0), Fraction(71, 120))
    audit = connection_audit(connection)
    assert audit["torsion_defect_count"] == 0
    assert audit["metric_compatibility_defect_count"] == 0


def test_all_six_local_rod_blocks_are_present():
    payload = payload_document()
    assert {block["id"] for block in payload["blocks"]} == {
        "Gamma_R", "Gamma_R_sharp", "K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"
    }


def test_metric_hessian_matches_direct_second_variations():
    assert action_hessian_audit()["direct_second_variation_defect_count"] == 0


def test_mixed_wave_block_matches_direct_nonholonomic_variation():
    audit = mixed_wave_audit()
    assert audit["direct_nonholonomic_metric_variation_fixture_count"] == 10
    assert audit["direct_nonholonomic_metric_variation_defect_count"] == 0


def test_complete_q1_remains_a_separate_replay_gate():
    flags = build()["flags"]
    assert flags["SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED"]
    assert flags["SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED"]
    assert not flags["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    assert not flags["COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED"]
