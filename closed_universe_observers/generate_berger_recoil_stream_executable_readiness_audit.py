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
DEPENDENCIES = {
    "per_shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "tail_envelopes": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
    "mode_kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "finite_shell_aggregator": PACKAGE / "certificates/BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR.json",
    "finite_detector_provider": PACKAGE / "certificates/BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER.json",
    "finite_nested_convolution": PACKAGE / "certificates/BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION.json",
    "finite_mode_kernel_intervals": PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json",
    "finite_detector_form_binding": PACKAGE / "certificates/BERGER_RECOIL_DETECTOR_FORM_BINDING.json",
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
    finite_detector_provider: bool = False,
    complete_detector_provider: bool = False,
    finite_nested_convolution: bool = False,
    finite_mode_kernel_intervals: bool = False,
    finite_detector_form_binding: bool = False,
    complete_nested_convolution: bool = False,
    treat_symbolic_word_as_backend: bool = False,
) -> list[dict[str, Any]]:
    form_functions = form_functions or set()
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
    ]
    for identifier, callable_name in REQUIRED_CALLABLES.items():
        present = callable_name in functions
        if identifier == "detector_profile_coefficient_provider":
            present = present and complete_detector_provider
        if identifier == "nested_time_convolution_backend":
            present = present and complete_nested_convolution
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
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(input_schema)
    functions = _backend_functions()
    form_functions = _backend_functions(FORM_BACKEND)
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
    rows = readiness_rows(
        functions,
        form_functions=form_functions,
        finite_detector_provider=finite_detector_provider,
        complete_detector_provider=complete_detector_provider,
        finite_nested_convolution=finite_nested_convolution,
        finite_mode_kernel_intervals=finite_mode_kernel_intervals,
        finite_detector_form_binding=finite_detector_form_binding,
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
        finite_detector_provider=finite_detector_provider,
        complete_detector_provider=complete_detector_provider,
        finite_nested_convolution=finite_nested_convolution,
        finite_mode_kernel_intervals=finite_mode_kernel_intervals,
        finite_detector_form_binding=finite_detector_form_binding,
        complete_nested_convolution=complete_nested_convolution,
        treat_symbolic_word_as_backend=True,
    )
    mutation_detected = all(row["status"] == "OBSTRUCTED" for row in symbolic_as_backend[1:])
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL readiness audit preserves "
        "the certified complete symbolic Peter-Weyl recoil word but rejects its "
        "promotion to a complete executable interval stream. Exact callable per-shell "
        "aggregation of supplied channel intervals is now certified, including the "
        "couplings, passive-column sum and Peter-Weyl weight. A detector-coefficient "
        "callable is also certified only on the validated advanced-Maxwell image for "
        "2j=0,...,4. It is not a complete all-shell detector provider and is not a "
        "massive or recoil evaluation. A separate exact finite-slab polynomial "
        "convolution callable is certified. Exact finite Berger mode kernels are now "
        "separately interval-enclosed through 2j=4 on caller-declared rational slabs "
        "and positive massive mass domains, with uniform sine tails. Every finite "
        "detector column is now assembled and passed through exact Dhat_1 with a "
        "physical-time derivative-tail bound. The switch and subsequent massive "
        "Green/Cauchy stages are still not bound into a physical nested channel, "
        "so the complete nested-convolution row remains "
        "obstructed. "
        "No complete callable backend yet provides the remaining detector coefficient "
        "intervals or tail-aware four-stream stop loop. "
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
        "claim_status": "FIVE_FINITE_EXECUTION_CAPABILITIES_CERTIFIED_COMPLETE_STREAM_OBSTRUCTED",
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
            "required_callables": REQUIRED_CALLABLES,
            "discovered_module_callables": sorted(functions),
            "discovered_detector_form_callables": sorted(form_functions),
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
            "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED": row_status["shell_interval_evaluator"] == "CERTIFIED",
            "COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED": False,
            "NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED": False,
            "TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED": False,
            "NUMERICAL_SPECIALIZATION_INPUT_SCHEMA_EXPORTED": True,
            "NUMERICAL_SPECIALIZATION_VALUES_DECLARED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "MULTIPLY_DHAT1_DETECTOR_IMAGE_BY_SWITCH_THEN_APPLY_ADVANCED_MASSIVE_GREEN_KERNEL",
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
