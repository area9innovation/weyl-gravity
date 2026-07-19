from __future__ import annotations

import copy
import json

import pytest

from spectral.euclidean.generic_background_physical_hessian_triangle_relative_ibp_boundary_flux import (
    INTEGRATED_BASIS,
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_triangle_relative_ibp_boundary_flux import (
    verify,
)


def _value() -> dict:
    return json.loads(OUTPUT.read_text())


def test_independent_exact_holdout_replay() -> None:
    verify(_value())


def test_strict_schema_and_digest() -> None:
    value = _value()
    validate(value)
    mutant = copy.deepcopy(value)
    mutant["channel_rows"][0]["corner_rows"][0][
        "angular_numerator_coefficients"
    ][0]["numerator_terms"][0]["coefficient"]["numerator"] += 1
    with pytest.raises(ValueError, match="digest"):
        validate(mutant)


def test_all_channels_have_complete_structured_basis() -> None:
    value = _value()
    assert value["identity_ledger"] == {
        "channel_count": 11,
        "tangent_identity_count": 11,
        "corner_count": 33,
        "integrated_basis_coordinate_count": 77,
        "symmetric_scale_regression_count": 11,
        "status": "ALL_EXACT",
    }
    assert all(
        set(row["integrated_function_basis"]) == set(INTEGRATED_BASIS)
        for row in value["channel_rows"]
    )
    assert all(
        row["symmetric_scale_regression"]["actual"]
        == row["symmetric_scale_regression"]["expected"]
        for row in value["channel_rows"]
    )


def test_lifecycle_stops_before_repository_form_factors() -> None:
    flags = _value()["claim_flags"]
    assert flags["PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"] is True
    assert flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"] is True
    assert flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert flags["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"] is False
    assert flags["QME_RESTORED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
