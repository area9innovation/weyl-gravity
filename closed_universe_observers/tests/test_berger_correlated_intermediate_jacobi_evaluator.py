import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_correlated_intermediate_jacobi_evaluator import CERTIFICATE
from closed_universe_observers.verify_berger_correlated_intermediate_jacobi_evaluator import verify


def test_low_intermediate_audit_overlaps() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["low_rail_audit"]["two_j"] == 4
    assert value["low_rail_audit"]["basis_index"] == 1
    assert value["low_rail_audit"]["published_interval_overlap"] is True


def test_refined_intermediate_widths_are_below_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in value["intermediate_sentinel_audits"])
    assert Fraction(value["resolution_mutation"]["coarse_interval"]["width"]) > Fraction(1, 10)


def test_intermediate_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["intermediate_sentinel_audits"][1]["interval"]["width"] = "1/10"
    with pytest.raises(AssertionError):
        verify(value)
