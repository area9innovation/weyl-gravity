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
    "finite_kernel_intervals": PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json",
    "partitioned_matched_feedback": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json",
    "cross_window_detector_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "six_mismatched_feedback": PACKAGE / "certificates/BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "first_omitted_shell_provider": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "two_j5_all_channel_column_binding": PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json",
    "direct_shell_and_tail_stop_gate": PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json",
    "real_shell_extraction": PACKAGE / "certificates/BERGER_RECOIL_REAL_SHELL_EXTRACTION.json",
    "two_j6_reality_folded_binding": PACKAGE / "certificates/BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING.json",
    "reality_folded_stream_adapter": PACKAGE / "certificates/BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER.json",
    "numerical_input_contract": PACKAGE / "certificates/BERGER_RECOIL_NUMERICAL_INPUT_CONTRACT_V2.json",
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
            "id": "finite_detector_coefficient_provider_two_j0_to_4",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED",
        },
        {
            "id": "finite_polynomial_nested_time_convolution",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED",
        },
        {
            "id": "finite_exact_mode_kernel_interval_enclosure",
            "status": "CERTIFIED" if values["finite_kernel_intervals"]["flags"]["FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED",
        },
        {
            "id": "finite_detector_matched_absolute_g3_feedback_channels",
            "status": "CERTIFIED" if values["executable_readiness"]["flags"]["FINITE_DETECTOR_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "FINITE_DETECTOR_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED",
        },
        {
            "id": "finite_partitioned_detector_matched_absolute_g3_feedback",
            "status": "CERTIFIED" if values["partitioned_matched_feedback"]["flags"]["MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8"] else "OBSTRUCTED",
            "evidence_flag": "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8",
        },
        {
            "id": "finite_cross_window_detector_advanced_maxwell_remainder",
            "status": "CERTIFIED" if values["cross_window_detector_remainder"]["flags"]["D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        },
        {
            "id": "finite_six_mismatched_absolute_g3_feedback_channels",
            "status": "CERTIFIED" if values["six_mismatched_feedback"]["flags"]["SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED"] else "OBSTRUCTED",
            "evidence_flag": "SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED",
        },
        {
            "id": "finite_first_omitted_shell_direct_provider_two_j5",
            "status": "CERTIFIED" if values["first_omitted_shell_provider"]["flags"]["TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED"] else "OBSTRUCTED",
            "evidence_flag": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        },
        {
            "id": "finite_two_j5_all_channel_column_feedback_binding",
            "status": "CERTIFIED" if values["two_j5_all_channel_column_binding"]["flags"]["ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED"] else "OBSTRUCTED",
            "evidence_flag": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED",
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
        {
            "id": "generic_direct_finite_shell_provider",
            "status": "CERTIFIED" if values["direct_shell_and_tail_stop_gate"]["flags"]["GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED",
        },
        {
            "id": "complex_channel_to_real_shell_scalar_map",
            "status": "CERTIFIED" if values["real_shell_extraction"]["flags"]["COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED"] else "OBSTRUCTED",
            "evidence_flag": "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED",
        },
        {
            "id": "finite_two_j6_reality_folded_feedback_binding",
            "status": "CERTIFIED" if values["two_j6_reality_folded_binding"]["flags"]["ALL_56_TWO_J6_CHANNEL_COLUMN_BLOCKS_CERTIFIED"] else "OBSTRUCTED",
            "evidence_flag": "ALL_56_TWO_J6_CHANNEL_COLUMN_BLOCKS_CERTIFIED",
        },
        {
            "id": "generic_reality_folded_successive_shell_adapter",
            "status": "CERTIFIED" if values["reality_folded_stream_adapter"]["flags"]["CONTIGUOUS_SUCCESSIVE_SHELL_STREAM_ADAPTER_EXPORTED"] else "OBSTRUCTED",
            "evidence_flag": "CONTIGUOUS_SUCCESSIVE_SHELL_STREAM_ADAPTER_EXPORTED",
        },
    ]
    external = [
        {
            "id": "exact_numerical_input_contract_v2",
            "status": "CERTIFIED" if values["numerical_input_contract"]["flags"]["EXACT_NUMERICAL_INPUT_CONTRACT_V2_EXPORTED"] else "OBSTRUCTED",
            "activation": "AVAILABLE",
            "legacy_v1_status": "OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH",
        },
        {"id": "numerical_positive_masses", "status": "OPEN", "activation": "DEFERRED", "required_domain": "m_0>0 and m_1>0"},
        {"id": "numerical_nonzero_couplings", "status": "OPEN", "activation": "DEFERRED", "required_domain": "g_0!=0 and g_1!=0"},
        {"id": "positive_inverse_Berger_volume", "status": "OPEN", "activation": "DEFERRED", "required_domain": "Vol_gHat(S^3)^(-1)>0"},
        {"id": "contiguous_shell_and_four_tail_schedule", "status": "OPEN", "activation": "DEFERRED"},
        {"id": "scalar_stopping_goal", "status": "OPEN", "activation": "DEFERRED", "allowed": ["entry_tolerance", "entry_nonzero", "entry_sign", "rank_two"]},
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
        "finite_kernel_intervals": "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED",
        "partitioned_matched_feedback": "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8",
        "cross_window_detector_remainder": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        "six_mismatched_feedback": "SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED",
        "first_omitted_shell_provider": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "two_j5_all_channel_column_binding": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED",
        "direct_shell_and_tail_stop_gate": "TAIL_AWARE_FOUR_STREAM_STOP_CALLABLE_EXPORTED",
        "real_shell_extraction": "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED",
        "two_j6_reality_folded_binding": "ALL_56_TWO_J6_CHANNEL_COLUMN_BLOCKS_CERTIFIED",
        "reality_folded_stream_adapter": "CONTIGUOUS_SUCCESSIVE_SHELL_STREAM_ADAPTER_EXPORTED",
        "numerical_input_contract": "EXACT_NUMERICAL_INPUT_CONTRACT_V2_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    readiness = readiness_audit(values)
    if not readiness["symbolic_modewise_word_ready"] or not readiness["internal_modewise_stream_ready"] or readiness["four_scalar_stream_active"]:
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
        "certified. The symbolic word and internal executable stream are now ready: "
        "exact shell aggregation is callable and the validated "
        "advanced-Maxwell detector coefficients are callable for 2j=0,...,4, but the "
        "latter are not a complete all-shell detector provider or a massive/recoil "
        "evaluation. A finite polynomial causal-convolution engine and exact finite "
        "Berger mode-kernel interval enclosures through 2j=4 are certified, including "
        "the massive scalar/one-form physical-correction carrier. The detector-matched "
        "I_000[0,0] and I_111[0,0] coefficient blocks are now evaluated on the "
        "validation mass domain by Green adjunction. A causal cellwise refinement "
        "strictly contracts both matched complex enclosures on its 2/4/8-cell rail "
        "below the whole-support hulls, but both 8-cell enclosures still contain "
        "zero. The D1/h0 cross-window remainder is certified, and all six "
        "mismatched two_j=0,column-0 channels are evaluated: four are exact "
        "support zeros and the two allowed channels have contracting but "
        "zero-containing enclosures. The direct detector-polynomial, D1/h0 "
        "remainder and exact-kernel payload is now extended to two_j=5 by an "
        "explicit source-hash carrier crosswalk, while the separate hashed "
        "exact-T stream remains unidentified. All 48 two_j=5 channel-column "
        "blocks are now evaluated on the validation mass domain: 24 are exact "
        "support zeros and the other 24 contain zero, while the four allowed "
        "k=0 paths contract from two to four cells. A content-addressed generic "
        "direct finite-shell provider now has a contiguous two_j=6 sentinel, and "
        "the fail-closed four-stream tail stop callable is exported. The two_j=6 "
        "feedback shell is now complete: 32 representative blocks are evaluated "
        "directly and 24 partner blocks are exact reality images, yielding all 56 "
        "blocks and eight real channel sums. The SU(2) conjugate-column theorem "
        "certifies the complex-to-real shell map. The generic successive-shell "
        "adapter builds and binds each shell, evaluates only independent columns, "
        "derives reality partners, aggregates all four entries and invokes the stop "
        "gate after every shell. The v2 numerical schema and callable translator are now "
        "certified and legacy v1 is explicitly obstructed. Numerical masses, couplings, "
        "inverse volume, shell/tail schedule, precision and a stopping goal remain deferred "
        "pending a provenance-complete EXPLICIT_EXTERNAL_VALUES declaration. The exact "
        "generic coefficient functional is not itself a numerical Green-image "
        "evaluation. Numerical values must not be invented. This gate does not evaluate a recoil scalar, "
        "restrict to the tangent cone, activate Bridge 3, promote finite-r/"
        "all-orders observer-morphism stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-scalar-stream-activation-gate-v1",
        "result_id": "BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE",
        "setting_id": values["dual_norms"]["setting_id"],
        "claim_status": "INTERNAL_EXECUTABLE_RECOIL_STREAM_READY_EXTERNAL_NUMERICAL_SPECIALIZATION_DEFERRED",
        "atlas_status": "CERTIFIED",
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
            "current_active_gate": "await a provenance-complete explicit external value declaration",
            "external_specialization_gate": "DEFERRED_UNTIL_EXACT_VALUES_ARE_EXPLICITLY_DECLARED",
            "numerical_input_contract_v2": "CERTIFIED_SCHEMA_AND_TRANSLATOR_VALUES_DEFERRED",
            "legacy_input_contract_v1": "OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH",
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
            "INTERNAL_MODEWISE_RECOIL_STREAM_READY": True,
            "SYMBOLIC_MODEWISE_RECOIL_WORD_READY": True,
            "EXECUTABLE_MODEWISE_RECOIL_STREAM_READY": True,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": True,
            "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED": True,
            "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED": True,
            "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED": True,
            "FINITE_DETECTOR_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED": True,
            "FINITE_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK_EXPORTED": True,
            "FINITE_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER_EXPORTED": True,
            "FINITE_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED": True,
            "ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EXPORTED": True,
            "FINITE_FIRST_OMITTED_SHELL_DIRECT_PROVIDER_TWO_J5_EXPORTED": True,
            "TWO_J5_FEEDBACK_CHANNELS_EVALUATED": True,
            "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED": True,
            "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED": True,
            "TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED": True,
            "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED": True,
            "TWO_J6_FEEDBACK_CHANNELS_EVALUATED": True,
            "GENERIC_REALITY_FOLDED_SUCCESSIVE_SHELL_ADAPTER_EXPORTED": True,
            "NUMERICAL_RECOIL_SPECIALIZATION_INPUT_EXPORTED": False,
            "EXACT_NUMERICAL_INPUT_CONTRACT_V2_EXPORTED": True,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
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
        raise SystemExit("stale recoil scalar stream activation gate")
    print("BERGER_RECOIL_SCALAR_STREAM_ACTIVATION_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
