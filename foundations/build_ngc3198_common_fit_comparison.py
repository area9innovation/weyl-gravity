#!/usr/bin/env python3
"""Fit three NGC 3198 model families under one bounded protocol."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_mannheim_ngc3198_assembly import model as mannheim_model, read_sparc


FOUNDATIONS = ROOT / "foundations"
PROTOCOL = FOUNDATIONS / "data/ngc3198-common-fit-protocol-v1.json"
PARAMETERS = FOUNDATIONS / "data/mannheim-ngc3198-parameters-v1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json"
REPORT = FOUNDATIONS / "reports/ngc3198-common-fit-comparison-v1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def golden_minimum(function: Callable[[float], float], lower: float, upper: float, iterations: int = 90) -> tuple[float, float]:
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    c = upper - ratio * (upper - lower)
    d = lower + ratio * (upper - lower)
    fc, fd = function(c), function(d)
    for _ in range(iterations):
        if fc <= fd:
            upper, d, fd = d, c, fc
            c = upper - ratio * (upper - lower)
            fc = function(c)
        else:
            lower, c, fc = c, d, fd
            d = lower + ratio * (upper - lower)
            fd = function(d)
    x = (lower + upper) / 2.0
    return x, function(x)


def prepared_points() -> list[dict[str, float]]:
    parameters = load(PARAMETERS)
    published = {key: float(value) for key, value in parameters["published_ngc3198_row"].items()}
    predict = mannheim_model(parameters)
    points = []
    for row in read_sparc():
        radius = row["radius_kpc"] * 14.1 / row["distance_mpc"]
        if radius > published["last_radius_kpc"]:
            continue
        components = predict(radius)["components_v2_km2_s2"]
        points.append({
            "source_radius_kpc": row["radius_kpc"],
            "radius_kpc": radius,
            "observed_km_s": row["observed_km_s"],
            "error_km_s": row["error_km_s"],
            "star_newtonian_v2": components["stellar_newtonian"],
            "star_linear_v2": components["stellar_linear"],
            "gas_newtonian_v2": components["gas_newtonian"],
            "gas_linear_v2": components["gas_linear"],
            "global_linear_v2": components["global_linear"],
            "global_quadratic_v2": components["global_quadratic"],
        })
    if len(points) != 39:
        raise ValueError("protocol must select exactly 39 points")
    return points


def nfw_v2(radius_kpc: float, v200: float, concentration: float, h0: float = 70.0) -> float:
    r200 = 100.0 * v200 / h0
    x = radius_kpc / r200
    numerator = math.log1p(concentration * x) - concentration * x / (1.0 + concentration * x)
    denominator = x * (math.log1p(concentration) - concentration / (1.0 + concentration))
    return v200 * v200 * numerator / denominator


def velocity(point: dict[str, float], family: str, q_star: float, v200: float | None = None, concentration: float | None = None) -> float:
    if family == "NEWTONIAN_BARYONS_ONLY":
        total = q_star * point["star_newtonian_v2"] + point["gas_newtonian_v2"]
    elif family == "MANNHEIM_CONFORMAL_GRAVITY":
        total = q_star * (point["star_newtonian_v2"] + point["star_linear_v2"])
        total += point["gas_newtonian_v2"] + point["gas_linear_v2"] + point["global_linear_v2"] + point["global_quadratic_v2"]
    elif family == "GR_NFW_DARK_HALO" and v200 is not None and concentration is not None:
        total = q_star * point["star_newtonian_v2"] + point["gas_newtonian_v2"] + nfw_v2(point["radius_kpc"], v200, concentration)
    else:
        raise ValueError("unknown model family or missing NFW parameters")
    if total <= 0:
        return float("nan")
    return math.sqrt(total)


def chi2(points: list[dict[str, float]], family: str, q_star: float, v200: float | None = None, concentration: float | None = None) -> float:
    total = 0.0
    for point in points:
        predicted = velocity(point, family, q_star, v200, concentration)
        if not math.isfinite(predicted):
            return float("inf")
        total += ((predicted - point["observed_km_s"]) / point["error_km_s"]) ** 2
    return total


def fit_nfw(points: list[dict[str, float]]) -> tuple[float, float, float, float]:
    q_bounds = (0.1, 3.0)
    log_v_bounds = [math.log(20.0), math.log(500.0)]
    log_c_bounds = [math.log(1.0), math.log(40.0)]
    best = (float("inf"), 0.0, 0.0, 0.0)
    # A deterministic nested grid narrows in log-space; q is minimized at every node.
    for _level in range(15):
        candidate = best
        for iv in range(31):
            log_v = log_v_bounds[0] + (log_v_bounds[1] - log_v_bounds[0]) * iv / 30.0
            v200 = math.exp(log_v)
            for ic in range(31):
                log_c = log_c_bounds[0] + (log_c_bounds[1] - log_c_bounds[0]) * ic / 30.0
                concentration = math.exp(log_c)
                q_star, score = golden_minimum(lambda q: chi2(points, "GR_NFW_DARK_HALO", q, v200, concentration), *q_bounds, iterations=60)
                if score < candidate[0]:
                    candidate = (score, q_star, v200, concentration)
        best = candidate
        # Retain a broad overlapping neighborhood.  Shrinking to a single old
        # grid interval can falsely lock onto the curved q--V200--c ridge.
        dv = (log_v_bounds[1] - log_v_bounds[0]) / 4.0
        dc = (log_c_bounds[1] - log_c_bounds[0]) / 4.0
        center_v, center_c = math.log(best[2]), math.log(best[3])
        log_v_bounds = [max(math.log(20.0), center_v - dv), min(math.log(500.0), center_v + dv)]
        log_c_bounds = [max(math.log(1.0), center_c - dc), min(math.log(40.0), center_c + dc)]
    return best[1], best[2], best[3], best[0]


def record(points: list[dict[str, float]], family: str, parameters: dict[str, float], parameter_count: int) -> dict[str, Any]:
    predictions = []
    for point in points:
        predicted = velocity(point, family, parameters["q_star"], parameters.get("V200_km_s"), parameters.get("concentration_c200"))
        residual = predicted - point["observed_km_s"]
        predictions.append({
            "radius_kpc": point["radius_kpc"], "observed_km_s": point["observed_km_s"],
            "error_km_s": point["error_km_s"], "predicted_km_s": predicted,
            "residual_km_s": residual, "standardized_residual": residual / point["error_km_s"],
        })
    n = len(points)
    score = sum(item["standardized_residual"] ** 2 for item in predictions)
    rss = sum(item["residual_km_s"] ** 2 for item in predictions)
    aic = score + 2.0 * parameter_count
    bounded_parameters = [(parameters["q_star"], (0.1, 3.0))]
    if family == "GR_NFW_DARK_HALO":
        bounded_parameters.extend([
            (parameters["V200_km_s"], (20.0, 500.0)),
            (parameters["concentration_c200"], (1.0, 40.0)),
        ])
    return {
        "model_id": family,
        "fitted_parameters": parameters,
        "parameter_count": parameter_count,
        "metrics": {
            "point_count": n, "chi_squared": score, "degrees_of_freedom": n - parameter_count,
            "reduced_chi_squared": score / (n - parameter_count), "unweighted_rms_residual_km_s": math.sqrt(rss / n),
            "maximum_absolute_residual_km_s": max(abs(item["residual_km_s"]) for item in predictions),
            "AIC": aic, "AICc": aic + 2.0 * parameter_count * (parameter_count + 1) / (n - parameter_count - 1),
            "BIC": score + parameter_count * math.log(n),
        },
        "random_error_gate": {"threshold_reduced_chi_squared": 2.0, "passed": score / (n - parameter_count) <= 2.0},
        "parameter_boundary_hit": any(
            abs(value - bound) <= 1e-8 * max(1.0, abs(bound))
            for value, bounds in bounded_parameters for bound in bounds
        ),
        "predictions": predictions,
    }


def build() -> dict[str, Any]:
    points = prepared_points()
    q_baryon, _ = golden_minimum(lambda q: chi2(points, "NEWTONIAN_BARYONS_ONLY", q), 0.1, 3.0)
    q_mannheim, _ = golden_minimum(lambda q: chi2(points, "MANNHEIM_CONFORMAL_GRAVITY", q), 0.1, 3.0)
    q_nfw, v200, concentration, _ = fit_nfw(points)
    models = [
        record(points, "NEWTONIAN_BARYONS_ONLY", {"q_star": q_baryon}, 1),
        record(points, "GR_NFW_DARK_HALO", {"q_star": q_nfw, "V200_km_s": v200, "concentration_c200": concentration}, 3),
        record(points, "MANNHEIM_CONFORMAL_GRAVITY", {"q_star": q_mannheim}, 1),
    ]
    ranking = [item["model_id"] for item in sorted(models, key=lambda item: item["metrics"]["AICc"])]
    value = {
        "schema_version": "foundational-ngc3198-common-fit-comparison-v1",
        "result_id": "FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1",
        "result_kind": "BOUNDED_SINGLE_GALAXY_COMMON_PROTOCOL_MODEL_COMPARISON",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "protocol": "foundations/data/ngc3198-common-fit-protocol-v1.json",
        "protocol_sha256": sha(PROTOCOL),
        "input_hashes": {
            "mannheim_parameters": sha(PARAMETERS),
            "sparc_extract": sha(FOUNDATIONS / "data/ngc3198-sparc-mass-model-v1.tsv"),
        },
        "models": models,
        "ranking_by_AICc": ranking,
        "scoped_finding": "GR_NFW_DARK_HALO has the lowest AICc and is the only family that passes the declared random-error gate within this common analytic, single-galaxy protocol.",
        "does_not_establish": load(PROTOCOL)["does_not_establish"],
        "claim_flags": {
            "common_observations_used": True, "common_baryonic_geometry_used": True,
            "independent_optimizer_agreement_required": True, "single_galaxy_only": True,
            "systematic_uncertainties_marginalized": False, "population_or_heldout_validation": False,
            "complete_theory_selected": False,
        },
        "human_report": "foundations/reports/ngc3198-common-fit-comparison-v1.md",
        "independent_checker": "foundations/check_ngc3198_common_fit_comparison.py",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    rows = []
    for item in value["models"]:
        p = item["fitted_parameters"]
        detail = f"q*={p['q_star']:.6f}"
        if "V200_km_s" in p:
            detail += f", V200={p['V200_km_s']:.4f} km/s, c200={p['concentration_c200']:.5f}"
        m = item["metrics"]
        rows.append(f"| {item['model_id']} | {detail} | {m['unweighted_rms_residual_km_s']:.3f} | {m['reduced_chi_squared']:.3f} | {m['AICc']:.3f} | {'PASS' if item['random_error_gate']['passed'] else 'FAIL'} |")
    return "\n".join([
        "# NGC 3198 common-protocol fit comparison v1", "",
        "**Dependency:** `LOCAL-ALGEBRAIC`. **Result kind:** bounded numerical single-galaxy comparison.", "",
        "All families use the same 39 SPARC velocities, random-error-only diagonal objective, distance rescaling, and analytic thin exponential stellar/gas geometry. The stellar mass scale `q*` is fitted for every family; gas is fixed. NFW additionally fits `V200` and `c200`.", "",
        "| Family | fitted parameters | RMS (km/s) | reduced chi-squared | AICc | gate <= 2 |", "|---|---:|---:|---:|---:|---:|", *rows, "",
        "## Scoped result", "", value["scoped_finding"], "",
        "This is a useful control: baryons alone fail strongly, the one-parameter Mannheim curve improves substantially but still fails the declared random-error gate, and the three-parameter GR+NFW curve passes. AICc and BIC penalize the two extra NFW parameters and retain that ordering.", "",
        "## Boundaries", "", *[f"- Does not establish {item}." for item in value["does_not_establish"]], "",
        "The shared analytic baryonic model is used for comparability. It is neither a full SPARC mass-model likelihood nor an identity claim between the later SPARC photometry and the dataset used in the original Mannheim fit.", "",
        "## Reproduction", "", "```bash", "python3 foundations/build_ngc3198_common_fit_comparison.py --write", "python3 foundations/check_ngc3198_common_fit_comparison.py", "python3 foundations/verify_ngc3198_common_fit_comparison.py", "```", "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        REPORT.write_text(report(value))
    else:
        print(json.dumps(value, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
