from closed_universe_observers.generate_berger_recoil_exact_mode_kernel_payload import build


def test_all_twenty_physical_finite_blocks_are_exported():
    value = build()
    assert len(value["blocks"]) == 20
    assert {block["two_j"] for block in value["blocks"]} == set(range(5))
    assert {block["family"] for block in value["blocks"]} == {"Maxwell", "massive_two_form"}


def test_exact_series_recurrence_and_sparse_payload_close():
    value = build()
    assert all(block["recurrence_defect_count_through_order4"] == 0 for block in value["blocks"])
    assert all(len(block["series_coefficients"]) == 6 for block in value["blocks"])
    assert len(value["payload_sha256"]) == 64
    assert value["mutation_results"][0]["detected"] is True


def test_symbolic_mass_is_retained_and_interval_promotion_is_fail_closed():
    value = build()
    massive = [block for block in value["blocks"] if block["family"] == "massive_two_form"]
    assert {block["mass_squared"] for block in massive} == {"mu_squared"}
    assert value["flags"]["MASS_RANGE_DECLARED"] is False
    assert value["flags"]["INTERVAL_KERNEL_ENCLOSURES_EXPORTED"] is False
