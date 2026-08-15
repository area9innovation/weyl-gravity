#!/usr/bin/env python3
"""Independent receiver replay for the cylinder polarized-Bach evaluator receipt."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cylinder_polarized_bach_evaluator import (
    PAIRS,
    ZERO_MULTIINDEX,
    bach_euler_density_coefficient,
    brinkmann_background,
    conformal_metric_fixture,
    cylinder_background_invariants,
    polarized_bach_euler_density,
    polarized_weyl_trace_identity,
    ppwave_profile_fixture,
    sparse_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT = HERE / "certificates/STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.json"
EXPECTED_OUTPUT = ("-119/24", "5/2", "0", "9", "-29/12", "-11/8", "-1/6", "19/3", "31/6", "-7/8")
EXPECTED_STAGES = (
    ("P0_BIVARIATE_EXACT_JETS", "PROTOTYPE_EXECUTED"),
    ("P1_CYLINDER_GEOMETRIC_PIPELINE", "PROTOTYPE_EXECUTED"),
    ("P2_LOCAL_IDENTITIES", "PARTIAL"),
    ("P3_PHYSICAL_FIXTURE_ADAPTERS", "PARTIAL"),
    ("P4_PORTABLE_AST_EXPORT", "OPEN"),
)
FALSE_FLAGS = {
    "GENERAL_UNIVERSAL_COMPONENT_AST_EXPORTED",
    "ALL_BENCHMARK_GATES_PASSED",
    "STRICT_HSTAR_Q2_ROW_PORTABLE",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def serialize(values: dict[tuple[int, int], Fraction]) -> list[dict[str, object]]:
    return [{"output_pair": list(pair), "coefficient": str(values[pair])} for pair in PAIRS]


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("result_state") != "EVALUATOR_PROTOTYPE_EXECUTED_UNIVERSAL_AST_AND_DIFF_IDENTITY_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state/lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag promotion")
    scope = value.get("scope", {})
    if scope.get("input_metric_jet_order") != 4 or scope.get("parameter_algebra") != "Q[a,b]/(a^2,b^2)":
        errors.append("jet/parameter scope drift")
    if scope.get("action_normalization") != "B_action=-2 B_standard" or scope.get("output_scalar_type") != "fractions.Fraction":
        errors.append("normalization or exact scalar type drift")
    if "not yet exported" not in scope.get("support_boundary", ""):
        errors.append("portable support-local boundary weakened")

    invariants = cylinder_background_invariants()
    if value.get("cylinder_background_invariants") != invariants:
        errors.append("cylinder background invariant replay drift")
    expected_invariants = {
        "ricci_lower": [["0", "0", "0", "0"], ["0", "2", "0", "0"], ["0", "0", "2", "0"], ["0", "0", "0", "2"]],
        "scalar": "6",
        "weyl_background_nonzero_components": 0,
        "bach_background_nonzero_components": 0,
    }
    if invariants != expected_invariants:
        errors.append("unit conformal-cylinder geometry is not the exact expected geometry")

    direct = polarized_bach_euler_density(sparse_fixture(1), sparse_fixture(2))
    swapped = polarized_bach_euler_density(sparse_fixture(2), sparse_fixture(1))
    serialized = serialize(direct)
    trial = value.get("arbitrary_sparse_trial", {})
    if tuple(item["coefficient"] for item in serialized) != EXPECTED_OUTPUT:
        errors.append("independent sparse-trial regression changed")
    if trial.get("output") != serialized or trial.get("nonzero_output_count") != 9:
        errors.append("serialized sparse-trial output drift")
    if direct != swapped or trial.get("swapped_output_sha256") != digest(serialize(swapped)):
        errors.append("polarization symmetry replay failed")
    trace = polarized_weyl_trace_identity(sparse_fixture(1), sparse_fixture(2))
    if trace != 0 or trial.get("trace_identity_defect") != "0":
        errors.append("twice-polarized Weyl trace identity failed")

    expected_ppwave = []
    for left_seed, right_seed in ((3, 7), (1, 9), (4, 6)):
        result = polarized_bach_euler_density(ppwave_profile_fixture(left_seed), ppwave_profile_fixture(right_seed), background=brinkmann_background())
        expected_ppwave.append({"left_seed": left_seed, "right_seed": right_seed, "all_ten_outputs_zero": all(item == 0 for item in result.values()), "result_sha256": digest(serialize(result))})
    if value.get("ppwave_restriction_trials") != expected_ppwave or not all(item["all_ten_outputs_zero"] for item in expected_ppwave):
        errors.append("pp-wave restriction replay drift")

    omega = {ZERO_MULTIINDEX: Fraction(3, 2), (1, 0, 0, 0): -2, (0, 1, 1, 0): Fraction(5, 3), (0, 0, 0, 4): Fraction(-1, 7)}
    conformal = bach_euler_density_coefficient(conformal_metric_fixture(omega), {}, 1, 0)
    conformal_record = value.get("conformal_unary_trial", {})
    if not all(item == 0 for item in conformal.values()) or conformal_record.get("all_ten_outputs_zero") is not True or conformal_record.get("result_sha256") != digest(serialize(conformal)):
        errors.append("local conformal unary replay drift")

    checks = value.get("exact_checks", {})
    expected_check_ids = {
        "reciprocal_exact_in_square_free_bivariate_quotient", "sqrt_exact_in_square_free_bivariate_quotient",
        "coordinate_derivative_leibniz_exact", "no_floating_point_scalar_type", "cylinder_background_geometry_exact",
        "arbitrary_sparse_trial_swap_symmetric", "arbitrary_sparse_trial_nonlinear_nonzero",
        "twice_polarized_weyl_trace_identity_zero", "three_ppwave_polynomial_trials_zero", "local_conformal_unary_trial_zero",
    }
    if set(checks) != expected_check_ids or any(item is not True for item in checks.values()):
        errors.append("exact check inventory or status drift")
    stages = value.get("benchmark_stage_progress", [])
    if tuple((item.get("stage"), item.get("status")) for item in stages) != EXPECTED_STAGES:
        errors.append("benchmark stage progress promoted or regressed")
    open_gates = value.get("open_acceptance_gates", [])
    if len(open_gates) != 5 or not any("Diff Noether" in item for item in open_gates) or not any("universal 10 x 10" in item for item in open_gates):
        errors.append("open acceptance gate ledger weakened")

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "scope_sha256": digest(scope),
        "exact_checks_sha256": digest(checks),
        "arbitrary_sparse_trial_sha256": digest(trial),
        "ppwave_restriction_trials_sha256": digest(value.get("ppwave_restriction_trials")),
        "benchmark_stage_progress_sha256": digest(stages),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    implementation = value.get("implementation", {})
    implementation_path = ROOT / implementation.get("path", "")
    if not implementation_path.is_file() or hashlib.sha256(implementation_path.read_bytes()).hexdigest() != implementation.get("sha256"):
        errors.append("implementation hash drift")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    flags = value.get("claim_flags", {})
    if flags.get("EXACT_ARBITRARY_RATIONAL_JET_INTERFACE_EXECUTED") is not True or flags.get("CYLINDER_GEOMETRIC_PIPELINE_PROTOTYPE_EXECUTED") is not True or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim boundary flag promoted")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - exact cylinder, swap, Weyl-trace, conformal and pp-wave replays pass")
        print("  - universal AST, Diff identity and HT1B adapters remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
