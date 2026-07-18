from closed_universe_observers.generate_berger_recoil_chain_graph_norm_gate import build


def test_exact_switch_commutator_requires_derivative_control():
    value = build()
    identities = value["exact_chain_identities"]
    assert "i_grad(h_b)dA" in identities["recoil_current_decomposition"]
    assert "nonvanishing" in identities["causal_scope"]
    assert value["flags"]["CURRENT_MAXWELL_L2_TAIL_SUFFICIENT_FOR_FACTORWISE_RECOIL_BOUND"] is False


def test_longitudinal_massive_inverse_has_no_high_mode_smoothing():
    value = build()
    assert value["spectral_typing"]["massive_inverse_candidate"][1][1] == "1/m2"
    assert value["flags"]["MAXWELL_GRAPH_NORM_TAIL_REQUIRED_OR_CANCELLATION"] is True


def test_gate_does_not_claim_full_operator_unboundedness_or_recoil():
    value = build()
    assert value["route_disposition"]["full_recoil_operator_unbounded_theorem"] == "NOT_CLAIMED"
    assert value["flags"]["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
