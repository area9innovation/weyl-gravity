#!/usr/bin/env python3
"""Independently verify the v2 Berger numerical declaration contract."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2.json"
SCHEMA = PACKAGE / "schema/berger-recoil-numerical-input-contract-v2.schema.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v2.schema.json"
LEGACY_SCHEMA = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v1.schema.json"
FIXTURE = PACKAGE / "fixtures/berger_recoil_numerical_input_contract_validation.json"
ARGUMENTS = [
    "two_js", "mass_squared_intervals", "couplings", "inverse_berger_volume",
    "tail_radii_by_two_j", "goal", "partition_count", "radical_bits",
    "outward_bits", "initial_partial_intervals",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _interval(value: dict[str, str], *, square: bool = False) -> dict[str, str]:
    lower, upper = Fraction(value["lower"]), Fraction(value["upper"])
    if lower <= 0 or lower > upper:
        raise ValueError("positive interval failed independent audit")
    if square:
        lower, upper = lower**2, upper**2
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _independent_translate(declaration: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator(schema).validate(declaration)
    two_js = list(declaration["two_js"])
    cutoff = declaration["carrier_cutoff_two_j"]
    if two_js != list(range(cutoff + 1, cutoff + 1 + len(two_js))):
        raise ValueError("noncontiguous shell schedule")
    rows = declaration["tail_radii_by_two_j"]
    row_shells = [row["two_j"] for row in rows]
    if len(row_shells) != len(set(row_shells)) or set(row_shells) != set(two_js):
        raise ValueError("tail shell schedule mismatch")
    mass_square = declaration["mass_domain"]["representation"] == "mass"
    return {
        "two_js": two_js,
        "mass_squared_intervals": {
            channel: _interval(
                declaration["mass_domain"]["channels"][channel], square=mass_square
            )
            for channel in ("0", "1")
        },
        "couplings": {
            channel: str(Fraction(declaration["couplings"][channel]))
            for channel in ("0", "1")
        },
        "inverse_berger_volume": _interval(declaration["inverse_berger_volume"]),
        "tail_radii_by_two_j": {
            str(row["two_j"]): {
                key: str(Fraction(row["radii"][key]))
                for key in ("00", "01", "10", "11")
            }
            for row in rows
        },
        "goal": deepcopy(declaration["stopping_goal"]),
        "partition_count": declaration["precision"]["partition_count"],
        "radical_bits": declaration["precision"]["radical_bits"],
        "outward_bits": declaration["precision"]["outward_bits"],
        "initial_partial_intervals": None,
    }


def _rejected(declaration: dict[str, Any]) -> bool:
    try:
        _independent_translate(declaration)
    except (ValidationError, ValueError):
        return True
    return False


def _mutations(base: dict[str, Any]) -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        ("reject_legacy_interval_tolerance_goal_name", lambda d: d.__setitem__("stopping_goal", {"kind": "interval_tolerance", "absolute_tolerance": "1/100"})),
        ("reject_missing_inverse_berger_volume", lambda d: d.pop("inverse_berger_volume")),
        ("reject_missing_shell_schedule", lambda d: d.pop("two_js")),
        ("reject_duplicate_shell", lambda d: d.__setitem__("two_js", [7, 7])),
        ("reject_noncontiguous_shell", lambda d: d.__setitem__("two_js", [7, 9])),
        ("reject_missing_tail_shell", lambda d: d.__setitem__("tail_radii_by_two_j", d["tail_radii_by_two_j"][:1])),
        ("reject_absent_tail_entry", lambda d: d["tail_radii_by_two_j"][0]["radii"].pop("11")),
        ("reject_nonpositive_mass", lambda d: d["mass_domain"]["channels"]["0"].__setitem__("lower", "0")),
        ("reject_nonpositive_inverse_volume", lambda d: d["inverse_berger_volume"].__setitem__("lower", "0")),
        ("reject_zero_coupling", lambda d: d["couplings"].__setitem__("1", "0")),
        ("reject_undeclared_provenance", lambda d: d.pop("provenance")),
    ]


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator(schema).validate(value)
    for ref in list(value["dependency_refs"].values()) + value["provenance"]["source_manifest"]:
        path = ROOT / ref["path"]
        if _sha256(path) != ref["sha256"]:
            raise SystemExit(f"content hash drift: {ref['path']}")

    fixture = json.loads(FIXTURE.read_text())
    if fixture["fixture_status"] != "VALIDATION_ONLY_NOT_PHYSICAL_DATA":
        raise SystemExit("validation fixture was promoted")
    expected = {}
    for goal in fixture["goal_variants"]:
        declaration = deepcopy(fixture["base_declaration"])
        declaration["provenance"]["declaration_id"] += f"-{goal['type']}"
        declaration["stopping_goal"] = deepcopy(goal)
        expected[goal["type"]] = (_payload_hash(declaration), _independent_translate(declaration))
    actual = {row["goal_type"]: row for row in value["validation_replays"]}
    if set(actual) != set(expected) or list(value["translator_contract"]["declaration_controlled_runtime_arguments"]) != ARGUMENTS:
        raise SystemExit("runtime goal or argument coverage drifted")
    for goal_type, (declaration_hash, translated) in expected.items():
        row = actual[goal_type]
        if row["declaration_sha256"] != declaration_hash or row["serialized_runtime_kwargs"] != translated:
            raise SystemExit(f"independent translation disagreement for {goal_type}")
        if row["declaration_status"] != "VALIDATION_ONLY" or row["physical_activation_eligible"] is not False:
            raise SystemExit("validation replay became physical")

    base = deepcopy(fixture["base_declaration"])
    base["stopping_goal"] = deepcopy(fixture["goal_variants"][0])
    independent_mutations = {}
    for name, mutate in _mutations(base):
        declaration = deepcopy(base)
        mutate(declaration)
        independent_mutations[name] = _rejected(declaration)
    certified_mutations = {row["name"]: row["detected"] for row in value["mutation_results"]}
    if independent_mutations != certified_mutations or not all(independent_mutations.values()):
        raise SystemExit("mutation rail disagreement")

    old = json.loads(LEGACY_SCHEMA.read_text())
    old_required = set(old["required"])
    if any(name in old_required for name in value["legacy_v1_audit"]["missing_runtime_inputs"]):
        raise SystemExit("legacy missing-input audit drifted")
    if value["flags"]["PHYSICAL_SPECIALIZATION_VALUES_DECLARED"] or value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"]:
        raise SystemExit("contract certificate promoted a physical stream")
    print("BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
