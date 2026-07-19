#!/usr/bin/env python3
"""Fail closed unless the symbolic Berger recoil word has an interval backend."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_STREAM_EXECUTABLE_READINESS_AUDIT.json"
SCHEMA = PACKAGE / "schema/berger-recoil-stream-executable-readiness-audit-v1.schema.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-recoil-numerical-specialization-input-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-stream-executable-readiness-audit.md"
BACKEND = PACKAGE / "berger_recoil_interval_stream.py"
FORM_BACKEND = PACKAGE / "berger_recoil_detector_form_binding.py"
MASSIVE_BACKEND = PACKAGE / "berger_recoil_massive_diagonal_preparation.py"
RETARDED_BACKEND = PACKAGE / "berger_recoil_free_emitter_retarded_channel.py"
PARTITIONED_BACKEND = PACKAGE / "berger_recoil_partitioned_massive_preparation.py"
MATCHED_FEEDBACK_BACKEND = PACKAGE / "berger_recoil_matched_feedback_channel.py"
PARTITIONED_FEEDBACK_BACKEND = PACKAGE / "berger_recoil_partitioned_feedback_channel.py"
MISMATCHED_FEEDBACK_BACKEND = PACKAGE / "berger_recoil_mismatched_feedback_channel.py"
FIRST_OMITTED_BINDING_BACKEND = PACKAGE / "berger_recoil_first_omitted_shell_binding.py"
DIRECT_SHELL_BACKEND = PACKAGE / "berger_recoil_direct_finite_shell_provider.py"
REAL_SHELL_BACKEND = PACKAGE / "berger_recoil_real_shell_extraction.py"
DEPENDENCIES = {
    "per_shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "tail_envelopes": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
    "mode_kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "finite_shell_aggregator": PACKAGE / "certificates/BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR.json",
    "finite_detector_provider": PACKAGE / "certificates/BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER.json",
    "finite_nested_convolution": PACKAGE / "certificates/BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION.json",
    "finite_mode_kernel_intervals": PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json",
    "finite_detector_form_binding": PACKAGE / "certificates/BERGER_RECOIL_DETECTOR_FORM_BINDING.json",
    "finite_massive_diagonal_preparation": PACKAGE / "certificates/BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION.json",
    "finite_physical_massive_cauchy": PACKAGE / "certificates/BERGER_RECOIL_PHYSICAL_MASSIVE_CAUCHY_PREPARATION.json",
    "finite_positive_energy_preparation": PACKAGE / "certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json",
    "finite_free_emitter_retarded_channel": PACKAGE / "certificates/BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL.json",
    "finite_partitioned_leading_response_rank_two": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json",
    "finite_matched_feedback_channels": PACKAGE / "certificates/BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "finite_partitioned_matched_feedback": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json",
    "finite_cross_window_detector_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "finite_six_mismatched_feedback": PACKAGE / "certificates/BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "finite_first_omitted_shell_provider": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "finite_two_j5_all_channel_column_binding": PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json",
    "direct_shell_and_tail_stop_gate": PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json",
    "real_shell_extraction": PACKAGE / "certificates/BERGER_RECOIL_REAL_SHELL_EXTRACTION.json",
}
REQUIRED_CALLABLES = {
    "detector_profile_coefficient_provider": "detector_profile_coefficient_interval",
    "nested_time_convolution_backend": "evaluate_nested_green_time_convolution_interval",
    "shell_interval_evaluator": "evaluate_recoil_shell_interval",
    "tail_aware_aggregate_stop_loop": "stream_recoil_intervals",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_recoil_stream_executable_readiness_audit.py",
    PACKAGE / "tests/test_berger_recoil_stream_executable_readiness_audit.py",
    SCHEMA,
    INPUT_SCHEMA,
    REPORT,
    BACKEND,
    FORM_BACKEND,
    MASSIVE_BACKEND,
    RETARDED_BACKEND,
    PARTITIONED_BACKEND,
    MATCHED_FEEDBACK_BACKEND,
    PARTITIONED_FEEDBACK_BACKEND,
    MISMATCHED_FEEDBACK_BACKEND,
    FIRST_OMITTED_BINDING_BACKEND,
    DIRECT_SHELL_BACKEND,
    REAL_SHELL_BACKEND,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _backend_functions(path: Path = BACKEND) -> set[str]:
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text())
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def readiness_rows(
    functions: set[str],
    *,
    form_functions: set[str] | None = None,
    massive_functions: set[str] | None = None,
    retarded_functions: set[str] | None = None,
    partitioned_functions: set[str] | None = None,
    matched_feedback_functions: set[str] | None = None,
    partitioned_feedback_functions: set[str] | None = None,
    mismatched_feedback_functions: set[str] | None = None,
    real_shell_functions: set[str] | None = None,
    finite_detector_provider: bool = False,
    complete_detector_provider: bool = False,
    finite_nested_convolution: bool = False,
    finite_mode_kernel_intervals: bool = False,
    finite_detector_form_binding: bool = False,
    finite_massive_diagonal_preparation: bool = False,
    finite_physical_massive_cauchy: bool = False,
    finite_positive_energy_preparation: bool = False,
    finite_free_emitter_retarded_channel: bool = False,
    finite_partitioned_leading_response_rank_two: bool = False,
    finite_matched_feedback_channels: bool = False,
    finite_partitioned_matched_feedback: bool = False,
    finite_cross_window_detector_remainder: bool = False,
    finite_six_mismatched_feedback: bool = False,
    finite_first_omitted_shell_provider: bool = False,
    finite_two_j5_all_channel_column_binding: bool = False,
    generic_direct_shell_provider: bool = False,
    certified_tail_stop_gate: bool = False,
    certified_real_shell_extraction: bool = False,
    complete_nested_convolution: bool = False,
    treat_symbolic_word_as_backend: bool = False,
) -> list[dict[str, Any]]:
    form_functions = form_functions or set()
    massive_functions = massive_functions or set()
    retarded_functions = retarded_functions or set()
    partitioned_functions = partitioned_functions or set()
    matched_feedback_functions = matched_feedback_functions or set()
    partitioned_feedback_functions = partitioned_feedback_functions or set()
    mismatched_feedback_functions = mismatched_feedback_functions or set()
    real_shell_functions = real_shell_functions or set()
    rows = [
        {
            "id": "complete_symbolic_operator_word",
            "status": "CERTIFIED",
            "evidence": "BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD",
        },
        {
            "id": "finite_detector_coefficient_provider_two_j0_to_4",
            "status": (
                "CERTIFIED"
                if finite_detector_provider
                and REQUIRED_CALLABLES["detector_profile_coefficient_provider"] in functions
                else "OBSTRUCTED"
            ),
            "required_callable": REQUIRED_CALLABLES["detector_profile_coefficient_provider"],
            "coverage": "two_j_inclusive_0_to_4",
            "evidence": (
                "BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER"
                if finite_detector_provider
                and REQUIRED_CALLABLES["detector_profile_coefficient_provider"] in functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_polynomial_nested_time_convolution",
            "status": (
                "CERTIFIED"
                if finite_nested_convolution
                and REQUIRED_CALLABLES["nested_time_convolution_backend"] in functions
                else "OBSTRUCTED"
            ),
            "required_callable": REQUIRED_CALLABLES["nested_time_convolution_backend"],
            "coverage": "supplied_finite_slab_polynomial_enclosures",
            "evidence": (
                "BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION"
                if finite_nested_convolution
                and REQUIRED_CALLABLES["nested_time_convolution_backend"] in functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_exact_mode_kernel_interval_enclosure",
            "status": (
                "CERTIFIED"
                if finite_mode_kernel_intervals
                and "enclose_exact_mode_sine_kernel" in functions
                else "OBSTRUCTED"
            ),
            "required_callable": "enclose_exact_mode_sine_kernel",
            "coverage": "Maxwell_and_massive_two_form_two_j_inclusive_0_to_4",
            "evidence": (
                "BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE"
                if finite_mode_kernel_intervals
                and "enclose_exact_mode_sine_kernel" in functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_detector_advanced_maxwell_Dhat1_binding",
            "status": (
                "CERTIFIED"
                if finite_detector_form_binding
                and "assemble_detector_advanced_maxwell_polynomial" in form_functions
                and "apply_spacetime_dhat1_to_detector_advanced_maxwell" in form_functions
                else "OBSTRUCTED"
            ),
            "required_callables": [
                "assemble_detector_advanced_maxwell_polynomial",
                "apply_spacetime_dhat1_to_detector_advanced_maxwell",
            ],
            "coverage": "D0_D1_all_passive_columns_two_j_inclusive_0_to_4",
            "evidence": (
                "BERGER_RECOIL_DETECTOR_FORM_BINDING"
                if finite_detector_form_binding
                and "assemble_detector_advanced_maxwell_polynomial" in form_functions
                and "apply_spacetime_dhat1_to_detector_advanced_maxwell" in form_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_switched_diagonal_massive_advanced_preparation",
            "status": (
                "CERTIFIED"
                if finite_massive_diagonal_preparation
                and "evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left" in massive_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left",
            "coverage": "D0_D1_all_passive_columns_two_j_inclusive_0_to_4_runtime_positive_mass_interval",
            "evidence": (
                "BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION"
                if finite_massive_diagonal_preparation
                and "evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left" in massive_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_physical_massive_advanced_cauchy_pair",
            "status": (
                "CERTIFIED"
                if finite_physical_massive_cauchy
                and "evaluate_physical_massive_advanced_cauchy_pair_at_support_left" in massive_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_physical_massive_advanced_cauchy_pair_at_support_left",
            "coverage": "D0_D1_all_passive_columns_two_j_inclusive_0_to_4_runtime_positive_mass_interval",
            "evidence": "BERGER_RECOIL_PHYSICAL_MASSIVE_CAUCHY_PREPARATION" if finite_physical_massive_cauchy and "evaluate_physical_massive_advanced_cauchy_pair_at_support_left" in massive_functions else "NO_CERTIFIED_FINITE_CALLABLE",
        },
        {
            "id": "finite_coupling_stripped_positive_energy_preparation_coefficients",
            "status": (
                "CERTIFIED"
                if finite_positive_energy_preparation
                and "evaluate_coupling_stripped_positive_energy_preparation_at_support_left" in massive_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_coupling_stripped_positive_energy_preparation_at_support_left",
            "coverage": "D0_D1_all_passive_columns_two_j_inclusive_0_to_4_runtime_positive_mass_interval",
            "evidence": "BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS" if finite_positive_energy_preparation and "evaluate_coupling_stripped_positive_energy_preparation_at_support_left" in massive_functions else "NO_CERTIFIED_FINITE_CALLABLE",
        },
        {
            "id": "finite_free_emitter_first_retarded_maxwell_channel",
            "status": (
                "CERTIFIED"
                if finite_free_emitter_retarded_channel
                and "evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right"
                in retarded_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right",
            "coverage": "D0_D1_all_passive_columns_two_j_inclusive_0_to_4_runtime_positive_mass_interval",
            "evidence": (
                "BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL"
                if finite_free_emitter_retarded_channel
                and "evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right"
                in retarded_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_partitioned_detector_selected_leading_response_rank_two",
            "status": (
                "CERTIFIED"
                if finite_partitioned_leading_response_rank_two
                and "evaluate_partitioned_positive_energy_preparation_at_support_left"
                in partitioned_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_partitioned_positive_energy_preparation_at_support_left",
            "coverage": "D0_D1_two_j0_column0_mass_squared_interval_1_to_2_partition_count_32",
            "evidence": (
                "BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO"
                if finite_partitioned_leading_response_rank_two
                and "evaluate_partitioned_positive_energy_preparation_at_support_left"
                in partitioned_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_detector_matched_absolute_g3_feedback_channels",
            "status": (
                "CERTIFIED"
                if finite_matched_feedback_channels
                and "evaluate_detector_matched_absolute_g3_feedback_channel"
                in matched_feedback_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_detector_matched_absolute_g3_feedback_channel",
            "coverage": "I_000_and_I_111_two_j0_column0_mass_squared_interval_1_to_2_zero_containing",
            "evidence": (
                "BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS"
                if finite_matched_feedback_channels
                and "evaluate_detector_matched_absolute_g3_feedback_channel"
                in matched_feedback_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_partitioned_detector_matched_absolute_g3_feedback",
            "status": (
                "CERTIFIED"
                if finite_partitioned_matched_feedback
                and "evaluate_partitioned_detector_matched_absolute_g3_feedback_channel"
                in partitioned_feedback_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_partitioned_detector_matched_absolute_g3_feedback_channel",
            "coverage": "I_000_and_I_111_two_j0_column0_partition_counts_2_4_8_zero_containing",
            "evidence": (
                "BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK"
                if finite_partitioned_matched_feedback
                and "evaluate_partitioned_detector_matched_absolute_g3_feedback_channel"
                in partitioned_feedback_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_cross_window_detector_advanced_maxwell_remainder",
            "status": (
                "CERTIFIED"
                if finite_cross_window_detector_remainder
                and "_cross_window_detector_image" in mismatched_feedback_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "_cross_window_detector_image",
            "coverage": "D1_advanced_Maxwell_polynomial_on_h0_two_j0_to_4_tau_max_3_over_8",
            "evidence": (
                "BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER"
                if finite_cross_window_detector_remainder
                and "_cross_window_detector_image" in mismatched_feedback_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_six_mismatched_absolute_g3_feedback_channels",
            "status": (
                "CERTIFIED"
                if finite_six_mismatched_feedback
                and "evaluate_partitioned_absolute_g3_feedback_channel"
                in mismatched_feedback_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_partitioned_absolute_g3_feedback_channel",
            "coverage": "six_mismatched_two_j0_column0_four_causal_zeros_two_zero_containing_partition_rails",
            "evidence": (
                "BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS"
                if finite_six_mismatched_feedback
                and "evaluate_partitioned_absolute_g3_feedback_channel"
                in mismatched_feedback_functions
                else "NO_CERTIFIED_FINITE_CALLABLE"
            ),
        },
        {
            "id": "finite_first_omitted_shell_direct_provider_two_j5",
            "status": (
                "CERTIFIED"
                if finite_first_omitted_shell_provider
                else "OBSTRUCTED"
            ),
            "coverage": "D0_D1_direct_detector_polynomials_D1_on_h0_remainder_and_five_exact_kernel_blocks_at_two_j5",
            "evidence": (
                "BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5"
                if finite_first_omitted_shell_provider
                else "NO_CERTIFIED_FIRST_OMITTED_SHELL_PAYLOAD"
            ),
            "feedback_binding_status": (
                "CERTIFIED"
                if finite_two_j5_all_channel_column_binding
                else "OPEN"
            ),
        },
        {
            "id": "finite_two_j5_all_channel_column_feedback_binding",
            "status": (
                "CERTIFIED"
                if finite_two_j5_all_channel_column_binding
                and "evaluate_partitioned_absolute_g3_feedback_column_bundle"
                in mismatched_feedback_functions
                else "OBSTRUCTED"
            ),
            "required_callable": "evaluate_partitioned_absolute_g3_feedback_column_bundle",
            "coverage": "all_8_Iabc_channels_times_all_6_passive_columns_at_two_j5_partition2_plus_partition4_column0_sentinel",
            "evidence": (
                "BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING"
                if finite_two_j5_all_channel_column_binding
                else "NO_CERTIFIED_TWO_J5_FEEDBACK_BINDING"
            ),
        },
        {
            "id": "generic_direct_finite_shell_provider",
            "status": "CERTIFIED" if generic_direct_shell_provider else "OBSTRUCTED",
            "required_callable": "build_direct_finite_shell_payload",
            "coverage": "content_addressed_arbitrary_declared_finite_two_j_with_contiguous_two_j6_sentinel",
            "evidence": "BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE" if generic_direct_shell_provider else "NO_CERTIFIED_GENERIC_DIRECT_SHELL_PROVIDER",
        },
        {
            "id": "complex_channel_to_real_shell_scalar_map",
            "status": (
                "CERTIFIED"
                if certified_real_shell_extraction
                and "extract_real_channel_column_sum" in real_shell_functions
                and "reality_reduced_columns" in real_shell_functions
                else "OBSTRUCTED"
            ),
            "required_callables": [
                "extract_real_channel_column_sum",
                "reality_reduced_columns",
            ],
            "coverage": "generic direct finite-shell SU2 reality theorem plus all eight two_j5 channel sums",
            "evidence": (
                "BERGER_RECOIL_REAL_SHELL_EXTRACTION"
                if certified_real_shell_extraction
                else "NO_CERTIFIED_MAP"
            ),
        },
    ]
    for identifier, callable_name in REQUIRED_CALLABLES.items():
        present = callable_name in functions
        if identifier == "detector_profile_coefficient_provider":
            present = present and complete_detector_provider
        if identifier == "nested_time_convolution_backend":
            present = present and complete_nested_convolution
        if identifier == "tail_aware_aggregate_stop_loop":
            present = present and certified_tail_stop_gate
        if treat_symbolic_word_as_backend:
            present = False
        rows.append(
            {
                "id": identifier,
                "status": "CERTIFIED" if present else "OBSTRUCTED",
                "required_callable": callable_name,
                "evidence": (
                    str(BACKEND.relative_to(ROOT))
                    if present
                    else (
                        "CALLABLE_SCOPED_TWO_J0_TO_4_ONLY"
                        if identifier == "detector_profile_coefficient_provider"
                        and finite_detector_provider
                        and callable_name in functions
                        else (
                            "CALLABLE_SCOPED_TO_SUPPLIED_POLYNOMIAL_ENCLOSURES"
                            if identifier == "nested_time_convolution_backend"
                            and finite_nested_convolution
                            and callable_name in functions
                            else "NO_CALLABLE_IMPLEMENTATION"
                        )
                    )
                ),
            }
        )
    return rows


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "per_shell_word": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
        "tail_envelopes": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
        "mode_kernels": "EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED",
        "finite_shell_aggregator": "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED",
        "finite_detector_provider": "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED",
        "finite_nested_convolution": "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED",
        "finite_mode_kernel_intervals": "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED",
        "finite_detector_form_binding": "EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE",
        "finite_massive_diagonal_preparation": "DIAGONAL_MASSIVE_DEGREE_TWO_ADVANCED_IMAGE_AT_SUPPORT_LEFT_EXPORTED",
        "finite_physical_massive_cauchy": "EMITTER_FULL_FORM_CAUCHY_PAIR_EXPORTED",
        "finite_positive_energy_preparation": "COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED",
        "finite_free_emitter_retarded_channel": "FIRST_RETARDED_MAXWELL_CAUCHY_PAIR_AT_SUPPORT_RIGHT_EXPORTED",
        "finite_partitioned_leading_response_rank_two": "FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_ON_MASS_DOMAIN",
        "finite_matched_feedback_channels": "I_000_TWO_J0_K0_INTERVAL_EVALUATED",
        "finite_partitioned_matched_feedback": "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8",
        "finite_cross_window_detector_remainder": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        "finite_six_mismatched_feedback": "SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED",
        "finite_first_omitted_shell_provider": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "finite_two_j5_all_channel_column_binding": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED",
        "direct_shell_and_tail_stop_gate": "TAIL_AWARE_FOUR_STREAM_STOP_CALLABLE_EXPORTED",
        "real_shell_extraction": "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(input_schema)
    functions = _backend_functions()
    form_functions = _backend_functions(FORM_BACKEND)
    massive_functions = _backend_functions(MASSIVE_BACKEND)
    retarded_functions = _backend_functions(RETARDED_BACKEND)
    partitioned_functions = _backend_functions(PARTITIONED_BACKEND)
    matched_feedback_functions = _backend_functions(MATCHED_FEEDBACK_BACKEND)
    partitioned_feedback_functions = _backend_functions(PARTITIONED_FEEDBACK_BACKEND)
    mismatched_feedback_functions = _backend_functions(MISMATCHED_FEEDBACK_BACKEND)
    real_shell_functions = _backend_functions(REAL_SHELL_BACKEND)
    finite_detector_provider = values["finite_detector_provider"]["flags"][
        "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"
    ]
    complete_detector_provider = values["finite_detector_provider"]["flags"][
        "COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED"
    ]
    finite_nested_convolution = values["finite_nested_convolution"]["flags"][
        "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"
    ]
    complete_nested_convolution = values["finite_nested_convolution"]["flags"][
        "COMPLETE_PHYSICAL_NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED"
    ]
    finite_mode_kernel_intervals = values["finite_mode_kernel_intervals"]["flags"][
        "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED"
    ]
    finite_detector_form_binding = values["finite_detector_form_binding"]["flags"][
        "EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE"
    ]
    finite_massive_diagonal_preparation = values["finite_massive_diagonal_preparation"]["flags"][
        "DIAGONAL_MASSIVE_DEGREE_TWO_ADVANCED_IMAGE_AT_SUPPORT_LEFT_EXPORTED"
    ]
    finite_physical_massive_cauchy = values["finite_physical_massive_cauchy"]["flags"][
        "EMITTER_FULL_FORM_CAUCHY_PAIR_EXPORTED"
    ]
    finite_positive_energy_preparation = values["finite_positive_energy_preparation"]["flags"][
        "COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED"
    ]
    finite_free_emitter_retarded_channel = values[
        "finite_free_emitter_retarded_channel"
    ]["flags"]["FIRST_RETARDED_MAXWELL_CAUCHY_PAIR_AT_SUPPORT_RIGHT_EXPORTED"]
    finite_partitioned_leading_response_rank_two = values[
        "finite_partitioned_leading_response_rank_two"
    ]["flags"]["FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_ON_MASS_DOMAIN"]
    finite_matched_feedback_channels = values["finite_matched_feedback_channels"][
        "flags"
    ]["I_111_TWO_J0_K0_INTERVAL_EVALUATED"]
    finite_partitioned_matched_feedback = values[
        "finite_partitioned_matched_feedback"
    ]["flags"]["PARTITION8_WIDTHS_STRICTLY_BELOW_COARSE_HULLS"]
    finite_cross_window_detector_remainder = values[
        "finite_cross_window_detector_remainder"
    ]["flags"]["D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"]
    finite_six_mismatched_feedback = values["finite_six_mismatched_feedback"][
        "flags"
    ]["SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED"]
    finite_first_omitted_shell_provider = values[
        "finite_first_omitted_shell_provider"
    ]["flags"]["TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED"]
    finite_two_j5_all_channel_column_binding = values[
        "finite_two_j5_all_channel_column_binding"
    ]["flags"]["ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED"]
    generic_direct_shell_provider = values["direct_shell_and_tail_stop_gate"]["flags"][
        "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED"
    ]
    certified_tail_stop_gate = values["direct_shell_and_tail_stop_gate"]["flags"][
        "TAIL_AWARE_FOUR_STREAM_STOP_CALLABLE_EXPORTED"
    ]
    certified_real_shell_extraction = values["real_shell_extraction"]["flags"][
        "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED"
    ]
    rows = readiness_rows(
        functions,
        form_functions=form_functions,
        massive_functions=massive_functions,
        retarded_functions=retarded_functions,
        partitioned_functions=partitioned_functions,
        matched_feedback_functions=matched_feedback_functions,
        partitioned_feedback_functions=partitioned_feedback_functions,
        mismatched_feedback_functions=mismatched_feedback_functions,
        real_shell_functions=real_shell_functions,
        finite_detector_provider=finite_detector_provider,
        complete_detector_provider=generic_direct_shell_provider,
        finite_nested_convolution=finite_nested_convolution,
        finite_mode_kernel_intervals=finite_mode_kernel_intervals,
        finite_detector_form_binding=finite_detector_form_binding,
        finite_massive_diagonal_preparation=finite_massive_diagonal_preparation,
        finite_physical_massive_cauchy=finite_physical_massive_cauchy,
        finite_positive_energy_preparation=finite_positive_energy_preparation,
        finite_free_emitter_retarded_channel=finite_free_emitter_retarded_channel,
        finite_partitioned_leading_response_rank_two=finite_partitioned_leading_response_rank_two,
        finite_matched_feedback_channels=finite_matched_feedback_channels,
        finite_partitioned_matched_feedback=finite_partitioned_matched_feedback,
        finite_cross_window_detector_remainder=finite_cross_window_detector_remainder,
        finite_six_mismatched_feedback=finite_six_mismatched_feedback,
        finite_first_omitted_shell_provider=finite_first_omitted_shell_provider,
        finite_two_j5_all_channel_column_binding=finite_two_j5_all_channel_column_binding,
        generic_direct_shell_provider=generic_direct_shell_provider,
        certified_tail_stop_gate=certified_tail_stop_gate,
        certified_real_shell_extraction=certified_real_shell_extraction,
        complete_nested_convolution=complete_nested_convolution,
    )
    row_status = {row["id"]: row["status"] for row in rows}
    internal_ready = all(row_status[identifier] == "CERTIFIED" for identifier in REQUIRED_CALLABLES)
    if internal_ready:
        raise AssertionError("obstruction audit must be retired after the executable backend lands")
    if any(name in functions for name in REQUIRED_CALLABLES.values()) and not BACKEND.exists():
        raise AssertionError("backend function inventory is inconsistent")

    symbolic_as_backend = readiness_rows(
        set(),
        form_functions=set(),
        massive_functions=set(),
        retarded_functions=set(),
        partitioned_functions=set(),
        matched_feedback_functions=set(),
        partitioned_feedback_functions=set(),
        mismatched_feedback_functions=set(),
        real_shell_functions=set(),
        finite_detector_provider=finite_detector_provider,
        complete_detector_provider=complete_detector_provider,
        finite_nested_convolution=finite_nested_convolution,
        finite_mode_kernel_intervals=finite_mode_kernel_intervals,
        finite_detector_form_binding=finite_detector_form_binding,
        finite_massive_diagonal_preparation=finite_massive_diagonal_preparation,
        finite_physical_massive_cauchy=finite_physical_massive_cauchy,
        finite_positive_energy_preparation=finite_positive_energy_preparation,
        finite_free_emitter_retarded_channel=finite_free_emitter_retarded_channel,
        finite_partitioned_leading_response_rank_two=finite_partitioned_leading_response_rank_two,
        finite_matched_feedback_channels=finite_matched_feedback_channels,
        finite_partitioned_matched_feedback=finite_partitioned_matched_feedback,
        finite_cross_window_detector_remainder=finite_cross_window_detector_remainder,
        finite_six_mismatched_feedback=finite_six_mismatched_feedback,
        finite_first_omitted_shell_provider=finite_first_omitted_shell_provider,
        finite_two_j5_all_channel_column_binding=finite_two_j5_all_channel_column_binding,
        generic_direct_shell_provider=False,
        certified_tail_stop_gate=False,
        certified_real_shell_extraction=False,
        complete_nested_convolution=complete_nested_convolution,
        treat_symbolic_word_as_backend=True,
    )
    mutation_detected = all(
        row["status"] == "OBSTRUCTED"
        for row in symbolic_as_backend[1:]
        if row["id"] not in {
            "finite_first_omitted_shell_direct_provider_two_j5",
            "finite_two_j5_all_channel_column_feedback_binding",
        }
    )
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL readiness audit preserves "
        "the certified complete symbolic Peter-Weyl recoil word but rejects its "
        "promotion to a complete executable interval stream. Exact callable per-shell "
        "aggregation of supplied channel intervals is now certified, including the "
        "couplings, passive-column sum and Peter-Weyl weight. A content-addressed "
        "detector-coefficient callable is now certified for arbitrary declared finite "
        "shells with a contiguous two_j=6 sentinel. It is not an evaluated all-shell "
        "massive or recoil stream. A separate exact finite-slab polynomial "
        "convolution callable is certified. Exact finite Berger mode kernels are now "
        "separately interval-enclosed through 2j=4 on caller-declared rational slabs "
        "and positive massive mass domains, with uniform sine tails. The massive "
        "scalar block now completes the one-form carrier required by the physical "
        "m^-2 d G_(P1+m^2) delta correction. Every finite "
        "detector column is now assembled and passed through exact Dhat_1 with a "
        "physical-time derivative-tail bound. The switched source is also propagated "
        "through the block-diagonal massive wave kernel to the support-left slice. "
        "The physical Proca correction and full-form Cauchy pair are now finite "
        "callables. The unrestricted canonical trace and coupling-stripped full positive-energy dual "
        "are also bound to finite preparation coefficients; the previously declared co-closed restriction is now certified to give a zero observer source. The unrestricted canonical preparation is now freely evolved on its exact switch slab, its conserved switched current is exported, and the first retarded Maxwell Cauchy pair is enclosed at the support-right slice. A cell-partitioned positive-switch refinement now proves both selected two_j=0 advanced Cauchy covectors nonzero uniformly for mass squared in [1,2]. Green adjunction identifies the two diagonal detector contractions with strict positive-energy lower bounds, so the leading selected response has rank two on that validation parameter domain. Green adjunction now also evaluates the detector-matched I_000[0,0] and I_111[0,0] absolute-g3 coefficient blocks on the same validation mass domain, including the physical massive correction and Lorentzian two-form pairing. A cellwise causal backend partitions every switch and switch-derivative occurrence; its 2/4/8-cell rail strictly contracts both complex enclosures below the whole-support hulls, while both 8-cell enclosures still contain zero. The D1 advanced detector remainder is extended to the earlier h0 feedback window. All six mismatched two_j=0,column-0 channels are evaluated: four are exact causal-support zeros, while I_100 and I_101 have strictly contracting 2/4/8-cell enclosures that still contain zero. The direct detector-polynomial, D1/h0 remainder and exact-kernel payload is now extended by one shell to two_j=5 with an explicit source-hash carrier crosswalk; no map to the separate hashed exact-T stream is inferred. All 48 two_j=5 channel-column blocks are now bound at partition count two on the validation mass domain, with 24 exact support zeros and 24 causally allowed zero-containing enclosures. The four allowed k=0 paths strictly contract in both components at partition count four. Arbitrary positive masses and feedback shell sums with couplings are not yet bound, "
        "so the complete nested-convolution row remains "
        "obstructed. "
        "A content-addressed generic direct-shell provider now supplies a contiguous "
        "two_j=6 sentinel and the tail-aware four-stream stop callable is certified. "
        "The exact SU(2) conjugate-column relation now supplies a certified map from "
        "complex channel rectangles to real shell inputs; all eight two_j=5 channel "
        "sums pass that carrier audit. The feedback backend itself is still evaluated "
        "only through two_j=5. "
        "Supplying masses and "
        "couplings would therefore still not produce a physical recoil interval. The "
        "numerical input schema is certified only as a deferred exact "
        "contract in the gHat operator units; it contains no chosen physical values. "
        "This audit does not demote the symbolic operator theorem, evaluate recoil, "
        "restrict records to the second-order cone, activate Bridge 3, promote finite-r/"
        "all-orders observer stability, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-stream-executable-readiness-audit-v1",
        "result_id": "BERGER_RECOIL_STREAM_EXECUTABLE_READINESS_AUDIT",
        "setting_id": values["per_shell_word"]["setting_id"],
        "claim_status": "GENERIC_DIRECT_SHELL_REALITY_AND_TAIL_STOP_CERTIFIED_TWO_J6_FEEDBACK_STREAM_OBSTRUCTED",
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
        "mode_scope": values["per_shell_word"]["mode_scope"],
        "execution_protocol": {
            "backend_module": str(BACKEND.relative_to(ROOT)),
            "backend_module_present": BACKEND.exists(),
            "detector_form_backend_module": str(FORM_BACKEND.relative_to(ROOT)),
            "detector_form_backend_module_present": FORM_BACKEND.exists(),
            "massive_preparation_backend_module": str(MASSIVE_BACKEND.relative_to(ROOT)),
            "massive_preparation_backend_module_present": MASSIVE_BACKEND.exists(),
            "free_emitter_retarded_backend_module": str(RETARDED_BACKEND.relative_to(ROOT)),
            "free_emitter_retarded_backend_module_present": RETARDED_BACKEND.exists(),
            "partitioned_preparation_backend_module": str(PARTITIONED_BACKEND.relative_to(ROOT)),
            "partitioned_preparation_backend_module_present": PARTITIONED_BACKEND.exists(),
            "matched_feedback_backend_module": str(MATCHED_FEEDBACK_BACKEND.relative_to(ROOT)),
            "matched_feedback_backend_module_present": MATCHED_FEEDBACK_BACKEND.exists(),
            "partitioned_feedback_backend_module": str(PARTITIONED_FEEDBACK_BACKEND.relative_to(ROOT)),
            "partitioned_feedback_backend_module_present": PARTITIONED_FEEDBACK_BACKEND.exists(),
            "mismatched_feedback_backend_module": str(MISMATCHED_FEEDBACK_BACKEND.relative_to(ROOT)),
            "mismatched_feedback_backend_module_present": MISMATCHED_FEEDBACK_BACKEND.exists(),
            "real_shell_backend_module": str(REAL_SHELL_BACKEND.relative_to(ROOT)),
            "real_shell_backend_module_present": REAL_SHELL_BACKEND.exists(),
            "required_callables": REQUIRED_CALLABLES,
            "discovered_module_callables": sorted(functions),
            "discovered_detector_form_callables": sorted(form_functions),
            "discovered_massive_preparation_callables": sorted(massive_functions),
            "discovered_free_emitter_retarded_callables": sorted(retarded_functions),
            "discovered_partitioned_preparation_callables": sorted(partitioned_functions),
            "discovered_matched_feedback_callables": sorted(matched_feedback_functions),
            "discovered_partitioned_feedback_callables": sorted(partitioned_feedback_functions),
            "discovered_mismatched_feedback_callables": sorted(mismatched_feedback_functions),
            "discovered_real_shell_callables": sorted(real_shell_functions),
            "interval_output_requirement": "directed-rounding lower/upper endpoints plus retained-shell and analytic-tail bounds",
        },
        "readiness": {
            "rows": rows,
            "symbolic_word_ready": True,
            "internal_executable_stream_ready": internal_ready,
            "external_specialization_deferred": True,
            "four_scalar_stream_active": False,
        },
        "numerical_input_contract": {
            "path": str(INPUT_SCHEMA.relative_to(ROOT)),
            "sha256": _sha256(INPUT_SCHEMA),
            "operator_units": "certified_gHat_clock_and_Berger_spatial_operator_units",
            "status": "CERTIFIED_SCHEMA_VALUES_DEFERRED",
        },
        "mutation_results": [
            {
                "name": "treat_symbolic_operator_word_as_executable_backend",
                "detected": mutation_detected,
            },
            {
                "name": "request_external_values_before_internal_backend",
                "detected": not internal_ready,
            },
        ],
        "flags": {
            "COMPLETE_SYMBOLIC_OPERATOR_WORD_RETAINED": True,
            "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED": row_status["finite_detector_coefficient_provider_two_j0_to_4"] == "CERTIFIED",
            "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED": row_status["finite_polynomial_nested_time_convolution"] == "CERTIFIED",
            "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED": row_status["finite_exact_mode_kernel_interval_enclosure"] == "CERTIFIED",
            "FINITE_DETECTOR_ADVANCED_MAXWELL_DHAT1_BINDING_EXPORTED": row_status["finite_detector_advanced_maxwell_Dhat1_binding"] == "CERTIFIED",
            "FINITE_SWITCHED_DIAGONAL_MASSIVE_ADVANCED_PREPARATION_EXPORTED": row_status["finite_switched_diagonal_massive_advanced_preparation"] == "CERTIFIED",
            "FINITE_PHYSICAL_MASSIVE_ADVANCED_CAUCHY_PAIR_EXPORTED": row_status["finite_physical_massive_advanced_cauchy_pair"] == "CERTIFIED",
            "FINITE_COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED": row_status["finite_coupling_stripped_positive_energy_preparation_coefficients"] == "CERTIFIED",
            "FINITE_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL_EXPORTED": row_status["finite_free_emitter_first_retarded_maxwell_channel"] == "CERTIFIED",
            "FINITE_PARTITIONED_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_EXPORTED": row_status["finite_partitioned_detector_selected_leading_response_rank_two"] == "CERTIFIED",
            "FINITE_DETECTOR_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED": row_status["finite_detector_matched_absolute_g3_feedback_channels"] == "CERTIFIED",
            "FINITE_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK_EXPORTED": row_status["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED",
            "FINITE_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER_EXPORTED": row_status["finite_cross_window_detector_advanced_maxwell_remainder"] == "CERTIFIED",
            "FINITE_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS_EXPORTED": row_status["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED",
            "ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EXPORTED": row_status["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED" and row_status["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED",
            "FINITE_FIRST_OMITTED_SHELL_DIRECT_PROVIDER_TWO_J5_EXPORTED": row_status["finite_first_omitted_shell_direct_provider_two_j5"] == "CERTIFIED",
            "TWO_J5_FEEDBACK_CHANNELS_EVALUATED": row_status["finite_two_j5_all_channel_column_feedback_binding"] == "CERTIFIED",
            "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED": row_status["finite_two_j5_all_channel_column_feedback_binding"] == "CERTIFIED",
            "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED": row_status["generic_direct_finite_shell_provider"] == "CERTIFIED",
            "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED": row_status["shell_interval_evaluator"] == "CERTIFIED",
            "COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED": row_status["detector_profile_coefficient_provider"] == "CERTIFIED",
            "NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED": False,
            "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED": row_status["complex_channel_to_real_shell_scalar_map"] == "CERTIFIED",
            "TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED": row_status["tail_aware_aggregate_stop_loop"] == "CERTIFIED",
            "NUMERICAL_SPECIALIZATION_INPUT_SCHEMA_EXPORTED": True,
            "NUMERICAL_SPECIALIZATION_VALUES_DECLARED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BIND_TWO_J6_FEEDBACK_CHANNEL_COLUMNS_WITH_CERTIFIED_REALITY_PAIR_FOLDING",
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
        raise SystemExit("stale Berger recoil executable-readiness audit")
    print("BERGER_RECOIL_STREAM_EXECUTABLE_READINESS_AUDIT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
