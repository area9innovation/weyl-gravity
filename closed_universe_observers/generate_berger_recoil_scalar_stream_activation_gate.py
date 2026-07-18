#!/usr/bin/env python3
"""Audit activation of the four Berger recoil-scalar shell streams."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE.json"
SCHEMA = PACKAGE / "schema/berger-recoil-scalar-stream-activation-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-scalar-stream-activation-gate.md"
DEPENDENCIES = {
    "recoil_operator": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "preparations": PACKAGE / "certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json",
    "mode_kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "clock_transform": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM.json",
    "streaming_preflight": PACKAGE / "certificates/BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT.json",
    "dual_norms": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
    "coupling_stripped": PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json",
    "spacetime_signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "per_shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "executable_readiness": PACKAGE / "certificates/BERGER_RECOIL_STREAM_EXECUTABLE_READINESS_AUDIT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_recoil_scalar_stream_activation_gate.py",
    PACKAGE / "tests/test_berger_recoil_scalar_stream_activation_gate.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readiness_audit(values: dict[str, dict[str, Any]], *, drop_per_shell_word: bool = False) -> dict[str, Any]:
    word_flags = dict(values["per_shell_word"]["flags"])
    if drop_per_shell_word:
        word_flags["DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED"] = False
        word_flags["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] = False
    internal = [
        {
            "id": "exact_absolute_g3_operator",
            "status": "CERTIFIED" if values["recoil_operator"]["flags"]["FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED"] else "OPEN",
            "evidence_flag": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
        },
        {
            "id": "exact_normalized_switches",
            "status": "CERTIFIED" if values["switches"]["flags"]["EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED"] else "OPEN",
            "evidence_flag": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        },
        {
            "id": "finite_mode_Maxwell_and_massive_kernels",
            "status": "CERTIFIED" if values["mode_kernels"]["flags"]["EXACT_FINITE_MODE_MAXWELL_GREEN_KERNELS_EXPORTED"] and values["mode_kernels"]["flags"]["EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED"] else "OPEN",
            "evidence_flag": "EXACT_FINITE_MODE_MAXWELL_GREEN_KERNELS_EXPORTED+EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED",
        },
        {
            "id": "response_specific_stopping_envelope",
            "status": "CERTIFIED" if values["dual_norms"]["flags"]["FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED"] else "OPEN",
            "evidence_flag": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
        },
        {
            "id": "fixed_preparation_coupling_factorization",
            "status": "CERTIFIED" if values["coupling_stripped"]["flags"]["ABSOLUTE_G3_CHANNEL_MONOMIALS_EXPORTED"] else "OPEN",
            "evidence_flag": "ABSOLUTE_G3_CHANNEL_MONOMIALS_EXPORTED",
        },
        {
            "id": "spacetime_form_block_signs",
            "status": "CERTIFIED" if values["spacetime_signs"]["flags"]["RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED"] else "OPEN",
            "evidence_flag": "RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED",
        },
        {
            "id": "complete_symbolic_harmonic_preparation_functional",
            "status": "CERTIFIED" if word_flags["DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED"] else "OPEN",
            "evidence_flag": "DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED",
        },
        {
            "id": "advanced_massive_preparation_operator_word",
            "status": "CERTIFIED" if word_flags["DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED"] else "OPEN",
            "evidence_flag": "DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED",
        },
        {
            "id": "complete_modewise_recoil_scalar_integrand",
            "status": "CERTIFIED" if word_flags["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] else "OPEN",
            "evidence_flag": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
        },
        {
            "id": "callable_shell_interval_backend",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED",
        },
        {
            "id": "complete_detector_coefficient_provider",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED",
        },
        {
            "id": "nested_time_convolution_backend",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED",
        },
        {
            "id": "tail_aware_aggregate_stop_loop",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED",
        },
    ]
    external = [
        {"id": "numerical_positive_masses", "status": "OPEN", "activation": "DEFERRED", "required_domain": "m_0>0 and m_1>0"},
        {"id": "numerical_nonzero_couplings", "status": "OPEN", "activation": "DEFERRED", "required_domain": "g_0!=0 and g_1!=0"},
        {"id": "scalar_stopping_goal", "status": "OPEN", "activation": "DEFERRED", "allowed": ["interval_tolerance", "nonzero", "sign"]},
    ]
    internal_ready = all(row["status"] == "CERTIFIED" for row in internal)
    external_ready = all(row["status"] == "CERTIFIED" for row in external)
    return {
        "internal_rows": internal,
        "external_rows": external,
        "symbolic_modewise_word_ready": all(row["status"] == "CERTIFIED" for row in internal[:9]),
        "internal_modewise_stream_ready": internal_ready,
        "numerical_specialization_ready": external_ready,
        "four_scalar_stream_active": internal_ready and external_ready,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "recoil_operator": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "preparations": "OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED",
        "mode_kernels": "EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED",
        "clock_transform": "FINITE_SELECTED_EXACT_T_TEMPORAL_IMAGE_REPRESENTATION_EXPORTED",
        "streaming_preflight": "RESPONSE_SPECIFIC_STREAMING_STOPPING_RULE_EXPORTED",
        "dual_norms": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
        "coupling_stripped": "ABSOLUTE_G3_CHANNEL_MONOMIALS_EXPORTED",
        "spacetime_signs": "RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED",
        "per_shell_word": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
        "executable_readiness": "NUMERICAL_SPECIALIZATION_INPUT_SCHEMA_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    readiness = readiness_audit(values)
    if not readiness["symbolic_modewise_word_ready"] or readiness["internal_modewise_stream_ready"] or readiness["four_scalar_stream_active"]:
        raise AssertionError("internal recoil readiness or external gate drifted")
    mutation = readiness_audit(values, drop_per_shell_word=True)
    word_rows = {
        row["id"]: row["status"] for row in mutation["internal_rows"]
    }
    if word_rows["complete_symbolic_harmonic_preparation_functional"] != "OPEN" or word_rows["complete_modewise_recoil_scalar_integrand"] != "OPEN":
        raise AssertionError("per-shell-word deletion mutation was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL activation gate "
        "separates the internal modewise recoil construction from later "
        "numerical specialization. The absolute-g3 operator, exact switches, "
        "finite Maxwell/massive kernels, selected exact-T clock transform, "
        "the four symbolic detector tail radii, the fixed coupling-stripped "
        "preparations, the Lorentzian spacetime form-block signs, and the "
        "complete symbolic per-shell preparation/recoil word are all "
        "certified. The symbolic word is ready, but the executable stream is "
        "still obstructed: exact shell aggregation is callable, but no coefficient "
        "provider, nested time-convolution backend or tail-aware aggregate stop loop "
        "is exported. Numerical masses, couplings and a stopping goal are therefore "
        "deferred; supplying them now would not produce an interval. The exact "
        "generic coefficient functional is not itself a numerical Green-image "
        "evaluation. Numerical values must not be invented. This gate does not evaluate a recoil scalar, "
        "restrict to the tangent cone, activate Bridge 3, promote finite-r/"
        "all-orders observer-morphism stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-scalar-stream-activation-gate-v1",
        "result_id": "BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE",
        "setting_id": values["dual_norms"]["setting_id"],
        "claim_status": "SYMBOLIC_WORD_READY_EXECUTABLE_RECOIL_STREAM_OBSTRUCTED",
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
        "readiness": readiness,
        "sequencing_decision": {
            "completed_internal_gate": "complete symbolic preparation/recoil scalar operator word with exact Peter-Weyl reconstruction",
            "parameterization_during_internal_gate": "hold tilde_u_0,tilde_u_1 fixed; m_0,m_1 symbolic positive; factor explicit g_b g_c^2 monomials",
            "current_active_gate": "implement detector coefficient and nested time-convolution backends",
            "external_specialization_gate": "DEFERRED_UNTIL_EXECUTABLE_BACKEND",
            "dense_profile_materialization": "NOT_SELECTED",
            "physical_branch_bridge": "INACTIVE_NO_CERTIFIED_MAP",
        },
        "mutation_results": [
            {
                "name": "delete_complete_per_shell_operator_word",
                "detected": True,
                "mutated_rows": [
                    "complete_symbolic_harmonic_preparation_functional",
                    "advanced_massive_preparation_operator_word",
                    "complete_modewise_recoil_scalar_integrand",
                ],
            },
            {
                "name": "activate_stream_from_symbolic_tail_radius_alone",
                "detected": readiness["four_scalar_stream_active"] is False,
            },
        ],
        "flags": {
            "RECOIL_SCALAR_STREAM_ACTIVATION_AUDIT_EXPORTED": True,
            "ANALYTIC_SYMBOLIC_TAIL_ENVELOPE_COMPLETE": True,
            "INTERNAL_MODEWISE_RECOIL_STREAM_READY": False,
            "SYMBOLIC_MODEWISE_RECOIL_WORD_READY": True,
            "EXECUTABLE_MODEWISE_RECOIL_STREAM_READY": False,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": True,
            "NUMERICAL_RECOIL_SPECIALIZATION_INPUT_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPLEMENT_DETECTOR_COEFFICIENT_AND_NESTED_TIME_CONVOLUTION_BACKENDS",
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
        raise SystemExit("stale recoil scalar stream activation gate")
    print("BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
