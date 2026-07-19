from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    coclosed_two_form_projector_audit,
    evaluate_coupling_stripped_positive_energy_preparation_at_support_left,
)
from closed_universe_observers.generate_berger_recoil_positive_energy_preparation_coefficients import (
    build,
)


def test_exact_coclosed_projector_rail():
    rows = [coclosed_two_form_projector_audit(two_j) for two_j in range(5)]
    assert [row["coclosed_rank"] for row in rows] == [0, 2, 3, 4, 5]
    assert all(
        row[field] == 0
        for row in rows
        for field in (
            "idempotence_defect_count",
            "self_adjoint_defect_count",
            "coderivative_defect_count",
            "exact_form_annihilation_defect_count",
            "temporal_component_reconstruction_defect_count",
            "clock_switched_observer_current_defect_count",
        )
    )


def test_positive_energy_coefficient_certificate_is_fail_closed():
    value = build()
    assert value["flags"]["CANONICAL_SPATIAL_CAUCHY_TRACE_EXPORTED"]
    assert value["flags"]["FULL_CANONICAL_POSITIVE_ENERGY_DUAL_CERTIFIED"]
    assert value["flags"]["COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED"]
    assert not value["flags"]["COCLOSED_RESTRICTED_DUAL_VALID_AS_OBSERVER_SOURCE"]
    assert not value["flags"]["RETAINED_COEFFICIENT_NONVANISHING_CERTIFIED"]
    assert not value["flags"]["FREE_EMITTER_EVOLUTION_BOUND"]


def test_nonpositive_mass_fails_before_dependency_use():
    with pytest.raises(ValueError, match="positive mass squared"):
        evaluate_coupling_stripped_positive_energy_preparation_at_support_left(
            detector_image_certificate={},
            detector_profile_certificate={},
            switch_certificate={},
            moment_certificate={},
            exact_kernel_certificate={},
            detector="D0",
            two_j=0,
            column=0,
            mass_squared_interval=RationalInterval(Fraction(0), Fraction(1)),
        )
