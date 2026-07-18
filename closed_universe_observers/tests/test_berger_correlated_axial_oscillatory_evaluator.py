import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_correlated_axial_oscillatory_evaluator import CERTIFICATE
from closed_universe_observers.verify_berger_correlated_axial_oscillatory_evaluator import verify


def test_low_axial_audits_overlap() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert [row["two_j"] for row in value["low_rail_audits"]] == [0, 1, 2, 3, 4]
    assert all(row["published_interval_overlap"] for row in value["low_rail_audits"])


def test_refined_high_axial_widths_are_below_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in value["high_axial_sentinel_audits"])
    assert Fraction(value["resolution_mutation"]["coarse_interval"]["width"]) > Fraction(1, 10)


def test_refined_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["high_axial_sentinel_audits"][0]["interval"]["width"] = "1/10"
    with pytest.raises(AssertionError):
        verify(value)
