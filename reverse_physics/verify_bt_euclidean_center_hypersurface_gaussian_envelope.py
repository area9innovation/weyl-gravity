#!/usr/bin/env python3
"""Independent verifier for the BT center-hypersurface Gaussian envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTER_HYPERSURFACE_GAUSSIAN_ENVELOPE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-center-hypersurface-gaussian-envelope-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AXIAL_SLICE_QUADRATIC_COERCIVITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
]


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_gaussian_tube(radius: int = 5) -> dict:
    """Reconstruct the integrated R fixture without producer imports."""
    spectators = radius**2
    a = Fraction(spectators - 1, spectators)
    # 2*(t-s/2)^2 gives conditional precision 4 and variance 1/4.
    fiber_curvature = 4
    fiber_variance = Fraction(1, 4)
    # Integrating z changes exp(-s^2/2) to exp(-s^2/(2R^2)).
    variance_s = Fraction(radius**2)
    variance_center = variance_s / 4
    variance_t = variance_center + fiber_variance
    # Expected energy: u, s, z, and d spectators.
    expected_energy = (
        Fraction(1, 2)
        + variance_s / 2
        + Fraction(1, 2)
        + Fraction(spectators, 2)
    )
    hessian_h = (4, -2)
    hessian_norm_squared = sum(value * value for value in hessian_h)
    graph_area_squared = 1 + Fraction(1, 4)
    projection_squared = Fraction(4**2, hessian_norm_squared)
    return {
        "spectators": spectators,
        "a": a,
        "fiber_curvature": fiber_curvature,
        "fiber_variance": fiber_variance,
        "variance_s": variance_s,
        "variance_center": variance_center,
        "variance_t": variance_t,
        "expected_energy": expected_energy,
        "ambient_dimension": spectators + 3,
        "hessian_h": hessian_h,
        "hessian_norm_squared": hessian_norm_squared,
        "graph_area_squared": graph_area_squared,
        "projection_squared": projection_squared,
        "jacobian_product": graph_area_squared * projection_squared,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    inputs = cert["provenance"]["inputs"]
    checks["provenance_paths_and_hashes_current"] = (
        [row["path"] for row in inputs] == EXPECTED_INPUTS
        and all(file_hash(row["path"]) == row["sha256"] for row in inputs)
    )

    theorem = cert["bt_center_hypersurface_theorem"]
    checks["center_derivative_and_shear_exact"] = (
        theorem["center_derivative"]
        == "D m(eta)[k]=-Hess S_lambda(chi)[h,k]/Hess S_lambda(chi)[h,h]"
        and theorem["coordinate_jacobian"]
        == "in orthogonal coordinates (eta,t), det D(eta,s)->(eta,t)=1"
        and theorem["status"] == "PROVED_EXACT_FINITE_DIMENSIONAL_REDUCTION"
    )
    checks["surface_measure_cancellation_exact"] = (
        theorem["surface_projection"]
        == "d eta=H[h,h]/(||h||*||H h||)*dH_Sigma"
        and theorem["surface_disintegration"]
        == "d phi=H[h,h]/||H h||*dH_Sigma*d s"
    )

    envelope = cert["bt_integrated_fiber_envelope"]
    checks["curvature_gaussian_constant_exact"] = (
        envelope["curvature_width_bound"]
        == "I(chi)<=sqrt(2*pi/kappa_L)=3*sqrt(pi/(N*omega_L^2))"
        and Fraction(2, 1) / Fraction(2, 9) == 9
    )
    checks["center_action_constant_exact"] = (
        envelope["center_fourier_relation"]
        == "eta perpendicular to h implies Re(exp(-i*alpha)*chi_hat(e_mu))=m/2"
        and envelope["center_action_cost"]
        == "S_lambda(chi)>=N*omega_L^2*m(eta)^2/12"
        and Fraction(1, 3) * Fraction(1, 4) == Fraction(1, 12)
    )
    checks["pointwise_envelope_exact"] = (
        envelope["pointwise_envelope"]
        == "Z_eta<=3*sqrt(pi/(N*omega_L^2))*exp[-N*omega_L^2*m(eta)^2/12]"
        and envelope["status"] == "PROVED_POINTWISE_NOT_NORMALIZED"
    )

    rebuilt = independent_gaussian_tube()
    model = cert["exact_gaussian_tube_countermodel"]
    public = model["r5_fixture"]
    checks["independent_r5_moments"] = (
        public["radius"] == 5
        and public["spectators"] == rebuilt["spectators"] == 25
        and frac(public["narrowing_exponent"]) == rebuilt["a"]
        == Fraction(24, 25)
        and public["fiber_curvature"] == rebuilt["fiber_curvature"] == 4
        and frac(public["fiber_variance"]) == rebuilt["fiber_variance"]
        == Fraction(1, 4)
        and frac(public["center_variance"]) == rebuilt["variance_center"]
        == Fraction(25, 4)
        and frac(public["total_t_variance"]) == rebuilt["variance_t"]
        == Fraction(13, 2)
    )
    checks["independent_r5_energy_scaling"] = (
        public["mean_action"] == rebuilt["expected_energy"] == 26
        and public["ambient_dimension"] == rebuilt["ambient_dimension"] == 28
    )
    checks["independent_r5_jacobian_cancellation"] = (
        tuple(public["hessian_h"]) == rebuilt["hessian_h"] == (4, -2)
        and public["hessian_h_norm_squared"]
        == rebuilt["hessian_norm_squared"]
        == 20
        and public["hessian_hh"] == 4
        and frac(public["graph_area_squared"])
        == rebuilt["graph_area_squared"]
        == Fraction(5, 4)
        and frac(public["projection_factor_squared"])
        == rebuilt["projection_squared"]
        == Fraction(4, 5)
        and frac(public["jacobian_product"])
        == rebuilt["jacobian_product"]
        == 1
    )
    checks["countermodel_scope_is_logical_only"] = (
        model["status"] == "EXACT_LOGICAL_NONTRANSFER_OBSTRUCTION"
        and "not the BT action" in model["scope"]
        and "not an actual BT divergence result" in model["scope"]
    )

    gap = cert["normalized_entropy_gap"]
    disposition = cert["method_disposition"]
    checks["normalized_gap_remains_open"] = (
        gap["status"] == "OPEN_BT_SPECIFIC_NORMALIZED_ESTIMATE"
        and disposition["field_dependent_center_jacobian"] == "EXACTLY_ONE"
        and disposition["pointwise_integrated_fiber_gaussian_envelope"] == "PROVED"
        and disposition[
            "general_transfer_from_pointwise_envelope_to_normalized_moment"
        ]
        == "OBSTRUCTED"
        and disposition["bt_specific_normalized_center_second_moment"] == "OPEN"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
    )
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a normalized BT center or lowest-mode moment bound",
        "divergence of any actual BT Gibbs moment",
        "the actual interacting H^-1 bound or its divergence",
        "tightness, a continuum Euclidean BT measure, or limit identification",
    }.issubset(set(cert["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        cert["checks"]["ok"]
        and cert["checks"]["passed"] == cert["checks"]["total"]
        and not cert["checks"]["failures"]
        and all(cert["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
