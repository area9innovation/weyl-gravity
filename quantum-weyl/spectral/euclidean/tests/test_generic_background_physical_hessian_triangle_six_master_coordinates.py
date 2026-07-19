from __future__ import annotations

import copy
import json

import pytest

from spectral.euclidean.generic_background_physical_hessian_triangle_six_master_coordinates import (
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_triangle_six_master_coordinates import (
    verify,
)


def _value() -> dict:
    return json.loads(OUTPUT.read_text())


def test_independent_replay() -> None:
    verify(_value())


def test_strict_schema_and_digest() -> None:
    value = _value()
    validate(value)
    mutant = copy.deepcopy(value)
    mutant["channel_rows"][0]["master_coordinates"][0]["homogeneity_weight"] += 1
    with pytest.raises(ValueError, match="digest"):
        validate(mutant)


def test_reduced_denominators_are_not_hard_coded_to_lambda5() -> None:
    value = _value()
    first = value["channel_rows"][0]["master_coordinates"]
    assert len(first[0]["coordinate"]["denominator_terms"]) > 1
    assert all(
        len(row["coordinate"]["denominator_terms"]) == 1
        for row in first[3:]
    )


def test_downstream_claims_remain_open() -> None:
    flags = _value()["claim_flags"]
    assert flags["PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"] is True
    assert flags["PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"] is False
    assert flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"] is False
    assert flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert flags["QME_RESTORED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
