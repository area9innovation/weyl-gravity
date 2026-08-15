#!/usr/bin/env python3
"""Independent verifier for BT reciprocal-phase inverse ellipticity."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-reciprocal-phase-inverse-ellipticity-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
]


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_fixture() -> dict[str, Fraction | int]:
    """Reconstruct the 4^4 two-level field without producer imports."""
    length = 4
    transverse_sites = length**3
    sites = length * transverse_sites
    even_mass = Fraction(9, 10)
    odd_mass = Fraction(1, 10)
    even_probability = even_mass / (2 * transverse_sites)
    odd_probability = odd_mass / (2 * transverse_sites)
    axial_ratio = even_probability / odd_probability
    even_residual = 2 * axial_ratio + 6 - 8
    odd_residual = 2 / axial_ratio + 6 - 8
    energy = even_mass * even_residual**2 + odd_mass * odd_residual**2
    edge_sum = even_mass * even_residual + odd_mass * odd_residual
    contrast = even_mass - odd_mass
    defect = 1 - contrast
    sine_squared = Fraction(1)

    # Every one of the 256 positive-axis edges joins unlike levels.
    harmonic_per_edge = (
        even_probability
        * odd_probability
        / (even_probability + odd_probability)
    )
    harmonic_factor = sites * harmonic_per_edge
    telescoping = 2 * contrast
    lower = 16 * sine_squared**2 * contrast**4 / defect**2
    participation = (
        Fraction(sites, 2) * even_probability**2
        + Fraction(sites, 2) * odd_probability**2
    )
    return {
        "length": length,
        "sites": sites,
        "even_probability": even_probability,
        "odd_probability": odd_probability,
        "contrast": contrast,
        "defect": defect,
        "sine_squared": sine_squared,
        "even_residual": even_residual,
        "odd_residual": odd_residual,
        "energy": energy,
        "edge_sum": edge_sum,
        "harmonic_factor": harmonic_factor,
        "telescoping": telescoping,
        "weighted_cauchy_product": edge_sum * harmonic_factor,
        "lower": lower,
        "ratio": energy / lower,
        "participation": participation,
        "diversity": 1 - participation,
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

    rebuilt = independent_fixture()
    public = cert["exact_tensor_fixture"]
    checks["independent_probability_and_phase"] = (
        rebuilt["sites"] == 256
        and frac(public["epsilon"]) == Fraction(1, 10)
        and frac(public["even_site_probability"])
        == rebuilt["even_probability"]
        == Fraction(9, 1280)
        and frac(public["odd_site_probability"])
        == rebuilt["odd_probability"]
        == Fraction(1, 1280)
        and frac(public["contrast"])
        == rebuilt["contrast"]
        == Fraction(4, 5)
        and frac(public["phase_defect"])
        == rebuilt["defect"]
        == Fraction(1, 5)
        and frac(public["sine_squared"])
        == rebuilt["sine_squared"]
        == 1
    )
    checks["independent_residual_and_energy"] = (
        frac(public["even_residual"])
        == rebuilt["even_residual"]
        == 16
        and frac(public["odd_residual"])
        == rebuilt["odd_residual"]
        == Fraction(-16, 9)
        and frac(public["weighted_residual_energy"])
        == rebuilt["energy"]
        == Fraction(18688, 81)
    )
    checks["independent_edge_uncertainty"] = (
        frac(public["reciprocal_edge_sum"])
        == rebuilt["edge_sum"]
        == Fraction(128, 9)
        and frac(public["harmonic_edge_factor"])
        == rebuilt["harmonic_factor"]
        == Fraction(9, 50)
        and frac(public["telescoping_magnitude"])
        == rebuilt["telescoping"]
        == Fraction(8, 5)
        and frac(public["weighted_cauchy_product"])
        == rebuilt["weighted_cauchy_product"]
        == Fraction(64, 25)
        == rebuilt["telescoping"] ** 2
    )
    checks["independent_lower_bound_chain"] = (
        frac(public["pointwise_lower_bound"])
        == rebuilt["lower"]
        == Fraction(4096, 25)
        and rebuilt["energy"] >= rebuilt["edge_sum"] ** 2 >= rebuilt["lower"]
        and frac(public["lower_bound_ratio"])
        == rebuilt["ratio"]
        == Fraction(1825, 1296)
    )
    checks["independent_simplex_diversity"] = (
        frac(public["participation"])
        == rebuilt["participation"]
        == Fraction(41, 6400)
        and frac(public["diversity"])
        == rebuilt["diversity"]
        == Fraction(6359, 6400)
    )

    edge = cert["reciprocal_edge_identity"]
    uncertainty = cert["weighted_phase_uncertainty"]
    pointwise = cert["pointwise_localization_bound"]
    checks["reciprocal_edge_identity_exact"] = (
        "sum_x pi_x*r_x=" in edge["identity"]
        and "(pi_x-pi_y)^2*(pi_x+pi_y)/(pi_x*pi_y)" in edge["identity"]
        and edge["site_cauchy"] == "sum_x pi_x*r_x^2>=Q(pi)^2"
        and edge["status"] == "PROVED_POINTWISE"
    )
    checks["weighted_phase_uncertainty_exact"] = (
        uncertainty["weighted_cauchy"]
        == "4*s_L^2*c^2<=Q_mu(pi)*B"
        and uncertainty["summed_potential_bound"] == "B<=delta"
        and uncertainty["consequence"] == "Q(pi)>=4*s_L^2*c^2/delta"
        and uncertainty["status"] == "PROVED_POINTWISE"
    )
    checks["pointwise_localization_bound_exact"] = (
        pointwise["theorem"]
        == "sum_x pi_x*r_x^2>=16*s_L^4*c^4/delta^2"
        and "asymptotically sharp" in pointwise["constant"]
        and pointwise["status"] == "PROVED_EXACT_ALL_FIELD"
    )

    gibbs = cert["normalized_gibbs_lift"]
    inverse = cert["inverse_phase_ellipticity"]
    checks["normalized_gibbs_lift_exact"] = (
        gibbs["ward_input"]
        == "E_mu[sum_x pi_x*r_x^2]=lambda^2*E_mu[1-sum_x pi_x^2]"
        and gibbs["localization_moment"]
        == "E_mu[c^4/delta^2]<=lambda^2*(1-1/N)/(16*s_L^4)"
        and gibbs["inverse_defect_moment"]
        == "E_mu[delta^-2]<=4+lambda^2*(1-1/N)/s_L^4"
        and gibbs["status"] == "PROVED_NORMALIZED_ACTUAL_GIBBS_ESTIMATE"
    )
    checks["inverse_phase_ellipticity_exact"] = (
        inverse["inverse_norm"] == "operator_norm(G^-1)=2/delta"
        and inverse["exact_bound"]
        == "E_mu[operator_norm(G^-1)^2]<=16+4*lambda^2*(1-1/N)/s_L^4"
        and inverse["scaled_bound"]
        == "E_mu[(s_L^2*operator_norm(G^-1))^2]<=16*s_L^4+4*lambda^2*(1-1/N)<=16+4*lambda^2"
        and "416/25" in inverse["lambda_two_fifths"]
        and inverse["status"]
        == "PROVED_VOLUME_UNIFORM_UNREGULARIZED_INVERSE_ESTIMATE"
    )

    sharpness = cert["sharpness_family"]
    checks["sharpness_family_exact"] = (
        sharpness["contrast"] == "c=1-2*epsilon and delta=2*epsilon"
        and "-> 1" in sharpness["ratio"]
        and sharpness["status"] == "ASYMPTOTIC_SHARPNESS_PROVED"
    )
    disposition = cert["method_disposition"]
    checks["claim_boundary"] = (
        disposition["reciprocal_second_harmonic_localization_barrier"]
        == "CONTROLLED_AT_THE_LOWEST_FREQUENCY_SCALE"
        and disposition["unregularized_inverse_phase_matrix_second_moment"]
        == "PROVED"
        and disposition["normalized_conjugate_score_coercivity"] == "OPEN"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"]
        == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a normalized BT lowest-mode or field second moment",
        "boundedness or divergence of the actual interacting H^-1 moment",
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
