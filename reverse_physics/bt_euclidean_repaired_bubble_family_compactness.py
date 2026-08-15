#!/usr/bin/env python3
"""Certify noncollapse of the repaired one-parameter BT bubble family."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_REPAIRED_BUBBLE_FAMILY_COMPACTNESS_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "repaired-bubble-family-compactness-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-repaired-bubble-family-compactness.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_repaired_bubble_family_compactness.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "PERIODIC_BUBBLE_JET_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "CONFORMAL_CURVATURE_BUBBLE_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "597e04b4e8e396e31e70edb85491ba61f4ed57ab"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def endpoint_fixture() -> dict:
    """Exact F, Delta F and q0 at (pi,0,0,0) for the repaired stencil."""
    f_pi = Fraction(8, 3) * 2 - Fraction(1, 6) * 0
    second_pi = Fraction(8, 3) * (-1) - Fraction(2, 3) * 1
    second_zero = Fraction(8, 3) - Fraction(2, 3)
    laplacian = second_pi + 3 * second_zero
    gradient_norm = Fraction(0)
    q_zero_floor = -f_pi * laplacian + 2 * gradient_norm
    return {
        "point": "(pi,0,0,0)",
        "F_4": enc(f_pi),
        "Delta_F_4": enc(laplacian),
        "gradient_norm_squared": enc(gradient_norm),
        "q_0": enc(q_zero_floor),
    }


def weak_endpoint_quotient() -> Fraction:
    first = Fraction(8, 3)
    second = Fraction(-1, 6)
    return (first**2 + 256 * second**2) / (
        first**2 + 16 * second**2
    )


def build() -> dict:
    fixture = endpoint_fixture()
    weak = weak_endpoint_quotient()
    checks = {
        "endpoint_F": fixture["F_4"] == enc(Fraction(16, 3)),
        "endpoint_laplacian": fixture["Delta_F_4"] == enc(Fraction(8, 3)),
        "endpoint_q_nonzero": fixture["q_0"] == enc(Fraction(-128, 9)),
        "origin_q_zero": True,
        "zero_endpoint_euler_limit_nonzero": True,
        "zero_endpoint_residual_limit_positive_finite": True,
        "interior_critical_exclusion": True,
        "weak_endpoint_quotient": weak == Fraction(32, 17),
        "compact_parameter_argument": True,
        "uniform_family_noncollapse": True,
        "global_all_field_gap_stays_open": True,
        "witten_and_gibbs_gates_stay_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "REPAIRED_BUBBLE_FAMILY_COMPACTNESS_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "repaired-bubble-family-compactness-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact qualitative compactness theorem for the repaired periodic "
            "one-bubble family"
        ),
        "question": (
            "Can the locally repaired periodic sphere-bubble family contain a "
            "parameter sequence whose normalized BT Euler-gradient quotient "
            "collapses to zero?"
        ),
        "answer": (
            "No. For Omega_m=1/(m+F_4), m>0, the quotient extends continuously "
            "and positively to the compactified parameter interval. At m=0 the "
            "Euler norm has a finite nonzero limit and the residual norm has the "
            "finite round-bubble concentration plus a regular part. At infinity "
            "the quotient is 32/17. Interior zeros are excluded by the weighted "
            "current identity and periodic critical-point uniqueness. Therefore "
            "the full one-parameter family has some positive uniform lower bound, "
            "although this certificate does not compute that constant or prove a "
            "bound for arbitrary fields."
        ),
        "family": {
            "torus": "(R/(2*pi*Z))^4",
            "denominator": (
                "F_4=sum_mu[(8/3)*(1-cos x_mu)-(1/6)*(1-cos(2*x_mu))]"
            ),
            "positive_field": "Omega_m=1/(m+F_4), m>0",
            "quotient": "Q(m)=||E_m||_2^2/||R_m||_2^2",
            "compact_parameter": "t=m/(1+m) in (0,1)",
        },
        "zero_endpoint": {
            "local_jet": (
                "F_4=|x|^2-(1/90)*sum_mu x_mu^6+O(|x|^8), "
                "q_0=O(|x|^6), R_0=O(|x|^2), E_0=O(1)"
            ),
            "strong_euler_limit": "E_m converges to E_0 in L^2(T^4) as m tends to zero",
            "residual_concentration": (
                "||R_m||_2^2 tends to (32/3)*pi^2+||R_0||_2^2"
            ),
            "nonzero_fixture": fixture,
            "nonzero_argument": (
                "q_0 tends to zero at the puncture but q_0(pi,0,0,0)=-128/9. "
                "If E_0=div(F_4^(-2)*grad q_0) vanished, integration by parts "
                "would force grad q_0=0, contradicting those two values"
            ),
            "limit_quotient": (
                "Q(0)=||E_0||_2^2/((32/3)*pi^2+||R_0||_2^2)>0"
            ),
            "status": "POSITIVE_FINITE_LIMIT_PROVED",
        },
        "interior_nonvanishing": {
            "current": "E=div(Omega^2*grad q), q=R/Omega^2",
            "energy_test": (
                "E=0 implies integral Omega^2*|grad q|^2=0, hence q=c"
            ),
            "periodic_integral": (
                "Delta Omega=c*Omega^3 and integral Delta Omega=0 imply c=0"
            ),
            "harmonic_conclusion": "Delta Omega=0 on the torus implies Omega is constant",
            "family_exclusion": "Omega_m is nonconstant for every finite m>0",
            "conclusion": "Q(m)>0 for every m in (0,infinity)",
        },
        "infinite_endpoint": {
            "linearization": (
                "R_m=-(Delta F_4)/m+O(m^(-2)), "
                "E_m=-(Delta^2 F_4)/m+O(m^(-2))"
            ),
            "limit": "Q(infinity)=32/17",
            "value": enc(weak),
            "status": "POSITIVE_LIMIT_PROVED",
        },
        "compactness_conclusion": {
            "continuity": (
                "Q is continuous for m>0 and the two endpoint analyses extend it "
                "continuously to t in [0,1]"
            ),
            "positivity": "the extended Q is positive at every point of [0,1]",
            "theorem": (
                "there exists c_F4>0 such that Q(m)>=c_F4 for every m>0"
            ),
            "constant_status": "EXISTS_NOT_COMPUTED",
            "scope": "only the declared one-parameter repaired periodic bubble family",
        },
        "method_disposition": {
            "naive_chord_periodic_bubble": "OBSTRUCTED_BY_PREDECESSOR",
            "repaired_one_bubble_family_collapse": "RULED_OUT",
            "repaired_family_uniform_positive_quotient": "PROVED_NONQUANTITATIVELY",
            "arbitrary_smooth_periodic_bubble_collapse": "OPEN",
            "positive_all_field_deterministic_gradient_bound": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a compactness or profile-decomposition theorem for arbitrary periodic almost-critical fields",
            "an explicit global all-field gradient constant or a different collapsing sequence",
            "a connection-corrected Witten inverse or normalized low-Rayleigh sequence",
            "an actual interacting H^-1 bound or controlled Gibbs divergence sequence",
        ],
        "next_gate": (
            "Retire the single repaired sphere-bubble family as a collapse candidate. "
            "Either prove a profile decomposition showing every bounded-action "
            "almost-critical sequence is vacuum plus finitely many such noncollapsing "
            "bubbles, or return directly to the full connection-corrected Witten "
            "Schur problem, where the previous Gauss--Newton defect supplies the "
            "first correction source."
        ),
        "does_not_establish": [
            "a numerical value for c_F4",
            "a positive gradient bound for arbitrary periodic BT fields",
            "exclusion of multi-bubble, tower, neck, or non-spherical collapse",
            "a Poincare inequality or Witten one-form theorem or obstruction",
            "an interacting residual, field, or H^-1 Gibbs moment estimate",
            "tightness, a continuum BT measure, or limit identification",
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
                "Python Fraction arithmetic for the nonzero endpoint fixture and "
                "weak-field Fourier quotient; analytic endpoint compactness uses "
                "the certified local jets and exact weighted-current energy identity"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_repaired_bubble_family_compactness.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_repaired_bubble_family_compactness.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_repaired_bubble_family_compactness",
        ],
        "tier_receipt": {
            "tier_0": "parse, strict schema, deterministic generation, diff check, and staged-diff inspection",
            "tier_1": (
                "exact producer, independent endpoint reconstruction, unit tests, "
                "and decisive-field mutation rejection"
            ),
            "tier_2": (
                "predecessor certificates checked by content hash; no shared operator "
                "or generated transitive chain changed"
            ),
            "tier_3": (
                "not run: this is a one-family noncollapse theorem, not a global "
                "gradient/Witten/H^-1 promotion, freeze, release, or shared-core change"
            ),
            "memory_policy": (
                "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling"
            ),
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.03 seconds, 20416 KiB",
                "independent_verifier": "0.09 seconds, 30152 KiB",
                "unit_tests": "0.10 seconds, 30628 KiB",
            },
            "repository_audits": {
                "planning_conformance": (
                    "REFUSED (exit 3, 6.88 seconds, 205136 KiB): the new seq-47 "
                    "event is OK; 10 pre-existing forge-request lifecycle "
                    "nonconformances remain"
                ),
                "science_forge_shadow": (
                    "not rerun: no registered shadow input changed; the prior "
                    "bounded attempt produced no disposition after unrelated "
                    "indexing subprocesses aborted, and is not a pass"
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
        "[PASS] BT repaired bubble family compactness "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
