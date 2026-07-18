import json

from closed_universe_observers.generate_berger_streamable_polarization_sectors import (
    CERTIFICATE,
    build,
    exact_commutator_defects,
    helicity_sectors,
    sector_entry_upper,
)


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_charge_blocks_have_dimension_at_most_three():
    for two_j in (0, 1, 4, 17, 138):
        assert max(map(len, helicity_sectors(two_j).values())) <= 3


def test_sector_entry_formula_and_scale():
    for dimension in range(2, 20):
        assert sector_entry_upper(dimension) == 9 * dimension - 8
    scale = build()["capacity_rail_scale"]
    assert scale["two_detector_input_entry_upper"] == 86736
    assert scale["all_column_charge_block_apply_upper"] == 8066172


def test_helicity_sign_mutation_breaks_commutation():
    assert exact_commutator_defects(2) == 0
    assert exact_commutator_defects(2, mutated_signs=True) > 0


def test_high_mode_values_and_tail_remain_open():
    flags = build()["flags"]
    assert flags["ALL_FINITE_TWO_J_GREEN_CHARGE_BLOCKS_EXPORTED"] is True
    assert flags["HIGH_MODE_COEFFICIENT_VALUES_EVALUATED"] is False
    assert flags["GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED"] is False
