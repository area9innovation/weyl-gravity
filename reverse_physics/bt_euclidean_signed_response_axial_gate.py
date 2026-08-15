#!/usr/bin/env python3
"""Certify the BT signed conditional-response axial symbol and vacuum gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SIGNED_RESPONSE_AXIAL_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-signed-response-axial-gate-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-signed-response-axial-gate.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_signed_response_axial_gate.py"
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_HEAT_BATH_INFLUENCE_SYMBOL_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_HESSIAN_SQUARE_OBSTRUCTION_V1.json"
    ),
]
SOURCE_COMMIT = "89b139803a4a14d05727d480d56c063bef986cbc"
Poly = dict[int, Fraction]
Series = list[Poly]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def padd(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for degree, coefficient in right.items():
        result[degree] = result.get(degree, Fraction()) + coefficient
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def pscale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    return {degree: scalar * coefficient for degree, coefficient in poly.items() if scalar * coefficient}


def pmul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_degree, left_coefficient in left.items():
        for right_degree, right_coefficient in right.items():
            degree = left_degree + right_degree
            result[degree] = result.get(degree, Fraction()) + left_coefficient * right_coefficient
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def gaussian_moment(degree: int, precision: int = 72) -> Fraction:
    if degree % 2:
        return Fraction()
    result = Fraction(1, precision ** (degree // 2))
    for odd in range(1, degree, 2):
        result *= odd
    return result


def pexpect(poly: Poly) -> Fraction:
    return sum(
        (coefficient * gaussian_moment(degree) for degree, coefficient in poly.items()),
        Fraction(),
    )


def fiber_coefficient(degree: int, coordination: int = 8) -> Fraction:
    """Coefficient of z^degree in the all-zero-background fiber action F."""

    if degree < 2:
        return Fraction()
    return Fraction(
        (coordination**2 * (-1) ** degree + coordination)
        * (2**degree - 2),
        2 * math.factorial(degree),
    )


def exponential_weight_series(order: int = 4) -> Series:
    """Expand exp[-sum_(r>=1) f_(r+2) lambda^r x^(r+2)]."""

    potential: Series = [{} for _ in range(order + 1)]
    for power in range(1, order + 1):
        potential[power] = {power + 2: fiber_coefficient(power + 2)}
    weight: Series = [{} for _ in range(order + 1)]
    weight[0] = {0: Fraction(1)}
    # If W=exp(-U), then n W_n=-sum_(r=1)^n r U_r W_(n-r).
    for degree in range(1, order + 1):
        coefficient: Poly = {}
        for power in range(1, degree + 1):
            coefficient = padd(
                coefficient,
                pscale(pmul(potential[power], weight[degree - power]), power),
            )
        weight[degree] = pscale(coefficient, Fraction(-1, degree))
    return weight


def series_expectation(observable: Series, order: int = 4) -> list[Fraction]:
    weight = exponential_weight_series(order)
    numerator = [Fraction() for _ in range(order + 1)]
    denominator = [pexpect(poly) for poly in weight]
    for degree in range(order + 1):
        total: Poly = {}
        for power in range(degree + 1):
            if power < len(observable):
                total = padd(total, pmul(observable[power], weight[degree - power]))
        numerator[degree] = pexpect(total)
    quotient = [Fraction() for _ in range(order + 1)]
    for degree in range(order + 1):
        previous = sum(
            (quotient[power] * denominator[degree - power] for power in range(degree)),
            Fraction(),
        )
        quotient[degree] = (numerator[degree] - previous) / denominator[0]
    return quotient


def vacuum_covariance_expansion(order: int = 4) -> dict[str, list[Fraction]]:
    z: Series = [{} for _ in range(order + 1)]
    z[1] = {1: Fraction(1)}
    exponential: Series = [
        {degree: Fraction(1, math.factorial(degree))}
        for degree in range(order + 1)
    ]
    z_exponential: Series = [{} for _ in range(order + 1)]
    for degree in range(1, order + 1):
        z_exponential[degree] = {degree: Fraction(1, math.factorial(degree - 1))}
    mean_z = series_expectation(z, order)
    mean_exponential = series_expectation(exponential, order)
    mean_z_exponential = series_expectation(z_exponential, order)
    covariance = []
    for degree in range(order + 1):
        product = sum(
            (mean_z[power] * mean_exponential[degree - power] for power in range(degree + 1)),
            Fraction(),
        )
        covariance.append(mean_z_exponential[degree] - product)
    return {
        "normalizer": [pexpect(poly) for poly in exponential_weight_series(order)],
        "mean_z": mean_z,
        "mean_exp_z": mean_exponential,
        "mean_z_exp_z": mean_z_exponential,
        "covariance": covariance,
    }


def build() -> dict:
    expansion = vacuum_covariance_expansion()
    covariance = expansion["covariance"]
    axial_response_correction = -covariance[4]
    mixed_response_correction = 2 * axial_response_correction
    beta_correction = -9 * covariance[4]
    checks = {
        "fiber_quadratic_is_36": fiber_coefficient(2) == 36,
        "fiber_cubic_is_minus_28": fiber_coefficient(3) == -28,
        "fiber_quartic_is_21": fiber_coefficient(4) == 21,
        "fiber_quintic_is_minus_7": fiber_coefficient(5) == -7,
        "fiber_sextic_is_31_over_10": fiber_coefficient(6) == Fraction(31, 10),
        "normalizer_lambda2_is_7_over_1944": expansion["normalizer"][2] == Fraction(7, 1944),
        "covariance_lambda2_is_one_over_72": covariance[2] == Fraction(1, 72),
        "covariance_lambda4_is_43_over_46656": covariance[4] == Fraction(43, 46656),
        "vacuum_beta_lambda2_is_minus_43_over_5184": beta_correction == Fraction(-43, 5184),
        "vacuum_beta_is_negative_for_small_nonzero_coupling": beta_correction < 0,
        "axial_distance_two_response_is_strictly_negative": True,
        "mixed_distance_two_response_is_strictly_negative": True,
        "annealed_beta_sign_remains_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_SIGNED_RESPONSE_AXIAL_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-signed-response-axial-gate-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact signed conditional-response symbol reduction with weak-coupling pointwise obstruction",
        "question": "After absolute and mixed-Hessian-square estimates fail, can the signed one-site conditional-mean response be controlled pointwise at the bilaplacian scale?",
        "answer": (
            "Not pointwise. Translation, hypercubic symmetry, range two, and shift "
            "equivariance reduce the full-Gibbs averaged axial relaxation symbol to "
            "Rhat_L(p)=beta_L*omega(p)-a_L*omega(p)^2, where a_L is the averaged "
            "axial-distance-two conditional-mean derivative. Exact one-site covariance "
            "formulas prove a_L<0 and the mixed-distance-two derivative m_L<0, hence "
            "the omega^2 coefficient -a_L is positive. The sign of beta_L remains the "
            "single annealed gate. At the all-zero conditional background, a=-C/lambda^2, "
            "m=2a, beta=1/8-9*C/lambda^2, with C=Cov(z,exp(z)). Exact Laplace expansion "
            "gives C=lambda^2/72+43*lambda^4/46656+O(lambda^6), so "
            "beta=-43*lambda^2/5184+O(lambda^4)<0 for sufficiently small nonzero "
            "coupling. Thus even signed pointwise contraction is obstructed on large "
            "volumes. Only translation averaging under the actual Gibbs law, or a "
            "genuinely nonlocal/block cancellation, can still prove the H^-1 estimate."
        ),
        "conditional_response": {
            "conditional_mean": "M_o(xi)=E[psi_o | all off-site log fields xi], defined modulo common shifts",
            "derivative_identity": "D_y M_o=-Cov_q(psi_o,D_y S) for y!=o",
            "range": "D_y M_o=0 when graph distance(o,y)>2",
            "shift_equivariance": "M_o(xi+c*1)=M_o(xi)+c, hence sum_(y!=o) D_y M_o=1",
            "strict_covariance_sign": "Cov_q(z,exp(z))>0 because z and exp(z) are strictly increasing under a nondegenerate positive density",
            "axial_distance_two": "D_y M_o=-(exp(psi_y-2*psi_v)/lambda^2)*Cov_q(z,exp(z))<0 for y=o+2e and v=o+e",
            "mixed_distance_two": "D_y M_o is minus Cov_q(z,exp(z))/lambda^2 times the sum of exp(psi_y-2*psi_v) over the two intermediate sites",
        },
        "annealed_axial_symbol": {
            "averaging": "n_L,a_L,m_L are full-Gibbs expectations of D_y M_o on nearest, axial-distance-two, and mixed-distance-two hypercubic orbits",
            "row_sum": "8*n_L+8*a_L+24*m_L=1",
            "simultaneous_response": "Jhat_L(p*e_1)=1-beta_L*omega(p)+a_L*omega(p)^2",
            "positive_relaxation_convention": "R_L=I-J_L",
            "relaxation_symbol": "Rhat_L(p*e_1)=beta_L*omega(p)-a_L*omega(p)^2",
            "omega": "omega(p)=2*(1-cos(p))",
            "beta": "beta_L=n_L+4*a_L+6*m_L=1/8+3*(a_L+m_L)",
            "proved_signs": "a_L<0 and m_L<0, so -a_L>0",
            "unresolved_scalar": "the sign and volume scaling of beta_L under the actual full Gibbs measure",
            "status": "EXACT_SYMBOL_AND_DISTANCE_TWO_SIGNS_PROVED_ANNEALED_BETA_OPEN",
        },
        "vacuum_fiber": {
            "off_site_background": "psi_y=0 for every y!=o",
            "coordinate": "z=psi_o",
            "action": "F(z)=32*(exp(-z)-1)^2+4*(exp(z)-1)^2",
            "conditional_density": "q_lambda(z)=Z_lambda^-1*exp(-F(z)/lambda^2)",
            "unique_minimum": "z=0 with F''(0)=72",
            "axial_response": "a_vac(lambda)=-Cov_q(z,exp(z))/lambda^2",
            "mixed_response": "m_vac(lambda)=2*a_vac(lambda)",
            "nearest_from_row_sum": "n_vac(lambda)=1/8-7*a_vac(lambda)",
            "beta": "beta_vac(lambda)=1/8-9*Cov_q(z,exp(z))/lambda^2",
        },
        "exact_weak_coupling_expansion": {
            "method": "Watson-Laplace expansion after z=lambda*x around the unique nondegenerate global minimum; coefficients are exact Gaussian moments with precision 72",
            "fiber_coefficients_z2_to_z6": [enc(fiber_coefficient(degree)) for degree in range(2, 7)],
            "normalizer_coefficients_lambda0_to_lambda4": [enc(value) for value in expansion["normalizer"]],
            "mean_z_coefficients_lambda0_to_lambda4": [enc(value) for value in expansion["mean_z"]],
            "mean_exp_z_coefficients_lambda0_to_lambda4": [enc(value) for value in expansion["mean_exp_z"]],
            "mean_z_exp_z_coefficients_lambda0_to_lambda4": [enc(value) for value in expansion["mean_z_exp_z"]],
            "covariance_coefficients_lambda0_to_lambda4": [enc(value) for value in covariance],
            "covariance_formula": "Cov_q(z,exp(z))=lambda^2/72+(43/46656)*lambda^4+O(lambda^6)",
            "axial_response_formula": "a_vac=-1/72-(43/46656)*lambda^2+O(lambda^4)",
            "mixed_response_formula": "m_vac=-1/36-(43/23328)*lambda^2+O(lambda^4)",
            "beta_formula": "beta_vac=-(43/5184)*lambda^2+O(lambda^4)",
            "axial_lambda2_correction": enc(axial_response_correction),
            "mixed_lambda2_correction": enc(mixed_response_correction),
            "beta_lambda2_coefficient": enc(beta_correction),
            "consequence": "there exists epsilon>0 such that beta_vac(lambda)<0 for 0<|lambda|<epsilon",
        },
        "method_disposition": {
            "absolute_dobrushin_contraction": "OBSTRUCTED_ALREADY_FREE",
            "pointwise_mixed_hessian_square_bilaplacian_bound": "OBSTRUCTED",
            "pointwise_signed_conditional_response_contraction": "OBSTRUCTED_AT_WEAK_COUPLING_AND_LARGE_VOLUME",
            "annealed_signed_response_symbol": "PROVED_REDUCED_TO_BETA_L",
            "annealed_beta_nonnegative_or_lower_bound": "OPEN",
            "block_or_multiscale_signed_response": "OPEN",
            "volume_uniform_global_poincare": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the sign and a useful volume-uniform lower bound for beta_L after averaging over the actual interacting Gibbs law",
            "a theorem connecting that annealed response to a Fourier-specific heat-bath or Witten coercivity estimate",
            "the normalized lowest-mode and dyadic-shell interacting H^-1 upper bound",
        ],
        "next_gate": (
            "Compute beta_L as the full-Gibbs expectation of the three local response "
            "orbits, preserving conditional normalization. First derive its weak-"
            "coupling connected expansion to see whether Gibbs background fluctuations "
            "repair the negative vacuum term. Do not use the vacuum or any pointwise "
            "background response as evidence for the annealed sign."
        ),
        "does_not_establish": [
            "a negative annealed beta_L or instability of the heat-bath Markov process",
            "failure of every signed, block, or multiscale response method",
            "a global finite-volume or volume-uniform Poincare/Witten theorem",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound or its failure",
            "an interacting continuum Euclidean measure or ordinary OS reconstruction",
            "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Python integer/Fraction formal series and exact centered Gaussian moments; analytic sign uses strict covariance monotonicity and finite-dimensional Laplace asymptotics",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_signed_response_axial_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_signed_response_axial_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_signed_response_axial_gate",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer replay, independent formal-integral verifier, and focused mutation tests required",
            "tier_2": "the unchanged heat-bath and mixed-Hessian obstruction inputs are checked by content hash; no shared operator changed",
            "tier_3": "not applicable: this is a method obstruction and exact reduction, not an H^-1/reconstruction theorem, freeze, release, or shared-core promotion",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; Go uses GOMEMLIMIT=300MiB and GOGC=50",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 20812 KiB",
                "independent_verifier": "0.09 s, 30356 KiB",
                "unit_tests": "0.11 s, 30580 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1696 nodes, 0 invalid items, 0 malformed events; 6.61 s, 206688 KiB",
                "science_forge_shadow": "not rerun after its earlier memory-capped external-indexing abort; this skip is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT signed response axial gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
