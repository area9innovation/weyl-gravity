from closed_universe_observers.generate_berger_coupling_stripped_detector_preparations import build


def test_preparations_are_fixed_after_stripping_the_selection_coupling():
    value = build()
    assert all(row["held_fixed_in_coupling_expansion"] for row in value["preparation_rows"])
    assert value["factorization"]["fixed_data_convention"] == (
        "tilde_u_a is held fixed in the formal coupling expansion"
    )


def test_leading_and_recoil_coupling_monomials_are_unambiguous():
    factorization = build()["factorization"]
    assert factorization["leading_diagonal"] == "M_aa^(1)=g_a tilde_E_a"
    assert factorization["absolute_g3_channel_monomial"] == "g_b g_c^2"
    assert factorization["relative_g2_channel_monomial"] == "g_c^2"


def test_harmonic_evaluation_remains_open():
    value = build()
    assert value["flags"]["COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED"] is True
    assert value["flags"]["HARMONIC_COEFFICIENTS_EVALUATED"] is False
    assert value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"] is False
