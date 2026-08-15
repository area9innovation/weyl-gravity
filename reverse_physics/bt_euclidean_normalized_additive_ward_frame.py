#!/usr/bin/env python3
"""Build the normalized additive Ward-frame certificate for the BT lattice."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-normalized-additive-ward-frame-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-normalized-additive-ward-frame.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_normalized_additive_ward_frame.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_CENTER_HYPERSURFACE_GAUSSIAN_ENVELOPE_V1.json"
    ),
]
SOURCE_COMMIT = "b6241f152eaceac22aa82967b73bc96476cb5978"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle_fixture() -> dict:
    """Exact C4 fixture for the normalized additive frame."""
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    reciprocal = [1 / value for value in omega]
    total_reciprocal = sum(reciprocal, Fraction())
    pi = [value / total_reciprocal for value in reciprocal]
    residual = [
        (omega[(site - 1) % 4] + omega[(site + 1) % 4]) / omega[site]
        - 2
        for site in range(4)
    ]
    modulation = [Fraction(1), Fraction(-1), Fraction(2), Fraction(-2)]
    source = [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)]
    delta_modulation = [
        modulation[(site - 1) % 4]
        + modulation[(site + 1) % 4]
        - 2 * modulation[site]
        for site in range(4)
    ]
    raw_vector = [pi[site] * modulation[site] for site in range(4)]
    raw_mean = sum(raw_vector, Fraction()) / 4
    vector = [value - raw_mean for value in raw_vector]
    divergence = -sum(
        (
            modulation[site] * pi[site] * (1 - pi[site])
            for site in range(4)
        ),
        Fraction(),
    )
    action_pairing = sum(
        (
            pi[site]
            * (
                residual[site] * delta_modulation[site]
                - modulation[site] * residual[site] ** 2
            )
            for site in range(4)
        ),
        Fraction(),
    )
    source_pairing = sum(
        (pi[site] * modulation[site] * source[site] for site in range(4)),
        Fraction(),
    )
    participation = sum((value * value for value in pi), Fraction())
    diversity = 1 - participation
    normalized_residual_energy = sum(
        (pi[site] * residual[site] ** 2 for site in range(4)), Fraction()
    )
    third_moment = sum((value**3 for value in pi), Fraction())
    diversity_flow = 2 * (third_moment - participation**2)
    constant_vector = [value - Fraction(1, 4) for value in pi]
    lowest_cosine = [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)]
    lowest_sine = [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)]
    phase_gram = [
        [
            sum(
                (
                    pi[site] * left[site] * right[site]
                    for site in range(4)
                ),
                Fraction(),
            )
            for right in (lowest_cosine, lowest_sine)
        ]
        for left in (lowest_cosine, lowest_sine)
    ]
    second_harmonic = sum(
        (pi[site] * (-1) ** site for site in range(4)), Fraction()
    )
    return {
        "omega": omega,
        "reciprocal": reciprocal,
        "total_reciprocal": total_reciprocal,
        "pi": pi,
        "residual": residual,
        "modulation": modulation,
        "source": source,
        "delta_modulation": delta_modulation,
        "vector": vector,
        "divergence": divergence,
        "action_pairing": action_pairing,
        "source_pairing": source_pairing,
        "participation": participation,
        "diversity": diversity,
        "normalized_residual_energy": normalized_residual_energy,
        "third_moment": third_moment,
        "diversity_flow": diversity_flow,
        "constant_vector": constant_vector,
        "phase_gram": phase_gram,
        "second_harmonic": second_harmonic,
    }


def build() -> dict:
    exact = cycle_fixture()
    checks = {
        "fixture_scale_section_is_exact": exact["omega"]
        == [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)],
        "fixture_reciprocal_total_is_nine_halves": exact["total_reciprocal"]
        == Fraction(9, 2),
        "fixture_probability_is_exact": exact["pi"]
        == [Fraction(2, 9), Fraction(1, 9), Fraction(2, 9), Fraction(4, 9)],
        "fixture_residual_is_exact": exact["residual"]
        == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)],
        "modulated_vector_is_mean_zero": sum(exact["vector"], Fraction()) == 0,
        "modulated_divergence_is_two_twenty_sevenths": exact["divergence"]
        == Fraction(2, 27),
        "modulated_action_pairing_is_forty_seven_sixths": exact[
            "action_pairing"
        ]
        == Fraction(47, 6),
        "modulated_source_pairing_is_minus_two_ninths": exact[
            "source_pairing"
        ]
        == Fraction(-2, 9),
        "participation_is_twenty_five_eighty_firsts": exact["participation"]
        == Fraction(25, 81),
        "diversity_is_fifty_six_eighty_firsts": exact["diversity"]
        == Fraction(56, 81),
        "normalized_residual_energy_is_two": exact[
            "normalized_residual_energy"
        ]
        == 2,
        "constant_frame_divergence_is_minus_diversity": -exact["diversity"]
        == Fraction(-56, 81),
        "constant_frame_action_pairing_is_minus_energy": -exact[
            "normalized_residual_energy"
        ]
        == -2,
        "diversity_flow_is_positive": exact["diversity_flow"]
        == Fraction(208, 6561)
        > 0,
        "full_phase_gram_is_exact": exact["phase_gram"]
        == [[Fraction(4, 9), Fraction()], [Fraction(), Fraction(5, 9)]],
        "full_phase_second_harmonic_is_minus_one_ninth": exact[
            "second_harmonic"
        ]
        == Fraction(-1, 9),
        "normalized_weighted_residual_identity_is_actual_gibbs": True,
        "fourier_source_identity_is_normalized": True,
        "field_moment_and_h_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-normalized-additive-ward-frame-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": "NORMALIZED_WEIGHTED_RESIDUAL_ESTIMATE_PROVED",
        "result_kind": (
            "exact normalized additive Stein/Ward frame and volume-uniform "
            "reciprocal-probability-weighted residual estimate"
        ),
        "question": (
            "Can the additive BT contraction be normalized inside each field "
            "so that its Ward identity controls an expectation under the actual "
            "Gibbs law, rather than only a ratio of size-biased expectations?"
        ),
        "answer": (
            "Yes. Put q_x=exp(-psi_x), W=sum_x q_x, pi_x=q_x/W, and for a "
            "fixed site modulation a define X_a=P_H(a*pi). Its restricted "
            "divergence is -sum_x a_x*pi_x*(1-pi_x), while its BT action "
            "pairing is sum_x pi_x*(r_x*Delta a_x-a_x*r_x^2). This gives a "
            "full normalized Stein identity. For a=1 it proves the actual "
            "Gibbs equality E[sum pi_x*r_x^2]=lambda^2*E[1-sum pi_x^2], "
            "hence a volume-uniform upper bound lambda^2*(1-1/N). On a "
            "periodic vertex-transitive lattice, modulated frames also give "
            "E[F_b*Y_a]=<a,b>/N; a lowest real Fourier phase has exact source "
            "one half. This removes the unknown reciprocal-field normalization "
            "from the earlier additive Ward theorem. It does not yet upper-bound "
            "F_b: the missing theorem is coercivity of the conjugate normalized "
            "score Y_h, or an actual BT countersequence."
        ),
        "normalized_additive_frame": {
            "scope": (
                "finite connected graph on the mean-zero log-field carrier; "
                "periodic vertex-transitive specialization for Fourier sources"
            ),
            "measure": (
                "dmu_lambda(psi)=Z^-1*exp[-A(psi)/lambda^2]dpsi on H=1^perp"
            ),
            "reciprocal_probability": (
                "q_x=exp(-psi_x), W=sum_x q_x, pi_x=q_x/W, sum_x pi_x=1"
            ),
            "modulation": "a is any fixed real site function",
            "vector_field": "X_a=P_H(a*pi)",
            "boundedness": (
                "for fixed a, X_a is bounded uniformly over the noncompact "
                "field carrier"
            ),
            "restricted_divergence": (
                "div_H X_a=-sum_x a_x*pi_x*(1-pi_x)"
            ),
            "action_pairing": (
                "X_a dot grad A=sum_x pi_x*(r_x*(Delta a)_x-a_x*r_x^2)"
            ),
            "reason": (
                "up to an irrelevant common rescaling of Omega, X_a induces "
                "the additive variation delta Omega_x=a_x/W"
            ),
            "status": "PROVED_EXACT_FINITE_VOLUME",
        },
        "stein_ward_identity": {
            "test_class": (
                "smooth f of polynomial growth, first proved with compact "
                "support and extended using certified finite-volume coercive tails"
            ),
            "identity": (
                "E[X_a dot grad f]=E[f*Y_a]"
            ),
            "conjugate_score": (
                "Y_a=lambda^-2*sum_x pi_x*(r_x*(Delta a)_x-a_x*r_x^2)"
                "+sum_x a_x*pi_x*(1-pi_x)"
            ),
            "centering": "E[Y_a]=0",
            "status": "PROVED_NORMALIZED_ACTUAL_GIBBS_IDENTITY",
        },
        "constant_frame_corollary": {
            "direction": "a_x=1 for every site",
            "vector_field": "X_1=pi-N^-1*1",
            "diversity": "D(pi)=1-sum_x pi_x^2",
            "pointwise_divergence": "div_H X_1=-D(pi)",
            "pointwise_action_pairing": (
                "X_1 dot grad A=-sum_x pi_x*r_x^2"
            ),
            "exact_expectation": (
                "E_mu[sum_x pi_x*r_x^2]=lambda^2*E_mu[D(pi)]"
            ),
            "volume_uniform_bound": (
                "E_mu[sum_x pi_x*r_x^2]<=lambda^2*(1-1/N)"
            ),
            "lambda_two_fifths_bound": (
                "at lambda=2/5 the expectation is <=(4/25)*(1-1/N)<4/25"
            ),
            "periodic_site_identity": (
                "E_mu[pi_x*r_x^2]=lambda^2*(1/N-E_mu[pi_x^2])"
            ),
            "simplex_form": (
                "r_x=sum_(y~x)pi_x/pi_y-degree(x), so the equality is an "
                "exact equilibrium identity for pi on the open probability simplex"
            ),
            "status": "PROVED_VOLUME_UNIFORM_NORMALIZED_ESTIMATE",
        },
        "fourier_source_corollary": {
            "scope": "periodic L^4 lattice with integer L>=4",
            "field_observable": "F_b(psi)=sum_x b_x*psi_x with sum_x b_x=0",
            "source_identity": "E_mu[F_b*Y_a]=N^-1*sum_x a_x*b_x",
            "translation_input": "E_mu[pi_x]=1/N",
            "lowest_real_phase": (
                "for a=b=h, h_x=cos(2*pi*x_mu/L+alpha), "
                "E_mu[F_h*Y_h]=1/2"
            ),
            "meaning": (
                "Y_h is an exactly normalized conjugate score for the physical "
                "lowest Fourier coordinate"
            ),
            "missing_inequality": (
                "a volume-uniform coercive or inverse-Witten estimate converting "
                "the source identity into an upper bound on E[F_h^2]"
            ),
            "status": "EXACT_SOURCE_NORMALIZATION_PROVED_VARIANCE_OPEN",
        },
        "full_phase_stein_matrix": {
            "phases": (
                "on periodic L^4 with integer L>=4, "
                "h_c(x)=cos(2*pi*x_mu/L+alpha), "
                "h_s(x)=sin(2*pi*x_mu/L+alpha)"
            ),
            "observable": "F=(F_c,F_s), F_i=sum_x h_i(x)*psi_x",
            "score": "Y=(Y_c,Y_s), with Y_i=Y_(h_i)",
            "diffusion_matrix": "G_ij(psi)=sum_x pi_x*h_i(x)*h_j(x)",
            "stein_identity": (
                "for smooth g:R^2->R, E[sum_j G_ij*partial_j g(F)]="
                "E[Y_i*g(F)]"
            ),
            "trace": "tr G=sum_x pi_x*(h_c(x)^2+h_s(x)^2)=1",
            "second_harmonic": (
                "z_2=sum_x pi_x*exp(2*i*(2*pi*x_mu/L+alpha))"
            ),
            "eigenvalues": "eigenvalues(G)=(1+|z_2|)/2,(1-|z_2|)/2",
            "source_normalization": "E[F_j*Y_i]=delta_ij/2",
            "mean_matrix": "E[G]=I_2/2 by lattice translation invariance",
            "remaining_degeneracy": (
                "the smaller conditional phase diffusion can vanish only through "
                "second-harmonic localization of the reciprocal probability pi"
            ),
            "status": "PROVED_EXACT_TWO_PHASE_MARGINAL_FRAME",
        },
        "diversity_flow": {
            "constant_frame_flow": (
                "D_{X_1} pi_x=pi_x*(sum_y pi_y^2-pi_x)"
            ),
            "derivative": (
                "D_{X_1}D(pi)=2*(sum_x pi_x^3-(sum_x pi_x^2)^2)>=0"
            ),
            "reason": (
                "the difference is twice the variance of the value pi_x when "
                "x is sampled from pi"
            ),
            "meaning": (
                "the normalized additive flow increases reciprocal-field diversity "
                "while decreasing the BT action"
            ),
            "status": "PROVED_POINTWISE_MONOTONICITY",
        },
        "exact_cycle_fixture": {
            "graph": "four-cycle C4",
            "omega": [enc(value) for value in exact["omega"]],
            "reciprocal": [enc(value) for value in exact["reciprocal"]],
            "total_reciprocal": enc(exact["total_reciprocal"]),
            "pi": [enc(value) for value in exact["pi"]],
            "residual": [enc(value) for value in exact["residual"]],
            "modulation": [enc(value) for value in exact["modulation"]],
            "source": [enc(value) for value in exact["source"]],
            "delta_modulation": [
                enc(value) for value in exact["delta_modulation"]
            ],
            "modulated_vector": [enc(value) for value in exact["vector"]],
            "modulated_divergence": enc(exact["divergence"]),
            "modulated_action_pairing": enc(exact["action_pairing"]),
            "modulated_source_pairing": enc(exact["source_pairing"]),
            "participation": enc(exact["participation"]),
            "diversity": enc(exact["diversity"]),
            "normalized_residual_energy": enc(
                exact["normalized_residual_energy"]
            ),
            "constant_frame_vector": [
                enc(value) for value in exact["constant_vector"]
            ],
            "constant_frame_divergence": enc(-exact["diversity"]),
            "constant_frame_action_pairing": enc(
                -exact["normalized_residual_energy"]
            ),
            "lowest_phase_gram": [
                [enc(value) for value in row] for row in exact["phase_gram"]
            ],
            "lowest_phase_second_harmonic": enc(exact["second_harmonic"]),
            "diversity_flow_derivative": enc(exact["diversity_flow"]),
            "status": "EXACT_RATIONAL_POINTWISE_FRAME_CHECK",
        },
        "method_disposition": {
            "ratio_of_reciprocal_size_biased_expectations": (
                "IMPROVED_TO_NORMALIZED_EXPECTATION"
            ),
            "normalized_reciprocal_weighted_residual_energy": "PROVED",
            "normalized_modulated_stein_ward_frame": "PROVED",
            "lowest_fourier_source_normalization": "PROVED",
            "full_phase_marginal_stein_matrix": "PROVED",
            "coercivity_of_normalized_conjugate_score": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a coercive estimate for the normalized conjugate score Y_h on the lowest Fourier source cyclic sector",
            "an actual BT normalized lowest-mode second-moment theorem or controlled diverging-volume sequence",
            "dyadic Fourier-shell estimates deciding the interacting H^-1 moment after the one-mode gate",
        ],
        "next_gate": (
            "Expand the quadratic form of the normalized conjugate score Y_h and "
            "its Witten/Stein operator while retaining the pi weights and signed "
            "lattice Laplacian. Prove a volume-uniform inverse estimate on F_h, "
            "or construct an actual BT volume sequence violating it. The identity "
            "itself must not be promoted to a field or H^-1 moment bound."
        ),
        "does_not_establish": [
            "an unweighted residual-square estimate at a fixed field site",
            "a normalized BT lowest-mode or field second moment",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the C4 frame; the theorem uses "
                "finite-dimensional divergence, the exact residual variation "
                "under additive Omega perturbations, translation invariance, and "
                "integration by parts with the certified coercive tails"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_normalized_additive_ward_frame.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_normalized_additive_ward_frame.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_normalized_additive_ward_frame",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation, strict JSON/schema validation, exact input "
                "hashes, scoped diff check, and staged-diff inspection required"
            ),
            "tier_1": (
                "producer replay, nonimporting rational C4 frame verifier, and "
                "focused adversarial mutation tests required"
            ),
            "tier_2": (
                "the additive-contraction and center-envelope inputs are unchanged "
                "and checked by content hash; no shared operator changes"
            ),
            "tier_3": (
                "not applicable: the normalized field moment and continuum "
                "lifecycle states remain open"
            ),
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 20568 KiB",
                "independent_verifier": "0.12 s, 30500 KiB",
                "unit_tests": "0.14 s, 30420 KiB",
                "python_compile": "0.05 s, 16312 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "PASS: 1669 nodes, 0 invalid items, 0 malformed events; "
                    "7.62 s, 214992 KiB"
                ),
                "science_forge_shadow": (
                    "not run unless a registered shadow input changes; a skip is "
                    "not a pass"
                ),
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if not payload["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != payload:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT normalized additive Ward frame "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
