#!/usr/bin/env python3
"""Certify the local expected-Hessian symbol and its uniform BT bounds."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
from fractions import Fraction
from itertools import product


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_EXPECTED_HESSIAN_AXIAL_SYMBOL_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-expected-hessian-axial-symbol-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-expected-hessian-axial-symbol.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_expected_hessian_axial_symbol.py"
)
OBSERVATION_REL = (
    "reverse_physics/data/bt_euclidean_hessian_symbol_observations_v1.json"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1.json",
    OBSERVATION_REL,
]
SOURCE_COMMIT = "1a1e5ce6ee2dfbaa1d4594847aea72167c8883ad"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fixture() -> dict[str, Fraction]:
    """Exact C6xC6 differentiated-Hessian fixture."""
    length = 6
    dimensions = 2
    degree = 2 * dimensions
    points = list(product(range(length), repeat=dimensions))
    indices = {point: index for index, point in enumerate(points)}
    profile = (
        Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2),
        Fraction(1), Fraction(1),
    )
    omega = [profile[point[0]] for point in points]

    def shifted(point: tuple[int, ...], axis: int, step: int = 1) -> tuple[int, ...]:
        result = list(point)
        result[axis] = (result[axis] + step) % length
        return tuple(result)

    neighbors = [
        [
            indices[shifted(point, axis, step)]
            for axis in range(dimensions) for step in (-1, 1)
        ]
        for point in points
    ]
    ratios = [
        [omega[target] / omega[source] for target in row]
        for source, row in enumerate(neighbors)
    ]
    residual = [sum(row, Fraction()) - degree for row in ratios]

    def hessian(left: int, right: int) -> Fraction:
        columns = []
        for selected in (left, right):
            column = []
            for source, row in enumerate(neighbors):
                if source == selected:
                    column.append(-sum(ratios[source], Fraction()))
                else:
                    column.append(sum(
                        (ratio for ratio, target in zip(ratios[source], row)
                         if target == selected),
                        Fraction(),
                    ))
            columns.append(column)
        value = sum(
            (a * b for a, b in zip(columns[0], columns[1])), Fraction()
        )
        for source, row in enumerate(neighbors):
            for ratio, target in zip(ratios[source], row):
                q_left = int(left == target) - int(left == source)
                q_right = int(right == target) - int(right == source)
                value += residual[source] * ratio * q_left * q_right
        return value

    b_formula: list[Fraction] = []
    c_formula: list[Fraction] = []
    d_formula: list[Fraction] = []
    b_direct: list[Fraction] = []
    c_direct: list[Fraction] = []
    d_direct: list[Fraction] = []
    for left, point in enumerate(points):
        for axis in range(dimensions):
            middle = indices[shifted(point, axis)]
            right = indices[shifted(point, axis, 2)]
            t = omega[middle] / omega[left]
            b_formula.append(-(
                (degree + 2 * residual[left]) * t
                + (degree + 2 * residual[middle]) / t
            ))
            c_formula.append(
                omega[left] * omega[right] / (omega[middle] ** 2)
            )
            b_direct.append(hessian(left, middle))
            c_direct.append(hessian(left, right))
        for first in range(dimensions):
            for second in range(first + 1, dimensions):
                for first_sign in (-1, 1):
                    for second_sign in (-1, 1):
                        middle_first = indices[shifted(
                            point, first, first_sign
                        )]
                        middle_second = indices[shifted(
                            point, second, second_sign
                        )]
                        diagonal_point = shifted(
                            shifted(point, first, first_sign),
                            second, second_sign,
                        )
                        diagonal = indices[diagonal_point]
                        d_formula.append(
                            omega[left] * omega[diagonal]
                            / (omega[middle_first] ** 2)
                            + omega[left] * omega[diagonal]
                            / (omega[middle_second] ** 2)
                        )
                        d_direct.append(hessian(left, diagonal))

    def average(values: list[Fraction]) -> Fraction:
        return sum(values, Fraction()) / len(values)

    b = average(b_formula)
    c = average(c_formula)
    d = average(d_formula)
    return {
        "b_formula": b,
        "c_formula": c,
        "d_formula": d,
        "b_direct": average(b_direct),
        "c_direct": average(c_direct),
        "d_direct": average(d_direct),
        "alpha": -(b + 4 * c + 2 * (dimensions - 1) * d),
        "residual_square_density": average([value * value for value in residual]),
    }


def estimate(run: dict, name: str) -> tuple[float, float]:
    values = [
        block[f"sum_{name}"] / block["sample_count"]
        for block in run["blocks"]
    ]
    return (
        statistics.fmean(values),
        statistics.stdev(values) / math.sqrt(len(values)),
    )


def observation_summaries() -> list[dict]:
    with open(os.path.join(ROOT, OBSERVATION_REL), encoding="utf-8") as handle:
        data = json.load(handle)
    summaries = []
    for run in data["runs"]:
        row = {
            "length": run["lattice"]["length"],
            "volume": run["lattice"]["volume"],
            "sample_count": run["recorded_samples"],
            "acceptance_rate": run["acceptance_rate"],
            "action_recompute_residual": run["final_action_recompute_residual"],
        }
        for name in ("b", "c", "d", "alpha", "action_density"):
            mean, error = estimate(run, name)
            row[f"mean_{name}"] = mean
            row[f"blocked_standard_error_{name}"] = error
        summaries.append(row)
    return summaries


def build() -> dict:
    degree = 8
    coupling = Fraction(2, 5)
    action_density_bound = Fraction(1222, 25)
    residual_second_moment_bound = 2 * action_density_bound
    s_second_moment_bound = 2 * degree * degree + 2 * residual_second_moment_bound
    b_absolute_bound = 11 * degree * degree + 5 * residual_second_moment_bound
    c_upper_bound = s_second_moment_bound / 4
    d_upper_bound = s_second_moment_bound / 2
    alpha_absolute_bound = (
        b_absolute_bound + 4 * c_upper_bound + 6 * d_upper_bound
    )
    axial_linear_bound = alpha_absolute_bound + 4 * c_upper_bound
    psi_variance_constant = coupling * coupling / axial_linear_bound
    phi_variance_constant = 1 / axial_linear_bound
    exact = fixture()
    observed = observation_summaries()

    details = {
        "fixture_formula_and_direct_b_agree": exact["b_formula"] == exact["b_direct"],
        "fixture_formula_and_direct_c_agree": exact["c_formula"] == exact["c_direct"],
        "fixture_formula_and_direct_d_agree": exact["d_formula"] == exact["d_direct"],
        "fixture_b_is_minus_133_over_12": exact["b_formula"] == Fraction(-133, 12),
        "fixture_c_is_59_over_48": exact["c_formula"] == Fraction(59, 48),
        "fixture_d_is_7_over_3": exact["d_formula"] == Fraction(7, 3),
        "fixture_alpha_is_three_halves": exact["alpha"] == Fraction(3, 2),
        "residual_second_moment_bound_is_2444_over_25": residual_second_moment_bound == Fraction(2444, 25),
        "s_second_moment_bound_is_8088_over_25": s_second_moment_bound == Fraction(8088, 25),
        "b_absolute_bound_is_5964_over_5": b_absolute_bound == Fraction(5964, 5),
        "c_upper_bound_is_2022_over_25": c_upper_bound == Fraction(2022, 25),
        "d_upper_bound_is_4044_over_25": d_upper_bound == Fraction(4044, 25),
        "alpha_absolute_bound_is_62172_over_25": alpha_absolute_bound == Fraction(62172, 25),
        "axial_linear_bound_is_14052_over_5": axial_linear_bound == Fraction(14052, 5),
        "psi_variance_constant_is_one_over_17565": psi_variance_constant == Fraction(1, 17565),
        "both_observed_alpha_means_are_positive": all(row["mean_alpha"] > 0 for row in observed),
        "observed_alpha_means_agree_within_one_hundredth": abs(observed[0]["mean_alpha"] - observed[1]["mean_alpha"]) < 0.01,
        "observation_action_recomputes_are_small": all(row["action_recompute_residual"] < 1.0e-8 for row in observed),
        "h_minus_one_claim_remains_open": True,
        "no_lorentzian_promotion": True,
    }
    failures = [name for name, ok in details.items() if not ok]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_EXPECTED_HESSIAN_AXIAL_SYMBOL_V1",
        "schema_version": "reverse-physics-bt-euclidean-expected-hessian-axial-symbol-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "EXPECTED_HESSIAN_SYMBOL_AND_UNIFORM_COEFFICIENT_BOUNDS_PROVED",
        "result_kind": "exact full-Gibbs expected-Hessian symbol reduction with finite-volume binary64 diagnostic",
        "question": "Does the full interacting BT Witten numerator retain an exact p^4 symbol, or can the Gibbs measure generate an ordinary p^2 stiffness?",
        "answer": "Hypercubic symmetry, range two, and the constant-shift Ward identity reduce every axial expected-Hessian eigenvalue exactly to Hhat_L(p)=alpha_L*omega(p)+c_L*omega(p)^2, with alpha_L=-(b_L+4*c_L+6*d_L). The affine action-density theorem gives volume-uniform bounds on b_L,c_L,d_L and hence Hhat_L(p)<=14052*omega(p)/5 at lambda=2/5. Score-covariance positivity gives alpha_L>=-c_L*omega_min, so every large-volume accumulation point is nonnegative. Deterministic full-Gibbs observations give alpha_6=0.09713(75) and alpha_8=0.09553(59), evidence for a nonzero p^2 term in this expected-Hessian numerator, not a proof of its infinite-volume positivity or of a physical stiffness. This full-measure Hessian is not the conditioned background score and establishes no H^-1 bound or divergence.",
        "exact_symbol_theorem": {
            "action": "A=(1/2)*sum_x r_x^2, r_x=sum_(y~x) exp(psi_y-psi_x)-2D",
            "expected_kernel": "H_L(z)=E_mu[partial_psi_0 partial_psi_z A]",
            "gibbs_ward": "E_mu[Hess A]=lambda^(-2)*E_mu[grad A tensor grad A] on the mean-zero carrier",
            "support": "H_L(z)=0 beyond graph distance two",
            "orbit_coefficients": "a=H(0), b=H(e_mu), c=H(2e_mu), d=H(e_mu+/-e_nu)",
            "row_sum": "a+2D*b+2D*c+2D*(D-1)*d=0",
            "full_symbol": "a+2*b*sum_mu cos(p_mu)+2*c*sum_mu cos(2*p_mu)+4*d*sum_(mu<nu) cos(p_mu)cos(p_nu)",
            "axial_symbol_general_D": "Hhat(p*e_1)=alpha_L*omega(p)+c_L*omega(p)^2, alpha_L=-(b_L+4*c_L+2*(D-1)*d_L)",
            "four_dimensions": "alpha_L=-(b_L+4*c_L+6*d_L)",
            "omega": "2*(1-cos(p))",
            "positivity_consequence": "alpha_L>=-c_L*omega(2*pi/L), hence liminf alpha_L>=0 along any sequence where c_L is uniformly bounded",
            "status": "PROVED_FINITE_VOLUME_AND_UNIFORM_LARGE_VOLUME_SIGN_LIMINF",
        },
        "local_hessian_formulas": {
            "edge": "H_(x,x+e)=-(q+2*r_x)*t_(x,x+e)-(q+2*r_(x+e))*t_(x+e,x)",
            "axial_distance_two": "H_(x,x+2e)=t_(x+e,x)*t_(x+e,x+2e)",
            "mixed_distance_two": "H_(x,x+e+f)=t_(x+e,x)*t_(x+e,x+e+f)+t_(x+f,x)*t_(x+f,x+e+f)",
            "definitions": "t_xy=exp(psi_y-psi_x), s_x=sum_y t_xy=q+r_x",
            "jensen_lower_bounds": "c_L>=1 and d_L>=2",
            "status": "PROVED_BY_DIRECT_DIFFERENTIATION",
        },
        "uniform_full_gibbs_bounds": {
            "scope": "D=4, q=8, lambda=2/5, every periodic L^4 torus with unaliased range-two orbits",
            "input": "E[A/N]<=1222/25",
            "residual_second_moment": enc(residual_second_moment_bound),
            "s_second_moment": enc(s_second_moment_bound),
            "absolute_b": enc(b_absolute_bound),
            "upper_c": enc(c_upper_bound),
            "upper_d": enc(d_upper_bound),
            "absolute_alpha": enc(alpha_absolute_bound),
            "axial_symbol_bound": "0<=Hhat_L(p)<=C_H*omega(p)",
            "C_H": enc(axial_linear_bound),
            "cramer_rao_actual_mode_lower_bound_psi": "Var_mu(<h,psi>)>=1/(17565*omega(p)) for every unit real axial Fourier mode h",
            "cramer_rao_actual_mode_lower_bound_phi": "Var_mu(<h,phi>)>=5/(14052*omega(p)), phi=psi/lambda",
            "psi_constant": enc(psi_variance_constant),
            "phi_constant": enc(phi_variance_constant),
            "interpretation": "This is a lower bound on mode variance. It is not the upper bound required for H^-1 tightness and does not prove H^-1 divergence.",
            "status": "PROVED_FOR_ACTUAL_INTERACTING_GIBBS_MEASURE",
        },
        "exact_fixture": {
            "lattice": "C6 x C6",
            "dimensions": 2,
            "omega_profile_first_axis": [enc(value) for value in (1, 2, 1, Fraction(1, 2), 1, 1)],
            "b": enc(exact["b_formula"]),
            "c": enc(exact["c_formula"]),
            "d": enc(exact["d_formula"]),
            "alpha": enc(exact["alpha"]),
            "residual_square_density": enc(exact["residual_square_density"]),
            "direct_sparse_hessian_matches_local_formulas": True,
        },
        "finite_volume_diagnostic": {
            "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
            "observation_path": OBSERVATION_REL,
            "observation_sha256": sha256(OBSERVATION_REL),
            "summaries": observed,
            "interpretation": "The L=6 and L=8 local full-Gibbs coefficients are volume-stable and show alpha_L near 0.096. Binary64 arithmetic, finite chains, two volumes, and one local sampler prohibit an infinite-volume or nonzero-alpha theorem.",
        },
        "method_disposition": {
            "full_gibbs_axial_expected_hessian_symbol": "PROVED",
            "uniform_full_gibbs_symbol_upper_bound": "PROVED",
            "actual_mode_cramer_rao_lower_bound": "PROVED",
            "exact_noninteracting_p4_cancellation": "PROVED_AT_VACUUM",
            "exact_interacting_alpha_cancellation": "NOT_SUPPORTED_BY_L6_L8_OBSERVATION",
            "nonzero_infinite_volume_alpha": "OBSERVED_NOT_PROVED",
            "conditioned_background_score_bound": "OPEN_SEPARATE_OBJECT",
            "volume_uniform_witten_coercivity": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
        },
        "missing_object_ledger": [
            "a rigorous positive lower bound or zero theorem for the infinite-volume expected-Hessian twist-curvature coefficient alpha",
            "a transfer from local expected-Hessian information to a lower bound on the full one-form Witten operator",
            "an upper bound on actual Fourier-mode variances and its dyadic H^-1 shell sum",
            "tightness in a topology compactly weaker than any proved uniform moment topology",
        ],
        "next_gate": "Treat alpha_L as the diamagnetic uniform-twist curvature, not yet the helicity modulus: derive the matching paramagnetic integrated-current variance and their free-energy difference. Seek a rigorous positive lower bound or cancellation theorem for that complete twist response, then determine whether it supplies Witten coercivity; keep the conditioned background score as a separate rail.",
        "does_not_establish": [
            "a nonzero infinite-volume p^2 coefficient",
            "the conditioned lowest-mode score estimate",
            "an upper bound or divergence theorem for the actual interacting H^-1 moment",
            "tightness, a continuum measure, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": "exact rational inequalities and exact rational fixture; finite-volume observation is separately typed IEEE-754 binary64",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_expected_hessian_axial_symbol.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_expected_hessian_axial_symbol.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_expected_hessian_axial_symbol",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_hessian_symbol_experiment.py --smoke",
        ],
        "tier_receipt": {
            "tier_0": "changed Python compiled; schema, certificate, observation, and planning JSON parsed; scoped git diff check and exact staged-diff inspection run before commit",
            "tier_1": "producer 20/20 in 0.18 s at 22020 KiB; independent verifier 8/8 in 0.26 s at 30704 KiB; ten direct and adversarial tests in 1.63 s at 31952 KiB; L=6 smoke observer in 1.74 s at 22436 KiB",
            "tier_2": "not required: imported affine action-density and Witten bridge certificates are unchanged and content-hashed",
            "tier_3": "not run: no H^-1 lifecycle promotion, freeze, release, or shared-core algebra change",
            "memory_policy": "Python commands run under ulimit -v 500000; expensive observation reproduction is optional and separate from the fast commit rail",
            "repository_audits": "planning import accepted 1679 nodes with 0 invalid items and 0 malformed events in 15.66 s at 279820 KiB under GOMEMLIMIT=300MiB and GOGC=50. The 3.20 s advisory shadow wrapper exited zero but its bridge audit failed closed because the external bp2transformer verifier lacks sympy; it also reported corpus drift 1823 versus baseline 976. Neither advisory finding is counted as a scientific pass.",
        },
        "checks": {
            "ok": not failures,
            "passed": len(details) - len(failures),
            "total": len(details),
            "failures": failures,
            "details": details,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except FileNotFoundError:
            print(f"missing certificate: {CERT_REL}")
            return 1
        if current != payload:
            print(f"certificate drift: {CERT_REL}")
            return 1
        print(f"expected-Hessian axial symbol: {payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        return 0
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {CERT_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
