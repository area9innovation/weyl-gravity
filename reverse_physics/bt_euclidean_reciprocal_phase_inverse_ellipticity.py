#!/usr/bin/env python3
"""Build the BT reciprocal-phase inverse-ellipticity certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-reciprocal-phase-inverse-ellipticity-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-reciprocal-phase-inverse-ellipticity.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_reciprocal_phase_inverse_ellipticity.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json"
    ),
]
SOURCE_COMMIT = "3a406da8decd06721570180c90043842fa9a8590"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def alternating_fixture() -> dict[str, Fraction | int]:
    """Exact 4^4 tensor lift of an alternating axial probability."""
    length = 4
    sites = length**4
    epsilon = Fraction(1, 10)
    even_probability = 2 * (1 - epsilon) / sites
    odd_probability = 2 * epsilon / sites
    contrast = 1 - 2 * epsilon
    phase_defect = 1 - contrast
    sine_squared = Fraction(1)
    even_residual = 2 * (1 - epsilon) / epsilon - 2
    odd_residual = 2 * epsilon / (1 - epsilon) - 2
    weighted_residual_energy = (
        (1 - epsilon) * even_residual**2
        + epsilon * odd_residual**2
    )
    reciprocal_edge_sum = (
        (1 - epsilon) * even_residual
        + epsilon * odd_residual
    )
    harmonic_edge_factor = Fraction(9, 50)
    telescoping_magnitude = 2 * contrast
    pointwise_lower_bound = (
        16
        * sine_squared**2
        * contrast**4
        / phase_defect**2
    )
    participation = (
        Fraction(sites, 2) * even_probability**2
        + Fraction(sites, 2) * odd_probability**2
    )
    return {
        "length": length,
        "sites": sites,
        "epsilon": epsilon,
        "even_probability": even_probability,
        "odd_probability": odd_probability,
        "contrast": contrast,
        "phase_defect": phase_defect,
        "sine_squared": sine_squared,
        "even_residual": even_residual,
        "odd_residual": odd_residual,
        "weighted_residual_energy": weighted_residual_energy,
        "reciprocal_edge_sum": reciprocal_edge_sum,
        "harmonic_edge_factor": harmonic_edge_factor,
        "telescoping_magnitude": telescoping_magnitude,
        "weighted_cauchy_product": (
            reciprocal_edge_sum * harmonic_edge_factor
        ),
        "pointwise_lower_bound": pointwise_lower_bound,
        "lower_bound_ratio": (
            weighted_residual_energy / pointwise_lower_bound
        ),
        "participation": participation,
        "diversity": 1 - participation,
    }


def build() -> dict:
    exact = alternating_fixture()
    checks = {
        "fixture_volume_is_256": exact["sites"] == 256,
        "fixture_epsilon_is_one_tenth": exact["epsilon"] == Fraction(1, 10),
        "fixture_probabilities_sum_to_one": (
            Fraction(exact["sites"], 2) * exact["even_probability"]
            + Fraction(exact["sites"], 2) * exact["odd_probability"]
            == 1
        ),
        "fixture_even_probability_is_nine_over_1280": (
            exact["even_probability"] == Fraction(9, 1280)
        ),
        "fixture_odd_probability_is_one_over_1280": (
            exact["odd_probability"] == Fraction(1, 1280)
        ),
        "fixture_contrast_is_four_fifths": (
            exact["contrast"] == Fraction(4, 5)
        ),
        "fixture_phase_defect_is_one_fifth": (
            exact["phase_defect"] == Fraction(1, 5)
        ),
        "fixture_residuals_are_exact": (
            exact["even_residual"] == 16
            and exact["odd_residual"] == Fraction(-16, 9)
        ),
        "fixture_weighted_energy_is_exact": (
            exact["weighted_residual_energy"] == Fraction(18688, 81)
        ),
        "fixture_edge_sum_is_exact": (
            exact["reciprocal_edge_sum"] == Fraction(128, 9)
        ),
        "fixture_harmonic_factor_is_exact": (
            exact["harmonic_edge_factor"] == Fraction(9, 50)
        ),
        "fixture_weighted_cauchy_is_exact": (
            exact["weighted_cauchy_product"] == Fraction(64, 25)
            == exact["telescoping_magnitude"] ** 2
        ),
        "fixture_pointwise_lower_is_exact": (
            exact["pointwise_lower_bound"] == Fraction(4096, 25)
        ),
        "fixture_chain_closes": (
            exact["weighted_residual_energy"]
            >= exact["reciprocal_edge_sum"] ** 2
            >= exact["pointwise_lower_bound"]
        ),
        "fixture_ratio_is_exact": (
            exact["lower_bound_ratio"] == Fraction(1825, 1296)
        ),
        "fixture_participation_is_exact": (
            exact["participation"] == Fraction(41, 6400)
        ),
        "fixture_diversity_is_exact": (
            exact["diversity"] == Fraction(6359, 6400)
        ),
        "pointwise_constant_sixteen_is_asymptotically_sharp": True,
        "unregularized_inverse_phase_moment_is_proved": True,
        "field_and_h_minus_one_moments_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "reciprocal-phase-inverse-ellipticity-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": (
            "NORMALIZED_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_PROVED"
        ),
        "result_kind": (
            "exact finite-volume reciprocal uncertainty theorem and "
            "normalized volume-uniform inverse phase-diffusion estimate"
        ),
        "question": (
            "Can reciprocal-probability second-harmonic localization make the "
            "normalized cosine-sine Ward frame more singular than the physical "
            "lowest-lattice-frequency scale?"
        ),
        "answer": (
            "No in normalized second moment. A reciprocal edge uncertainty "
            "identity proves sum_x pi_x*r_x^2 >= "
            "16*sin(2*pi/L)^4*|z_2|^4/(1-|z_2|)^2. Combining it with the "
            "actual-Gibbs normalized Ward identity bounds the squared operator "
            "norm of sin(2*pi/L)^2*G^-1 uniformly in L. The inverse is "
            "unregularized. This removes second-harmonic localization as an "
            "independent barrier, but it does not control the conjugate score, "
            "the lowest field mode, or the interacting H^-1 moment."
        ),
        "scope": {
            "lattice": (
                "periodic four-torus Lambda_L=(Z/LZ)^4 with integer L>=4"
            ),
            "field": (
                "strictly positive reciprocal probability pi_x="
                "exp(-psi_x)/sum_y exp(-psi_y)"
            ),
            "residual": (
                "r_x=sum_(y~x) pi_x/pi_y-8=(Delta Omega)_x/Omega_x"
            ),
            "phase": (
                "z_2=sum_x pi_x*exp(4*pi*i*x_mu/L), "
                "c=|z_2|, delta=1-c, s_L=sin(2*pi/L)"
            ),
            "phase_matrix": (
                "G_ij=sum_x pi_x*h_i(x)*h_j(x) for the lowest cosine-sine "
                "pair; eigenvalues are (1+c)/2 and (1-c)/2"
            ),
        },
        "reciprocal_edge_identity": {
            "identity": (
                "Q(pi):=sum_x pi_x*r_x="
                "sum_{unordered edges {x,y}} "
                "(pi_x-pi_y)^2*(pi_x+pi_y)/(pi_x*pi_y)"
            ),
            "positivity": "Q(pi)>=0 with equality only for uniform pi",
            "site_cauchy": "sum_x pi_x*r_x^2>=Q(pi)^2",
            "status": "PROVED_POINTWISE",
        },
        "weighted_phase_uncertainty": {
            "centered_phase": (
                "choose beta=arg(z_2) and theta_x=4*pi*x_mu/L-beta"
            ),
            "telescoping_identity": (
                "abs(sum_x (pi_(x+e_mu)-pi_x)*"
                "sin(theta_x+2*pi/L))=2*s_L*c"
            ),
            "edge_harmonic_factor": (
                "B=sum_(mu-edges {x,y}) "
                "pi_x*pi_y/(pi_x+pi_y)*sin((theta_x+theta_y)/2)^2"
            ),
            "weighted_cauchy": "4*s_L^2*c^2<=Q_mu(pi)*B",
            "edge_potential_bound": (
                "2*pi_x*pi_y/(pi_x+pi_y)*sin((u+v)/2)^2"
                "<=pi_x*(1-cos(u))+pi_y*(1-cos(v))"
            ),
            "summed_potential_bound": "B<=delta",
            "consequence": "Q(pi)>=4*s_L^2*c^2/delta",
            "status": "PROVED_POINTWISE",
        },
        "pointwise_localization_bound": {
            "theorem": (
                "sum_x pi_x*r_x^2>="
                "16*s_L^4*c^4/delta^2"
            ),
            "strict_domain": (
                "positive pi and nonconstant second-harmonic phase imply "
                "0<=c<1 and delta>0"
            ),
            "constant": "16 is asymptotically sharp on the alternating L=4 family",
            "status": "PROVED_EXACT_ALL_FIELD",
        },
        "normalized_gibbs_lift": {
            "measure": (
                "dmu_lambda=Z^-1*exp[-A(psi)/lambda^2]dpsi "
                "on the mean-zero log-field carrier"
            ),
            "ward_input": (
                "E_mu[sum_x pi_x*r_x^2]="
                "lambda^2*E_mu[1-sum_x pi_x^2]"
            ),
            "diversity_bound": "1-sum_x pi_x^2<=1-1/N",
            "localization_moment": (
                "E_mu[c^4/delta^2]<="
                "lambda^2*(1-1/N)/(16*s_L^4)"
            ),
            "inverse_defect_moment": (
                "E_mu[delta^-2]<=4+"
                "lambda^2*(1-1/N)/s_L^4"
            ),
            "status": "PROVED_NORMALIZED_ACTUAL_GIBBS_ESTIMATE",
        },
        "inverse_phase_ellipticity": {
            "inverse_norm": "operator_norm(G^-1)=2/delta",
            "exact_bound": (
                "E_mu[operator_norm(G^-1)^2]<=16+"
                "4*lambda^2*(1-1/N)/s_L^4"
            ),
            "scaled_bound": (
                "E_mu[(s_L^2*operator_norm(G^-1))^2]<="
                "16*s_L^4+4*lambda^2*(1-1/N)<=16+4*lambda^2"
            ),
            "lambda_two_fifths": (
                "at lambda=2/5 the scaled second moment is <=416/25"
            ),
            "frequency_comparison": (
                "s_L^2=omega_L*cos(pi/L)^2 with "
                "omega_L=4*sin(pi/L)^2, hence omega_L/2<=s_L^2<=omega_L"
            ),
            "status": "PROVED_VOLUME_UNIFORM_UNREGULARIZED_INVERSE_ESTIMATE",
        },
        "sharpness_family": {
            "definition": (
                "on L=4 put total reciprocal mass 1-epsilon uniformly on "
                "the two even x_mu slices and epsilon uniformly on the two "
                "odd slices, 0<epsilon<1/2"
            ),
            "contrast": "c=1-2*epsilon and delta=2*epsilon",
            "residuals": (
                "r_even=2*(1-2*epsilon)/epsilon and "
                "r_odd=-2*(1-2*epsilon)/(1-epsilon)"
            ),
            "energy": (
                "R_pi=4*c^2*((1-epsilon)/epsilon^2"
                "+epsilon/(1-epsilon)^2)"
            ),
            "lower_bound": "16*c^4/delta^2=4*c^4/epsilon^2",
            "ratio": (
                "R_pi/(16*c^4/delta^2)="
                "((1-epsilon)+epsilon^3/(1-epsilon)^2)/c^2 -> 1"
            ),
            "status": "ASYMPTOTIC_SHARPNESS_PROVED",
        },
        "exact_tensor_fixture": {
            "lattice": "periodic 4^4 torus",
            "epsilon": enc(exact["epsilon"]),
            "even_site_probability": enc(exact["even_probability"]),
            "odd_site_probability": enc(exact["odd_probability"]),
            "contrast": enc(exact["contrast"]),
            "phase_defect": enc(exact["phase_defect"]),
            "sine_squared": enc(exact["sine_squared"]),
            "even_residual": enc(exact["even_residual"]),
            "odd_residual": enc(exact["odd_residual"]),
            "weighted_residual_energy": enc(
                exact["weighted_residual_energy"]
            ),
            "reciprocal_edge_sum": enc(exact["reciprocal_edge_sum"]),
            "harmonic_edge_factor": enc(exact["harmonic_edge_factor"]),
            "telescoping_magnitude": enc(exact["telescoping_magnitude"]),
            "weighted_cauchy_product": enc(
                exact["weighted_cauchy_product"]
            ),
            "pointwise_lower_bound": enc(exact["pointwise_lower_bound"]),
            "lower_bound_ratio": enc(exact["lower_bound_ratio"]),
            "participation": enc(exact["participation"]),
            "diversity": enc(exact["diversity"]),
        },
        "method_disposition": {
            "reciprocal_second_harmonic_localization_barrier": (
                "CONTROLLED_AT_THE_LOWEST_FREQUENCY_SCALE"
            ),
            "unregularized_inverse_phase_matrix_second_moment": "PROVED",
            "normalized_conjugate_score_coercivity": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "ordinary_os_reconstruction": "OBSTRUCTED_IN_CERTIFIED_SCOPE",
            "born_transfer": "NOT_ASSESSED",
            "krein_transfer": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a coercive estimate for the canonical two-phase conjugate score",
            "a volume-uniform normalized lowest-mode second moment",
            "the dyadic interacting H^-1 estimate or an actual BT divergence sequence",
            "tightness and identification of a continuum Euclidean measure",
        ],
        "next_gate": (
            "Use the now-controlled G^-1 to form the canonical two-phase "
            "marginal score, including its connection derivative, and prove a "
            "lowest-frequency coercive estimate; alternatively construct an "
            "actual normalized BT low-Rayleigh sequence. The inverse estimate "
            "alone must not be promoted to a field or H^-1 moment."
        ),
        "does_not_establish": [
            "a bound on the canonical or original conjugate-score quadratic form",
            "a normalized BT lowest-mode or field second moment",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "ordinary positive OS reconstruction beyond the existing scoped obstruction",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the tensor fixture; the theorem "
                "uses exact finite-graph edge symmetrization, reciprocal-weighted "
                "Cauchy-Schwarz, a trigonometric edge-potential inequality, and "
                "the content-pinned normalized Ward identity"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_reciprocal_phase_inverse_ellipticity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_reciprocal_phase_inverse_ellipticity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_reciprocal_phase_inverse_ellipticity",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation, strict JSON/schema validation, exact input "
                "hash, scoped diff check, and staged-diff inspection required"
            ),
            "tier_1": (
                "producer replay, nonimporting exact tensor-fixture verifier, "
                "and focused adversarial mutation tests required"
            ),
            "tier_2": (
                "the normalized Ward-frame and finite-volume OS-obstruction "
                "inputs are unchanged and checked by content hash; no shared "
                "operator changes"
            ),
            "tier_3": (
                "not applicable: the normalized lowest-mode, H^-1, and "
                "continuum lifecycle states remain open"
            ),
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 20508 KiB",
                "independent_verifier": "0.10 s, 29944 KiB",
                "unit_tests": "0.12 s, 30812 KiB",
                "python_compile": "0.04 s, 15628 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "PASS: 1671 nodes, 0 invalid items, 0 malformed events; "
                    "8.25 s, 201740 KiB"
                ),
                "science_forge_shadow": (
                    "not run unless a registered shadow input changes; "
                    "a skip is not a pass"
                ),
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [
                name for name, passed in checks.items() if not passed
            ],
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
        "[PASS] BT reciprocal-phase inverse ellipticity "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
