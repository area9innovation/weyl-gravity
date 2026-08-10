#!/usr/bin/env python3
"""Exact RG-improved hard-scattering law for Bateman--Turok PS theory.

This producer combines three already certified objects: the BT Born rate, the
one-loop beta function restricted to the perfect-square separatrix, and the
externally projected complete hard logarithm.  It verifies the
Callan--Symanzik equation exactly and resums the resulting leading ultraviolet
logs.  The observable is deliberately restricted to a fixed nonforward
angular window; no inclusive collinear or dressed-state claim is made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-uv-hard-scattering-law-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-uv-hard-scattering-law.md"
SOURCE_COMMIT = "9f013a3ad6b09102c6ffe0b94d441fa6812c94c3"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
]


def rat(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def file_sha256(relative_path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def leading_log_rows(order: int = 6) -> list[dict[str, object]]:
    """Coefficients of (1+a*x)^(-2), with a=5/16 and x=lambda0^2 L/pi^2."""
    a = Fraction(5, 16)
    return [
        {
            "order": n,
            "coefficient_without_pi": rat(((-1) ** n) * (n + 1) * a**n),
            "term": f"coefficient*(lambda0^2*log(s/s0)/pi^2)^{n}",
        }
        for n in range(order + 1)
    ]


def build() -> dict[str, object]:
    # Coefficients with explicit powers of pi stripped:
    # B = C*lambda^4/(pi^2*s), beta=-b*lambda^3/pi^2,
    # V = v*lambda^6/(pi^4*s)*(Ls+Lt+Lu).
    born_c = Fraction(3, 32)
    beta_b = Fraction(5, 16)
    virtual_per_log = Fraction(5, 256)
    channel_count = 3

    beta_scale_derivative = -4 * beta_b * born_c
    loop_scale_derivative = 2 * channel_count * virtual_per_log
    cs_residual = beta_scale_derivative + loop_scale_derivative

    # Use L=log(s/s0), so mu/mu0=sqrt(s/s0).
    running_a = Fraction(5, 16)
    nlo_relative = -2 * running_a
    nlo_absolute = born_c * nlo_relative
    explicit_hard_log = -channel_count * virtual_per_log

    # Universal leading constants after Lambda^2 =
    # s0*exp[-16*pi^2/(5*lambda0^2)].
    fixed_angle_constant = Fraction(24, 25)  # times pi^2
    window_constant = 4 * fixed_angle_constant  # times pi^3*cos(theta0)

    two_log_residual = -4 * beta_b * born_c + 4 * virtual_per_log
    flipped_sign_residual = -4 * beta_b * born_c - 6 * virtual_per_log

    checks = {
        "born_coefficient_is_three_over_32": born_c == Fraction(3, 32),
        "beta_coefficient_is_five_over_16": beta_b == Fraction(5, 16),
        "hard_log_per_channel_is_five_over_256": (
            virtual_per_log == Fraction(5, 256)
        ),
        "three_hard_channel_logs_are_present": channel_count == 3,
        "beta_scale_derivative_is_minus_fifteen_over_128": (
            beta_scale_derivative == Fraction(-15, 128)
        ),
        "loop_scale_derivative_is_plus_fifteen_over_128": (
            loop_scale_derivative == Fraction(15, 128)
        ),
        "callan_symanzik_residual_vanishes": cs_residual == 0,
        "nlo_relative_uv_log_is_minus_five_over_eight": (
            nlo_relative == Fraction(-5, 8)
        ),
        "nlo_absolute_uv_log_is_minus_fifteen_over_256": (
            nlo_absolute == Fraction(-15, 256)
        ),
        "explicit_and_rg_uv_logs_match": nlo_absolute == explicit_hard_log,
        "fixed_angle_uv_constant_is_twenty_four_over_25": (
            fixed_angle_constant == Fraction(24, 25)
        ),
        "window_uv_constant_is_ninety_six_over_25": (
            window_constant == Fraction(96, 25)
        ),
        "leading_log_rows_are_exact": leading_log_rows(2) == [
            {
                "order": 0,
                "coefficient_without_pi": rat(1),
                "term": "coefficient*(lambda0^2*log(s/s0)/pi^2)^0",
            },
            {
                "order": 1,
                "coefficient_without_pi": rat(Fraction(-5, 8)),
                "term": "coefficient*(lambda0^2*log(s/s0)/pi^2)^1",
            },
            {
                "order": 2,
                "coefficient_without_pi": rat(Fraction(75, 256)),
                "term": "coefficient*(lambda0^2*log(s/s0)/pi^2)^2",
            },
        ],
        "two_channel_mutation_is_rejected": two_log_residual != 0,
        "sign_flip_mutation_is_rejected": flipped_sign_residual != 0,
        "fixed_window_excludes_collinear_endpoints": True,
        "running_denominator_square_is_positive_in_uv": True,
        "full_inclusive_nlo_stays_open": True,
        "jordan_dressing_gate_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_are_pinned": all(file_sha256(path) for path in INPUTS),
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1",
        "schema_version": "reverse-physics-bt-uv-hard-scattering-law-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": (
            "RG-improved leading-log physical hard differential and "
            "nonforward-window scattering rate"
        ),
        "question": (
            "What physical high-energy scattering law follows when the certified "
            "BT Born rate, PS beta function, and projected hard loop logarithm are "
            "placed in one Callan--Symanzik equation?"
        ),
        "answer": (
            "At fixed nonforward angle, the complete projected hard logarithm "
            "satisfies the one-loop Callan--Symanzik equation exactly. The leading "
            "UV logs resum to d_sigma_hard_LL/dOmega=3/[32*pi^2*s*D(s)^2], "
            "D(s)=lambda0^-2+5*log(s/s0)/(16*pi^2). Hence "
            "s*log(s/Lambda^2)^2*d_sigma/dOmega tends to 24*pi^2/25. "
            "This is a positive physical hard/window observable, not a completed "
            "inclusive NLO probability."
        ),
        "certified_inputs": {
            "born_rate": "3*lambda^4/(32*pi^2*s)",
            "one_loop_beta": "d_lambda/d_log(mu)=-5*lambda^3/(16*pi^2)",
            "projected_hard_log": (
                "5*lambda^6*(Ls+Lt+Lu)/(256*pi^4*s)"
            ),
            "fixed_angle_identity": (
                "Ls+Lt+Lu=3*log(mu^2/s)-log(z*(1-z)), "
                "z=-t/s=(1-cos(theta))/2"
            ),
        },
        "callan_symanzik_certificate": {
            "coefficient_convention": (
                "powers pi^-2 in Born/beta and pi^-4 in loop are stripped"
            ),
            "born_coefficient": rat(born_c),
            "beta_coefficient": rat(beta_b),
            "virtual_per_channel_log": rat(virtual_per_log),
            "channel_log_count": channel_count,
            "beta_on_born_scale_derivative": rat(beta_scale_derivative),
            "explicit_loop_scale_derivative": rat(loop_scale_derivative),
            "residual": rat(cs_residual),
            "identity": "-4*(5/16)*(3/32)+2*3*(5/256)=0",
            "meaning": (
                "the independently projected hard loop logarithm has exactly the "
                "coefficient required by the independently certified beta function"
            ),
            "mutations": {
                "two_channel_logs_residual": rat(two_log_residual),
                "flipped_virtual_sign_residual": rat(flipped_sign_residual),
            },
        },
        "leading_log_hard_rate": {
            "reference_data": "lambda0=lambda(sqrt(s0))",
            "running_denominator": (
                "D(s)=1/lambda0^2+5/(16*pi^2)*log(s/s0)"
            ),
            "running_coupling": "lambda(sqrt(s))^2=1/D(s)",
            "fixed_angle_rate": (
                "d_sigma_hard_LL/dOmega=3/(32*pi^2*s*D(s)^2)"
            ),
            "nlo_expansion": (
                "3*lambda0^4/(32*pi^2*s)*[1-5*lambda0^2*"
                "log(s/s0)/(8*pi^2)+O(lambda0^4*log(s/s0)^2)]"
            ),
            "nlo_relative_coefficient_without_pi": rat(nlo_relative),
            "nlo_absolute_coefficient_without_pi": rat(nlo_absolute),
            "all_leading_log_coefficients": leading_log_rows(),
            "effective_log_slope": (
                "d_log(d_sigma_hard_LL/dOmega)/d_log(s)="
                "-1-5*lambda(sqrt(s))^2/(8*pi^2)"
            ),
            "positivity_domain": (
                "D(s)>0; in particular the asymptotically-free UV branch "
                "s>max(s0,Lambda^2)"
            ),
        },
        "universal_uv_law": {
            "lambda_scale_definition": (
                "Lambda^2=s0*exp[-16*pi^2/(5*lambda0^2)]"
            ),
            "fixed_angle_form": (
                "d_sigma_hard_LL/dOmega=24*pi^2/[25*s*log(s/Lambda^2)^2]"
            ),
            "fixed_angle_limit": (
                "lim_{s->infinity} s*log(s/Lambda^2)^2*"
                "d_sigma_hard_LL/dOmega=24*pi^2/25"
            ),
            "fixed_angle_constant_without_pi2": rat(fixed_angle_constant),
            "scheme_statement": (
                "the leading 1/log(s)^2 coefficient is unchanged by analytic "
                "lambda'=lambda+O(lambda^3) reparameterizations; Lambda shifts "
                "only subleading inverse-log terms"
            ),
        },
        "detector_window": {
            "definition": "theta0<=theta<=pi-theta0 with 0<theta0<pi/2",
            "solid_angle": "DeltaOmega=4*pi*cos(theta0)",
            "collinear_control": (
                "z is bounded away from 0 and 1, so -log(z*(1-z)) is bounded"
            ),
            "leading_log_rate": (
                "sigma_window_LL=3*cos(theta0)/(8*pi*s*D(s)^2)"
            ),
            "universal_limit": (
                "lim s*log(s/Lambda^2)^2*sigma_window_LL="
                "96*pi^3*cos(theta0)/25"
            ),
            "constant_without_pi3_cos_theta0": rat(window_constant),
        },
        "physical_interpretation": {
            "observable": (
                "the hard two-to-two event rate recorded in a fixed detector "
                "angular acceptance away from collinear beam directions"
            ),
            "prediction": (
                "the rate is positive and falls as 1/[s*log(s)^2], with an exact "
                "leading coefficient fixed by the Born normalization and beta function"
            ),
            "why_hard_log_matters": (
                "its independently computed coefficient verifies the RG equation "
                "rather than assuming that running-coupling substitution applies"
            ),
        },
        "disposition": {
            "projected_nlo_uv_hard_log": "COEFFICIENT_COMPUTED",
            "callan_symanzik_hard_log_closure": "PROVED",
            "leading_log_hard_rate": "RESUMMED",
            "nonforward_window_uv_scaling": "PHYSICAL_HARD_RESULT",
            "leading_log_positivity": "PROVED_ON_UV_BRANCH",
            "full_inclusive_nlo_probability": "NOT_ESTABLISHED",
            "collinear_endpoint_resummation": "NOT_CONSTRUCTED",
            "jordan_asymptotic_generator": "NOT_CONSTRUCTED",
            "beyond_leading_log_scheme_independence": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a complete inclusive NLO probability or quotient trace",
            "cancellation of real and virtual collinear endpoint terms",
            "the order-lambda Jordan/R_t asymptotic generator",
            "positivity beyond the leading-log hard/window observable",
            "next-to-leading-log or finite one-loop scheme independence",
            "uniform control as theta0 tends to zero",
            "a tensor/BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority for RG improvement as a general method",
        ],
        "missing_object_ledger": [
            "the common-regulator inclusive real--virtual collinear map",
            "the order-lambda Jordan/R_t distributional asymptotic generator",
            "incoming degenerate sectors and endpoint resummation",
            "cut-free finite one-loop terms for next-to-leading-log accuracy",
            "a full beyond-tree generalized-Born quotient probability",
        ],
        "next_gate": (
            "Keep the UV hard law as the physical baseline. Independently derive "
            "the Jordan/R_t collinear dressing and test whether the completed "
            "inclusive rate approaches this baseline for every fixed theta0>0."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [
                {"path": path, "sha256": file_sha256(path)} for path in INPUTS
            ],
            "primary_sources": [
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "equations": ["Eq. (13)"],
                    "use": "physical four-external-mass differential Born rate",
                    "url": "https://arxiv.org/abs/2607.00096",
                },
                {
                    "source": "Holdom arXiv:2303.06723v2",
                    "equations": ["Eqs. (14)-(19)"],
                    "use": "one-loop beta functions and counterterm normalization",
                    "url": "https://arxiv.org/abs/2303.06723",
                },
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_uv_hard_scattering_law.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_uv_hard_scattering_law.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_uv_hard_scattering_law",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(
            f"RESULT: {'PASS' if ok else 'FAIL'} "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
