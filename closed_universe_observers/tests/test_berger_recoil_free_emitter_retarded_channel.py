from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_free_emitter_retarded_channel import (
    evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right,
)
from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.generate_berger_recoil_free_emitter_retarded_channel import (
    build,
    canonical_free_evolution_audit,
)


def test_exact_canonical_evolution_and_current_audit():
    rows = [canonical_free_evolution_audit(two_j) for two_j in range(5)]
    fields = (
        "A_L_minus_H_defect_count",
        "L_A_minus_H_defect_count",
        "dSigma_squared_defect_count",
        "deltaSigma_squared_defect_count",
        "constraint_preservation_defect_count",
        "A_self_adjoint_defect_count",
        "L_self_adjoint_defect_count",
        "symplectic_generator_defect_count",
    )
    assert all(row[field] == 0 for row in rows for field in fields)


def test_certificate_exports_channel_but_not_detector_record():
    value = build()
    assert value["flags"]["FULL_CANONICAL_FREE_EMITTER_EVOLUTION_BOUND"]
    assert value["flags"]["CONSERVED_SWITCHED_CURRENT_EXPORTED"]
    assert value["flags"][
        "FIRST_RETARDED_MAXWELL_CAUCHY_PAIR_AT_SUPPORT_RIGHT_EXPORTED"
    ]
    assert not value["flags"]["RETAINED_CHANNEL_NONVANISHING_CERTIFIED"]
    assert not value["flags"]["DETECTOR_Q_CONTRACTION_EXPORTED"]
    assert not value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"]
    for fixture in value["serialized_fixture_channels"].values():
        n = fixture["two_j"] + 1
        assert len(
            fixture["first_retarded_maxwell_channel_summary"]["support_right_field"]
        ) == 4 * n
        assert fixture["switched_current_summary"]["temporal_block_structural_zero"]
        assert all(fixture["causal_initial_data_audit"].values())


def test_nonpositive_mass_fails_before_dependency_use():
    with pytest.raises(ValueError, match="positive mass squared"):
        evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right(
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
