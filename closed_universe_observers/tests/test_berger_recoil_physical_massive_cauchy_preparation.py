from closed_universe_observers.generate_berger_recoil_physical_massive_cauchy_preparation import build
def test_physical_cauchy_certificate_is_fail_closed_after_pair():
 v=build();assert v["flags"]["COSINE_KERNEL_DERIVATIVE_ENCLOSURE_EXPORTED"];assert v["flags"]["PHYSICAL_PROCA_TWO_FORM_GREEN_CORRECTION_EXPORTED"];assert v["flags"]["EMITTER_FULL_FORM_CAUCHY_PAIR_EXPORTED"];assert not v["flags"]["POSITIVE_ENERGY_DUAL_COEFFICIENTS_EXPORTED"]
