from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import pytest

from closed_universe_observers.berger_recoil_detector_form_binding import (
    assemble_detector_advanced_maxwell_polynomial,
)
from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_first_omitted_shell_direct_carriers,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    _EXACT_MODE_SINE_KERNEL_CACHE,
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_mismatched_feedback_channel import (
    evaluate_partitioned_absolute_g3_feedback_channel,
    evaluate_partitioned_absolute_g3_feedback_column_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "closed_universe_observers"


def _read(name):
    return json.loads((PACKAGE / "certificates" / name).read_text())


@pytest.fixture(scope="module")
def carriers():
    return bind_first_omitted_shell_direct_carriers(
        detector_image_certificate=_read("BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json"),
        cross_window_remainder_certificate=_read("BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json"),
        exact_kernel_certificate=_read("BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json"),
        first_omitted_shell_certificate=_read("BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json"),
    )


def test_bound_carriers_expose_exactly_the_first_omitted_shell(carriers):
    detector = carriers["detector_image"]
    for label in ("D0", "D1"):
        row = assemble_detector_advanced_maxwell_polynomial(
            detector, detector=label, two_j=5, column=5
        )
        assert row["dimension"] == 24
    kernel = enclose_exact_mode_sine_kernel(
        carriers["exact_kernel"],
        two_j=5,
        family="Maxwell",
        form_degree=1,
        mass_squared_interval=RationalInterval.point(0),
        slab_length=Fraction(1, 24),
    )
    assert kernel["dimension"] == 18
    with pytest.raises(ValueError):
        enclose_exact_mode_sine_kernel(
            carriers["exact_kernel"],
            two_j=6,
            family="Maxwell",
            form_degree=1,
            mass_squared_interval=RationalInterval.point(0),
            slab_length=Fraction(1, 24),
        )


def test_exact_kernel_cache_is_scope_keyed_and_mutation_isolated(carriers):
    _EXACT_MODE_SINE_KERNEL_CACHE.clear()
    arguments = {
        "two_j": 5,
        "family": "Maxwell",
        "form_degree": 0,
        "mass_squared_interval": RationalInterval.point(0),
        "slab_length": Fraction(1, 8),
        "series_order": 5,
        "radical_bits": 80,
    }
    first = enclose_exact_mode_sine_kernel(carriers["exact_kernel"], **arguments)
    assert first["two_j"] == 5
    assert first["family"] == "Maxwell"
    first["coefficient_matrices"][0]["entries"][0]["real"]["lower"] = "poisoned"
    second = enclose_exact_mode_sine_kernel(carriers["exact_kernel"], **arguments)
    assert second["coefficient_matrices"][0]["entries"][0]["real"]["lower"] != "poisoned"
    assert len(_EXACT_MODE_SINE_KERNEL_CACHE) == 1
    assert next(iter(_EXACT_MODE_SINE_KERNEL_CACHE))[1:4] == (5, "Maxwell", 0)


def test_adapter_rejects_exact_t_identification_mutation():
    first = _read("BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json")
    first = deepcopy(first)
    first["flags"]["HASHED_EXACT_T_TWO_J138_STREAM_IDENTIFIED_WITH_DIRECT_PROVIDER"] = True
    with pytest.raises(ValueError):
        bind_first_omitted_shell_direct_carriers(
            detector_image_certificate=_read("BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json"),
            cross_window_remainder_certificate=_read("BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json"),
            exact_kernel_certificate=_read("BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json"),
            first_omitted_shell_certificate=first,
        )


def test_dyadic_outward_rounding_contains_original_interval():
    original = RationalInterval(Fraction(-7, 13), Fraction(11, 17))
    rounded = original.round_outward(16)
    assert rounded.lower <= original.lower <= original.upper <= rounded.upper
    assert rounded.lower.denominator <= 2**16
    assert rounded.upper.denominator <= 2**16


def test_generated_certificate_is_fail_closed_and_complete():
    certificate = _read("BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json")
    rows = [
        channel
        for column in certificate["base_partition_columns"]
        for channel in column["channels"]
    ]
    assert len(rows) == 48
    assert len({(row["channel_id"], row["column"]) for row in rows}) == 48
    assert sum(row["causal_support_zero"] for row in rows) == 24
    assert certificate["flags"]["ALL_SIX_PASSIVE_COLUMNS_PER_TWO_J5_CHANNEL_EVALUATED"]
    assert not certificate["flags"]["TWO_J5_SHELL_SCALARS_WITH_COUPLINGS_EVALUATED"]
    assert not certificate["flags"]["COMPLETE_ALL_SHELL_PROVIDER_EXPORTED"]


def test_shared_bundle_matches_scalar_backend_and_rounding_encloses_exact():
    detector = _read("BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json")
    cross = _read("BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json")
    profiles = _read("BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json")
    switches = _read("BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json")
    moments = _read("BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json")
    kernels = _read("BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json")
    mass = RationalInterval(Fraction(1), Fraction(2))
    common = {
        "detector_image_certificate": detector,
        "cross_window_remainder_certificate": cross,
        "detector_profile_certificate": profiles,
        "switch_certificate": switches,
        "moment_certificate": moments,
        "exact_kernel_certificate": kernels,
        "two_j": 0,
        "column": 0,
        "partition_count": 2,
    }
    exact = {
        f"I_{a}{b}{c}": evaluate_partitioned_absolute_g3_feedback_channel(
            detector=a,
            source_preparation=b,
            feedback_emitter=c,
            source_mass_squared_interval=mass,
            feedback_mass_squared_interval=mass,
            **common,
        )["coefficient_block_interval"]
        for a in (0, 1)
        for b in (0, 1)
        for c in (0, 1)
    }
    rounded_bundle = evaluate_partitioned_absolute_g3_feedback_column_bundle(
        mass_squared_intervals={0: mass, 1: mass},
        outward_bits=48,
        **common,
    )
    for row in rounded_bundle:
        rounded = row["coefficient_block_interval"]
        reference = exact[row["channel_id"]]
        for part in ("real", "imaginary"):
            assert Fraction(rounded[part]["lower"]) <= Fraction(reference[part]["lower"])
            assert Fraction(reference[part]["upper"]) <= Fraction(rounded[part]["upper"])
