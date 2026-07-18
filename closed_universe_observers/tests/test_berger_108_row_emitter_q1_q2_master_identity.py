from closed_universe_observers.generate_berger_108_row_emitter_q1_q2_master_identity import (
    build,
    master_identity_audit,
    row_coverage_audit,
)


def test_covariant_master_identity_has_zero_defect() -> None:
    assert master_identity_audit()["total_defect_count"] == 0


def test_all_108_output_rows_are_covered_once() -> None:
    audit = row_coverage_audit()
    assert audit["covered_row_count"] == 108
    assert audit["all_output_rows_covered_exactly_once"] is True
    assert audit["certified_arity_two_defect_count_by_output_row"] == [0] * 108


def test_reciprocal_orbit_mutations_fail() -> None:
    assert master_identity_audit(remove_outer_codifferential=True)["total_defect_count"] > 0
    assert master_identity_audit(omit_clock_source=True)["total_defect_count"] > 0
    assert master_identity_audit(omit_metric_output=True)["total_defect_count"] > 0
    assert master_identity_audit(omit_clock_output=True)["total_defect_count"] > 0
    assert master_identity_audit(omit_clock_modulus_partner=True)["total_defect_count"] > 0
    assert master_identity_audit(delete_diff_cotangent_partner=True)["total_defect_count"] > 0


def test_missing_output_row_is_detected() -> None:
    audit = row_coverage_audit(delete_last_emitter_row=True)
    assert audit["missing_rows"] == [107]
    assert audit["all_output_rows_covered_exactly_once"] is False


def test_pbw_and_later_claims_remain_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED"] is True
    assert flags["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"] is False
    assert flags["COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert flags["QUANTUM_CLAIM"] is False
