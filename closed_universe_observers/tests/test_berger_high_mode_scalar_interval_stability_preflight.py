import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_high_mode_scalar_interval_stability_preflight import (
    CERTIFICATE,
    _clip_unit_bound,
)
from closed_universe_observers.verify_berger_high_mode_scalar_interval_stability_preflight import verify


def test_exact_unit_bound_clipping() -> None:
    assert _clip_unit_bound((Fraction(-10), Fraction(11))) == (Fraction(-1), Fraction(1))


def test_unit_bound_does_not_fake_decay() -> None:
    value = json.loads(CERTIFICATE.read_text())
    widened = {row["two_j"]: row for row in value["sentinel_audits"]}[256]
    assert Fraction(widened["unit_bound_intersection_width"]) == 2


def test_raw_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    widened = {row["two_j"]: row for row in value["sentinel_audits"]}[256]
    widened["raw_width"] = str(10**8)
    with pytest.raises(AssertionError):
        verify(value)
