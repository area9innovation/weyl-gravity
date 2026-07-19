#!/usr/bin/env python3
"""Certify the v2 Berger numerical declaration-to-runtime contract."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError

from closed_universe_observers.berger_recoil_numerical_input_contract import (
    DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS,
    serialize_runtime_kwargs,
    translate_numerical_specialization,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2.json"
SCHEMA = PACKAGE / "schema/berger-recoil-numerical-input-contract-v2.schema.json"
INPUT_SCHEMA_V2 = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v2.schema.json"
INPUT_SCHEMA_V1 = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v1.schema.json"
FIXTURE = PACKAGE / "fixtures/berger_recoil_numerical_input_contract_validation.json"
REPORT = PACKAGE / "reports/berger-recoil-numerical-input-contract-v2.md"
DEPENDENCIES = {
    "stream_adapter": PACKAGE / "certificates/BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_numerical_input_contract.py",
    PACKAGE / "berger_recoil_reality_folded_stream.py",
    PACKAGE / "verify_berger_recoil_numerical_input_contract.py",
    PACKAGE / "tests/test_berger_recoil_numerical_input_contract.py",
    SCHEMA,
    INPUT_SCHEMA_V2,
    INPUT_SCHEMA_V1,
    FIXTURE,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validation_declarations() -> list[dict[str, Any]]:
    fixture = json.loads(FIXTURE.read_text())
    if fixture["fixture_status"] != "VALIDATION_ONLY_NOT_PHYSICAL_DATA":
        raise AssertionError("validation fixture status drifted")
    declarations = []
    for goal in fixture["goal_variants"]:
        declaration = deepcopy(fixture["base_declaration"])
        declaration["provenance"]["declaration_id"] += f"-{goal['type']}"
        declaration["stopping_goal"] = deepcopy(goal)
        declarations.append(declaration)
    return declarations


def _rejected(declaration: dict[str, Any]) -> bool:
    try:
        translate_numerical_specialization(declaration)
    except (ValidationError, ValueError):
        return True
    return False


def mutation_audit(base: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
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
    results = []
    for name, mutate in mutations:
        value = deepcopy(base)
        mutate(value)
        results.append({"name": name, "detected": _rejected(value)})
    if not all(row["detected"] for row in results):
        raise AssertionError("numerical-input contract mutation escaped")
    return results


def _legacy_audit() -> dict[str, Any]:
    old = json.loads(INPUT_SCHEMA_V1.read_text())
    old_required = set(old["required"])
    missing = [
        name
        for name in (
            "inverse_berger_volume",
            "carrier_cutoff_two_j",
            "two_js",
            "tail_radii_by_two_j",
            "precision",
            "provenance",
        )
        if name not in old_required
    ]
    old_goal_kinds = sorted(
        option["properties"]["kind"]["const"]
        for option in old["properties"]["stopping_goal"]["oneOf"]
    )
    if missing != [
        "inverse_berger_volume", "carrier_cutoff_two_j", "two_js",
        "tail_radii_by_two_j", "precision", "provenance",
    ] or old_goal_kinds != ["interval_tolerance", "nonzero", "sign"]:
        raise AssertionError("legacy v1 mismatch audit drifted")
    return {
        "path": str(INPUT_SCHEMA_V1.relative_to(ROOT)),
        "sha256": _sha256(INPUT_SCHEMA_V1),
        "status": "OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH",
        "missing_runtime_inputs": missing,
        "goal_name_mismatches": {
            "legacy": old_goal_kinds,
            "runtime": ["entry_tolerance", "entry_nonzero", "entry_sign", "rank_two"],
        },
    }


def build() -> dict[str, Any]:
    adapter = json.loads(DEPENDENCIES["stream_adapter"].read_text())
    if adapter["flags"].get("CONTIGUOUS_SUCCESSIVE_SHELL_STREAM_ADAPTER_EXPORTED") is not True:
        raise AssertionError("reality-folded stream adapter dependency dropped")
    input_schema = json.loads(INPUT_SCHEMA_V2.read_text())
    Draft202012Validator.check_schema(input_schema)

    declarations = validation_declarations()
    replays = []
    for declaration in declarations:
        translated = translate_numerical_specialization(declaration)
        if translated["physical_activation_eligible"]:
            raise AssertionError("validation fixture became activation eligible")
        replays.append({
            "goal_type": declaration["stopping_goal"]["type"],
            "declaration_status": declaration["declaration_status"],
            "declaration_sha256": _payload_hash(declaration),
            "serialized_runtime_kwargs": serialize_runtime_kwargs(translated["runtime_kwargs"]),
            "physical_activation_eligible": False,
        })
    if {row["goal_type"] for row in replays} != {
        "entry_tolerance", "entry_nonzero", "entry_sign", "rank_two"
    }:
        raise AssertionError("four runtime stopping goals were not covered")

    mutations = mutation_audit(declarations[0])
    boundary = (
        "This certificate exports an exact v2 declaration schema and callable translator for all "
        "declaration-controlled arguments of run_reality_folded_shell_stream. The four replays use "
        "synthetic VALIDATION_ONLY rational data and do not declare or recommend physical masses, "
        "couplings, inverse volume, shell cutoff, tail radii, precision or stopping goal. The v1 "
        "schema is retained with OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH status. Physical stream "
        "activation, recoil-corrected rank two, tangent-cone restriction, Bridge 3, hashed exact-T "
        "identification, nonlinear observer stability and quantum claims remain unavailable."
    )
    return {
        "schema": "closed-universe-berger-recoil-numerical-input-contract-v2",
        "result_id": "BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2",
        "setting_id": adapter["setting_id"],
        "claim_status": "CERTIFIED_EXACT_TRANSLATOR_PHYSICAL_VALUES_DEFERRED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": adapter["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "pure-Weyl Berger observer apparatus with dynamical emitters",
            "background": "R x Berger(S^3) positive-clock laboratory",
            "boundaries": "compact spatial slices; causal retarded/advanced support windows",
            "charge_sector": "two neutral detector/source channels with recoil feedback",
            "carrier": "reality-folded direct Peter-Weyl shell stream; hashed exact-T stream unmapped",
            "degree": "classical detector response through first recoil order",
            "parity": "all certified direct carriers",
            "ell": "two_j/2 on caller-declared contiguous finite shells",
            "m": "all passive columns via independent representatives plus SU(2) reality",
            "k": "0,...,floor(two_j/2) evaluated directly",
            "omega": "finite exact mode-kernel interval carrier",
        },
        "legacy_v1_audit": _legacy_audit(),
        "translator_contract": {
            "input_schema": {"path": str(INPUT_SCHEMA_V2.relative_to(ROOT)), "sha256": _sha256(INPUT_SCHEMA_V2)},
            "module": "closed_universe_observers.berger_recoil_numerical_input_contract",
            "callable": "translate_numerical_specialization",
            "runtime_callable": "run_reality_folded_shell_stream",
            "declaration_controlled_runtime_arguments": list(DECLARATION_CONTROLLED_RUNTIME_ARGUMENTS),
            "static_certified_runtime_arguments": [
                "carriers", "moment_certificate", "detector_profile_certificate",
                "switch_certificate", "spectral_certificate",
            ],
            "physical_activation_policy": "translator eligibility is necessary but never sufficient; a separate activation certificate must verify an EXPLICIT_EXTERNAL_VALUES declaration and source hashes",
        },
        "validation_replays": replays,
        "mutation_results": mutations,
        "flags": {
            "EXACT_NUMERICAL_INPUT_CONTRACT_V2_EXPORTED": True,
            "CALLABLE_DECLARATION_TO_RUNTIME_TRANSLATOR_EXPORTED": True,
            "MASS_AND_MASS_SQUARED_DOMAINS_SUPPORTED": True,
            "ALL_FOUR_RUNTIME_STOPPING_GOALS_TRANSLATE": True,
            "PROVENANCE_REQUIRED_FOR_EVERY_NUMERICAL_INPUT_CLASS": True,
            "LEGACY_V1_SCHEMA_OBSTRUCTED": True,
            "PHYSICAL_SPECIALIZATION_VALUES_DECLARED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "PHYSICAL_BRANCH_BRIDGE_ACTIVE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "AWAIT_PROVENANCE_COMPLETE_EXPLICIT_EXTERNAL_VALUE_DECLARATION",
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
        raise SystemExit("stale Berger recoil numerical-input contract certificate")
    print("BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
