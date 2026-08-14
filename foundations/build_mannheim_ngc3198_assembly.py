#!/usr/bin/env python3
"""Build a bounded Mannheim--Kazanas to NGC 3198 prediction assembly.

Exact local predecessors, published model transcription, numerical
reproduction, and empirical comparison are deliberately separate rails.  The
numerical producer evaluates the modified-Bessel factors from their integral
definitions; the independent checker uses the C++ standard-library Bessel
implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
PARAMETERS = FOUNDATIONS / "data/mannheim-ngc3198-parameters-v1.json"
SPARC = FOUNDATIONS / "data/ngc3198-sparc-mass-model-v1.tsv"
BH0B = ROOT / "black_hole_programme/certificates/BH0B_GENERAL_STATIC_SPHERICAL_COMPLETENESS.json"
BH0C = ROOT / "black_hole_programme/certificates/BH0C_TULLY_FISHER_SCALING.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json"
REPORT = FOUNDATIONS / "reports/mannheim-ngc3198-model-assembly-v1.md"

OBLIGATIONS = [
    "KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION",
    "PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION", "GENERATOR_SPECTRAL_DYNAMICS",
    "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN", "GAUGE_BV_COHOMOLOGY",
    "INTERACTION_CONSTRUCTION", "COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION",
    "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER",
    "RECONSTRUCTION_LIMITS",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def bessel_i(order: int, x: float) -> float:
    """Power series for I_0 or I_1; independent checker uses libstdc++."""
    if order not in (0, 1) or x <= 0:
        raise ValueError("producer supports I_0/I_1 at positive x")
    term = 1.0 if order == 0 else x / 2.0
    total = term
    for index in range(1, 1000):
        term *= x * x / (4.0 * index * (index + order))
        total += term
        if abs(term) <= 1e-16 * abs(total):
            return total
    raise ArithmeticError("I_n series did not converge")


def bessel_k(order: int, x: float, panels: int = 4096) -> float:
    """K_n(x)=integral exp(-x cosh(t))cosh(nt)dt by composite Simpson."""
    if order not in (0, 1) or x <= 0 or panels <= 0 or panels % 2:
        raise ValueError("producer supports K_0/K_1 at positive x and even panels")
    upper = 1.0
    while x * math.cosh(upper) - order * upper < 42.0:
        upper += 0.25
    step = upper / panels

    def integrand(t: float) -> float:
        return math.exp(-x * math.cosh(t)) * math.cosh(order * t)

    odd = sum(integrand(index * step) for index in range(1, panels, 2))
    even = sum(integrand(index * step) for index in range(2, panels, 2))
    return step * (integrand(0.0) + integrand(upper) + 4.0 * odd + 2.0 * even) / 3.0


def read_sparc() -> list[dict[str, float]]:
    rows = []
    for line in SPARC.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 10 or parts[0] != "NGC3198":
            raise ValueError("unexpected SPARC extract row")
        values = list(map(float, parts[1:]))
        rows.append(dict(zip(
            ["distance_mpc", "radius_kpc", "observed_km_s", "error_km_s", "gas_km_s", "disk_km_s", "bulge_km_s", "disk_surface_brightness", "bulge_surface_brightness"],
            values,
        )))
    if len(rows) != 43 or {row["distance_mpc"] for row in rows} != {13.8}:
        raise ValueError("SPARC NGC 3198 extract closure")
    return rows


def model(parameters: dict[str, Any]):
    constants = {key: float(value) for key, value in parameters["published_constants_cgs"].items()}
    galaxy = {key: float(value) for key, value in parameters["published_ngc3198_row"].items()}
    beta_star = constants["beta_star_cm"]
    gamma_star = constants["gamma_star_per_cm"]
    gamma_0 = constants["gamma_0_per_cm"]
    kappa = constants["kappa_per_cm2"]
    c = constants["speed_of_light_cm_per_s"]
    kpc = constants["kpc_cm"]
    stars = galaxy["stellar_disk_mass_1e10_solar"] * 1e10
    gas = galaxy["hi_mass_1e10_solar"] * 1e10 * 1.4
    star_scale = galaxy["stellar_scale_length_kpc"] * kpc
    gas_scale = 4.0 * star_scale

    def disk_components(radius_cm: float, count: float, scale_cm: float, panels: int = 4096) -> tuple[float, float]:
        y = radius_cm / (2.0 * scale_cm)
        i0, i1 = bessel_i(0, y), bessel_i(1, y)
        k0, k1 = bessel_k(0, y, panels), bessel_k(1, y, panels)
        newtonian = count * beta_star * c * c * radius_cm * radius_cm * (i0 * k0 - i1 * k1) / (2.0 * scale_cm**3)
        linear = count * gamma_star * c * c * radius_cm * radius_cm * i1 * k1 / (2.0 * scale_cm)
        return newtonian, linear

    def predict(radius_kpc: float, panels: int = 4096) -> dict[str, float]:
        radius_cm = radius_kpc * kpc
        star_newtonian, star_linear = disk_components(radius_cm, stars, star_scale, panels)
        gas_newtonian, gas_linear = disk_components(radius_cm, gas, gas_scale, panels)
        global_linear = gamma_0 * c * c * radius_cm / 2.0
        global_quadratic = -kappa * c * c * radius_cm * radius_cm
        components = {
            "stellar_newtonian": star_newtonian,
            "stellar_linear": star_linear,
            "gas_newtonian": gas_newtonian,
            "gas_linear": gas_linear,
            "global_linear": global_linear,
            "global_quadratic": global_quadratic,
        }
        total = sum(components.values())
        if total <= 0:
            raise ArithmeticError("model has no circular orbit at requested radius")
        return {
            "radius_kpc": radius_kpc,
            "velocity_km_s": math.sqrt(total) / 1e5,
            "v2_over_c2r_per_cm": total / (c * c * radius_cm),
            "components_v2_km2_s2": {key: value / 1e10 for key, value in components.items()},
        }

    return predict


def applicability_mask() -> list[dict[str, str]]:
    required = {
        "KINEMATICS_OBSERVABLES": "The static metric, circular speed, disk light/mass model, and measured rotation curve are the declared configurations and observables.",
        "INTERACTION_CONSTRUCTION": "The nonlinear Bach equation and its static spherical vacuum family define the gravitational model feeding the weak-field prediction.",
        "RECONSTRUCTION_LIMITS": "The weak-field circular-orbit and disk integrations connect the metric coefficients to the observed velocity-radius curve.",
    }
    touched = {
        "GAUGE_BV_COHOMOLOGY": "The exact predecessor uses a conformal and radial gauge, but no BV complex or gauge cohomology is required or established.",
    }
    result = []
    for obligation in OBLIGATIONS:
        if obligation in required:
            status, reason = "IN_SCOPE_REQUIRED", required[obligation]
        elif obligation in touched:
            status, reason = "TOUCHED_NOT_REQUIRED", touched[obligation]
        else:
            status, reason = "OUT_OF_SCOPE", "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        result.append({"obligation": obligation, "status": status, "reason": reason})
    return result


def build() -> dict[str, Any]:
    parameters = load(PARAMETERS)
    bh0b, bh0c = load(BH0B), load(BH0C)
    if bh0b.get("certificate") != "BH0B_GENERAL_STATIC_SPHERICAL_COMPLETENESS":
        raise ValueError("BH0B identity")
    if bh0c.get("certificate") != "BH0C_TULLY_FISHER_SCALING":
        raise ValueError("BH0C identity")
    predict = model(parameters)
    galaxy = {key: float(value) for key, value in parameters["published_ngc3198_row"].items()}
    constants = {key: float(value) for key, value in parameters["published_constants_cgs"].items()}

    endpoint = predict(galaxy["last_radius_kpc"])
    endpoint_refined = predict(galaxy["last_radius_kpc"], 8192)
    observed_acceleration = galaxy["observed_last_v2_over_c2r_1e30_per_cm"] * 1e-30
    radius_cm = galaxy["last_radius_kpc"] * constants["kpc_cm"]
    observed_endpoint_velocity = math.sqrt(observed_acceleration * constants["speed_of_light_cm_per_s"]**2 * radius_cm) / 1e5
    endpoint_residual = endpoint["velocity_km_s"] - observed_endpoint_velocity
    endpoint_relative = abs(endpoint_residual) / observed_endpoint_velocity

    points = []
    for row in read_sparc():
        radius = row["radius_kpc"] * galaxy["distance_mpc"] / row["distance_mpc"]
        if radius > galaxy["last_radius_kpc"]:
            continue
        prediction = predict(radius)
        residual = prediction["velocity_km_s"] - row["observed_km_s"]
        points.append({
            "source_radius_kpc": row["radius_kpc"],
            "rescaled_radius_kpc": radius,
            "observed_velocity_km_s": row["observed_km_s"],
            "random_error_km_s": row["error_km_s"],
            "predicted_velocity_km_s": prediction["velocity_km_s"],
            "residual_km_s": residual,
            "standardized_residual": residual / row["error_km_s"],
        })
    rms = math.sqrt(sum(item["residual_km_s"]**2 for item in points) / len(points))
    chi2 = sum(item["standardized_residual"]**2 for item in points)
    reduced_chi2 = chi2 / len(points)  # no parameter was fit to these SPARC rows
    maximum = max(abs(item["residual_km_s"]) for item in points)
    coarse_gate = float(parameters["cross_dataset_protocol"]["coarse_rms_gate_km_per_s"])
    chi2_gate = float(parameters["cross_dataset_protocol"]["random_error_reduced_chi2_gate"])
    endpoint_gate = float(parameters["cross_dataset_protocol"]["endpoint_relative_velocity_gate"])
    mask = applicability_mask()

    stages = [
        {"id": "WEYL_FIELD_EQUATION", "label": "Weyl action and Bach equation", "status": "DECLARED_MODEL_INPUT", "establishes": "The classical model is four-dimensional pure metric conformal gravity with Bach equation B_mu_nu=0 in the exterior."},
        {"id": "STATIC_VACUUM_FAMILY", "label": "Mannheim--Kazanas vacuum family", "status": "CERTIFIED_LOCAL_PREDECESSOR", "establishes": "The local BH0B certificate derives the complete static spherical Bach-flat family in the declared conformal gauge."},
        {"id": "CIRCULAR_ORBIT_LAW", "label": "Weak-field circular-orbit law", "status": "CERTIFIED_LOCAL_PREDECESSOR", "establishes": "The local BH0C certificate derives the leading weak-field beta/r + gamma r/2 - k r^2 circular-speed law and records its exact-family correction."},
        {"id": "EXPONENTIAL_DISK_MODEL", "label": "Luminous exponential-disk prediction", "status": "PUBLISHED_MODEL_TRANSCRIPTION", "establishes": "Mannheim--O'Brien Eqs. (5) and (20) integrate the Newtonian and linear kernels over thin stellar and gas disks and add universal linear and quadratic terms."},
        {"id": "NGC3198_PARAMETER_ROW", "label": "Published NGC 3198 parameters", "status": "CONTENT_PINNED_TRANSCRIPTION", "establishes": "The model uses the paper's distance, scale length, stellar and HI masses, fitted M/L, endpoint radius, and fixed universal constants without refitting."},
        {"id": "PUBLISHED_ENDPOINT", "label": "Published endpoint reproduction", "status": "COARSE_NUMERICAL_REPRODUCTION", "establishes": "Independent evaluation of the displayed equations predicts the endpoint velocity within the declared five-percent coarse gate of the velocity reconstructed from the paper's endpoint acceleration."},
        {"id": "SPARC_CROSS_DATASET", "label": "Independent SPARC curve comparison", "status": "MIXED_RANDOM_ERROR_GATE_FAILED", "establishes": "Without refitting, the curve passes the declared five km/s RMS shape gate but fails the reduced-chi-squared gate based on SPARC random errors alone."},
    ]
    interfaces = [
        {"id": "ACTION_TO_BACH", "from": "WEYL_FIELD_EQUATION", "to": "STATIC_VACUUM_FAMILY", "relation": "DECLARED_THEORY_TO_CERTIFIED_SECTOR", "status": "CERTIFIED_WITH_SCOPE", "basis": "BH0B verifies the static spherical exterior classification in conformal gauge, not the full matter-coupled theory."},
        {"id": "VACUUM_TO_ORBIT", "from": "STATIC_VACUUM_FAMILY", "to": "CIRCULAR_ORBIT_LAW", "relation": "EXACT_TO_LEADING_WEAK_FIELD", "status": "CERTIFIED_WITH_SCOPE", "basis": "BH0C derives the orbit law and explicitly records the O(beta gamma) correction from the exact Bach-flat family."},
        {"id": "ORBIT_TO_DISK", "from": "CIRCULAR_ORBIT_LAW", "to": "EXPONENTIAL_DISK_MODEL", "relation": "PUBLISHED_THIN_DISK_INTEGRATION", "status": "REGISTERED", "basis": "Imports the paper's thin exponential stellar/gas geometry and Bessel-kernel integration; it does not solve a galactic interior matter sector."},
        {"id": "DISK_TO_PARAMETERS", "from": "EXPONENTIAL_DISK_MODEL", "to": "NGC3198_PARAMETER_ROW", "relation": "PUBLISHED_FIT_PARAMETER_INSTANTIATION", "status": "REGISTERED", "basis": "The reported stellar mass-to-light ratio is a fitted input; all other displayed parameters are transcribed as fixed model/data inputs."},
        {"id": "PARAMETERS_TO_ENDPOINT", "from": "NGC3198_PARAMETER_ROW", "to": "PUBLISHED_ENDPOINT", "relation": "INDEPENDENT_NUMERICAL_EVALUATION", "status": "CERTIFIED_NUMERIC", "basis": "The producer evaluates Bessel integrals directly and the checker uses std::cyl_bessel_i/k; agreement is tested independently."},
        {"id": "ENDPOINT_TO_SPARC", "from": "PUBLISHED_ENDPOINT", "to": "SPARC_CROSS_DATASET", "relation": "NONIDENTICAL_DATASET_COMPARISON", "status": "REGISTERED_WITH_WARNING", "basis": "SPARC observations are from the same galaxy and observational lineage but a later, non-identical photometric/data reduction; no empirical support is transferred automatically."},
    ]
    value = {
        "schema_version": "foundational-mannheim-ngc3198-model-assembly-v1",
        "result_id": "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1",
        "result_kind": "MODEL_SCOPED_PREDICTION_AND_CROSS_DATASET_ASSEMBLY",
        "lifecycle": "NUMERICAL_REPRODUCTION_WITH_MIXED_EMPIRICAL_COMPARISON",
        "created": "2026-08-14",
        "repository_base_commit": "a1980849c6e7c18802a0392cc21c9f3da199f9d3",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "title": "Mannheim conformal-gravity NGC 3198 assembly: field equation to rotation curve",
        "model_identity": {
            "id": "MANNHEIM_OBRIEN_NGC3198_THIN_DISK",
            "theory": "Four-dimensional pure metric conformal gravity in the Mannheim--Kazanas phenomenological branch",
            "sector": "Static weak-field circular motion for the NGC 3198 stellar and gas disks",
            "field_equations": "B_mu_nu=0 in the exterior, with published thin-disk convolution and global gamma_0/kappa terms",
            "matter_coupling": "Massive tracers are assumed to respond to the displayed metric; the macroscopic-versus-microscopic scalar dispute is not resolved",
            "approximation": "Leading weak field, infinitesimally thin exponential stellar and gas disks, gas scale length 4 R0, no bulge",
            "benchmark": "GALACTIC_DYNAMICS",
            "comparison_id": "MANNHEIM_OBRIEN_2012_NGC3198_AND_SPARC_2016",
        },
        "applicability_mask": mask,
        "applicability_summary": {
            "total_atlas_obligations": 16,
            "required": 3,
            "required_satisfied": 3,
            "touched_not_required": 1,
            "out_of_scope": 12,
        },
        "stages": stages,
        "interfaces": interfaces,
        "published_parameter_rail": {
            "source": parameters["published_model_source"],
            "constants_cgs": parameters["published_constants_cgs"],
            "ngc3198_row": parameters["published_ngc3198_row"],
            "modelling_assumptions": parameters["published_modelling_assumptions"],
            "parameter_fit_scope": "The stellar M/L=1.12 is imported from the published fit; this assembly performs no fit.",
        },
        "numerical_reproduction_rail": {
            "arithmetic": "BINARY64_NUMERIC_DISTINCT_FROM_EXACT_LOCAL_PREDECESSORS",
            "producer_method": "I_0/I_1 power series and K_0/K_1 integral definitions with 4096-panel composite Simpson quadrature",
            "independent_method": "C++17 std::cyl_bessel_i and std::cyl_bessel_k",
            "published_last_radius_kpc": galaxy["last_radius_kpc"],
            "published_observed_endpoint_acceleration_per_cm": observed_acceleration,
            "observed_endpoint_velocity_reconstructed_km_s": observed_endpoint_velocity,
            "predicted_endpoint": endpoint,
            "producer_refinement_absolute_velocity_difference_km_s": abs(endpoint["velocity_km_s"] - endpoint_refined["velocity_km_s"]),
            "endpoint_residual_km_s": endpoint_residual,
            "endpoint_relative_velocity_residual": endpoint_relative,
            "declared_relative_gate": endpoint_gate,
            "gate_passed": endpoint_relative <= endpoint_gate,
            "status": "COARSE_ENDPOINT_REPRODUCED" if endpoint_relative <= endpoint_gate else "COARSE_ENDPOINT_GATE_FAILED",
            "boundary": "The table endpoint carries no pointwise uncertainty and is not the full curve. The five-percent gate is an audit threshold chosen here, not a publisher confidence interval.",
        },
        "empirical_comparison_rail": {
            "type": "NO_REFIT_NONIDENTICAL_SPARC_CROSS_DATASET_CHECK",
            "protocol": parameters["cross_dataset_protocol"],
            "source": parameters["independent_observation_source"],
            "points_total_source": 43,
            "points_inside_published_radius": len(points),
            "points": points,
            "unweighted_rms_residual_km_s": rms,
            "maximum_absolute_residual_km_s": maximum,
            "chi_squared_random_errors_only": chi2,
            "reduced_chi_squared_no_refit": reduced_chi2,
            "coarse_rms_gate_passed": rms <= coarse_gate,
            "random_error_reduced_chi2_gate_passed": reduced_chi2 <= chi2_gate,
            "comparison_status": "MIXED_COARSE_SHAPE_PASS_RANDOM_ERROR_GATE_FAILED" if rms <= coarse_gate and reduced_chi2 > chi2_gate else "REVIEW_REQUIRED",
            "data_lifecycle": "CONTENT_PINNED_EXTRACT_DIFFERENT_PHOTOMETRIC_REDUCTION",
            "boundary": "SPARC supplies a later 3.6-micron photometric reduction, whereas the published fit used heterogeneous blue-band luminosities and its own gas approximation. Random errors exclude inclination and other systematics. This is an external no-refit stress test, not a reproduction of the original likelihood.",
        },
        "maturity_rails": [
            {"id": "MODEL_IDENTITY", "status": "SATISFIED_WITH_MATTER_BOUNDARY", "basis": "All stages retain the Mannheim--O'Brien NGC 3198 thin-disk model; the disputed massive-tracer coupling is declared, not resolved."},
            {"id": "APPLICABILITY", "status": "SATISFIED", "basis": "All three obligations required by this bounded prediction are present; quantum and causal-PDE obligations are explicitly out of scope."},
            {"id": "CROSS_STAGE_COMPOSITION", "status": "PARTIALLY_CERTIFIED", "basis": "The local metric/orbit and numerical joins are checked; thin-disk, fitted-parameter, and non-identical-dataset joins remain typed imports."},
            {"id": "PREDICTION_DERIVATION", "status": "SATISFIED_WITH_PUBLISHED_MODEL_INPUT", "basis": "The local exact predecessors and published disk equations determine a curve after the table parameters are supplied."},
            {"id": "OBSERVABLE_IDENTIFICATION", "status": "SATISFIED_WITH_MATTER_BOUNDARY", "basis": "Circular speed is the displayed observable only under the declared massive-tracer response assumption."},
            {"id": "NUMERICAL_REPRODUCIBILITY", "status": "COARSE_ENDPOINT_REPRODUCED", "basis": f"Endpoint relative velocity residual {endpoint_relative:.4f} is below the declared {endpoint_gate:.2f} audit gate."},
            {"id": "EMPIRICAL_COMPARISON", "status": "MIXED_RANDOM_ERROR_GATE_FAILED", "basis": f"No-refit SPARC RMS is {rms:.3f} km/s, while reduced chi-squared using random errors alone is {reduced_chi2:.3f} and exceeds {chi2_gate:.1f}."},
            {"id": "ROBUSTNESS_OUT_OF_SAMPLE", "status": "NOT_ASSESSED", "basis": "One galaxy and one later cross-dataset are insufficient for robustness or the published 111-galaxy population claim."},
        ],
        "assembly_disposition": {
            "status": "BOUNDED_ASSEMBLY_PARTIAL_MIXED_COMPARISON",
            "complete_within_declared_scope": False,
            "formula_endpoint_coarsely_reproduced": endpoint_relative <= endpoint_gate,
            "cross_dataset_coarse_shape_gate_passed": rms <= coarse_gate,
            "cross_dataset_random_error_gate_passed": reduced_chi2 <= chi2_gate,
            "empirically_supported_within_declared_scope": False,
            "complete_theory": False,
        },
        "provenance": {
            "inputs": [
                {"path": str(PARAMETERS.relative_to(ROOT)), "sha256": sha(PARAMETERS), "role": "content-addressed literature/data transcription and comparison protocol"},
                {"path": str(SPARC.relative_to(ROOT)), "sha256": sha(SPARC), "role": "43-row content-pinned NGC 3198 SPARC extract"},
                {"path": str(BH0B.relative_to(ROOT)), "sha256": sha(BH0B), "role": "unchanged exact static spherical Bach-vacuum classification"},
                {"path": str(BH0C.relative_to(ROOT)), "sha256": sha(BH0C), "role": "unchanged local circular-orbit and Tully--Fisher conditional with correction ledger"},
            ],
            "remote_source_pins": [parameters["published_model_source"], parameters["independent_observation_source"]],
        },
        "independent_checker": {
            "path": "foundations/check_mannheim_ngc3198_assembly.py",
            "numeric_source": "foundations/mannheim_ngc3198_numeric_checker.cpp",
            "method": "Independent C++17 Bessel evaluation, source/data hash closure, stage/interface/applicability audit, and fail-closed gate recomputation.",
        },
        "claim_flags": {
            "single_model_identity_declared": True,
            "applicability_mask_complete": True,
            "exact_local_predecessors_imported_by_hash": True,
            "published_parameters_content_pinned": True,
            "independent_numeric_bessel_rail": True,
            "published_endpoint_coarsely_reproduced": endpoint_relative <= endpoint_gate,
            "sparc_cross_dataset_coarse_shape_gate_passed": rms <= coarse_gate,
            "sparc_cross_dataset_random_error_gate_passed": reduced_chi2 <= chi2_gate,
            "original_full_curve_digitized": False,
            "original_fit_likelihood_reproduced": False,
            "mass_to_light_ratio_refit": False,
            "matter_coupling_dispute_resolved": False,
            "galaxy_population_claim_assessed": False,
            "empirical_support_established": False,
            "bounded_prediction_assembly_complete": False,
            "complete_conformal_gravity_theory_established": False,
            "quantum_lifecycle_promoted": False,
        },
        "does_not_establish": [
            "that the macroscopic scalar conformal frame is irrelevant to massive-particle trajectories or that Mannheim's matter-sector response is correct",
            "an interior galactic solution of the Bach equation with baryonic matter",
            "identity of the 2012 heterogeneous blue-band fit data with the 2016 SPARC 3.6-micron reduction",
            "reproduction of the original pointwise curve, fitting algorithm, likelihood, covariance model, distance uncertainty, or systematic-error budget",
            "that the fitted stellar mass-to-light ratio is independently preferred; it is imported without refitting",
            "empirical support under the SPARC random-error gate, which fails",
            "the published 111- or 141-galaxy population claims, lensing, cosmology, or another observational sector",
            "ghost freedom, quantum unitarity, a Mannheim C operator, or any quantum lifecycle promotion",
            "a complete observationally validated conformal-gravity theory",
        ],
        "human_report": "foundations/reports/mannheim-ngc3198-model-assembly-v1.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render_report(value: dict[str, Any]) -> str:
    numeric = value["numerical_reproduction_rail"]
    empirical = value["empirical_comparison_rail"]
    disposition = value["assembly_disposition"]
    lines = [
        "# Mannheim--Kazanas to NGC 3198 model assembly v1", "",
        f"**Result:** `{value['result_id']}`", "",
        f"**Lifecycle:** `{value['lifecycle']}`", "", "## Outcome", "",
        "This is the first model-scoped Mannheim conformal-gravity prediction assembly in the foundations atlas. It keeps the Weyl/Bach model, Mannheim--Kazanas exterior, circular-orbit law, published thin-disk formula, published NGC 3198 parameters, endpoint calculation, and independent SPARC comparison on one typed chain.", "",
        "It is deliberately **partial**. The endpoint is coarsely reproduced, but the independent SPARC comparison fails the declared random-error reduced-chi-squared gate. The result therefore does not certify empirical support or a complete assembly.", "", "## Seven-stage chain", "",
        "| Stage | State | Establishes |", "|---|---|---|",
    ]
    lines.extend(f"| {item['label']} | `{item['status']}` | {item['establishes']} |" for item in value["stages"])
    lines.extend([
        "", "## Published endpoint reproduction", "",
        f"At the published last radius `{numeric['published_last_radius_kpc']:.1f} kpc`, the paper's tabulated endpoint acceleration reconstructs an observed velocity of `{numeric['observed_endpoint_velocity_reconstructed_km_s']:.3f} km/s`. Independent evaluation of the paper's disk formula and tabulated parameters gives `{numeric['predicted_endpoint']['velocity_km_s']:.3f} km/s`.", "",
        f"The residual is `{numeric['endpoint_residual_km_s']:.3f} km/s`, or `{100*numeric['endpoint_relative_velocity_residual']:.3f}%`. This passes the declared five-percent **coarse reproduction** gate. The endpoint has no tabulated pointwise uncertainty, so this is not a significance test or a full-curve reproduction.", "", "## Independent SPARC cross-dataset check", "",
        f"The content-pinned SPARC extract contains `{empirical['points_total_source']}` measurements; `{empirical['points_inside_published_radius']}` remain after rescaling radii from 13.8 to 14.1 Mpc and applying the paper's 38.6 kpc endpoint. No parameter is refitted.", "",
        f"- Unweighted RMS residual: `{empirical['unweighted_rms_residual_km_s']:.3f} km/s` — coarse 5 km/s shape gate **passes**.",
        f"- Maximum absolute residual: `{empirical['maximum_absolute_residual_km_s']:.3f} km/s`.",
        f"- Reduced chi-squared from SPARC random errors only: `{empirical['reduced_chi_squared_no_refit']:.3f}` — declared gate `<=2` **fails**.", "",
        "The pass and failure are not averaged. SPARC is a later 3.6-micron reduction rather than the heterogeneous blue-band input of the original fit, and its quoted errors omit inclination and other systematics. This rail is a useful stress test, not an exact replay of the publisher's likelihood.", "", "## Disposition", "",
        f"`{disposition['status']}`: endpoint reproduction is `{disposition['formula_endpoint_coarsely_reproduced']}`, the coarse SPARC shape gate is `{disposition['cross_dataset_coarse_shape_gate_passed']}`, the SPARC random-error gate is `{disposition['cross_dataset_random_error_gate_passed']}`, and bounded completion is `{disposition['complete_within_declared_scope']}`.", "", "## Boundaries", "",
    ])
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines.extend(["", "## Verification", "", "```bash", "python3 foundations/build_mannheim_ngc3198_assembly.py --check", "python3 foundations/check_mannheim_ngc3198_assembly.py", "python3 foundations/verify_mannheim_ngc3198_assembly.py", "python3 -m unittest foundations.tests.test_mannheim_ngc3198_assembly", "```", ""])
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render_report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    if args.check:
        current = OUTPUT.is_file() and REPORT.is_file() and OUTPUT.read_bytes() == result_bytes and REPORT.read_bytes() == report_bytes
        print(("PASS " if current else "FAIL ") + "Mannheim NGC 3198 generated artifacts are " + ("current" if current else "stale"))
        return 0 if current else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(result_bytes)
    REPORT.write_bytes(report_bytes)
    print(f"wrote {OUTPUT.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
