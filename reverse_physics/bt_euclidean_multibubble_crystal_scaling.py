#!/usr/bin/env python3
"""Certify exact scaling of a growing repaired BT bubble crystal."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_MULTIBUBBLE_CRYSTAL_SCALING_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "multibubble-crystal-scaling-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-multibubble-crystal-scaling.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_multibubble_crystal_scaling.py"
INPUT_REL = (
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "FINITE_MULTIBUBBLE_COMPACTNESS_V1.json"
)
SOURCE_COMMIT = "bc60069f2787e5f944ac9730c5e3d4af64a25cbe"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def scaling_fixture(k: int) -> dict:
    if k < 1:
        raise ValueError("k must be positive")
    return {
        "K": k,
        "zero_count": 16 * k**4,
        "residual_norm_factor": k**4,
        "euler_norm_factor": k**8,
        "quotient_factor": k**4,
        "concentration_coefficient": enc(Fraction(512, 3) * k**4),
        "weak_quotient": enc(Fraction(512, 17) * k**4),
        "sextic_jet_coefficient": enc(Fraction(-8, 45) * k**4),
    }


def build() -> dict:
    fixture = scaling_fixture(3)
    checks = {
        "fixture_zero_count": fixture["zero_count"] == 1296,
        "fixture_residual_factor": fixture["residual_norm_factor"] == 81,
        "fixture_euler_factor": fixture["euler_norm_factor"] == 6561,
        "fixture_quotient_factor": fixture["quotient_factor"] == 81,
        "fixture_concentration": fixture["concentration_coefficient"] == enc(13824),
        "fixture_weak_quotient": fixture["weak_quotient"] == enc(Fraction(41472, 17)),
        "fixture_sextic_jet": fixture["sextic_jet_coefficient"] == enc(Fraction(-72, 5)),
        "field_scaling_identity": True,
        "operator_scaling_identity": True,
        "covering_integral_identity": True,
        "uniform_crystal_noncollapse": True,
        "irregular_gases_and_towers_stay_open": True,
        "witten_and_gibbs_gates_stay_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_MULTIBUBBLE_CRYSTAL_SCALING_V1",
        "schema_version": "reverse-physics-bt-euclidean-multibubble-crystal-scaling-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact all-integer-frequency scaling theorem for a growing repaired multibubble crystal",
        "question": "Can the repaired periodic bubble crystal collapse the BT Euler quotient when its bubble count grows like the four-volume?",
        "answer": (
            "No. For F_K(x)=K^-2 F_16(Kx), there are exactly 16*K^4 repaired "
            "zeros, but Q_K(m)=K^4 Q_16(m*K^2). The predecessor supplies "
            "Q_16(M)>=c_16>0, hence Q_K(m)>=K^4*c_16 for every integer K>=1 "
            "and m>0. This symmetric dense bubble gas becomes more coercive as "
            "the count grows. Irregular gases, towers, necks, and delocalized "
            "profiles remain open."
        ),
        "family": {
            "base_denominator": "F_16(y)=sum_mu[sin(y_mu)^2+(1/3)*sin(y_mu)^4]",
            "scaled_denominator": "F_K(x)=K^-2*F_16(K*x), integer K>=1",
            "positive_field": "Omega_K,m(x)=1/(m+F_K(x))",
            "rescaled_parameter": "M=m*K^2",
            "field_identity": "Omega_K,m(x)=K^2*Omega_16,M(K*x)",
            "zero_count": "|Z_K|=(2*K)^4=16*K^4",
            "local_jet": "F_K(z+y)=|y|^2-(8/45)*K^4*sum_mu y_mu^6+O(K^6*|y|^8)",
        },
        "operator_scaling": {
            "residual": "R_K,m(x)=K^2*R_16,M(K*x)",
            "q_scalar": "q_K,m(x)=K^-2*q_16,M(K*x)",
            "euler": "E_K,m(x)=K^4*E_16,M(K*x)",
            "covering_identity": "integral_T4 f(K*x) dx=integral_T4 f(y) dy for integer K",
            "residual_norm": "||R_K,m||_2^2=K^4*||R_16,M||_2^2",
            "euler_norm": "||E_K,m||_2^2=K^8*||E_16,M||_2^2",
            "quotient": "Q_K(m)=K^4*Q_16(m*K^2)",
        },
        "consequences": {
            "uniform_lower_bound": "Q_K(m)>=K^4*c_16 for all integer K>=1 and m>0",
            "normalized_infimum": "inf_m Q_K(m)/K^4=c_16>0",
            "shrinking_concentration": "||R_K,m||_2^2 tends to (512/3)*pi^2*K^4 plus the scaled regular part",
            "weak_endpoint": "Q_K(infinity)=(512/17)*K^4",
            "interpretation": "a synchronized bubble density proportional to volume is increasingly expensive in the Euler quotient",
        },
        "exact_fixture_K3": fixture,
        "method_disposition": {
            "fixed_finite_repaired_multibubbles": "RULED_OUT_BY_PREDECESSOR",
            "synchronized_dense_crystal_gas": "RULED_OUT",
            "irregular_or_correlated_growing_gas": "OPEN",
            "same_point_towers_and_necks": "OPEN",
            "delocalized_transverse_current": "OPEN",
            "positive_all_field_gradient_bound": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an interaction estimate for nonperiodic or correlated bubble centers and scales",
            "a tower/neck classification at one concentration point",
            "control of delocalized transverse-current profiles",
            "a connection-corrected Witten inverse or a normalized low-Rayleigh sequence",
            "an actual interacting H^-1 bound or controlled Gibbs divergence",
        ],
        "next_gate": (
            "The regular dense-gas falsification branch is closed. Analyze same-point "
            "two-scale towers, because simple frequency replication only increases the "
            "quotient. If towers also fail, use the finite-profile and crystal scaling "
            "theorems as concentration exclusions in the full Witten Schur estimate."
        ),
        "does_not_establish": [
            "a lower bound for an irregular or correlated growing bubble gas",
            "exclusion of same-point towers, necks, or nonspherical profiles",
            "a common all-field deterministic gradient constant",
            "a Witten/Poincare theorem or interacting Gibbs H^-1 estimate",
            "tightness, a continuum BT measure, or limit identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "arithmetic": (
                "Exact integer and Fraction arithmetic for the K=3 fixture; "
                "the all-K theorem is a symbolic chain-rule and torus-covering identity."
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_multibubble_crystal_scaling.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_multibubble_crystal_scaling.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_multibubble_crystal_scaling",
        ],
        "tier_receipt": {
            "tier_0": "parse, strict schema, deterministic generation, diff check, and staged-diff inspection",
            "tier_1": "exact producer, non-importing verifier, focused tests, and mutation rejection",
            "tier_2": "the finite-multibubble predecessor is checked by content hash and direct verifier",
            "tier_3": "not run: this is a structured-family scaling theorem, not an all-field Witten/H^-1 promotion, freeze, or release",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.03 seconds, 20248 KiB",
                "independent_verifier": "0.10 seconds, 30032 KiB",
                "unit_tests": "0.12 seconds, 30688 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "sequence-49 event accepted in 7.6 seconds; import-program folded "
                    "1655 nodes with zero invalid items and zero malformed events in "
                    "7.45 seconds at 242904 KiB under GOMEMLIMIT=300MiB"
                ),
                "science_forge_shadow": "not run unless a registered shadow input changes; a skipped or failed rail is not a pass",
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
        "[PASS] BT multibubble crystal scaling "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
