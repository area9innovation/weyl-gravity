from fractions import Fraction

from closed_universe_observers.generate_berger_downstream_maxwell_detector_dual_norms import build


def test_clock_lapse_cancels_in_detector_pairing():
    value = build()
    assert value["clock_lapse_cancellation"]["product"] == "(4/3)*(3/4)=1"


def test_both_detector_dual_norms_are_positive_and_distinct():
    rows = build()["detector_dual_norms"]
    assert len(rows) == 2
    assert all(Fraction(row["detector_energy_dual_norm_upper"]) > 0 for row in rows)
    assert Fraction(rows[1]["spatial_profile_L2_norm_squared_upper"]) == Fraction(40, 9) * Fraction(
        rows[0]["spatial_profile_L2_norm_squared_upper"]
    )


def test_four_symbolic_tail_radii_retain_both_mass_powers():
    rows = build()["retarded_energy_composition"]["four_channel_bounds"]
    assert len(rows) == 4
    assert all(Fraction(row["dual_times_m_inverse_squared_coefficient"]) > 0 for row in rows)
    assert all(Fraction(row["dual_times_m_inverse_coefficient"]) > 0 for row in rows)


def test_numerical_recoil_is_not_promoted():
    value = build()
    assert value["route_disposition"]["complete_modewise_scalar_integrand"] == "OPEN"
    assert value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
