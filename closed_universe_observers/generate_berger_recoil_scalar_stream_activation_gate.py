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


def readiness_audit(values: dict[str, dict[str, Any]], *, pretend_profiles_evaluated: bool = False) -> dict[str, Any]:
    preparation_flags = dict(values["preparations"]["flags"])
    if pretend_profiles_evaluated:
        preparation_flags["HARMONIC_COEFFICIENTS_EVALUATED"] = True
        preparation_flags["ADVANCED_GREEN_IMAGES_EVALUATED"] = True
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
            "id": "complete_harmonic_preparation_coefficients",
            "status": "CERTIFIED" if preparation_flags["HARMONIC_COEFFICIENTS_EVALUATED"] else "OPEN",
            "evidence_flag": "HARMONIC_COEFFICIENTS_EVALUATED",
        },
        {
            "id": "advanced_massive_preparation_image",
            "status": "CERTIFIED" if preparation_flags["ADVANCED_GREEN_IMAGES_EVALUATED"] else "OPEN",
            "evidence_flag": "ADVANCED_GREEN_IMAGES_EVALUATED",
        },
        {
            "id": "complete_modewise_recoil_scalar_integrand",
            "status": "CERTIFIED" if values["dual_norms"]["flags"]["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] else "OPEN",
            "evidence_flag": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
        },
    ]
    external = [
        {"id": "numerical_positive_masses", "status": "OPEN", "required_domain": "m_0>0 and m_1>0"},
        {"id": "numerical_nonzero_couplings", "status": "OPEN", "required_domain": "g_0!=0 and g_1!=0"},
        {"id": "scalar_stopping_goal", "status": "OPEN", "allowed": ["interval_tolerance", "nonzero", "sign"]},
    ]
    internal_ready = all(row["status"] == "CERTIFIED" for row in internal)
    external_ready = all(row["status"] == "CERTIFIED" for row in external)
    return {
        "internal_rows": internal,
        "external_rows": external,
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
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    readiness = readiness_audit(values)
    if readiness["internal_modewise_stream_ready"] or readiness["four_scalar_stream_active"]:
        raise AssertionError("recoil scalar stream was activated without complete inputs")
    mutation = readiness_audit(values, pretend_profiles_evaluated=True)
    harmonic_rows = {
        row["id"]: row["status"] for row in mutation["internal_rows"]
    }
    if harmonic_rows["complete_harmonic_preparation_coefficients"] != "CERTIFIED" or harmonic_rows["advanced_massive_preparation_image"] != "CERTIFIED":
        raise AssertionError("profile-evaluation mutation was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL activation gate "
        "separates the internal modewise recoil construction from later "
        "numerical specialization. The absolute-g3 operator, exact switches, "
        "finite Maxwell/massive kernels, selected exact-T clock transform and "
        "all four symbolic detector tail radii are certified. The stream is "
        "nevertheless inactive because the detector-selected preparations "
        "remain operator-defined: their harmonic coefficients and advanced "
        "massive Green images are explicitly unevaluated, so no complete "
        "per-shell scalar integrand exists. Numerical positive masses, "
        "nonzero couplings and an interval/nonzero/sign stopping goal are a "
        "separate later input gate. The next coherent calculation is to "
        "serialize the complete per-shell preparation and recoil contraction "
        "with masses symbolic and couplings factored; numerical values must "
        "not be invented. This gate does not evaluate a recoil scalar, "
        "restrict to the tangent cone, activate Bridge 3, promote finite-r/"
        "all-orders observer-morphism stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-scalar-stream-activation-gate-v1",
        "result_id": "BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE",
        "setting_id": values["dual_norms"]["setting_id"],
        "claim_status": "SYMBOLIC_TAIL_ENVELOPE_CERTIFIED_MODEWISE_SCALAR_STREAM_INPUTS_OPEN",
        "atlas_status": "OPEN",
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
            "current_active_gate": "construct complete modewise preparation/recoil scalar integrand",
            "parameterization_during_internal_gate": "m_0,m_1 symbolic positive; factor g_0,g_1 monomials",
            "later_external_gate": "declare numerical masses, nonzero couplings and interval/nonzero/sign stopping goal",
            "dense_profile_materialization": "NOT_SELECTED",
            "physical_branch_bridge": "INACTIVE_NO_CERTIFIED_MAP",
        },
        "mutation_results": [
            {
                "name": "pretend_operator_defined_preparations_are_harmonically_evaluated",
                "detected": True,
                "mutated_rows": [
                    "complete_harmonic_preparation_coefficients",
                    "advanced_massive_preparation_image",
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
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": False,
            "NUMERICAL_RECOIL_SPECIALIZATION_INPUT_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SERIALIZE_COMPLETE_PER_SHELL_PREPARATION_AND_RECOIL_CONTRACTION_WITH_SYMBOLIC_POSITIVE_MASSES_AND_FACTORED_COUPLINGS",
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
