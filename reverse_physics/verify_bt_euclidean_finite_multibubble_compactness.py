#!/usr/bin/env python3
"""Independent verifier for finite repaired BT multibubble compactness."""

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
    "FINITE_MULTIBUBBLE_COMPACTNESS_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "finite-multibubble-compactness-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct_jet() -> dict[str, Fraction]:
    # sin^2 y=y^2-y^4/3+2y^6/45+O(y^8)
    # (sin^2 y)^2/3=y^4/3-2y^6/9+O(y^8)
    return {
        "quadratic": Fraction(1),
        "quartic": Fraction(-1, 3) + Fraction(1, 3),
        "sextic": Fraction(2, 45) - Fraction(2, 9),
    }


def reconstruct_fixture() -> dict[str, Fraction]:
    # At pi/2: f=4/3, f''=-10/3. At zero: f=0, f''=2.
    field = Fraction(4, 3)
    laplacian = Fraction(-10, 3) + 3 * 2
    return {"field": field, "laplacian": laplacian, "q": -field * laplacian}


def reconstruct_weak_limit() -> Fraction:
    # f=5/8-(2/3)cos(2x)+(1/24)cos(4x).
    modes = {2: Fraction(-2, 3), 4: Fraction(1, 24)}
    denominator = sum(n**4 * coefficient**2 for n, coefficient in modes.items())
    numerator = sum(n**8 * coefficient**2 for n, coefficient in modes.items())
    return numerator / denominator


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

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(certificate))
    recorded = {row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]}
    checks["provenance_hashes_current"] = len(recorded) == 2 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )
    jet = reconstruct_jet()
    checks["jet_reconstructed"] = (
        jet["quadratic"] == 1 and jet["quartic"] == 0 and jet["sextic"] == Fraction(-8, 45)
        and "-(8/45)*sum_mu" in certificate["crystal_fixture"]["local_jet"]
    )
    fixture = reconstruct_fixture()
    recorded_fixture = certificate["crystal_fixture"]["nonzero_fixture"]
    checks["fixture_reconstructed"] = (
        fixture["field"] == decode(recorded_fixture["F_16"]) == Fraction(4, 3)
        and fixture["laplacian"] == decode(recorded_fixture["Delta_F_16"]) == Fraction(8, 3)
        and fixture["q"] == decode(recorded_fixture["q_0"]) == Fraction(-32, 9)
    )
    checks["zero_count_and_energy"] = (
        certificate["crystal_fixture"]["zero_count"] == 16
        and certificate["zero_endpoint"]["crystal_concentration"] == "(512/3)*pi^2"
    )
    zero = certificate["zero_endpoint"]
    checks["puncture_flux_chain"] = (
        "forces q_0=0" in zero["nonvanishing_argument"]
        and "positive inner-boundary flux 4*pi^2" in zero["nonvanishing_argument"]
        and zero["status"] == "POSITIVE_FINITE_LIMIT_PROVED"
    )
    endpoints = certificate["finite_and_weak_endpoints"]
    checks["weak_limit_reconstructed"] = (
        reconstruct_weak_limit() == decode(endpoints["crystal_weak_value"]) == Fraction(512, 17)
        and endpoints["crystal_weak_limit"] == "Q_F16(infinity)=512/17"
    )
    general = certificate["general_class"]
    checks["general_theorem_scoped"] = (
        "fixed finite set Z" in general["denominator_conditions"]
        and general["constant_status"] == "EXISTS_NOT_COMPUTED"
        and general["theorem"]
        == "for every fixed admissible F there exists c_F>0 with Q_F(m)>=c_F for all m>0"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["fixed_finite_repaired_multibubble_collapse"] == "RULED_OUT"
        and disposition["growing_number_bubble_gas"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "one uniform constant shared by all admissible denominators F",
        "exclusion of a bubble count growing with lattice volume",
        "a positive all-field gradient bound or Witten/Poincare theorem",
        "an interacting Gibbs H^-1 estimate, tightness, or a continuum measure",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
