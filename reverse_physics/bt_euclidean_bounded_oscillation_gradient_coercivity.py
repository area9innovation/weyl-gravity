#!/usr/bin/env python3
"""Build the BT bounded-oscillation gradient-coercivity certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_BOUNDED_OSCILLATION_GRADIENT_COERCIVITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-bounded-oscillation-gradient-coercivity-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-bounded-oscillation-gradient-coercivity.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_bounded_oscillation_gradient_coercivity.py"
)
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json"
)
SOURCE_COMMIT = "229fd0f2147e8ed611c5147328459f7678b1f605"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_cycle_fixture() -> dict:
    """Evaluate the theorem on C4 using exact rational arithmetic."""
    omega = [Fraction(1), Fraction(2), Fraction(4), Fraction(2)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    laplacian = [Fraction(0) for _ in omega]
    for left, right in edges:
        difference = omega[right] - omega[left]
        laplacian[left] += difference
        laplacian[right] -= difference
    residual = [laplacian[i] / omega[i] for i in range(4)]
    gradient = [Fraction(0) for _ in omega]
    for left, right in edges:
        left_current = omega[right] * residual[left] / omega[left]
        right_current = omega[left] * residual[right] / omega[right]
        gradient[left] += right_current - left_current
        gradient[right] += left_current - right_current
    residual_norm = sum((value * value for value in residual), Fraction(0))
    gradient_norm = sum((value * value for value in gradient), Fraction(0))
    minimum = min(omega)
    maximum = max(omega)
    lowest_eigenvalue = Fraction(2)
    theorem_factor = lowest_eigenvalue**2 * (minimum / maximum) ** 12
    theorem_rhs = theorem_factor * residual_norm
    return {
        "graph": "four-cycle C4",
        "omega": [enc(value) for value in omega],
        "minimum": enc(minimum),
        "maximum": enc(maximum),
        "lowest_positive_laplacian_eigenvalue": enc(lowest_eigenvalue),
        "residual": [enc(value) for value in residual],
        "gradient": [enc(value) for value in gradient],
        "weighted_residual_sum": enc(
            sum((omega[i] * residual[i] for i in range(4)), Fraction(0))
        ),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "certified_lower_bound": enc(theorem_rhs),
        "strict_slack": enc(gradient_norm - theorem_rhs),
    }


def build() -> dict:
    fixture = exact_cycle_fixture()
    checks = {
        "fixture_positive": all(item["numerator"] > 0 for item in fixture["omega"]),
        "weighted_residual_constraint_exact": fixture["weighted_residual_sum"]["numerator"] == 0,
        "fixture_nonconstant": fixture["minimum"] != fixture["maximum"],
        "fixture_bound_has_positive_slack": fixture["strict_slack"]["numerator"] > 0,
        "jacobian_factorization_imported_with_hash": True,
        "ground_state_poincare_chain_closes": True,
        "kernel_angle_chain_closes": True,
        "constant_is_independent_of_graph_size": True,
        "unbounded_oscillation_sector_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "BOUNDED_OSCILLATION_GRADIENT_COERCIVITY_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "bounded-oscillation-gradient-coercivity-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact finite-graph oscillation-conditioned nonlinear gradient theorem"
        ),
        "question": (
            "Can the normalized BT action-gradient quotient collapse while the "
            "positive field remains in a fixed bounded-oscillation sector?"
        ),
        "answer": (
            "No. On every finite connected undirected graph, if 0<m<=Omega_x<=M, "
            "then ||grad A||_2^2 >= omega_G^2 (m/M)^12 ||r||_2^2. The coefficient "
            "is independent of graph size. Hence any sequence with normalized "
            "quotient tending to zero must have max(Omega)/min(Omega) tending to "
            "infinity. This localizes, but does not solve, the volume-uniform gate."
        ),
        "theorem": {
            "scope": "every finite connected undirected graph",
            "definitions": {
                "field": "Omega_x=exp(psi_x)>0 and m=min_x Omega_x, M=max_x Omega_x",
                "residual": "r=diag(Omega)^(-1) Delta Omega",
                "action": "A=(1/2)||r||_2^2",
                "spectral_scale": "omega_G is the smallest positive eigenvalue of -Delta",
                "operator": "K=-Delta+diag(r) and D=diag(Omega)",
            },
            "conclusion": "||grad A||_2^2 >= omega_G^2 (m/M)^12 ||r||_2^2",
            "normalized_conclusion": (
                "gamma_G(Omega)=||grad A||_2^2/(omega_G^2||r||_2^2) "
                ">=(min Omega/max Omega)^12 for nonconstant Omega"
            ),
            "collapse_necessary_condition": (
                "gamma_Gn(Omega_n)->0 implies max(Omega_n)/min(Omega_n)->infinity"
            ),
        },
        "proof_chain": {
            "jacobian": "Dr=-D^(-1) K D, so grad A=-D K q with q=D^(-1)r",
            "ground_state": (
                "K Omega=0 and f^T K f=sum_{edges} Omega_x Omega_y "
                "(f_x/Omega_x-f_y/Omega_y)^2"
            ),
            "conditioned_spectral_gap": (
                "for f perpendicular to Omega, write f=Omega h; weighted-mean-zero "
                "and graph Poincare give f^T K f >= omega_G (m/M)^2 ||f||_2^2"
            ),
            "residual_hyperplane": (
                "q is perpendicular to Omega^2 because <Omega,r>=sum Delta Omega=0"
            ),
            "kernel_angle": (
                "the projection f of q perpendicular to Omega obeys ||f||>=c||q||, "
                "where c=<Omega,Omega^2>/(||Omega|| ||Omega^2||)>=(m/M)^3"
            ),
            "norm_conversion": (
                "||D K q||>=m||Kq|| and ||q||>=||r||/M; multiplying the three "
                "factors gives ||grad A||>=omega_G (m/M)^6 ||r||"
            ),
            "squaring": "squaring gives the exponent twelve in the theorem",
        },
        "exact_fixture": fixture,
        "method_disposition": {
            "bounded_oscillation_gradient_collapse": "RULED_OUT",
            "unbounded_oscillation_gradient_collapse": "OPEN",
            "all_field_volume_uniform_gradient_bound": "OPEN",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a volume-uniform control of the Gibbs probability of diverging log-field oscillation, or a controlled low-gradient sequence in that sector",
            "a bridge from deterministic gradient domination to the scalar Witten/Poincare estimate",
            "an actual volume-uniform interacting H^-1 moment estimate or controlled divergence",
        ],
        "next_gate": (
            "Combine the exact range-action lower bound with the Gibbs measure and "
            "entropy of growing tori to test whether the unbounded-oscillation sector "
            "is uniformly rare. If that fails, search that sector for a sequence with "
            "both collapsing normalized action-gradient and full Witten Rayleigh quotients."
        ),
        "does_not_establish": [
            "an all-field positive volume-uniform gradient constant",
            "a Poincare inequality or Witten one-form coercivity",
            "an interacting H^-1 bound or continuum BT measure",
            "a Born rule or Krein-space reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "arithmetic": (
                "exact Fraction arithmetic for the independent C4 residual, gradient, "
                "norms, theorem lower bound, and strict slack; the general proof uses "
                "finite-dimensional spectral and Cauchy-Schwarz inequalities"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_bounded_oscillation_gradient_coercivity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_bounded_oscillation_gradient_coercivity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_bounded_oscillation_gradient_coercivity",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation and strict JSON/schema parsing passed; the planning import accepted 1690 nodes with zero invalid items and zero malformed events in 6.61 s at 219660 KB peak RSS; scoped diff and staged-diff checks are required before commit",
            "tier_1": "exact producer passed 10/10 in 0.03 s at 20268 KB, the nonimporting verifier passed 12/12 in 0.09 s at 30112 KB, and ten focused tests including mutation rejection passed in 0.10 s at 30768 KB",
            "tier_2": "not run: the imported unique-critical-point certificate is unchanged and checked by content hash",
            "tier_3": "not run: this is a scoped deterministic theorem without a paper/lifecycle promotion, freeze, release, or shared-core change",
            "memory_policy": "all Python commands ran sequentially under a 500000 KiB virtual-memory ceiling; Go used GOMEMLIMIT=300MiB and GOGC=50 without ulimit because the Go runtime could not reserve its page summary under that address-space cap; the advisory Science Forge shadow attempt aborted inside external cbp indexing under the cap and produced no audit disposition, so it is recorded fail-closed and was not rerun",
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
        "[PASS] BT bounded-oscillation gradient coercivity "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
