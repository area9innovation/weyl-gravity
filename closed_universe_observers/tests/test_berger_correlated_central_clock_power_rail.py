import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_correlated_central_clock_power_rail import CERTIFICATE
from closed_universe_observers.verify_berger_correlated_central_clock_power_rail import verify


def test_all_clock_power_shards_are_present() -> None:
    value = json.loads(CERTIFICATE.read_text())
    powers = {row["clock_power"] for row in value["sentinel_audits"]}
    assert powers == set(range(0, 29, 2))


def test_all_central_overlap_comparisons_pass() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["coverage"]["low_rail_overlap_comparison_count"] == 1050
    assert value["coverage"]["low_rail_overlap_defect_count"] == 0


def test_maximum_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["maximum_sentinel_widths"]["256"] = "1/1000"
    with pytest.raises(AssertionError):
        verify(value)
