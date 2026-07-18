from fractions import Fraction

from closed_universe_observers.generate_berger_massive_recoil_finite_slab_energy_constant import build


def test_longitudinal_sector_is_kept_in_massive_bound():
    value = build()
    assert value["massive_energy_theorem"]["sector_inverse"][1][1] == "1/m2"
    assert all(
        Fraction(row["recoil_current_L1_m_inverse_squared_coefficient"]) > 0
        for row in value["switch_constants"]
    )


def test_clock_normalization_is_converted_to_physical_time():
    value = build()
    for row in value["switch_constants"]:
        assert Fraction(row["h_physical_time_L1"]) == Fraction(4, 3)
        assert Fraction(row["h_physical_time_total_variation_upper"]) == 2 * Fraction(
            row["h_sup_upper"]
        )


def test_only_massive_recoil_current_tail_is_promoted():
    value = build()
    assert value["route_disposition"]["maxwell_graph_tail_to_massive_recoil_current_L1"] == (
        "CERTIFIED_FOR_SYMBOLIC_POSITIVE_MASS"
    )
    assert value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
