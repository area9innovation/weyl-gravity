#!/usr/bin/env python3
"""Independent numeric and boundary checker for the Mannheim NGC 3198 assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json"
PARAMETERS = ROOT / "foundations/data/mannheim-ngc3198-parameters-v1.json"
SPARC = ROOT / "foundations/data/ngc3198-sparc-mass-model-v1.tsv"
CPP = ROOT / "foundations/mannheim_ngc3198_numeric_checker.cpp"

OBLIGATIONS = {
    "KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION",
    "PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION", "GENERATOR_SPECTRAL_DYNAMICS",
    "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN", "GAUGE_BV_COHOMOLOGY",
    "INTERACTION_CONSTRUCTION", "COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION",
    "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER",
    "RECONSTRUCTION_LIMITS",
}
REQUIRED = {"KINEMATICS_OBSERVABLES", "INTERACTION_CONSTRUCTION", "RECONSTRUCTION_LIMITS"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def independent_numeric() -> dict[str, float]:
    with tempfile.TemporaryDirectory(prefix="mannheim-ngc3198-check-") as directory:
        binary = Path(directory) / "checker"
        compile_result = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic", str(CPP), "-o", str(binary)],
            text=True, capture_output=True, check=False,
        )
        if compile_result.returncode:
            raise RuntimeError("independent checker compilation failed: " + compile_result.stderr)
        run = subprocess.run([str(binary), str(SPARC)], text=True, capture_output=True, check=False)
        if run.returncode:
            raise RuntimeError("independent numeric checker failed: " + run.stderr)
    result: dict[str, float] = {}
    for line in run.stdout.splitlines():
        key, value = line.split("=", 1)
        result[key] = float(value)
    return result


def near(left: float, right: float, tolerance: float = 2e-10) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    errors: list[str] = []
    params = load(PARAMETERS)
    if params.get("published_model_source", {}).get("source_archive_sha256") != "e366db37bc99ce08c96609f751d9b0ffb779dd4ce1c0140a2e226c1aefc075c1":
        errors.append("published source archive pin")
    if params.get("independent_observation_source", {}).get("full_source_sha256") != "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c":
        errors.append("SPARC full-source pin")
    provenance = {item.get("path"): item.get("sha256") for item in result.get("provenance", {}).get("inputs", [])}
    for path in (PARAMETERS, SPARC):
        relative = str(path.relative_to(ROOT))
        if provenance.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("local provenance " + relative)

    mask = {item.get("obligation"): item.get("status") for item in result.get("applicability_mask", [])}
    if set(mask) != OBLIGATIONS or {key for key, status in mask.items() if status == "IN_SCOPE_REQUIRED"} != REQUIRED:
        errors.append("applicability partition")
    if result.get("applicability_summary") != {"total_atlas_obligations": 16, "required": 3, "required_satisfied": 3, "touched_not_required": 1, "out_of_scope": 12}:
        errors.append("applicability summary")

    stage_ids = [item.get("id") for item in result.get("stages", [])]
    expected_stages = ["WEYL_FIELD_EQUATION", "STATIC_VACUUM_FAMILY", "CIRCULAR_ORBIT_LAW", "EXPONENTIAL_DISK_MODEL", "NGC3198_PARAMETER_ROW", "PUBLISHED_ENDPOINT", "SPARC_CROSS_DATASET"]
    if stage_ids != expected_stages:
        errors.append("stage closure")
    interfaces = result.get("interfaces", [])
    if len(interfaces) != 6 or any(item.get("from") != stage_ids[index] or item.get("to") != stage_ids[index + 1] for index, item in enumerate(interfaces)):
        errors.append("ordered interface closure")

    try:
        numeric = independent_numeric()
    except (RuntimeError, ValueError) as exc:
        errors.append(str(exc))
        numeric = {}
    producer_numeric = result.get("numerical_reproduction_rail", {})
    empirical = result.get("empirical_comparison_rail", {})
    comparisons = {
        "endpoint_velocity_km_s": producer_numeric.get("predicted_endpoint", {}).get("velocity_km_s"),
        "observed_endpoint_velocity_km_s": producer_numeric.get("observed_endpoint_velocity_reconstructed_km_s"),
        "endpoint_relative_residual": producer_numeric.get("endpoint_relative_velocity_residual"),
        "rms_residual_km_s": empirical.get("unweighted_rms_residual_km_s"),
        "maximum_absolute_residual_km_s": empirical.get("maximum_absolute_residual_km_s"),
        "chi_squared": empirical.get("chi_squared_random_errors_only"),
        "reduced_chi_squared": empirical.get("reduced_chi_squared_no_refit"),
    }
    for key, producer_value in comparisons.items():
        if key not in numeric or not isinstance(producer_value, (int, float)) or not near(numeric[key], float(producer_value)):
            errors.append("independent numeric " + key)
    if numeric.get("source_points") != 43 or numeric.get("selected_points") != 39:
        errors.append("independent point counts")
    if producer_numeric.get("producer_refinement_absolute_velocity_difference_km_s", 1) > 1e-9:
        errors.append("producer quadrature refinement")
    if producer_numeric.get("gate_passed") is not True or producer_numeric.get("status") != "COARSE_ENDPOINT_REPRODUCED":
        errors.append("endpoint coarse gate")
    if empirical.get("coarse_rms_gate_passed") is not True or empirical.get("random_error_reduced_chi2_gate_passed") is not False:
        errors.append("mixed empirical gates")
    if empirical.get("comparison_status") != "MIXED_COARSE_SHAPE_PASS_RANDOM_ERROR_GATE_FAILED":
        errors.append("mixed empirical status")

    disposition = result.get("assembly_disposition", {})
    expected_disposition = {
        "status": "BOUNDED_ASSEMBLY_PARTIAL_MIXED_COMPARISON",
        "complete_within_declared_scope": False,
        "formula_endpoint_coarsely_reproduced": True,
        "cross_dataset_coarse_shape_gate_passed": True,
        "cross_dataset_random_error_gate_passed": False,
        "empirically_supported_within_declared_scope": False,
        "complete_theory": False,
    }
    if disposition != expected_disposition:
        errors.append("fail-closed disposition")
    flags = result.get("claim_flags", {})
    for key in ("single_model_identity_declared", "applicability_mask_complete", "exact_local_predecessors_imported_by_hash", "published_parameters_content_pinned", "independent_numeric_bessel_rail", "published_endpoint_coarsely_reproduced", "sparc_cross_dataset_coarse_shape_gate_passed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("sparc_cross_dataset_random_error_gate_passed", "original_full_curve_digitized", "original_fit_likelihood_reproduced", "mass_to_light_ratio_refit", "matter_coupling_dispute_resolved", "galaxy_population_claim_assessed", "empirical_support_established", "bounded_prediction_assembly_complete", "complete_conformal_gravity_theory_established", "quantum_lifecycle_promoted"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    return errors, {
        "source_points": numeric.get("source_points"),
        "selected_points": numeric.get("selected_points"),
        "endpoint_relative_residual": numeric.get("endpoint_relative_residual"),
        "rms_residual_km_s": numeric.get("rms_residual_km_s"),
        "reduced_chi_squared": numeric.get("reduced_chi_squared"),
        "complete": disposition.get("complete_within_declared_scope"),
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
