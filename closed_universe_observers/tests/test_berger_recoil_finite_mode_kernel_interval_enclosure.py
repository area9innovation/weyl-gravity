import json
from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.generate_berger_recoil_exact_mode_kernel_payload import CERTIFICATE
from closed_universe_observers.generate_berger_recoil_finite_mode_kernel_interval_enclosure import build


def _payload():
    return json.loads(CERTIFICATE.read_text())


def test_zero_Maxwell_mode_is_exact_tau_identity():
    result = enclose_exact_mode_sine_kernel(
        _payload(),
        two_j=0,
        family="Maxwell",
        form_degree=0,
        mass_squared_interval=RationalInterval.point(0),
        slab_length=Fraction(1, 16),
    )
    assert result["uniform_sine_kernel_remainder_upper"] == "0"
    assert [len(row["entries"]) for row in result["coefficient_matrices"]] == [1, 0, 0, 0, 0, 0]


def test_massive_interval_and_algebraic_Maxwell_block_are_enclosed():
    massive = enclose_exact_mode_sine_kernel(
        _payload(),
        two_j=0,
        family="massive_two_form",
        form_degree=1,
        mass_squared_interval=RationalInterval(Fraction(1), Fraction(2)),
        slab_length=Fraction(1, 48),
    )
    assert massive["operator_row_sum_norm_upper"] == "58/9"
    assert Fraction(massive["uniform_sine_kernel_remainder_upper"]) > 0
    algebraic = enclose_exact_mode_sine_kernel(
        _payload(),
        two_j=4,
        family="Maxwell",
        form_degree=1,
        mass_squared_interval=RationalInterval.point(0),
        slab_length=Fraction(1, 48),
    )
    assert algebraic["dimension"] == 15
    assert Fraction(algebraic["tail_ratio_upper"]) < 1
    assert any(
        entry["imaginary"]["upper"] != "0"
        for coefficient in algebraic["coefficient_matrices"]
        for entry in coefficient["entries"]
    )


def test_all_twenty_five_exact_payload_blocks_accept_the_certified_interval_contract():
    payload = _payload()
    results = []
    for block in payload["blocks"]:
        results.append(
            enclose_exact_mode_sine_kernel(
                payload,
                two_j=block["two_j"],
                family=block["family"],
                form_degree=block["form_degree"],
                mass_squared_interval=(
                    RationalInterval.point(0)
                    if block["family"] == "Maxwell"
                    else RationalInterval(Fraction(1), Fraction(2))
                ),
                slab_length=Fraction(1, 64),
            )
        )
    assert len(results) == 25
    assert all(Fraction(result["tail_ratio_upper"]) < 1 for result in results)


def test_mass_and_tail_contracts_fail_closed():
    payload = _payload()
    with pytest.raises(ValueError, match="strictly positive"):
        enclose_exact_mode_sine_kernel(
            payload,
            two_j=0,
            family="massive_two_form",
            form_degree=1,
            mass_squared_interval=RationalInterval(Fraction(0), Fraction(1)),
            slab_length=Fraction(1, 48),
        )
    with pytest.raises(ValueError, match="exact zero"):
        enclose_exact_mode_sine_kernel(
            payload,
            two_j=0,
            family="Maxwell",
            form_degree=0,
            mass_squared_interval=RationalInterval.point(1),
            slab_length=Fraction(1, 48),
        )
    with pytest.raises(ValueError, match="does not contract"):
        enclose_exact_mode_sine_kernel(
            payload,
            two_j=0,
            family="massive_two_form",
            form_degree=1,
            mass_squared_interval=RationalInterval(Fraction(1), Fraction(2)),
            slab_length=Fraction(10),
        )


def test_certificate_keeps_physical_binding_open():
    value = build()
    assert value["flags"]["FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED"] is True
    assert value["flags"]["MASSIVE_ONE_FORM_CORRECTION_KERNEL_INTERVALS_EXPORTED"] is True
    assert value["flags"]["PHYSICAL_MASS_SPECIALIZATION_EXPORTED"] is False
    assert value["flags"]["ACTUAL_SWITCH_PROFILE_AND_FORM_BINDING_EXPORTED"] is False
