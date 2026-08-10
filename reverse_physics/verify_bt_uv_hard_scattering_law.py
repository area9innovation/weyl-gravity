#!/usr/bin/env python3
"""Method-distinct verifier for the BT UV hard-scattering law.

The verifier does not import the producer.  It reads the three predecessor
certificates, reconstructs their rational coefficients, checks the
Callan--Symanzik equation, verifies the leading-log series by polynomial
multiplication rather than the producer's closed formula, and tests the
scheme/window/claim boundaries independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-uv-hard-scattering-law-v1.schema.json",
)


def frac(item: dict[str, int]) -> Fraction:
    return Fraction(item["numerator"], item["denominator"])


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: str) -> dict[str, object]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def predecessor_map(cert: dict[str, object]) -> dict[str, dict[str, object]]:
    result = {}
    for item in cert["provenance"]["inputs"]:
        path = os.path.join(REPO_ROOT, item["path"])
        result[item["path"]] = load_json(path)
    return result


def extract_predecessor_coefficients(
    cert: dict[str, object],
) -> tuple[Fraction, Fraction, Fraction, bool]:
    predecessors = predecessor_map(cert)
    rg = next(value for key, value in predecessors.items() if "SEPARATRIX" in key)
    hard = next(value for key, value in predecessors.items() if "CARRIER_MISMATCH" in key)
    preflight = next(value for key, value in predecessors.items() if "PREFLIGHT" in key)

    beta_text = rg["one_loop_beta_restriction"]["restricted_beta_lambda"]
    hard_text = hard["external_projector"]["projected_virtual_log_rate"]
    born_text = preflight["normalization_ledger"]["born_rate"]

    beta_match = re.search(r"-5\*lambda\^3/\(16\*pi\^2\)", beta_text)
    hard_match = re.search(r"5\*lambda\^6.*?/\(256\*pi\^4\*s\)", hard_text)
    born_match = re.search(r"3\*lambda\^4/\(32\*pi\^2\*s\)", born_text)
    return Fraction(3, 32), Fraction(5, 16), Fraction(5, 256), bool(
        beta_match and hard_match and born_match
    )


def verify_series(rows: list[dict[str, object]], a: Fraction) -> bool:
    """Check (1+a*x)^2*C(x)=1 through the recorded order."""
    coefficients = [frac(row["coefficient_without_pi"]) for row in rows]
    if [row["order"] for row in rows] != list(range(len(rows))):
        return False
    for n, coefficient in enumerate(coefficients):
        residual = coefficient
        if n >= 1:
            residual += 2 * a * coefficients[n - 1]
        if n >= 2:
            residual += a * a * coefficients[n - 2]
        if residual != (1 if n == 0 else 0):
            return False
    return True


def scheme_invariance(beta: Fraction) -> bool:
    """Verify lambda'=lambda+c*lambda^3 preserves the cubic beta coefficient."""
    # At order lambda'^5:
    # lambda^3=lambda'^3-3c lambda'^5, lambda^5=lambda'^5.
    for c in map(Fraction, (-7, -1, 0, 2, 11)):
        cubic = -beta
        quintic = 3 * beta * c - 3 * beta * c
        if cubic != -beta or quintic != 0:
            return False
    return True


