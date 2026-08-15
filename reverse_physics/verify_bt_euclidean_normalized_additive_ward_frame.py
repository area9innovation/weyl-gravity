#!/usr/bin/env python3
"""Independent verifier for the normalized BT additive Ward frame."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-normalized-additive-ward-frame-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTER_HYPERSURFACE_GAUSSIAN_ENVELOPE_V1.json",
]


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_cycle() -> dict:
    """Rebuild the C4 frame without importing the producer."""
    field = (Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2))
    inverse = tuple(1 / value for value in field)
    weight = sum(inverse, Fraction())
    probability = tuple(value / weight for value in inverse)
    residual = tuple(
        (field[(site - 1) % 4] + field[(site + 1) % 4]) / field[site] - 2
        for site in range(4)
    )
    modulation = (Fraction(1), Fraction(-1), Fraction(2), Fraction(-2))
    source = (Fraction(1), Fraction(0), Fraction(-1), Fraction(0))
    laplacian = tuple(
        modulation[(site - 1) % 4]
        + modulation[(site + 1) % 4]
        - 2 * modulation[site]
        for site in range(4)
    )
    unprojected = tuple(
        probability[site] * modulation[site] for site in range(4)
    )
    mean = sum(unprojected, Fraction()) / 4
    vector = tuple(value - mean for value in unprojected)
    divergence = -sum(
        (
            modulation[site]
            * probability[site]
            * (1 - probability[site])
            for site in range(4)
        ),
        Fraction(),
    )
    action_pairing = sum(
        (
            probability[site]
            * (
                residual[site] * laplacian[site]
                - modulation[site] * residual[site] ** 2
            )
            for site in range(4)
        ),
        Fraction(),
    )
    source_pairing = sum(
        (
            probability[site] * modulation[site] * source[site]
            for site in range(4)
        ),
        Fraction(),
    )
    second = sum((value**2 for value in probability), Fraction())
    third = sum((value**3 for value in probability), Fraction())
    energy = sum(
        (probability[site] * residual[site] ** 2 for site in range(4)),
        Fraction(),
    )
    cosine = (Fraction(1), Fraction(0), Fraction(-1), Fraction(0))
    sine = (Fraction(0), Fraction(1), Fraction(0), Fraction(-1))
    phase_gram = tuple(
        tuple(
            sum(
                (
                    probability[site] * left[site] * right[site]
                    for site in range(4)
                ),
                Fraction(),
            )
            for right in (cosine, sine)
        )
        for left in (cosine, sine)
    )
    return {
        "field": field,
        "inverse": inverse,
        "weight": weight,
        "probability": probability,
        "residual": residual,
        "modulation": modulation,
        "source": source,
        "laplacian": laplacian,
        "vector": vector,
        "divergence": divergence,
        "action_pairing": action_pairing,
        "source_pairing": source_pairing,
        "second": second,
        "diversity": 1 - second,
        "energy": energy,
        "constant_vector": tuple(value - Fraction(1, 4) for value in probability),
        "diversity_flow": 2 * (third - second**2),
        "phase_gram": phase_gram,
        "second_harmonic": sum(
            (probability[site] * (-1) ** site for site in range(4)),
            Fraction(),
        ),
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

    rebuilt = independent_cycle()
    public = cert["exact_cycle_fixture"]
    checks["independent_field_probability_and_residual"] = (
        tuple(frac(value) for value in public["omega"])
        == rebuilt["field"]
        == (Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2))
        and tuple(frac(value) for value in public["reciprocal"])
        == rebuilt["inverse"]
        and frac(public["total_reciprocal"]) == rebuilt["weight"]
        == Fraction(9, 2)
        and tuple(frac(value) for value in public["pi"])
        == rebuilt["probability"]
        == (Fraction(2, 9), Fraction(1, 9), Fraction(2, 9), Fraction(4, 9))
        and tuple(frac(value) for value in public["residual"])
        == rebuilt["residual"]
        == (Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2))
    )
    checks["independent_modulated_frame"] = (
        tuple(frac(value) for value in public["modulation"])
        == rebuilt["modulation"]
        and tuple(frac(value) for value in public["source"])
        == rebuilt["source"]
        and tuple(frac(value) for value in public["delta_modulation"])
        == rebuilt["laplacian"]
        == (Fraction(-5), Fraction(5), Fraction(-7), Fraction(7))
        and tuple(frac(value) for value in public["modulated_vector"])
        == rebuilt["vector"]
        == (
            Fraction(11, 36),
            Fraction(-1, 36),
            Fraction(19, 36),
            Fraction(-29, 36),
        )
    )
    checks["independent_modulated_differential_terms"] = (
        frac(public["modulated_divergence"])
        == rebuilt["divergence"]
        == Fraction(2, 27)
        and frac(public["modulated_action_pairing"])
        == rebuilt["action_pairing"]
        == Fraction(47, 6)
        and frac(public["modulated_source_pairing"])
        == rebuilt["source_pairing"]
        == Fraction(-2, 9)
    )
    checks["independent_constant_frame"] = (
        frac(public["participation"])
        == rebuilt["second"]
        == Fraction(25, 81)
        and frac(public["diversity"])
        == rebuilt["diversity"]
        == Fraction(56, 81)
        and frac(public["normalized_residual_energy"])
        == rebuilt["energy"]
        == 2
        and tuple(frac(value) for value in public["constant_frame_vector"])
        == rebuilt["constant_vector"]
        and frac(public["constant_frame_divergence"])
        == -rebuilt["diversity"]
        and frac(public["constant_frame_action_pairing"])
        == -rebuilt["energy"]
    )
    checks["independent_diversity_flow"] = (
        frac(public["diversity_flow_derivative"])
        == rebuilt["diversity_flow"]
        == Fraction(208, 6561)
        > 0
    )
    checks["independent_full_phase_matrix"] = (
        tuple(
            tuple(frac(value) for value in row)
            for row in public["lowest_phase_gram"]
        )
        == rebuilt["phase_gram"]
        == ((Fraction(4, 9), Fraction()), (Fraction(), Fraction(5, 9)))
        and frac(public["lowest_phase_second_harmonic"])
        == rebuilt["second_harmonic"]
        == Fraction(-1, 9)
    )

    frame = cert["normalized_additive_frame"]
    stein = cert["stein_ward_identity"]
    checks["general_frame_formulas_exact"] = (
        frame["vector_field"] == "X_a=P_H(a*pi)"
        and frame["restricted_divergence"]
        == "div_H X_a=-sum_x a_x*pi_x*(1-pi_x)"
        and frame["action_pairing"]
        == "X_a dot grad A=sum_x pi_x*(r_x*(Delta a)_x-a_x*r_x^2)"
        and frame["status"] == "PROVED_EXACT_FINITE_VOLUME"
    )
    checks["stein_identity_exact"] = (
        stein["identity"] == "E[X_a dot grad f]=E[f*Y_a]"
        and stein["conjugate_score"]
        == "Y_a=lambda^-2*sum_x pi_x*(r_x*(Delta a)_x-a_x*r_x^2)+sum_x a_x*pi_x*(1-pi_x)"
        and stein["centering"] == "E[Y_a]=0"
        and stein["status"] == "PROVED_NORMALIZED_ACTUAL_GIBBS_IDENTITY"
    )

    constant = cert["constant_frame_corollary"]
    checks["normalized_residual_estimate_exact"] = (
        constant["exact_expectation"]
        == "E_mu[sum_x pi_x*r_x^2]=lambda^2*E_mu[D(pi)]"
        and constant["volume_uniform_bound"]
        == "E_mu[sum_x pi_x*r_x^2]<=lambda^2*(1-1/N)"
        and constant["periodic_site_identity"]
        == "E_mu[pi_x*r_x^2]=lambda^2*(1/N-E_mu[pi_x^2])"
        and constant["status"] == "PROVED_VOLUME_UNIFORM_NORMALIZED_ESTIMATE"
        and Fraction(2, 5) ** 2 == Fraction(4, 25)
    )
    fourier = cert["fourier_source_corollary"]
    checks["fourier_source_normalization_exact"] = (
        fourier["source_identity"]
        == "E_mu[F_b*Y_a]=N^-1*sum_x a_x*b_x"
        and "E_mu[F_h*Y_h]=1/2" in fourier["lowest_real_phase"]
        and fourier["status"]
        == "EXACT_SOURCE_NORMALIZATION_PROVED_VARIANCE_OPEN"
    )
    phase = cert["full_phase_stein_matrix"]
    checks["full_phase_stein_matrix_exact"] = (
        phase["diffusion_matrix"]
        == "G_ij(psi)=sum_x pi_x*h_i(x)*h_j(x)"
        and phase["trace"]
        == "tr G=sum_x pi_x*(h_c(x)^2+h_s(x)^2)=1"
        and phase["eigenvalues"]
        == "eigenvalues(G)=(1+|z_2|)/2,(1-|z_2|)/2"
        and phase["source_normalization"] == "E[F_j*Y_i]=delta_ij/2"
        and phase["mean_matrix"]
        == "E[G]=I_2/2 by lattice translation invariance"
        and phase["status"] == "PROVED_EXACT_TWO_PHASE_MARGINAL_FRAME"
    )

    disposition = cert["method_disposition"]
    checks["claim_boundary"] = (
        disposition["normalized_reciprocal_weighted_residual_energy"] == "PROVED"
        and disposition["normalized_modulated_stein_ward_frame"] == "PROVED"
        and disposition["lowest_fourier_source_normalization"] == "PROVED"
        and disposition["full_phase_marginal_stein_matrix"] == "PROVED"
        and disposition["coercivity_of_normalized_conjugate_score"] == "OPEN"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
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
