#!/usr/bin/env python3
"""Independent verifier for repaired BT bubble-family compactness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "REPAIRED_BUBBLE_FAMILY_COMPACTNESS_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "repaired-bubble-family-compactness-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def one_coordinate_values(cosine: Fraction, cosine_double: Fraction) -> dict[str, Fraction]:
    value = Fraction(8, 3) * (1 - cosine) - Fraction(1, 6) * (1 - cosine_double)
    second = Fraction(8, 3) * cosine - Fraction(2, 3) * cosine_double
    return {"value": value, "second": second}


def reconstruct_nonzero_fixture() -> dict[str, Fraction]:
    at_pi = one_coordinate_values(Fraction(-1), Fraction(1))
    at_zero = one_coordinate_values(Fraction(1), Fraction(1))
    field = at_pi["value"] + 3 * at_zero["value"]
    laplacian = at_pi["second"] + 3 * at_zero["second"]
    gradient_norm = Fraction(0)
    return {
        "field": field,
        "laplacian": laplacian,
        "gradient_norm": gradient_norm,
        "q": -field * laplacian + 2 * gradient_norm,
    }


def reconstruct_weak_quotient() -> Fraction:
    modes = {
        1: Fraction(8, 3),
        2: Fraction(-1, 6),
    }
    residual_norm = sum(
        frequency**4 * coefficient**2
        for frequency, coefficient in modes.items()
    )
    gradient_norm = sum(
        frequency**8 * coefficient**2
        for frequency, coefficient in modes.items()
    )
    return gradient_norm / residual_norm


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    recorded = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["provenance_hashes_current"] = len(recorded) == 2 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )

    fixture = certificate["zero_endpoint"]["nonzero_fixture"]
    rebuilt = reconstruct_nonzero_fixture()
    checks["nonzero_fixture_reconstructed"] = (
        rebuilt["field"] == decode(fixture["F_4"]) == Fraction(16, 3)
        and rebuilt["laplacian"]
        == decode(fixture["Delta_F_4"])
        == Fraction(8, 3)
        and rebuilt["gradient_norm"]
        == decode(fixture["gradient_norm_squared"])
        == 0
        and rebuilt["q"] == decode(fixture["q_0"]) == Fraction(-128, 9)
    )
    zero = certificate["zero_endpoint"]
    checks["zero_endpoint_chain"] = (
        "q_0=O(|x|^6)" in zero["local_jet"]
        and zero["strong_euler_limit"]
        == "E_m converges to E_0 in L^2(T^4) as m tends to zero"
        and "(32/3)*pi^2+||R_0||_2^2" in zero["residual_concentration"]
        and "force grad q_0=0" in zero["nonzero_argument"]
        and zero["status"] == "POSITIVE_FINITE_LIMIT_PROVED"
    )
    interior = certificate["interior_nonvanishing"]
    checks["interior_energy_chain"] = (
        interior["current"] == "E=div(Omega^2*grad q), q=R/Omega^2"
        and "Omega^2*|grad q|^2=0" in interior["energy_test"]
        and "integral Delta Omega=0" in interior["periodic_integral"]
        and "Omega is constant" in interior["harmonic_conclusion"]
        and interior["conclusion"] == "Q(m)>0 for every m in (0,infinity)"
    )
    infinity = certificate["infinite_endpoint"]
    checks["weak_endpoint_reconstructed"] = (
        reconstruct_weak_quotient()
        == decode(infinity["value"])
        == Fraction(32, 17)
        and infinity["limit"] == "Q(infinity)=32/17"
    )
    compactness = certificate["compactness_conclusion"]
    checks["compactness_theorem_recorded"] = (
        "t in [0,1]" in compactness["continuity"]
        and compactness["theorem"]
        == "there exists c_F4>0 such that Q(m)>=c_F4 for every m>0"
        and compactness["constant_status"] == "EXISTS_NOT_COMPUTED"
        and "one-parameter" in compactness["scope"]
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["repaired_one_bubble_family_collapse"] == "RULED_OUT"
        and disposition["repaired_family_uniform_positive_quotient"]
        == "PROVED_NONQUANTITATIVELY"
        and disposition["arbitrary_smooth_periodic_bubble_collapse"] == "OPEN"
        and disposition["positive_all_field_deterministic_gradient_bound"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a numerical value for c_F4",
        "a positive gradient bound for arbitrary periodic BT fields",
        "exclusion of multi-bubble, tower, neck, or non-spherical collapse",
        "a Poincare inequality or Witten one-form theorem or obstruction",
        "an interacting residual, field, or H^-1 Gibbs moment estimate",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    receipt = certificate["tier_receipt"]
    checks["receipt_boundaries"] = (
        receipt["elapsed_seconds_and_peak_kib"]["producer_check"]
        == "0.03 seconds, 20416 KiB"
        and "REFUSED" in receipt["repository_audits"]["planning_conformance"]
        and "not a pass" in receipt["repository_audits"]["science_forge_shadow"]
    )
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
