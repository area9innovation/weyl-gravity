#!/usr/bin/env python3
"""Non-importing verifier for the BT inhomogeneous-twist gauge obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_INHOMOGENEOUS_TWIST_GAUGE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-inhomogeneous-twist-gauge-obstruction-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TWIST_RESPONSE_GATE_V1.json",
]


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_cycle_fixture() -> dict:
    omega = tuple(Fraction(value) for value in (1, 2, 1, Fraction(1, 2)))
    gauge = tuple(Fraction(value) for value in (2, 1, Fraction(1, 2), 1))
    transformed = tuple(a * b for a, b in zip(omega, gauge))
    twisted = []
    direct = []
    forward = []
    for site in range(4):
        twisted.append(sum(
            (
                omega[target] / omega[site]
                * gauge[target] / gauge[site]
                for target in ((site - 1) % 4, (site + 1) % 4)
            ),
            Fraction(),
        ) - 2)
        direct.append(
            (
                transformed[(site - 1) % 4]
                + transformed[(site + 1) % 4]
            ) / transformed[site] - 2
        )
        forward.append(gauge[(site + 1) % 4] / gauge[site])
    product = Fraction(1)
    for value in forward:
        product *= value
    return {
        "omega": omega,
        "gauge": gauge,
        "transformed": transformed,
        "twisted": tuple(twisted),
        "direct": tuple(direct),
        "forward": tuple(forward),
        "holonomy": product,
        "action": sum((value * value for value in direct), Fraction()) / 2,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False
    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hash_current"] = (
        [item.get("path") for item in inputs] == EXPECTED_INPUTS
        and all(item.get("sha256") == file_hash(item["path"]) for item in inputs)
        and cert.get("provenance", {}).get("repository_base_commit")
        == "f8e6ca946f13ed83549758e715f55a92dcca1a55"
    )

    exact = independent_cycle_fixture()
    public = cert.get("exact_cycle_four_fixture", {})
    checks["independent_rational_fixture"] = (
        exact["twisted"] == exact["direct"]
        == (Fraction(-3, 4), Fraction(-3, 4), 3, 3)
        and exact["holonomy"] == 1
        and exact["action"] == Fraction(153, 16)
        and [dec(value) for value in public.get("omega", [])]
        == list(exact["omega"])
        and [dec(value) for value in public.get("gauge_multiplier", [])]
        == list(exact["gauge"])
        and [dec(value) for value in public.get("transformed_omega", [])]
        == list(exact["transformed"])
        and [dec(value) for value in public.get("forward_gradient_multipliers", [])]
        == list(exact["forward"])
        and [dec(value) for value in public.get("twisted_residual", [])]
        == list(exact["twisted"])
        and dec(public.get("gradient_holonomy", {})) == 1
        and dec(public.get("action", {})) == Fraction(153, 16)
        and dec(public.get("uniform_multiplier_two_holonomy", {})) == 16
    )

    theorem = cert.get("gauge_covariance_theorem", {})
    checks["gauge_covariance_identity"] = (
        theorem.get("oriented_edge_twist") == "theta_yx=-theta_xy"
        and theorem.get("site_coboundary") == "(d chi)_xy=chi_y-chi_x"
        and theorem.get("pointwise_identity")
        == "r_x^(theta+dchi)(psi)=r_x^theta(psi+chi)"
        and theorem.get("action_identity")
        == "A_(theta+dchi)(psi)=A_theta(psi+chi)"
        and theorem.get("partition_function_identity")
        == "Z[theta+dchi]=Z[theta] for every periodic chi"
        and theorem.get("status") == "PROVED_EXACTLY"
    )

    ward = cert.get("longitudinal_ward_nullspace", {})
    checks["longitudinal_ward_nullspace"] = (
        ward.get("first_derivative") == "D F(theta)[dchi]=0"
        and ward.get("response_hessian") == "R_theta=D^2F(theta)"
        and ward.get("right_nullspace") == "R_theta*d=0"
        and ward.get("left_nullspace")
        == "d^*R_theta=0 by symmetry of the Hessian"
        and ward.get("status") == "PROVED_EXACTLY"
    )

    harmonic = cert.get("harmonic_uniform_sector", {})
    checks["harmonic_nonexact_sector"] = (
        harmonic.get("closed") == "zero plaquette curl"
        and harmonic.get("co_closed") == "zero lattice divergence"
        and harmonic.get("period") == "sum along the mu cycle=L*tau"
        and "not exact" in harmonic.get("nonexact", "")
        and harmonic.get("status") == "PROVED_FINITE_TORUS"
    )

    disposition = cert.get("route_disposition", {})
    checks["claim_and_route_boundary"] = (
        disposition.get("longitudinal_inhomogeneous_twist_response")
        == "EXACTLY_ZERO_BY_GAUGE_WARD"
        and disposition.get("twist_response_to_scalar_witten_coercivity")
        == "OBSTRUCTED"
        and disposition.get("twist_response_to_interacting_h_minus_one")
        == "OBSTRUCTED_AS_PROOF_ROUTE"
        and disposition.get("source_generating_functional_covariance") == "LIVE"
        and disposition.get("actual_interacting_h_minus_one_second_moment") == "OPEN"
        and any(
            "LORENTZIAN-CAUSAL" in item
            for item in cert.get("does_not_establish", [])
        )
    )
    published = cert.get("checks", {})
    checks["producer_checks_consistent"] = (
        published.get("ok") is True
        and published.get("passed") == published.get("total") == 16
        and published.get("failures") == []
        and all(published.get("details", {}).values())
    )
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    ok = all(checks.values())
    print(
        "BT inhomogeneous-twist gauge obstruction independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
