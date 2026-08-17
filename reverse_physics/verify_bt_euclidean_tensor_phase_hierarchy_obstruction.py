#!/usr/bin/env python3
"""Independently verify the BT tensor-phase hierarchy obstruction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TENSOR_PHASE_HIERARCHY_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-tensor-phase-hierarchy-obstruction-v1.schema.json",
)


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct(member: int) -> dict[str, object]:
    m = member
    ramp = m**4
    slope = Fraction(m - 1, ramp)
    ascending = [
        Fraction(1) + slope * min(index, 2 * ramp - index)
        for index in range(2 * ramp + 1)
    ]
    edges = ascending + [
        1 / ascending[2 * ramp - index] for index in range(2 * ramp + 1)
    ]
    length = len(edges)
    rho = [
        edges[index] + 1 / edges[(index - 1) % length] - 2
        for index in range(length)
    ]
    rho_reverse = [
        1 / edges[index] + edges[(index - 1) % length] - 2
        for index in range(length)
    ]
    delta = [rho_reverse[index] - rho[index] for index in range(length)]
    flux = [
        rho[index] * edges[index]
        - rho[(index + 1) % length] / edges[index]
        for index in range(length)
    ]
    h = [flux[(index - 1) % length] - flux[index] for index in range(length)]
    first = (ramp + 1) // 2 + 1
    last = 3 * ramp // 4
    return {
        "length": length,
        "ramp": ramp,
        "rho": rho,
        "delta": delta,
        "h": h,
        "bulk": list(range(first, last + 1)),
    }


def norm_formula(data: dict[str, object], active: int) -> tuple[Fraction, Fraction]:
    """Closed combinatorial formula, independent of producer term expansion."""
    length = int(data["length"])
    rho = data["rho"]
    delta = data["delta"]
    h = data["h"]
    rho_sum = sum(rho, Fraction(0))
    rho2 = sum((value**2 for value in rho), Fraction(0))
    delta2 = sum((value**2 for value in delta), Fraction(0))
    h2 = sum((value**2 for value in h), Fraction(0))
    rho_delta = sum(
        (left * right for left, right in zip(rho, delta, strict=True)),
        Fraction(0),
    )
    h_delta = sum(
        (left * right for left, right in zip(h, delta, strict=True)),
        Fraction(0),
    )
    residual_norm = (
        active * length ** (active - 1) * rho2
        + active * (active - 1) * length ** (active - 2) * rho_sum**2
    )
    gradient_norm = active * length ** (active - 1) * h2
    gradient_norm += (
        active
        * (active - 1)
        * length ** (active - 2)
        * (delta2 * rho2 + rho_delta**2 + 2 * rho_sum * h_delta)
    )
    if active >= 3:
        gradient_norm += (
            active
            * (active - 1)
            * (active - 2)
            * length ** (active - 3)
            * delta2
            * rho_sum**2
        )
    return residual_norm, gradient_norm


def direct_two_phase_norm(data: dict[str, object]) -> tuple[Fraction, Fraction]:
    residual_norm = Fraction(0)
    gradient_norm = Fraction(0)
    for first, second in itertools.product(range(int(data["length"])), repeat=2):
        residual = data["rho"][first] + data["rho"][second]
        gradient = (
            data["h"][first]
            + data["h"][second]
            + data["delta"][first] * data["rho"][second]
            + data["rho"][first] * data["delta"][second]
        )
        residual_norm += residual**2
        gradient_norm += gradient**2
    return residual_norm, gradient_norm


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False

    input_row = certificate["provenance"]["inputs"][0]
    input_path = os.path.join(ROOT, input_row["path"])
    fixtures_ok = True
    sign_ok = True
    bound_ok = True
    for stored in certificate["exact_fixtures"]:
        data = reconstruct(stored["member"])
        bulk = data["bulk"]
        floor = Fraction(1, 8 * stored["member"] ** 2)
        fixtures_ok &= stored["length"] == data["length"]
        fixtures_ok &= stored["bulk_count"] == len(bulk)
        fixtures_ok &= stored["bulk_start"] == bulk[0]
        fixtures_ok &= stored["bulk_stop"] == bulk[-1]
        sign_ok &= all(data["rho"][index] > 0 for index in bulk)
        sign_ok &= all(data["delta"][index] < 0 for index in bulk)
        sign_ok &= all(data["h"][index] <= -floor for index in bulk)
        for row in stored["tensor_rows"]:
            residual_norm, gradient_norm = norm_formula(data, row["active_phases"])
            fixtures_ok &= dec(row["residual_norm_squared"]) == residual_norm
            fixtures_ok &= dec(row["gradient_norm_squared"]) == gradient_norm
            fixtures_ok &= dec(row["quotient"]) == gradient_norm / residual_norm
            fixtures_ok &= dec(row["quotient_scaled_by_m6"]) == (
                gradient_norm / residual_norm * stored["member"] ** 6
            )
            analytic = Fraction(
                1,
                256
                * 40 ** row["active_phases"]
                * stored["member"] ** 6,
            )
            bound_ok &= dec(row["analytic_lower_bound"]) == analytic
            bound_ok &= gradient_norm / residual_norm >= analytic

    small = reconstruct(2)
    direct_ok = direct_two_phase_norm(small) == norm_formula(small, 2)
    tags_ok = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    identity_ok = (
        certificate["tensor_identity"]["torus_gradient"]
        == "g(x)=sum_a h_(x_a)+sum_(a!=b) delta_(x_a)*rho_(x_b)"
    )
    conclusion_ok = (
        certificate["same_sign_bulk_theorem"]["quotient"]
        == "Q_k>=1/(256*40^k*m^6) for 2<=k<=4 and m>=4"
        and certificate["four_torus_corollary"]["normalized_bound"]
        == "Q_k/omega_L^2>=m^10/(16*40^k*pi^4)"
    )
    boundary_ok = (
        certificate["research_disposition"]["all_field_torus_scaled_PL"] == "OPEN"
        and certificate["research_disposition"]["nonseparable_transverse_corrector"]
        == "OPEN"
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    self_checks = certificate["checks"]
    self_ok = (
        self_checks["ok"]
        and self_checks["passed"] == 10
        and self_checks["total"] == 10
        and all(self_checks["details"].values())
    )
    return [
        ("schema", schema_ok),
        ("predecessor_hash", os.path.isfile(input_path) and file_hash(input_path) == input_row["sha256"]),
        ("fixture_metadata", fixtures_ok),
        ("same_sign_bulk", sign_ok),
        ("analytic_lower_bound", bound_ok),
        ("direct_two_phase_enumeration", direct_ok),
        ("dependency_tags", tags_ok),
        ("tensor_gradient_identity", identity_ok),
        ("free_scale_conclusion", conclusion_ok),
        ("claim_boundaries", boundary_ok),
        ("self_checks", self_ok),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(f"BT tensor-phase verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
