import json
import pytest

from closed_universe_observers import generate_berger_replacement112_mixed_metric_rod_hessian_interface as subject
from closed_universe_observers.verify_berger_replacement112_mixed_metric_rod_hessian_interface import verify


@pytest.fixture(scope="module")
def payload():
    return subject.build_payload()


def test_all_six_action_and_diff_block_families_are_serialized(payload):
    assert set(payload["operator_blocks"]) == {"Gamma_R", "Gamma_R_sharp", "K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"}
    assert all(set(parts) == {"eight_rod_addition", "six_rod_subtraction", "net_replacement_delta"} for parts in payload["operator_blocks"].values())


def test_frozen_carrier_and_odd_pairing_are_complete(payload):
    carrier = payload["carrier"]
    assert carrier["scalar_matrix_shape"] == [112, 112]
    assert carrier["rod_field_rows"] == [64, 65, 66, 67, 68, 69, 108, 109]
    assert carrier["rod_cotangent_rows"] == [74, 75, 76, 77, 78, 79, 110, 111]
    assert len(carrier["odd_pairing"]) == 16


def test_exact_audits_support_and_mutation_pass(payload):
    audit = payload["formal_adjoint_and_hessian_audit"]
    assert not any(value for key, value in audit.items() if key.endswith("defect_count"))
    assert payload["K_Berger_interface"]["invariance_defect_count"] == 0
    assert payload["independent_variation_anchor"]["sign_flip_mutation_defect_count"] == 1
    assert "retained as a hyperbolic time sector" in payload["support_and_zero_modes"]["spatial_zero_mode_action"]


def test_independent_full_transpose_and_action_reconstruction():
    verify()


def test_written_result_matches_fresh_build(payload):
    assert json.loads(subject.X.read_text()) == payload
    assert json.loads(subject.C.read_text()) == subject.build_certificate(payload)
