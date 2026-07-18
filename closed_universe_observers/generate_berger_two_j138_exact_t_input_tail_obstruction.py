#!/usr/bin/env python3
"""Certify a first-omitted-shell obstruction to the form two_j<=138 cutoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_adaptive_clock_weighted_scalar_stream import (
    CLOCK_POWERS as ADAPTIVE_POWERS,
    joint_clock_moments as adaptive_joint_clock_moments,
)
from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_stream import (
    block_powers,
    dressed_block,
)
from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    REMAINDER_BITS,
    _fixed_moment_factors,
    _mode,
    _moment_intervals,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    CLOCK_POWERS as LOW_POWERS,
    joint_clock_moments as low_joint_clock_moments,
)
from closed_universe_observers.generate_berger_order14_temporal_green_charge_stream import (
    CZERO,
    _encode_fraction,
    _encode_interval,
    _helicity_moments,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    axial_scalar_recurrence,
)
from closed_universe_observers.generate_berger_streamable_polarization_sectors import (
    helicity_sectors,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_TWO_J138_EXACT_T_INPUT_TAIL_OBSTRUCTION.json"
SCHEMA = PACKAGE / "schema/berger-two-j138-exact-t-input-tail-obstruction-v1.schema.json"
REPORT = PACKAGE / "reports/berger-two-j138-exact-t-input-tail-obstruction.md"
POWERS = LOW_POWERS + ADAPTIVE_POWERS
FORM_TWO_J = 139
SCALAR_UPPER_TWO_J = 140
DETECTOR = "D0"
COLUMN = 69
CHARGE = Fraction(-1, 2)
OUTPUT = 1
DEPENDENCIES = {
    "blockwise_stream": PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_STREAM_TWO_J138.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "exact_charge_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "high_clock": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in LOW_POWERS
    },
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in ADAPTIVE_POWERS
    },
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_two_j138_exact_t_input_tail_obstruction.py",
    PACKAGE / "tests/test_berger_two_j138_exact_t_input_tail_obstruction.py",
    SCHEMA,
    REPORT,
]

ComplexInterval = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absolute_component_lower(value: ComplexInterval) -> Fraction:
    """Return a rigorous lower bound using either Cartesian component."""
    return max(
        Fraction(0) if lower <= 0 <= upper else min(abs(lower), abs(upper))
        for lower, upper in value
    )


def _serialize_interval(value: ComplexInterval) -> dict[str, list[str]]:
    return {
        "real": [str(value[0][0]), str(value[0][1])],
        "imaginary": [str(value[1][0]), str(value[1][1])],
    }


def _scalar_upper_mode(values: dict[str, Any], power: int, radial) -> tuple[dict[str, Any], int]:
    clock = (
        low_joint_clock_moments(values, power)
        if power in LOW_POWERS
        else adaptive_joint_clock_moments(values, power)
    )
    mode, remainder = _mode(SCALAR_UPPER_TWO_J, _fixed_moment_factors(radial, clock))
    for row in mode["unique_diagonal"]:
        row["clock_weighted_local_amplitude"] = row.pop("clock_integrated_local_amplitude")
    return mode, remainder


def _zero_mode(mode: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(mode))
    for row in value["unique_diagonal"]:
        row["clock_weighted_local_amplitude"] = {
            "lower": "0",
            "upper": "0",
            "width": "0",
        }
    return value


def _extended_streams(values: dict[str, Any]):
    radial, _ = _moment_intervals(values)
    streams = {}
    summaries = []
    for power in POWERS:
        mode, remainder = _scalar_upper_mode(values, power, radial)
        summaries.append({
            "clock_power": power,
            "scalar_two_j": SCALAR_UPPER_TWO_J,
            "selected_indices": [
                {
                    "basis_index": index,
                    "interval": mode["unique_diagonal"][index]["clock_weighted_local_amplitude"],
                }
                for index in (69, 70)
            ],
            "uniform_truncation_remainder_upper": str(Fraction(remainder, 1 << REMAINDER_BITS)),
        })
        streams[power] = values[f"s{power}"]["modes"] + [mode]
    return streams, summaries


def _witness(streams: dict[int, Any], scalar_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    j = Fraction(FORM_TWO_J, 2)
    members = helicity_sectors(FORM_TWO_J)[CHARGE]
    helicity = _helicity_moments(streams, DETECTOR, FORM_TWO_J, COLUMN)
    moments = {
        power: [helicity[power].get((component, int(m + j)), CZERO) for component, m in members]
        for power in POWERS
    }
    spatial, temporal = dressed_block(
        FORM_TWO_J,
        CHARGE,
        moments,
        block_powers(FORM_TWO_J, CHARGE)[1],
    )
    digest = hashlib.sha256()
    digest.update(_encode_fraction(CHARGE))
    for power in POWERS:
        digest.update(bytes((power,)))
        for value in moments[power]:
            digest.update(_encode_interval(value))
    for value in spatial:
        digest.update(_encode_interval(value))
    digest.update(_encode_interval(temporal))
    return {
        "detector_id": DETECTOR,
        "form_two_j": FORM_TWO_J,
        "representation_column": COLUMN,
        "charge": str(CHARGE),
        "charge_block_members": [
            {"helicity_component": component, "m": str(m)} for component, m in members
        ],
        "selected_spatial_output": OUTPUT,
        "selected_spatial_dressed_amplitude": _serialize_interval(spatial[OUTPUT]),
        "selected_spatial_absolute_lower": str(_absolute_component_lower(spatial[OUTPUT])),
        "temporal_dressed_coderivative": _serialize_interval(temporal),
        "temporal_absolute_lower": str(_absolute_component_lower(temporal)),
        "all_spatial_dressed_amplitudes": [_serialize_interval(value) for value in spatial],
        "scalar_upper_neighbor_summaries": scalar_summaries,
        "canonical_witness_sha256": digest.hexdigest(),
    }


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "blockwise_stream": "FINITE_RAIL_EXACT_T_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
        "exact_charge_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
        "high_moments": "VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "high_clock": "VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    for power in POWERS:
        flag = (
            "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED"
            if power in LOW_POWERS
            else "ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_DIAGONAL_SCALAR_STREAM_EXPORTED"
        )
        if values[f"s{power}"]["flags"].get(flag) is not True:
            raise AssertionError(f"scalar stream s{power} dropped")
    recurrence = axial_scalar_recurrence(FORM_TWO_J, 69, 69, "y0")
    if not any(row["next_two_j"] == SCALAR_UPPER_TWO_J for row in recurrence):
        raise AssertionError("first omitted form shell lost its required scalar upper neighbor")
    streams, scalar_summaries = _extended_streams(values)
    witness = _witness(streams, scalar_summaries)
    spatial_lower = Fraction(witness["selected_spatial_absolute_lower"])
    temporal_lower = Fraction(witness["temporal_absolute_lower"])
    if spatial_lower <= Fraction(4, 5) or temporal_lower <= Fraction(4, 5):
        raise AssertionError("first omitted shell no longer obstructs the two_j<=138 cutoff")
    mutated_streams = {
        power: modes[:-1] + [_zero_mode(modes[-1])]
        for power, modes in streams.items()
    }
    mutation = _witness(mutated_streams, scalar_summaries)
    if mutation["canonical_witness_sha256"] == witness["canonical_witness_sha256"]:
        raise AssertionError("upper-neighbor deletion mutation escaped")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL obstruction extends only the scalar neighbor needed by the first omitted detector-form shell. For D0 at form two_j=139, column 69 and charge q=-1/2, the order-14 microphase-dressed spatial input has one coefficient with absolute value greater than 0.827, while the dressed coderivative coefficient has absolute value greater than 0.862. Hence the two_j<=138 finite rail cannot be promoted as a uniformly small detector-profile input tail, despite its certified exact-T temporal functional calculus. This is a coefficientwise first-omitted-shell lower bound, not an upper bound on the infinite tail, an evaluation of the exact-T cosine at detector separation, a full Maxwell or massive image, recoil, tangent-cone restriction, Bridge 3 or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-two-j138-exact-t-input-tail-obstruction-v1",
        "result_id": "BERGER_TWO_J138_EXACT_T_INPUT_TAIL_OBSTRUCTION",
        "setting_id": values["blockwise_stream"]["setting_id"],
        "claim_status": "FIRST_OMITTED_SHELL_LOWER_BOUND_CERTIFIED_TWO_J138_INPUT_TAIL_PROMOTION_OBSTRUCTED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "cutoff_audit": {
            "retained_form_two_j_maximum": 138,
            "first_omitted_form_two_j": FORM_TWO_J,
            "required_scalar_upper_neighbor_two_j": SCALAR_UPPER_TWO_J,
            "selected_recurrence": recurrence,
            "small_tail_threshold": "4/5",
            "witness": witness,
        },
        "mutation_results": [{
            "name": "delete_required_scalar_two_j140_upper_channel",
            "detected": True,
            "mutated_canonical_witness_sha256": mutation["canonical_witness_sha256"],
        }],
        "flags": {
            "FIRST_OMITTED_FORM_SHELL_TWO_J139_EVALUATED": True,
            "COEFFICIENTWISE_SPATIAL_TAIL_LOWER_BOUND_ABOVE_FOUR_FIFTHS": True,
            "COEFFICIENTWISE_TEMPORAL_CODERIVATIVE_LOWER_BOUND_ABOVE_FOUR_FIFTHS": True,
            "TWO_J138_UNIFORM_SMALL_INPUT_TAIL_CERTIFIED": False,
            "INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "WIDEN_THE_ADAPTIVE_HARMONIC_RAIL_OR_CERTIFY_A_PHYSICAL_SPACE_GREEN_CHAIN_BEFORE_RETESTING_THE_INFINITE_TAIL",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale two_j138 exact-T input-tail obstruction")
    print("BERGER_TWO_J138_EXACT_T_INPUT_TAIL_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
