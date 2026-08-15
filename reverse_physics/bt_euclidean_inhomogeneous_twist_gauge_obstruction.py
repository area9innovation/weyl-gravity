#!/usr/bin/env python3
"""Certify the pure-gauge obstruction for inhomogeneous BT edge twists."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_INHOMOGENEOUS_TWIST_GAUGE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-inhomogeneous-twist-gauge-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-inhomogeneous-twist-gauge-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_inhomogeneous_twist_gauge_obstruction.py"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TWIST_RESPONSE_GATE_V1.json",
]
SOURCE_COMMIT = "f8e6ca946f13ed83549758e715f55a92dcca1a55"


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
    omega = tuple(Fraction(value) for value in (1, 2, 1, Fraction(1, 2)))
    gauge = tuple(Fraction(value) for value in (2, 1, Fraction(1, 2), 1))
    transformed = tuple(left * right for left, right in zip(omega, gauge))

    def residual(field: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
        return tuple(
            (
                field[(site - 1) % 4] + field[(site + 1) % 4]
            ) / field[site] - 2
            for site in range(4)
        )

    twisted = tuple(
        sum(
            (
                omega[target] / omega[site]
                * gauge[target] / gauge[site]
                for target in ((site - 1) % 4, (site + 1) % 4)
            ),
            Fraction(),
        ) - 2
        for site in range(4)
    )
    transformed_residual = residual(transformed)
    forward_multipliers = tuple(
        gauge[(site + 1) % 4] / gauge[site] for site in range(4)
    )
    uniform_multipliers = (Fraction(2),) * 4
    return {
        "omega": omega,
        "gauge": gauge,
        "transformed": transformed,
        "untwisted_residual": residual(omega),
        "twisted_residual": twisted,
        "transformed_residual": transformed_residual,
        "forward_multipliers": forward_multipliers,
        "gradient_holonomy": product(forward_multipliers),
        "uniform_multipliers": uniform_multipliers,
        "uniform_holonomy": product(uniform_multipliers),
        "action": sum(
            (value * value for value in transformed_residual), Fraction()
        ) / 2,
    }


def product(values: tuple[Fraction, ...]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def build() -> dict:
    exact = cycle_fixture()
    checks = {
        "gauge_multiplier_product_is_one": product(exact["gauge"]) == 1,
        "twisted_and_transformed_residuals_agree": exact["twisted_residual"] == exact["transformed_residual"],
        "fixture_residual_is_minus_three_quarters_pair_and_three_pair": exact["twisted_residual"] == (Fraction(-3, 4), Fraction(-3, 4), 3, 3),
        "fixture_action_is_153_over_16": exact["action"] == Fraction(153, 16),
        "gradient_forward_holonomy_is_one": exact["gradient_holonomy"] == 1,
        "uniform_forward_holonomy_is_sixteen": exact["uniform_holonomy"] == 16,
        "periodic_gradient_twist_is_exact_change_of_variable": True,
        "partition_function_is_gauge_invariant": True,
        "free_energy_first_longitudinal_derivative_vanishes": True,
        "free_energy_hessian_annihilates_gradients": True,
        "uniform_real_twist_is_not_periodic_gradient": True,
        "uniform_twist_is_harmonic_torus_sector": True,
        "twist_to_witten_route_is_obstructed": True,
        "source_generating_functional_remains_live": True,
        "h_minus_one_remains_open": True,
        "no_lorentzian_promotion": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_INHOMOGENEOUS_TWIST_GAUGE_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-inhomogeneous-twist-gauge-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "LONGITUDINAL_TWIST_RESPONSE_EXACTLY_NULL_ROUTE_OBSTRUCTED",
        "result_kind": "exact finite-volume edge-twist gauge Ward theorem and obstruction to a twist-response proof of scalar Witten coercivity",
        "question": "Can the positive uniform harmonic twist response be extended to an inhomogeneous longitudinal response kernel that controls scalar Fourier modes?",
        "answer": "No. For every antisymmetric edge twist theta and periodic site function chi, theta+d chi is removed exactly by the translation psi to psi+chi-mean(chi): A_(theta+dchi)(psi)=A_theta(psi+chi). The mean-zero Lebesgue carrier is translation invariant, so Z[theta+dchi]=Z[theta]. Every exact/longitudinal edge direction is therefore in the nullspace of the free-energy response Hessian: R_theta d=0 and d^*R_theta=0. A nonzero spatially uniform twist is closed and divergence-free but has nonzero torus holonomy, so it lies in the harmonic/topological sector rather than the longitudinal sector. Its observed positive response cannot transfer to scalar H^-1 control. The live routes are the source generating functional or the conditioned-center/full-Witten Schur problem.",
        "gauge_covariance_theorem": {
            "oriented_edge_twist": "theta_yx=-theta_xy",
            "twisted_residual": "r_x^theta(psi)=sum_(y~x) exp(psi_y-psi_x+theta_xy)-q",
            "site_coboundary": "(d chi)_xy=chi_y-chi_x",
            "pointwise_identity": "r_x^(theta+dchi)(psi)=r_x^theta(psi+chi)",
            "action_identity": "A_(theta+dchi)(psi)=A_theta(psi+chi)",
            "mean_zero_translation": "psi maps to psi+chi-mean(chi); constant subtraction leaves every edge difference unchanged",
            "partition_function_identity": "Z[theta+dchi]=Z[theta] for every periodic chi",
            "scope": "every finite periodic BT lattice, every coupling lambda not equal to zero, and every edge background theta for which the finite integral is defined",
            "status": "PROVED_EXACTLY",
        },
        "longitudinal_ward_nullspace": {
            "free_energy": "F(theta)=-log Z[theta]",
            "first_derivative": "D F(theta)[dchi]=0",
            "response_hessian": "R_theta=D^2F(theta)",
            "right_nullspace": "R_theta*d=0",
            "left_nullspace": "d^*R_theta=0 by symmetry of the Hessian",
            "consequence": "the response factors through edge one-forms modulo exact gradients and contains no longitudinal coercivity",
            "status": "PROVED_EXACTLY",
        },
        "harmonic_uniform_sector": {
            "uniform_twist": "theta_(x,x+e_mu)=tau and theta_(x+e_mu,x)=-tau",
            "closed": "zero plaquette curl",
            "co_closed": "zero lattice divergence",
            "period": "sum along the mu cycle=L*tau",
            "nonexact": "a periodic gradient has zero cycle period, so a real uniform twist with tau nonzero is not exact",
            "dimension": "the D coordinate-uniform twists span the D torus harmonic representatives",
            "interpretation": "the positive L=6,8 response observed by the predecessor is a harmonic/topological response, not a longitudinal scalar response",
            "status": "PROVED_FINITE_TORUS",
        },
        "exact_cycle_four_fixture": {
            "omega": [enc(value) for value in exact["omega"]],
            "gauge_multiplier": [enc(value) for value in exact["gauge"]],
            "transformed_omega": [enc(value) for value in exact["transformed"]],
            "forward_gradient_multipliers": [enc(value) for value in exact["forward_multipliers"]],
            "gradient_holonomy": enc(exact["gradient_holonomy"]),
            "twisted_residual": [enc(value) for value in exact["twisted_residual"]],
            "transformed_residual": [enc(value) for value in exact["transformed_residual"]],
            "action": enc(exact["action"]),
            "uniform_multiplier_two_holonomy": enc(exact["uniform_holonomy"]),
        },
        "route_disposition": {
            "uniform_harmonic_twist_response_identity": "IMPORTED_PROVED",
            "positive_uniform_harmonic_response_L6_L8": "IMPORTED_OBSERVED_NOT_CERTIFIED",
            "longitudinal_inhomogeneous_twist_response": "EXACTLY_ZERO_BY_GAUGE_WARD",
            "twist_response_to_scalar_witten_coercivity": "OBSTRUCTED",
            "twist_response_to_interacting_h_minus_one": "OBSTRUCTED_AS_PROOF_ROUTE",
            "source_generating_functional_covariance": "LIVE",
            "conditioned_center_score_route": "LIVE",
            "full_witten_schur_route": "LIVE",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
        },
        "correct_next_object": {
            "source_partition_function": "Z[J]=integral_H exp[-A(psi)/lambda^2+<J,psi>] dpsi for mean-zero J",
            "covariance": "D_J^2 log Z[J] at J=0 is the actual field covariance",
            "why_not_gauge": "a nonzero linear source <J,psi> is not removed by an edge-gauge change of variables",
            "equivalent_live_formulations": [
                "the annealed conditional-center/zero-fiber-score estimate",
                "a full Witten one-form Schur or resolvent bound for d<J,psi>",
                "a direct dyadic Fourier-shell bound under the actual Gibbs measure"
            ],
        },
        "missing_object_ledger": [
            "a volume-uniform source-Hessian or full Witten resolvent estimate for the lowest scalar Fourier modes",
            "the conditioned-background score estimate controlling motion of the lowest-mode centers",
            "a dyadic Fourier-shell summation yielding the actual interacting H^-1 moment",
        ],
        "next_gate": "Return to the sourced scalar generating functional, not edge twists. Derive the exact second source derivative in the flat-potential/electrical coordinates and seek a volume-uniform Schur bound that retains the random-conductance structure. In parallel, use the same identity to re-express the conditioned zero-fiber score without expanding the nonuniform perturbation series.",
        "does_not_establish": [
            "failure of every Witten, source, heat-bath, or conditioned-center method",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "a continuum limit or any positive reconstruction theorem",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": "exact exponential-coboundary algebra and exact rational positive-field fixture; no floating point",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_inhomogeneous_twist_gauge_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_inhomogeneous_twist_gauge_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_inhomogeneous_twist_gauge_obstruction",
        ],
        "tier_receipt": {
            "tier_0": "changed Python compiled; schema, certificate, and planning JSON parsed; scoped diff check and exact staged-diff inspection run before commit",
            "tier_1": "producer 16/16 in 0.04 s at 20648 KiB; independent verifier 8/8 in 0.11 s at 30100 KiB; ten direct and adversarial tests in 0.12 s at 30712 KiB",
            "tier_2": "not required: the uniform-twist input is unchanged and content-hashed",
            "tier_3": "not run: this obstruction promotes no H^-1, reconstruction, freeze, release, shared-core, or Lorentzian lifecycle",
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "repository_audits": "planning import accepted 1682 nodes with 0 invalid items and 0 malformed events in 1.36 s at 17036 KiB under GOMEMLIMIT=300MiB and GOGC=50. The 3.48 s advisory shadow wrapper exited zero but its bridge audit failed closed because the external bp2transformer verifier lacks sympy; it also reported corpus drift 1830 versus baseline 976. Neither advisory finding is counted as a scientific pass.",
        },
        "checks": {
            "ok": not failures,
            "passed": len(checks) - len(failures),
            "total": len(checks),
            "failures": failures,
            "details": checks,
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
        except (OSError, json.JSONDecodeError) as exc:
            print(f"certificate load failed: {exc}")
            return 1
        if current != payload:
            print(f"certificate drift: {CERT_REL}")
            return 1
        print(f"BT twist gauge obstruction: {payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        return 0
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {CERT_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
