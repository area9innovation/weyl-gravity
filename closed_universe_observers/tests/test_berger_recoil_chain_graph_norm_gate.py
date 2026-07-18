from closed_universe_observers.generate_berger_recoil_chain_graph_norm_gate import build
def test_exact_switch_commutator_requires_derivative_control():
 v=build();assert "i_grad(h_b)dA" in v["exact_chain_identities"]["recoil_current_decomposition"];assert "nonvanishing" in v["exact_chain_identities"]["causal_scope"];assert v["flags"]["CURRENT_MAXWELL_L2_TAIL_SUFFICIENT_FOR_FACTORWISE_RECOIL_BOUND"] is False
def test_longitudinal_massive_inverse_has_no_high_mode_smoothing():
 v=build();assert v["spectral_typing"]["massive_inverse_candidate"][1][1]=="1/m2";assert v["flags"]["MAXWELL_GRAPH_NORM_TAIL_REQUIRED_OR_CANCELLATION"] is True
def test_gate_does_not_claim_full_operator_unboundedness_or_recoil():
 v=build();assert v["route_disposition"]["full_recoil_operator_unbounded_theorem"]=="NOT_CLAIMED";assert v["flags"]["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False;assert all(row["detected"] for row in v["mutation_results"])
