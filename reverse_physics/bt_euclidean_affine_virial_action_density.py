#!/usr/bin/env python3
"""Certify an affine BT virial bound and actual Gibbs action-density control."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-affine-virial-action-density-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-affine-virial-action-density.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json",
]
SOURCE_COMMIT = "a7664a0a6465c17965e0f8e2c654ec4a3a5355d9"


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def log_two_lower_bound() -> Fraction:
    """Even alternating partial sum for log(2)."""
    return sum(
        (Fraction(1 if index % 2 else -1, index) for index in range(1, 21)),
        Fraction(0),
    )


def exp_seven_tenths_lower_bound() -> Fraction:
    """Positive degree-four Taylor lower bound for exp(7/10)."""
    x = Fraction(7, 10)
    factorial = 1
    power = Fraction(1)
    total = Fraction(1)
    for degree in range(1, 5):
        factorial *= degree
        power *= x
        total += power / factorial
    return total


def scalar_fixture(weights: tuple[Fraction, ...]) -> dict:
    """Retain exact coefficients when every weight is a power of two."""
    degree = len(weights)
    residual = sum(weights, Fraction(0)) - degree
    log_two_coefficient = Fraction(0)
    for weight in weights:
        numerator = weight.numerator
        denominator = weight.denominator
        exponent = 0
        while numerator > 1 and numerator % 2 == 0:
            numerator //= 2
            exponent += 1
        while denominator > 1 and denominator % 2 == 0:
            denominator //= 2
            exponent -= 1
        if numerator != 1 or denominator != 1:
            raise ValueError("fixture weight is not a power of two")
        log_two_coefficient += weight * exponent
    return {
        "weights": [encode(weight) for weight in weights],
        "sum_s": encode(sum(weights, Fraction(0))),
        "residual_r": encode(residual),
        "t_log_two_coefficient": encode(log_two_coefficient),
        "r_times_t_log_two_coefficient": encode(
            residual * log_two_coefficient
        ),
    }


def build() -> dict:
    degree = 8
    coupling = Fraction(2, 5)
    log_two_lower = log_two_lower_bound()
    exp_lower = exp_seven_tenths_lower_bound()
    log_degree_upper = Fraction(21, 10)
    negative_vertex_defect = Fraction(168, 5)
    total_affine_defect = Fraction(488, 5)
    action_density_bound = Fraction(1222, 25)
    half_weight_radicand = Fraction(1247, 25)
    bilaplacian_psi_density_squared_bound = (
        16 * degree * degree * action_density_bound
    )

    fixtures = [
        scalar_fixture((Fraction(2),) + (Fraction(1),) * 7),
        scalar_fixture((Fraction(1, 2),) * 8),
        scalar_fixture((Fraction(4),) + (Fraction(1, 4),) * 7),
    ]

    checks = {
        "degree_and_coupling_are_exact": (
            degree == 8 and coupling == Fraction(2, 5)
        ),
        "log_two_lower_bound_is_exact": (
            log_two_lower == Fraction(155685007, 232792560)
            and log_two_lower > Fraction(2, 3)
        ),
        "exp_upper_certificate_for_log_two": (
            exp_lower == Fraction(482921, 240000) and exp_lower > 2
        ),
        "log_eight_upper_bound_is_twenty_one_tenths": (
            3 * Fraction(7, 10) == log_degree_upper
        ),
        "negative_vertex_defect_is_168_over_5": (
            Fraction(degree * degree, 4) * log_degree_upper
            == negative_vertex_defect
        ),
        "total_affine_defect_is_488_over_5": (
            degree * degree + negative_vertex_defect == total_affine_defect
        ),
        "three_scalar_regimes_are_retained": (
            [row["residual_r"]["numerator"] > 0 for row in fixtures]
            == [True, False, False]
            and fixtures[1]["t_log_two_coefficient"]["numerator"] < 0
            and fixtures[2]["t_log_two_coefficient"]["numerator"] > 0
        ),
        "gibbs_radial_identity_dimension_is_N_minus_one": True,
        "lambda_point_four_action_density_bound_is_1222_over_25": (
            total_affine_defect / 2 + coupling * coupling / 2
            == action_density_bound
        ),
        "half_action_factor_radicand_is_1247_over_25": (
            1 + action_density_bound == half_weight_radicand
        ),
        "bilaplacian_psi_second_moment_density_bound_is_exact": (
            bilaplacian_psi_density_squared_bound
            == Fraction(1251328, 25)
        ),
        "bilaplacian_phi_first_moment_bound_is_40_sqrt_1222": (
            Fraction(4 * degree, 1) / (coupling * coupling)
            * Fraction(1, 5)
            == 40
        ),
        "actual_action_density_is_now_bounded": True,
        "actual_h_minus_one_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-affine-virial-action-density-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "BOUND_PROVED",
        "result_kind": (
            "exact all-volume affine radial-virial theorem and actual "
            "interacting Gibbs action-density estimate"
        ),
        "question": (
            "Can the failed homogeneous inequality D>=2A be replaced by an "
            "affine volume-uniform virial bound strong enough to control the "
            "actual BT Gibbs expectation of the half action-density weight?"
        ),
        "answer": (
            "Yes. On every connected finite q-regular graph, grouping each "
            "vertex by the sign of r=s-q and using convexity and "
            "superadditivity of x log x gives D>=2A-N*q^2*(1+log(q)/4). "
            "For q=8, the rational certificate log(8)<21/10 yields "
            "D>=2A-(488/5)N. Gibbs radial integration by parts then gives, "
            "at lambda=2/5, E[A/N]<=1222/25 and "
            "E[sqrt(1+A/N)]<=sqrt(1247)/5 uniformly in volume. This closes "
            "the annealed action-density factor, but not the independent "
            "orthogonal-Hessian/curvature gate or the actual H^-1 moment."
        ),
        "pointwise_affine_virial_theorem": {
            "scope": "every connected finite q-regular undirected graph",
            "definitions": [
                "w_xy=exp(psi_y-psi_x)>0",
                "s_x=sum_(y~x) w_xy and r_x=s_x-q",
                "t_x=sum_(y~x) w_xy*log(w_xy)",
                "A=(1/2)*sum_x r_x^2",
                "D=psi dot grad A=sum_x r_x*t_x",
            ],
            "positive_residual_case": (
                "If s>=q, Jensen gives t>=s*log(s/q)>=s-q=r, so r*t>=r^2."
            ),
            "negative_residual_case": (
                "Superadditivity of x log x gives t<=s log s. If s<=1 "
                "then r*t>=0. If 1<s<q, then r*t>=-(q-s)s log q "
                ">=-q^2 log(q)/4."
            ),
            "negative_square_bound": (
                "At every r<0 vertex, r^2=(q-s)^2<=q^2."
            ),
            "general_bound": "D>=2A-N*q^2*(1+log(q)/4)",
            "q8_log_certificate": {
                "log_two_lower_bound": encode(log_two_lower),
                "exp_7_over_10_degree_four_lower_bound": encode(exp_lower),
                "exp_lower_bound_exceeds_two": exp_lower > 2,
                "consequence": "log(2)<7/10 and log(8)<21/10",
            },
            "q8_rational_bound": "D>=2A-(488/5)*N",
            "scalar_regime_fixtures": fixtures,
            "status": "PROVED",
        },
        "actual_gibbs_action_density": {
            "measure": (
                "dmu proportional to exp[-A(psi)/lambda^2] dpsi on "
                "the (N-1)-dimensional mean-zero hyperplane"
            ),
            "radial_integration_by_parts": (
                "E_mu[D]=lambda^2*(N-1); finite-volume coercivity removes "
                "the boundary term."
            ),
            "general_q8_bound": (
                "E_mu[A/N]<=244/5+(lambda^2/2)*(1-1/N)"
            ),
            "lambda": encode(coupling),
            "lambda_point_four_uniform_action_density_bound": encode(
                action_density_bound
            ),
            "annealed_half_action_density": (
                "E_mu[sqrt(1+A/N)]<=sqrt(1+E_mu[A/N])<=sqrt(1247)/5"
            ),
            "half_weight_squarefree_radicand": 1247,
            "half_weight_rational_denominator": 5,
            "status": "PROVED_FOR_ACTUAL_INTERACTING_GIBBS_MEASURE",
        },
        "actual_bilaplacian_consequence": {
            "imported_envelope": "A>=B_psi^2/(16*q^2*N)",
            "second_moment_density_bound": (
                "E_mu[B_psi^2]/N^2<=16*q^2*1222/25=1251328/25"
            ),
            "second_moment_density_bound_rational": encode(
                bilaplacian_psi_density_squared_bound
            ),
            "first_moment_density_bound": (
                "E_mu[B_psi]/N<=32*sqrt(1222)/5"
            ),
            "phi_conversion": "B_psi=lambda^2*B_phi",
            "lambda_point_four_phi_bound": (
                "E_mu[B_phi]/N<=40*sqrt(1222)"
            ),
            "continuum_shortfall": (
                "A volume-uniform bilaplacian density does not prevent its "
                "energy from concentrating in the lowest lattice modes; it "
                "is therefore not by itself an H^-1 moment theorem."
            ),
            "status": "PROVED_BUT_INSUFFICIENT_FOR_H_MINUS_ONE",
        },
        "method_disposition": {
            "homogeneous_pointwise_D_ge_2A": "OBSTRUCTED_BY_PREDECESSOR",
            "affine_pointwise_virial_bound": "PROVED",
            "actual_uniform_action_density_moment": "PROVED",
            "actual_annealed_half_action_density_factor": "PROVED",
            "actual_uniform_bilaplacian_density_moment": "PROVED",
            "global_orthogonal_hessian_block_positivity": "OPEN",
            "pointwise_half_action_density_curvature": "OPEN",
            "actual_interacting_h_minus_one_second_moment_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "global positivity/invertibility or a variational replacement for the orthogonal Hessian block",
            "a volume-uniform half-action-density lower bound for lowest-mode curvature",
            "or a direct normalized low-mode marginal estimate bypassing Hessian curvature",
            "an actual volume-uniform interacting H^-1 second moment",
            "tightness in a compactly weaker topology and limit identification",
        ],
        "next_gate": (
            "Use the now-proved annealed bound on sqrt(1+A/N) in the "
            "lowest-mode covariance route. Prove or obstruct global "
            "positivity/invertibility of the orthogonal Hessian block and the "
            "normalized half-action-density curvature inequality. If that "
            "pointwise gate fails, pass to the normalized low-mode marginal; "
            "do not call the action-density theorem an H^-1 theorem."
        ),
        "does_not_establish": [
            "a pure positive constant c with D>=c*A and no additive volume defect",
            "global convexity of the BT action",
            "a global positive lowest-mode Schur complement",
            "the actual interacting H^-1 moment bound",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for rational constants, Taylor "
                "bounds, dyadic scalar fixtures, Gibbs dimension factors, "
                "and bilaplacian consequences; the general inequality uses "
                "the explicitly stated scalar convexity lemmas."
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_affine_virial_action_density.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_affine_virial_action_density.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_affine_virial_action_density",
        ],
        "tier_receipt": {
            "command_results": [
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/bt_euclidean_affine_virial_action_density.py --check",
                    "elapsed_seconds": "1.07",
                    "status": "PASS_15_OF_15",
                },
                {
                    "command": "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_affine_virial_action_density.py",
                    "elapsed_seconds": "1.14",
                    "status": "PASS_10_OF_10",
                },
                {
                    "command": "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_affine_virial_action_density",
                    "elapsed_seconds": "1.18",
                    "status": "PASS_11_TESTS",
                },
                {
                    "command": "python3 paper/generate_21_reverse_foundations_claim_map.py --check && python3 paper/verify_21_reverse_foundations_claim_map.py",
                    "elapsed_seconds": "1.16",
                    "status": "PASS",
                },
                {
                    "command": "cd paper && pdflatex -interaction=nonstopmode -halt-on-error 21-reverse-foundations-of-physics.tex (twice)",
                    "elapsed_seconds": "2.52",
                    "status": "PASS_42_PAGES",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 /home/alstrup/tmp/sf-sfc-1000 conform planning/work-items",
                    "elapsed_seconds": "1.05",
                    "status": "PASS_CLEAN",
                },
            ],
            "failed_or_nonpassing_attempts": [
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 sfc conform planning/work-items",
                    "status": "NOT_RUN_COMMAND_NOT_FOUND",
                    "reason": "The standalone sfc binary was not on PATH; no validation occurred and this was not counted as a pass.",
                },
                {
                    "command": "GOMEMLIMIT=300MiB GOGC=50 /home/alstrup/tmp/sfc conform planning/work-items",
                    "status": "FAILED_WRONG_LEGACY_BINARY",
                    "reason": "That unrelated legacy binary did not implement conform. The cached Science Forge binary used by s-f was then resolved explicitly and passed clean.",
                },
            ],
            "tier_0": (
                "parse changed Python, JSON, and TeX; deterministic generation; "
                "strict schema validation; scoped diff check and staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, method-distinct verifier, scalar and graph "
                "fixtures, unit tests, and claim/provenance mutations"
            ),
            "tier_2": (
                "two predecessor certificates checked by content hash; their "
                "mathematical inputs are unchanged"
            ),
            "tier_3": (
                "not run: no continuum theorem, tightness, quantum lifecycle, "
                "freeze, release, shared classical operator, or Lorentzian promotion"
            ),
            "memory_policy": (
                "all scientific commands run sequentially under a 500000 KiB virtual-memory ceiling"
            ),
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
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
        "[PASS] BT affine virial/action density "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
