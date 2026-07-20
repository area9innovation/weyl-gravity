#!/usr/bin/env python3
"""Certify the first missing variational input for executable replacement q1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL.json"
PAYLOAD = P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement-112-executable-unary-variational-input-shortfall-v1.schema.json"
REPORT = P / "reports/berger-replacement-112-executable-unary-variational-input-shortfall.md"
DEPENDENCIES = {
    "replacement": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "old_108": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "old_108_payload": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json",
    "producer_shortfall": P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL.json",
    "producer_shortfall_payload": P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL_PAYLOAD.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def phi2_symbols(old_payload: dict[str, Any]) -> list[str]:
    symbols: set[str] = set()
    for block in old_payload["blocks"]:
        for entry in block["entries"]:
            for term in entry["terms"]:
                for factor in term["coefficient_factors"]:
                    if factor["name"].startswith("Phi2_"):
                        symbols.add(factor["name"])
    return sorted(symbols)


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for cert_name, payload_name in (
        ("replacement", "replacement_payload"),
        ("old_108", "old_108_payload"),
        ("producer_shortfall", "producer_shortfall_payload"),
    ):
        if sha256(DEPENDENCIES[payload_name]) != values[cert_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert_name} payload hash mismatch")
    symbols = phi2_symbols(values["old_108_payload"])
    if not symbols or "Phi2_00" not in symbols:
        raise AssertionError("old q1 ceased to expose local Phi2 jet symbols")
    background = values["replacement_payload"]["background_equation"]
    if "retained_to_component_jet_crosswalk" in background or "Phi2_local_jet_map" in background:
        raise AssertionError("replacement producer unexpectedly gained the missing evaluation map")
    return {
        "schema": "closed-universe-berger-replacement-112-executable-unary-variational-input-shortfall-payload-v1",
        "result_id": "BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL_PAYLOAD",
        "exact_absence_replay": {
            "old_executable_shape": values["old_108_payload"]["scalar_matrix_shape"],
            "old_parameterized_block_count": values["old_108_payload"]["block_count"],
            "old_local_Phi2_symbols": symbols,
            "replacement_retained_Phi2_sparse": background["Phi2_sparse"],
            "replacement_retained_to_component_jet_crosswalk_present": False,
            "replacement_local_Phi2_jet_map_present": False,
        },
        "first_missing_variational_derivative": {
            "formula": "D^3 S_108_nonrod[Phi0](Phi2_positive_mixed, e_input, e_output)",
            "equivalent_object": "evaluation of every old universal Phi2 component-jet coefficient factor on the new retained-basis Phi2 primitive",
            "affected_scope": "all Phi2-dependent nonrod q1 rows before removal of the old six-rod block",
            "status": "NO_CERTIFIED_MAP",
            "why_action_summary_is_insufficient": "four retained harmonic coefficients do not determine named local component jets and their spacetime derivatives without an explicit basis crosswalk",
        },
        "minimal_producer_contract": {
            "must_export": [
                "content-addressed retained-Phi2-basis to local component-jet map",
                "all local jets required by the serialized old universal coefficient factors",
                "evaluated normalized sparse D3S nonrod correction entries",
                "independent evaluation from the declared variational action",
            ],
            "then_compute": [
                "remove the obsolete six-rod action-derived entries",
                "derive and insert every eight-rod positive-mixed Hessian and adjoint entry",
                "replay q1 squared, cyclicity, real and K commutation directly from entries",
                "only after replacement-112 passes, attempt the material-parent-56 producer",
            ],
        },
        "disposition": {
            "replacement_112_executable_q1": "NO_CERTIFIED_MAP",
            "material_parent_56_export": "NOT_REACHED",
            "combined_160_export": "NO_CERTIFIED_MAP",
            "physical_reduction_and_downstream": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement-112-executable-unary-variational-input-shortfall-v1",
        "result_id": "BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL",
        "setting_id": values["replacement"]["setting_id"],
        "claim_status": "SHORTFALL_MISSING_POSITIVE_MIXED_PHI2_COMPONENT_JET_EVALUATION",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(), "canonical_sha256": canonical_sha256(payload),
        },
        "disposition": payload["disposition"],
        "next_gate": "EXPORT_POSITIVE_MIXED_PHI2_RETAINED_TO_COMPONENT_JET_MAP_AND_EVALUATED_D3S",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE audit imports the certified positive-mixed replacement-112 action result, the executable nonlinear-clock 108-row correction and the terminal two-producer serialization shortfall by content hash. It follows the work-package stop rule at the first missing variational derivative. The old executable correction is not blindly substituted: its normalized sparse terms contain explicit local background coefficient factors named Phi2_00 and further Phi2 component symbols with declared spacetime multiindices. The replacement producer instead exports its new positive-mixed Phi2 only as four coefficients in a retained 100-component harmonic basis. It exports neither a retained-basis-to-local-component-jet crosswalk nor evaluated local Phi2 jets. Therefore the coefficient-level object D^3 S_108_nonrod[Phi0](Phi2_positive_mixed,e_input,e_output), equivalently evaluation of every universal Phi2-dependent nonrod q1 coefficient on the new primitive, is not determined by the exported machine data. Four harmonic coefficients cannot be identified with named local component jets or their derivatives by row names or symmetry. This is the first missing variational input, before removal of the obsolete six-rod entries, insertion of the eight-rod positive-mixed Hessian, or any material-parent-56 calculation. The certificate does not claim that the derivative fails to exist, does not retract the action-level positive-mixed unary identities and does not reuse the old operator as replacement q1. Replacement-112 executable q1, the material-parent export, combined 160-row matrices and physical reduction remain fail-closed. No cohomology, q2, q3, Z2, memory, redshift, recoil, particle, positivity or quantum result is promoted. Activation requires a content-addressed retained-Phi2-basis to local component-jet map, all required evaluated jets, normalized sparse D3S nonrod entries and a method-distinct action evaluation."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_replacement_112_executable_unary_variational_input_shortfall --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement_112_executable_unary_variational_input_shortfall",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    cert = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        REPORT.write_text("# Replacement-112 executable unary variational input shortfall\n\nThe new retained-basis Phi2 has no certified local component-jet evaluation map, so the first required nonrod D3S correction is undefined.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
