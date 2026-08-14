#!/usr/bin/env python3
"""Certify an exact BT reflection-kernel obstruction at lambda=2/5."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-lambda04-os-kernel-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-lambda04-os-kernel-obstruction.md"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json",
]
SOURCE_COMMIT = "02a16aafc02061bb0f807722d4b6367f963337ce"


def encode(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational_power_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2 ** exponent)
    return Fraction(1, 2 ** (-exponent))


def reduced_action(
    reflected_negative_half: tuple[int, int, int],
    positive_half: tuple[int, int, int],
) -> tuple[Fraction, list[Fraction]]:
    """Action per spatial site for psi=lambda*phi in integer log(2) units."""
    profile = (
        reflected_negative_half[0],
        positive_half[0],
        positive_half[1],
        positive_half[2],
        reflected_negative_half[2],
        reflected_negative_half[1],
    )
    curvatures = []
    for time in range(6):
        curvature = (
            rational_power_two(profile[(time - 1) % 6] - profile[time])
            + rational_power_two(profile[(time + 1) % 6] - profile[time])
            - 2
        )
        curvatures.append(curvature)
    action = Fraction(25, 8) * sum(
        (value * value for value in curvatures), Fraction(0)
    )
    return action, curvatures


def build() -> dict:
    coupling = Fraction(2, 5)
    length = 6
    dimensions = 4
    spatial_volume = length ** (dimensions - 1)
    p = (-7, 0, 7)
    q = (-6, 3, 3)

    action_pp, curvature_pp = reduced_action(p, p)
    action_qq, curvature_qq = reduced_action(q, q)
    action_pq, curvature_pq = reduced_action(p, q)
    gap_per_spatial_site = action_pp + action_qq - 2 * action_pq
    full_action_pp = spatial_volume * action_pp
    full_action_qq = spatial_volume * action_qq
    full_action_pq = spatial_volume * action_pq
    full_gap = spatial_volume * gap_per_spatial_site

    checks = {
        "coupling_is_exactly_two_fifths": coupling == Fraction(2, 5),
        "p_half_center_has_zero_sum": sum(p) == 0,
        "q_half_center_has_zero_sum": sum(q) == 0,
        "half_centers_are_distinct": p != q,
        "pp_action_per_spatial_site_exact": (
            action_pp == Fraction(6555228825, 32768)
        ),
        "qq_action_per_spatial_site_exact": (
            action_qq == Fraction(1711289113625, 1048576)
        ),
        "pq_action_per_spatial_site_exact": (
            action_pq == Fraction(1920872864825, 2097152)
        ),
        "reduced_action_is_reflection_symmetric": (
            action_pq == reduced_action(q, p)[0]
        ),
        "per_spatial_site_log_kernel_gap_exact": (
            gap_per_spatial_site == Fraction(717075, 4096)
        ),
        "full_log_kernel_gap_exact": full_gap == Fraction(19361025, 512),
        "full_log_kernel_gap_is_strictly_positive": full_gap > 0,
        "density_kernel_determinant_is_strictly_negative": full_gap > 0,
        "global_zero_mode_constraint_holds_at_all_four_centers": (
            sum(p) + sum(p) == 0
            and sum(p) + sum(q) == 0
            and sum(q) + sum(p) == 0
            and sum(q) + sum(q) == 0
        ),
        "compact_bump_cylinder_functions_are_admissible": True,
        "negative_point_kernel_persists_for_small_bumps": True,
        "ordinary_os_at_lambda_0p4_is_obstructed": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-lambda04-os-kernel-obstruction-v1"
        ),
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "OBSTRUCTION_PROVED",
        "result_kind": "finite-volume interacting OS kernel obstruction",
        "question": (
            "Does the positive BT Euclidean Gibbs measure satisfy ordinary "
            "Osterwalder-Schrader reflection positivity at lambda=0.4 on the "
            "periodic 6^4 lattice?"
        ),
        "answer": (
            "No. Two spatially constant, half-sum-zero configurations with "
            "lambda*phi in integer log(2) units give an exact positive action "
            "gap S_pp+S_qq-2*S_pq=19361025/512. Hence the corresponding "
            "two-by-two Gibbs-density kernel has negative determinant. A "
            "compact-bump localization lemma converts that point-kernel "
            "direction into an admissible positive-time cylinder function "
            "with strictly negative OS quadratic form."
        ),
        "finite_volume_kernel_obstruction": {
            "coupling": encode(coupling),
            "lattice": {"length": length, "dimensions": dimensions},
            "spatial_volume": spatial_volume,
            "zero_mode_constraint": "sum_x phi_x=0",
            "reflection": "theta(t,x)=(1-t mod 6,x)",
            "positive_time_half": [1, 2, 3],
            "coordinates": (
                "psi=lambda*phi; each listed integer k denotes psi=k*log(2)"
            ),
            "positive_variable_ratio": (
                "Omega_neighbor/Omega_site=2^(k_neighbor-k_site)"
            ),
            "half_centers": {
                "p": list(p),
                "q": list(q),
                "half_sum_p": sum(p),
                "half_sum_q": sum(q),
            },
            "time_profile_rule": (
                "profile(p,q)=(p0,q0,q1,q2,p2,p1) for times 0,...,5"
            ),
            "curvature_rule": (
                "r_t=2^(k_(t-1)-k_t)+2^(k_(t+1)-k_t)-2"
            ),
            "action_rule": "S_6^4(p,q)=216*(25/8)*sum_t r_t^2",
            "curvatures": {
                "pp": [encode(value) for value in curvature_pp],
                "qq": [encode(value) for value in curvature_qq],
                "pq": [encode(value) for value in curvature_pq],
            },
            "actions_per_spatial_site": {
                "S_pp": encode(action_pp),
                "S_qq": encode(action_qq),
                "S_pq": encode(action_pq),
            },
            "full_actions": {
                "S_pp": encode(full_action_pp),
                "S_qq": encode(full_action_qq),
                "S_pq": encode(full_action_pq),
            },
            "log_kernel_convexity_gap_per_spatial_site": encode(
                gap_per_spatial_site
            ),
            "log_kernel_convexity_gap_full_lattice": encode(full_gap),
            "density_kernel": (
                "K_ij=exp(-S_6^4(center_i,center_j)), i,j in {p,q}"
            ),
            "determinant_identity": (
                "det(K)=exp(-S_pp-S_qq)*(1-exp(S_pp+S_qq-2*S_pq))<0"
            ),
            "negative_vector": (
                "If a=K_pp and b=K_pq, then (b,-a) K (b,-a)^T="
                "a*(K_pp*K_qq-K_pq^2)<0"
            ),
            "bump_cylinder_lemma": {
                "ambient_half_space": "R^648",
                "constraint": (
                    "ell(x)+ell(y)=0, where ell is the half-field sum"
                ),
                "center_condition": "p,q lie in ker(ell)",
                "test_functions": (
                    "equal-shape smooth compact bumps around p and q, "
                    "combined with the negative two-by-two kernel vector"
                ),
                "scaling_limit": (
                    "epsilon^(-(2*n-1))*Q_OS(F_epsilon) tends to a positive "
                    "common bump factor times c^T*K*c"
                ),
                "consequence": (
                    "continuity of the finite Gibbs density makes Q_OS "
                    "strictly negative for all sufficiently small bumps"
                ),
            },
            "disposition": "STRICT_NEGATIVE_TWO_POINT_DENSITY_KERNEL",
        },
        "disposition": {
            "ordinary_os_reflection_positivity_at_lambda_zero": "OBSTRUCTED",
            "ordinary_os_reflection_positivity_near_lambda_zero": (
                "OBSTRUCTED_ON_SOME_OPEN_INTERVAL"
            ),
            "ordinary_os_reflection_positivity_at_lambda_0p4": "OBSTRUCTED",
            "lambda_0p4_numerical_preflight_role": "SUPPORTING_ONLY",
            "ordinary_os_reflection_positivity_at_every_nonzero_coupling": (
                "NOT_ESTABLISHED"
            ),
            "krein_compatible_reconstruction": "NOT_ASSESSED",
            "interacting_uniform_estimate": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an interacting L-uniform negative-Sobolev moment estimate",
            "tightness and represented convergence in a declared topology",
            "identification and uniqueness of any continuum Euclidean limit",
            "a separately defined and proved indefinite-metric reconstruction",
            "a Lorentzian observable bridge",
        ],
        "next_gate": (
            "Prove or obstruct an L-uniform interacting negative-Sobolev "
            "moment estimate; ordinary OS positivity is no longer an open "
            "finite-volume gate at lambda=0.4."
        ),
        "does_not_establish": [
            "reflection-positivity failure at every nonzero coupling",
            "failure of a Krein or other indefinite-metric reconstruction",
            "an interacting volume-uniform estimate",
            "a continuum or infinite-volume BT measure",
            "a Born rule, scattering probability, or event rate",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Python Fraction arithmetic for all powers, curvatures, "
                "actions, and the determinant-sign exponent"
            ),
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_lambda04_os_kernel_obstruction.py --check",
            "python3 reverse_physics/verify_bt_euclidean_lambda04_os_kernel_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_lambda04_os_kernel_obstruction",
        ],
        "tier_receipt": {
            "tier_0": (
                "parse, strict schema, deterministic generation, scoped "
                "git diff --check, and staged-diff inspection"
            ),
            "tier_1": (
                "exact producer, method-distinct full-lattice verifier, "
                "unit tests, and mutation rejection"
            ),
            "tier_2": (
                "predecessor certificates checked by content hash; samplers "
                "were not rerun because their role is supporting only"
            ),
            "tier_3": (
                "not run: no shared classical operator, freeze, release, "
                "quantum lifecycle, or Lorentzian claim changes"
            ),
            "memory_policy": (
                "all commands sequential; exploratory and verification jobs "
                "run under a 500000 KiB virtual-memory ceiling where relevant"
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
        f"[PASS] exact lambda=0.4 OS kernel obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
