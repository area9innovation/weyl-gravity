import copy

import pytest

from closed_universe_observers import generate_berger_repaired112_physical_reduction_and_detector_rank_not_activated as subject


def test_nondefined_pushout_does_not_activate_reduction():
    gate = subject.build_payload()["activation_gate"]
    assert gate["apparatus_pushout"] == "NONDEFINED"
    assert gate["combined_row_count"] == "NO_CERTIFIED_MAP"
    assert gate["verdict"] == "NOT_ACTIVATED"


def test_all_support_and_zero_mode_sectors_fail_closed():
    sectors = subject.build_payload()["sector_disposition"]
    assert set(sectors) == {"generic_smooth", "compact_support", "spatial_zero_mode"}
    assert all(set(sector.values()) == {"NO_CERTIFIED_MAP"} for sector in sectors.values())


def test_contraction_pairing_and_detector_outputs_are_not_fabricated():
    payload = subject.build_payload()
    assert set(payload["contraction_and_pairing_disposition"].values()) == {"NO_CERTIFIED_MAP"}
    assert set(payload["observer_class_disposition"].values()) == {"NO_CERTIFIED_MAP"}


def test_material_rank_two_is_explicitly_not_a_physical_rank():
    fact = subject.build_payload()["separate_material_fact"]
    assert fact["standalone_material_coordinate_detector_rank"] == 2
    assert fact["status"] == "CERTIFIED_SEPARATE"
    assert fact["not_a_physical_combined_rank"] is True


def test_pre_repair_carrier_and_raw_rows_are_rejected():
    assert all(value.startswith("REJECTED") for value in subject.build_payload()["forbidden_imports"].values())


def test_false_pushout_activation_mutation_is_rejected():
    values = {name: subject.json.loads(path.read_text()) for name, path in subject.DEPS.items()}
    mutated = copy.deepcopy(values)
    mutated["pushout_payload"]["category_of_complexes_gate"]["apparatus_pushout"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        subject.validate_terminal_branch(mutated)


def test_replay_retains_nonzero_augmented_separator():
    replay = subject.build_payload()["method_distinct_obstruction_replay"]
    assert replay["coefficient_matrix_rank"] == 1
    assert replay["augmented_matrix_rank"] == 2
    assert replay["canonical_augmented_determinant"] != "0"
    assert replay["background_preserving_correction_dimension"] == 0