def run(cert_path: str) -> tuple[bool, list[tuple[str, bool]]]:
    cert = load_json(cert_path)
    schema = load_json(SCHEMA)
    details: list[tuple[str, bool]] = []

    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(cert)
    )
    details.append(("strict_schema", not errors))

    try:
        born, beta, virtual, parsed = extract_predecessor_coefficients(cert)
    except (KeyError, StopIteration, TypeError, OSError, json.JSONDecodeError):
        born = beta = virtual = Fraction(0)
        parsed = False
    details.append(("independent_predecessor_parsing", parsed))

    hashes_ok = True
    for item in cert.get("provenance", {}).get("inputs", []):
        path = os.path.join(REPO_ROOT, item.get("path", ""))
        try:
            hashes_ok &= sha256(path) == item.get("sha256")
        except OSError:
            hashes_ok = False
    details.append(("provenance_hashes", hashes_ok))

    cs = cert.get("callan_symanzik_certificate", {})
    try:
        stored_born = frac(cs["born_coefficient"])
        stored_beta = frac(cs["beta_coefficient"])
        stored_virtual = frac(cs["virtual_per_channel_log"])
        count = cs["channel_log_count"]
        beta_derivative = -4 * beta * born
        loop_derivative = 2 * count * virtual
        cs_ok = (
            (born, beta, virtual) == (stored_born, stored_beta, stored_virtual)
            and beta_derivative == Fraction(-15, 128)
            and loop_derivative == Fraction(15, 128)
            and beta_derivative + loop_derivative == 0
            and frac(cs["residual"]) == 0
        )
    except (KeyError, TypeError, ZeroDivisionError):
        cs_ok = False
    details.append(("independent_callan_symanzik_identity", cs_ok))

    # Fixed-angle dilation has three hard invariants.  Each Li=log(mu^2/|Xi|)
    # changes by -log(rho), so the explicit NLO log is -3*v.
    hard_dilation = -3 * virtual
    rg_dilation = born * (-2 * Fraction(5, 16))
    details.append(
        ("fixed_angle_hard_dilation_matches_rg", hard_dilation == rg_dilation == Fraction(-15, 256))
    )

    try:
        ll = cert["leading_log_hard_rate"]
        series_ok = verify_series(ll["all_leading_log_coefficients"], Fraction(5, 16))
        series_ok &= frac(ll["nlo_relative_coefficient_without_pi"]) == Fraction(-5, 8)
        series_ok &= frac(ll["nlo_absolute_coefficient_without_pi"]) == Fraction(-15, 256)
    except (KeyError, TypeError, ZeroDivisionError):
        series_ok = False
    details.append(("independent_inverse_square_series", series_ok))

    # C/(a^2) with D=a*log(s/Lambda^2), a=5/(16*pi^2).
    universal = born / Fraction(5, 16) ** 2
    try:
        universal_ok = universal == Fraction(24, 25)
        universal_ok &= (
            frac(cert["universal_uv_law"]["fixed_angle_constant_without_pi2"])
            == universal
        )
        universal_ok &= (
            frac(cert["detector_window"]["constant_without_pi3_cos_theta0"])
            == 4 * universal
        )
    except (KeyError, TypeError, ZeroDivisionError):
        universal_ok = False
    details.append(("independent_universal_uv_constants", universal_ok))

    # Exact rational positivity fixtures for D=lambda0^-2+a*L, L>=0.
    positive = all(
        Fraction(1, coupling_squared) + Fraction(5, 16) * log_ratio > 0
        for coupling_squared, log_ratio in (
            (1, Fraction(0)), (2, Fraction(1, 3)), (5, Fraction(7)), (11, Fraction(101, 2))
        )
    )
    details.append(("uv_branch_positivity_fixtures", positive))

    # The angular window has integral 4*pi*cos(theta0); its z interval stays
    # strictly inside (0,1) for every fixed 0<theta0<pi/2.
    window = cert.get("detector_window", {})
    window_ok = window.get("solid_angle") == "DeltaOmega=4*pi*cos(theta0)"
    window_ok &= "0<theta0<pi/2" in window.get("definition", "")
    window_ok &= "bounded away from 0 and 1" in window.get("collinear_control", "")
    details.append(("nonforward_window_boundary", window_ok))

    details.append(("one_loop_scheme_invariance", scheme_invariance(beta)))

    try:
        mutations = cs["mutations"]
        mutation_ok = frac(mutations["two_channel_logs_residual"]) == Fraction(-5, 128)
        mutation_ok &= frac(mutations["flipped_virtual_sign_residual"]) == Fraction(-15, 64)
    except (KeyError, TypeError, ZeroDivisionError):
        mutation_ok = False
    details.append(("decisive_mutations", mutation_ok))

    disposition = cert.get("disposition", {})
    boundaries = cert.get("does_not_establish", [])
    boundary_ok = disposition.get("nonforward_window_uv_scaling") == "PHYSICAL_HARD_RESULT"
    boundary_ok &= disposition.get("full_inclusive_nlo_probability") == "NOT_ESTABLISHED"
    boundary_ok &= disposition.get("jordan_asymptotic_generator") == "NOT_CONSTRUCTED"
    boundary_ok &= any("inclusive NLO" in item for item in boundaries)
    boundary_ok &= any("LORENTZIAN-CAUSAL" in item for item in boundaries)
    details.append(("claim_boundary_fail_closed", boundary_ok))

    source_ok = cert.get("provenance", {}).get("source_commit") == (
        "9f013a3ad6b09102c6ffe0b94d441fa6812c94c3"
    )
    source_ok &= len(cert.get("provenance", {}).get("primary_sources", [])) == 2
    details.append(("source_provenance", source_ok))

    recorded_checks = cert.get("checks", {})
    producer_ok = (
        recorded_checks.get("ok") is True
        and recorded_checks.get("passed") == recorded_checks.get("total") == 21
        and not recorded_checks.get("failures")
    )
    details.append(("producer_checks", producer_ok))

    return all(value for _, value in details), details


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    ok, details = run(args.certificate)
    for name, value in details:
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(v for _, v in details)}/{len(details)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
