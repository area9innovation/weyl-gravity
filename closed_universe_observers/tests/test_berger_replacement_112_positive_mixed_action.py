import json

from closed_universe_observers import generate_berger_replacement_112_positive_mixed_action as subject


def payload():
    return subject.build_payload()


def test_positive_mixed_action_and_background_pass():
    value = payload()
    assert value["mixed_action"]["K_invariance_defect_count"] == 0
    assert value["background_equation"]["Noether_defect_count"] == 0
    assert value["background_equation"]["Phi2_residual_count"] == 0


def test_complete_112_unary_passes_exact_identities():
    unary = payload()["complete_unary"]
    assert unary["q1_squared_defect_count"] == 0
    assert unary["odd_cyclicity_defect_count"] == 0
    assert unary["K_lower_order_commutator_defect_count"] == 0


def test_causal_boundary_is_fail_closed():
    gate = payload()["causal_and_charge_gate"]
    assert gate["support_local_retarded_green_parent"].startswith("G_R,ret")
    assert gate["full_off_shell_BV_propagator"] == "NO_CERTIFIED_MAP"


def test_leading_response_is_rank_two_but_not_reduced():
    observer = payload()["leading_observer_map"]
    assert observer["response_rank"] == 2
    assert observer["survives_full_112_gauge_reduction"] == "NO_CERTIFIED_MAP"


def test_written_certificate_matches_fresh_build():
    written = json.loads(subject.CERTIFICATE.read_text())
    fresh_payload = subject.build_payload()
    fresh = subject.build_certificate(fresh_payload)
    assert written == fresh
