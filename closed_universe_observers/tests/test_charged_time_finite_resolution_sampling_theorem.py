import sympy as sp
from closed_universe_observers.generate_charged_time_finite_resolution_sampling_theorem import build,error_audit,exact_profile_fixture,ratio_audit
def test_exact_profile_and_error_bound():
 p=exact_profile_fixture(); assert p["normalization"]=="1" and p["signed_first_moment"]=="0" and p["second_moment"]=="1/7"
 assert error_audit()["quadratic_saturates_bound"] and error_audit()["composition_symbolic_defect"]=="0"
def test_profile_mutations_fail_closed():
 assert exact_profile_fixture(normalization=sp.Rational(2))["normalization"]!="1"
 assert exact_profile_fixture(even=False)["signed_first_moment"]!="0"
 assert exact_profile_fixture(compact=False)["support_radius"]=="UNBOUNDED"
def test_ratio_and_counterflow_boundaries():
 assert ratio_audit()["origin_independent"] and not ratio_audit(co_shifted=False)["origin_independent"]
 v=build(); assert v["conditional_counterflow"]["physical_nonzero_receiver"]=="NO_CERTIFIED_MAP" and not v["flags"]["DETECTOR_OR_REDSHIFT_CERTIFIED"]
