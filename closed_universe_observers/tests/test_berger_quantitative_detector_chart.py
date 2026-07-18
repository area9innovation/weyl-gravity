from closed_universe_observers.generate_berger_quantitative_detector_chart import chart_audit
def test_exact_inverse_and_jacobian()->None:
 a=chart_audit();assert a["forward_inverse_defect_count"]==0;assert a["rod_jacobian"]=="8*c*a(t)^3"
def test_fixed_radius_has_large_positive_branch_margin()->None:assert chart_audit()["positive_branch_margin_y_norm_squared_below_1_over_10000"]
def test_double_radius_mutation_fails_margin()->None:assert not chart_audit(double_radius=True)["positive_branch_margin_y_norm_squared_below_1_over_10000"]
def test_cosine_lower_bound_is_positive()->None:assert chart_audit()["cosine_lower_bound"]=="82915/82944"
