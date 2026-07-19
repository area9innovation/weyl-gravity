"""Translate a provenance-complete Berger recoil declaration to runtime kwargs."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval


PACKAGE = Path(__file__).resolve().parent
SCHEMA = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v2.schema.json"
STREAM_KEYS = {(a, b) for a in (0, 1) for b in (0, 1)}
DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS = (
    "two_js",
    "mass_squared_intervals",
    "couplings",
    "inverse_berger_volume",
    "tail_radii_by_two_j",
    "goal",
    "partition_count",
    "radical_bits",
    "outward_bits",
    "initial_partial_intervals",
)


def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _positive_interval(value: Mapping[str, str], label: str) -> RationalInterval:
    interval = RationalInterval(Fraction(value["lower"]), Fraction(value["upper"]))
    if interval.lower <= 0:
        raise ValueError(f"{label} must be strictly positive")
    return interval


def translate_numerical_specialization(
    declaration: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and exactly translate all declaration-controlled runtime inputs."""
    copied = deepcopy(dict(declaration))
    _validator().validate(copied)

    mass_domain = copied["mass_domain"]
    masses = {
        channel: _positive_interval(
            mass_domain["channels"][str(channel)], f"mass channel {channel}"
        )
        for channel in (0, 1)
    }
    if mass_domain["representation"] == "mass":
        mass_squared = {
            channel: RationalInterval(value.lower**2, value.upper**2)
            for channel, value in masses.items()
        }
    else:
        mass_squared = masses

    couplings = {
        channel: Fraction(copied["couplings"][str(channel)])
        for channel in (0, 1)
    }
    if any(value == 0 for value in couplings.values()):
        raise ValueError("both couplings must be nonzero")
    inverse_volume = _positive_interval(
        copied["inverse_berger_volume"], "inverse Berger volume"
    )

    two_js = [int(value) for value in copied["two_js"]]
    cutoff = int(copied["carrier_cutoff_two_j"])
    expected = list(range(cutoff + 1, cutoff + 1 + len(two_js)))
    if two_js != expected:
        raise ValueError("shell schedule must be the contiguous extension of the carrier cutoff")

    tail_rows = copied["tail_radii_by_two_j"]
    tail_shells = [int(row["two_j"]) for row in tail_rows]
    if len(tail_shells) != len(set(tail_shells)):
        raise ValueError("tail schedule contains a duplicate shell")
    if set(tail_shells) != set(two_js):
        raise ValueError("tail radii are required after every declared shell")
    tail_radii = {
        int(row["two_j"]): {
            (detector, source): Fraction(row["radii"][f"{detector}{source}"])
            for detector, source in sorted(STREAM_KEYS)
        }
        for row in tail_rows
    }
    if any(
        radius < 0
        for shell in tail_radii.values()
        for radius in shell.values()
    ):
        raise ValueError("tail radii must be nonnegative")

    goal = deepcopy(copied["stopping_goal"])
    precision = copied["precision"]
    runtime_kwargs = {
        "two_js": two_js,
        "mass_squared_intervals": mass_squared,
        "couplings": couplings,
        "inverse_berger_volume": inverse_volume,
        "tail_radii_by_two_j": tail_radii,
        "goal": goal,
        "partition_count": int(precision["partition_count"]),
        "radical_bits": int(precision["radical_bits"]),
        "outward_bits": int(precision["outward_bits"]),
        "initial_partial_intervals": None,
    }
    if tuple(runtime_kwargs) != DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS:
        raise AssertionError("translator/runtime argument order drifted")
    return {
        "runtime_callable": "run_reality_folded_shell_stream",
        "runtime_kwargs": runtime_kwargs,
        "declaration_id": copied["provenance"]["declaration_id"],
        "declaration_status": copied["declaration_status"],
        "physical_activation_eligible": copied["declaration_status"]
        == "EXPLICIT_EXTERNAL_VALUES",
        "hashed_exact_T_stream_identification_status": "NO_CERTIFIED_MAP",
    }


def serialize_runtime_kwargs(runtime_kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic JSON representation of translated runtime kwargs."""
    if tuple(runtime_kwargs) != DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS:
        raise ValueError("runtime kwargs do not exactly match the declared contract")
    return {
        "two_js": list(runtime_kwargs["two_js"]),
        "mass_squared_intervals": {
            str(channel): runtime_kwargs["mass_squared_intervals"][channel].serialize()
            for channel in (0, 1)
        },
        "couplings": {
            str(channel): str(runtime_kwargs["couplings"][channel])
            for channel in (0, 1)
        },
        "inverse_berger_volume": runtime_kwargs["inverse_berger_volume"].serialize(),
        "tail_radii_by_two_j": {
            str(two_j): {
                f"{detector}{source}": str(
                    runtime_kwargs["tail_radii_by_two_j"][two_j][(detector, source)]
                )
                for detector, source in sorted(STREAM_KEYS)
            }
            for two_j in runtime_kwargs["two_js"]
        },
        "goal": deepcopy(runtime_kwargs["goal"]),
        "partition_count": runtime_kwargs["partition_count"],
        "radical_bits": runtime_kwargs["radical_bits"],
        "outward_bits": runtime_kwargs["outward_bits"],
        "initial_partial_intervals": None,
    }
