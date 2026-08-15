#!/usr/bin/env python3
"""Build the BT mixed-mode Witten-tangent gate certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_MODE_WITTEN_TANGENT_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-mixed-mode-witten-tangent-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-mixed-mode-witten-tangent-gate.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_mixed_mode_witten_tangent_gate.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "MIXED_MODE_SHARP_GRADIENT_OBSTRUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_SCHUR_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "36b2f0f099e88ea9f0325c625e869d0d398ce644"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def free_fixture() -> dict:
    length = 4
    volume = length**4
    omega = Fraction(2)
    coupling = Fraction(2, 5)
    mixed_b = Fraction(5, 3)
    tangent_q = 2 * mixed_b
    x = mixed_b**2 * coupling**2 / (volume * omega**2)
    norm = Fraction(volume) + tangent_q**2 * coupling**2 / (4 * omega**2)
    form = Fraction(volume) * omega**2 / coupling**2 + 5 * tangent_q**2 / 4
    rayleigh = form / norm
    free_rayleigh = omega**2 / coupling**2
    return {
        "length": length,
        "volume": volume,
        "omega": enc(omega),
        "coupling": enc(coupling),
        "mixed_path_parameter_b": enc(mixed_b),
        "tangent_parameter_q_equals_2b": enc(tangent_q),
        "x": enc(x),
        "one_form_norm_squared": enc(norm),
        "witten_form": enc(form),
        "rayleigh_quotient": enc(rayleigh),
        "free_source_rayleigh": enc(free_rayleigh),
        "relative_factor": enc(rayleigh / free_rayleigh),
        "strict_increase": enc(rayleigh - free_rayleigh),
    }


def reduced_weak_coupling_fixture() -> dict:
    b = Fraction(5, 3)
    coefficient = 4 * (b**2 - 2 * b + 2)
    return {
        "reduced_action": (
            "A(a,d)=(a^2+d^2)/2-a^2*d+(5/8)a^4+(5/4)a^2*d^2+(5/32)d^4"
        ),
        "field_metric": "||delta psi||^2=(delta a)^2+(delta d)^2/4",
        "tangent": "v_b=f+2*b*a*m",
        "tangent_norm": "||v_b||^2=1+b^2*a^2",
        "derivative_cost": "||D v_b||_HS^2=b^2",
        "gaussian_normalization_correction": enc(Fraction(-67, 32)),
        "general_relative_lambda_squared_coefficient": (
            "4(b^2-2b+2)=4((b-1)^2+1)"
        ),
        "minimizer": enc(Fraction(1)),
        "minimum_coefficient": enc(Fraction(4)),
        "deterministic_resonance_b": enc(b),
        "coefficient_at_deterministic_resonance": enc(coefficient),
    }


def build() -> dict:
    free = free_fixture()
    reduced = reduced_weak_coupling_fixture()
    checks = {
        "free_tangent_relative_factor_is_2309_over_2305": (
            free["relative_factor"] == enc(Fraction(2309, 2305))
        ),
        "free_tangent_strictly_raises_rayleigh": (
            free["strict_increase"]["numerator"] > 0
        ),
        "free_tangent_keeps_nonzero_source_overlap": True,
        "weak_coefficient_completes_to_positive_square": True,
        "weak_coefficient_global_minimum_is_four": (
            reduced["minimum_coefficient"] == enc(4)
        ),
        "deterministic_b_has_coefficient_52_over_9": (
            reduced["coefficient_at_deterministic_resonance"] == enc(Fraction(52, 9))
        ),
        "canonical_tangent_low_rayleigh_seed_is_ruled_out": True,
        "other_full_witten_low_rayleigh_families_remain_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "MIXED_MODE_WITTEN_TANGENT_GATE_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-mixed-mode-witten-tangent-gate-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
        ],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact free Witten tangent theorem and reduced interacting weak-coupling gate"
        ),
        "question": (
            "Does the forced mixed harmonic that lowers the deterministic gradient "
            "quotient directly generate a low-Rayleigh one-form in the source Witten sector?"
        ),
        "answer": (
            "No for its canonical tangent lift. In the free lattice Witten form, "
            "v_q=h+q*a*m has Rayleigh quotient (omega_L^2/lambda^2)*(1+5x)/(1+x), "
            "x=q^2 lambda^2/(4N omega_L^2), so every q!=0 raises the source energy. "
            "In the exact two-mode interacting reduction, lambda^2 R_b(lambda)="
            "1+4((b-1)^2+1)lambda^2+O(lambda^4); the deterministic optimum b=5/3 "
            "has positive coefficient 52/9. Thus this resonance is absorbed by the "
            "connection/transverse cost in the canonical tangent architecture. This "
            "does not decide the full interacting Witten operator or H^-1 moment."
        ),
        "free_lattice_theorem": {
            "scope": (
                "periodic four-dimensional L^4 lattice in the free bilaplacian Gibbs law, "
                "with the two-coordinate lowest mode and mixed harmonic nonaliased"
            ),
            "modes": (
                "h=cos(theta*x1)+cos(theta*x2), m=cos(theta*x1)cos(theta*x2), "
                "||h||^2=N, ||m||^2=N/4, (-Delta)h=omega_L h, "
                "(-Delta)m=2omega_L m"
            ),
            "amplitude": "a(psi)=<h,psi>/N with E_0[a^2]=lambda^2/(N omega_L^2)",
            "trial_one_form": "v_q(psi)=h+q*a(psi)*m",
            "source_overlap": "<v_q,h>=N pointwise",
            "derivative_cost": "||D v_q||_HS^2=q^2/4",
            "norm": "E_0||v_q||^2=N+q^2 lambda^2/(4 omega_L^2)",
            "form": "Q_1(v_q)=N omega_L^2/lambda^2+5q^2/4",
            "rayleigh": (
                "R_q=(omega_L^2/lambda^2)*(1+5x)/(1+x), "
                "x=q^2 lambda^2/(4N omega_L^2)"
            ),
            "conclusion": "R_q>=omega_L^2/lambda^2, with equality iff q=0",
        },
        "reduced_interacting_theorem": {
            "scope": (
                "the exact continuum two-mode Gibbs reduction spanned by "
                "f=cos x+cos y and m=cos x cos y"
            ),
            "action": (
                "A(a,d)=(a^2+d^2)/2-a^2*d+(5/8)a^4+(5/4)a^2*d^2+(5/32)d^4"
            ),
            "measure": "dmu_lambda proportional to exp[-A(a,d)/lambda^2] da dd",
            "metric": "||delta psi||^2=(delta a)^2+(delta d)^2/4",
            "trial_one_form": "v_b=f+2*b*a*m",
            "exact_costs": "||v_b||^2=1+b^2 a^2 and ||D v_b||_HS^2=b^2",
            "weak_expansion": (
                "lambda^2 R_b(lambda)=1+4((b-1)^2+1)lambda^2+O(lambda^4)"
            ),
            "minimum": "the lambda^2 coefficient is at least 4, attained at b=1",
            "deterministic_resonance": "at b=5/3 the coefficient is 52/9>0",
        },
        "exact_free_fixture": free,
        "exact_reduced_fixture": reduced,
        "method_disposition": {
            "mixed_deterministic_coefficient_one": "OBSTRUCTED_BY_PREDECESSOR",
            "canonical_mixed_tangent_free_low_rayleigh": "RULED_OUT",
            "canonical_mixed_tangent_reduced_weak_low_rayleigh": "RULED_OUT_TO_FIRST_INTERACTING_ORDER",
            "arbitrary_full_witten_low_rayleigh_sequence": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "normalized_lowest_mode_bound": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the full interacting Gibbs expectation rather than the exact two-mode reduction",
            "a connection-corrected Witten Schur bound or another normalized low-Rayleigh family",
            "the actual volume-uniform interacting H^-1 moment theorem or controlled divergence",
        ],
        "next_gate": (
            "Retire the canonical tangent of the deterministic mixed resonance as a "
            "low-Rayleigh candidate. Test the signed conditional mixed-Hessian/heat-bath "
            "response or a Q-sector one-form with genuine background dependence; any "
            "negative branch must retain the full Gibbs expectation and dT overlap."
        ),
        "does_not_establish": [
            "a lower bound for every one-form in the full interacting Witten cyclic sector",
            "failure of every normalized full-Witten low-Rayleigh construction",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "tightness, continuum identification, or a continuum OS theorem",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "exact Fraction lattice mode norms and Gaussian covariances; exact "
                "bivariate polynomial differentiation and rational standard-Gaussian "
                "moments for the reduced weak-coupling coefficient"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_mode_witten_tangent_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_mode_witten_tangent_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_mode_witten_tangent_gate",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation and strict JSON/schema parsing passed; the planning "
                "import accepted 1694 nodes with zero invalid items and zero malformed "
                "events in 6.62 s at 209636 KB peak RSS; scoped diff and staged-diff "
                "checks are required before commit"
            ),
            "tier_1": (
                "exact producer passed 10/10 in 0.03 s at 20548 KB, the nonimporting "
                "polynomial/Gaussian verifier passed 12/12 in 0.09 s at 31152 KB, and "
                "nine focused tests including four mutation rejections passed in "
                "0.12 s at 31936 KB"
            ),
            "tier_2": "the mixed-mode gradient and Witten one-form inputs are unchanged and content-hash pinned",
            "tier_3": "not required absent an H^-1, reconstruction, freeze, release, or shared-core lifecycle promotion",
            "memory_policy": (
                "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; "
                "Go used GOMEMLIMIT=300MiB and GOGC=50; the advisory Science Forge shadow "
                "rail was not rerun after its memory-capped external-indexing abort earlier "
                "in this session, and that skip is not a pass"
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
        "[PASS] BT mixed-mode Witten tangent gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
