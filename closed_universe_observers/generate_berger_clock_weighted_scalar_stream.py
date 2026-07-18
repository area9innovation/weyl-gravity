#!/usr/bin/env python3
"""Evaluate one even-clock-weighted Berger scalar stream through two_j=139."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import AMPLITUDE_LOWER
from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    MAX_K,
    MAX_TWO_J,
    REMAINDER_BITS,
    _fixed_moment_factors,
    _mode,
    _moment_intervals,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-clock-weighted-scalar-stream-two-j139-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-weighted-scalar-stream-two-j139.md"
CLOCK_POWERS = (0, 2, 4, 6, 8, 10)
DEPENDENCIES = {
    "scalar": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_clock_weighted_scalar_stream.py",
    "tests": PACKAGE / "tests/test_berger_clock_weighted_scalar_stream.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def certificate_path(clock_power: int) -> Path:
    return PACKAGE / f"certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{clock_power}_TWO_J139.json"


def result_id(clock_power: int) -> str:
    return f"BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{clock_power}_TWO_J139"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def joint_clock_moments(values: dict[str, Any], clock_power: int) -> list[tuple[Fraction, Fraction]]:
    if clock_power not in CLOCK_POWERS:
        raise ValueError(f"clock_power must be one of {CLOCK_POWERS}")
    base_row = values["low_moments"]["normalized_moments"]["clock_core_dimension_1"][clock_power // 2]
    base = base_row["normalized_even_moment"]
    base_interval = Fraction(base["lower"]), Fraction(base["upper"])
    answer = []
    for k in range(MAX_K + 1):
        secant_power = 2 * k - 1
        if secant_power == -1:
            answer.append((base_interval[0] * AMPLITUDE_LOWER, base_interval[1]))
        else:
            answer.append((base_interval[0], base_interval[1] / AMPLITUDE_LOWER**secant_power))
    return answer


@lru_cache(maxsize=None)
def build(clock_power: int) -> dict[str, Any]:
    if clock_power not in CLOCK_POWERS:
        raise ValueError(f"clock_power must be one of {CLOCK_POWERS}")
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "scalar": "CLOCK_INTEGRATED_DIAGONAL_SCALAR_COEFFICIENTS_TWO_J0_TO_139_EXPORTED",
        "high_moments": "VALIDATED_CLOCK_SECANT_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    scalar_producer = PACKAGE / "generate_berger_clock_integrated_scalar_stream.py"
    manifest = {row["path"]: row["sha256"] for row in values["scalar"]["provenance"]["source_manifest"]}
    if manifest.get(str(scalar_producer.relative_to(ROOT))) != _sha256(scalar_producer):
        raise AssertionError("certified scalar-stream implementation drifted")

    radial, _ = _moment_intervals(values)
    clock = joint_clock_moments(values, clock_power)
    factors = _fixed_moment_factors(radial, clock)
    modes = []
    maximum_remainder = 0
    maximum_location = None
    for n in range(MAX_TWO_J + 1):
        mode, remainder = _mode(n, factors)
        for row in mode["unique_diagonal"]:
            row["clock_weighted_local_amplitude"] = row.pop("clock_integrated_local_amplitude")
        modes.append(mode)
        if remainder > maximum_remainder:
            maximum_remainder = remainder
            maximum_location = n
    if len(modes) != 140 or sum(len(mode["unique_diagonal"]) for mode in modes) != 4970:
        raise AssertionError("clock-weighted scalar stream coverage failed")
    base_clock_lower = Fraction(
        values["low_moments"]["normalized_moments"]["clock_core_dimension_1"]
        [clock_power // 2]["normalized_even_moment"]["lower"]
    )
    if not clock[0][0] < base_clock_lower:
        raise AssertionError("external detector clock factor mutation escaped")
    boundary = (
        f"This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate evaluates the normalized external-clock-and-s^{clock_power}-weighted diagonal scalar detector-profile stream for two_j=0,...,139. The pointwise polarization recurrence contributes a(t)=cos(lambda s), so the required joint factor is s^p sec(lambda s)^(2k-1). The certified clock even moment, cos(lambda s)<=1 and cos(lambda s)>=82915/82944 give rigorous joint intervals without assuming independence. The certified specialized scalar evaluator then exports 4,970 symmetry-unique intervals reconstructing all 9,870 diagonal values, with its 1024-bit Taylor-remainder rail retained. This is one of six temporal-moment inputs to the finite Green polynomial. It does not yet combine the six external-clock-weighted streams with the polarization recurrence and Green charge blocks, certify the tail beyond form two_j=138, construct full Maxwell or massive images, evaluate recoil, restrict to the tangent cone, activate the physical-branch bridge, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-clock-weighted-scalar-stream-two-j139-v1",
        "result_id": result_id(clock_power),
        "setting_id": values["scalar"]["setting_id"],
        "claim_status": "VALIDATED_EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED_GREEN_COMPOSITION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "clock_weight": {"power": clock_power, "variable": "s=(Theta-Theta_a)/(1/64)", "external_detector_factor": "a(t)=cos(lambda s)", "joint_integrand": "s^p sec(lambda s)^(2k-1)", "joint_bound": "k=0: cos(lambda)E[s^p]<=E[s^p cos(lambda s)]<=E[s^p]; k>=1: E[s^p]<=E[s^p sec(lambda s)^(2k-1)]<=cos(lambda)^(-(2k-1))E[s^p]", "maximum_secant_index": MAX_K},
        "evaluation_convention": {"maximum_two_j": MAX_TWO_J, "moment_truncation_k": MAX_K, "remainder_dyadic_bits": REMAINDER_BITS, "clock_even_power": clock_power, "normalization": "expectation under the normalized dimension-one flat clock bump"},
        "joint_clock_moment_enclosures": [{"k": k, "interval": _serialize(value)} for k, value in enumerate(clock)],
        "coverage": {"mode_count": 140, "serialized_unique_diagonal_count": 4970, "reconstructed_full_diagonal_count": 9870, "reflection": "basis_index r and n-r have equal local amplitudes"},
        "modes": modes,
        "truncation_remainder_audit": {"maximum_uniform_remainder_upper": str(Fraction(maximum_remainder, 1 << REMAINDER_BITS)), "maximum_mode_two_j": maximum_location, "applied_to_every_serialized_interval": True},
        "mutation_results": [{"name": "drop_external_detector_clock_factor", "detected": True}],
        "flags": {"EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED": True, "JOINT_CLOCK_MOMENT_DEPENDENCE_BOUNDED_WITHOUT_FACTORIZATION": True, "POLARIZATION_RECURRENCE_AND_GREEN_CHARGE_BLOCKS_COMPOSED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "COMPOSE_CLOCK_POWERS_0_2_4_6_8_10_WITH_THE_POLARIZATION_RECURRENCE_AND_GREEN_CHARGE_BLOCKS_THROUGH_FORM_TWO_J138",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--power", type=int, choices=CLOCK_POWERS, required=True)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build(args.power)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    target = certificate_path(args.power)
    if args.emit:
        target.write_text(rendered)
    if args.check and (not target.exists() or target.read_text() != rendered):
        raise SystemExit(f"stale s^{args.power}-weighted scalar stream")
    print(f"{result_id(args.power)} generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
