#!/usr/bin/env python3
"""Independent verifier for the BT heat-bath influence symbol gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_HEAT_BATH_INFLUENCE_SYMBOL_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-heat-bath-influence-symbol-gate-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def direct_laplacian(field: dict[tuple[int, ...], int], length: int) -> dict[tuple[int, ...], int]:
    result: dict[tuple[int, ...], int] = {}
    for site in product(range(length), repeat=4):
        value = 8 * field.get(site, 0)
        for axis in range(4):
            for step in (-1, 1):
                other = list(site)
                other[axis] = (other[axis] + step) % length
                value -= field.get(tuple(other), 0)
        result[site] = value
    return result


def independent_fixture(length: int = 4) -> dict[str, int | Fraction]:
    sites = list(product(range(length), repeat=4))
    origin = (0, 0, 0, 0)
    delta = {site: int(site == origin) for site in sites}
    row = direct_laplacian(direct_laplacian(delta, length), length)
    lowest = {site: (1, 0, -1, 0)[site[0]] for site in sites}
    checker = {site: (-1) ** sum(site) for site in sites}
    lowest_image = direct_laplacian(direct_laplacian(lowest, length), length)[origin]
    checker_image = direct_laplacian(direct_laplacian(checker, length), length)[origin]
    diagonal = row[origin]
    off_l1 = sum(abs(value) for site, value in row.items() if site != origin)
    return {
        "diagonal": diagonal,
        "off_l1": off_l1,
        "nonzero": sum(value != 0 for value in row.values()),
        "lowest": lowest_image,
        "checker": checker_image,
        "lowest_rate": Fraction(lowest_image, diagonal),
        "checker_response": Fraction(diagonal - checker_image, diagonal),
    }


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
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    rebuilt = independent_fixture()
    fixture = certificate["exact_l4_fixture"]
    checks["independent_l4_kernel"] = (
        rebuilt["diagonal"] == fixture["diagonal"] == 72
        and rebuilt["off_l1"] == fixture["off_diagonal_l1"] == 184
        and rebuilt["nonzero"] == fixture["nonzero_origin_row_entries"]
        and rebuilt["lowest"] == fixture["lowest_bilaplacian_eigenvalue"] == 4
        and rebuilt["checker"] == fixture["checkerboard_bilaplacian_eigenvalue"] == 256
        and rebuilt["lowest_rate"] == decode(fixture["lowest_heat_bath_rate"]) == Fraction(1, 18)
        and rebuilt["checker_response"]
        == decode(fixture["checkerboard_simultaneous_response"])
        == Fraction(-23, 9)
    )
    obstruction = certificate["absolute_influence_obstruction"]
    checks["absolute_influence_obstruction"] = (
        obstruction["total_off_diagonal_absolute_sum"] == 184
        and decode(obstruction["normalized_absolute_row_sum"]) == Fraction(23, 9) > 1
        and obstruction["checkerboard_dispersion"] == 16
        and decode(obstruction["checkerboard_response"]) == Fraction(-23, 9)
    )
    free = certificate["free_operator"]
    scaling = certificate["free_scaling"]
    checks["signed_symbol_and_scaling"] = (
        free["free_precision"] == "K=L_G^2"
        and free["summed_continuous_time_mean_generator"]
        == "Markov drift=-K/72; positive relaxation operator R_HB=K/72 on H"
        and free["simultaneous_fourier_symbol"] == "tau(p)=1-omega(p)^2/72"
        and scaling["slow_heat_bath_rate"]
        == "gamma_L=omega_L^2/72=(2/9)*sin(pi/L)^4"
        and scaling["asymptotic"] == "gamma_L~(2*pi^4)/(9*L^4)"
    )
    response = certificate["interacting_response_identity"]
    checks["nonlinear_response_boundary"] = (
        response["exact_derivative"]
        == "D_k m_o(eta)=-Cov_q_eta(s,D_k S) for k in h_o^perp"
        and response["response_bound"]
        == "|D_k m_o(eta)|<=1/2*sqrt(E_q_eta[(Hess S[h_o,k])^2])"
        and response["status"] == "EXACT_REDUCTION_ESTIMATE_OPEN"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["absolute_dobrushin_contraction"] == "OBSTRUCTED_ALREADY_FREE"
        and disposition["signed_fourier_multiscale_influence"] == "OPEN"
        and disposition["volume_uniform_global_poincare"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "failure of every influence, heat-bath, or local-to-global method",
        "a global finite-volume or volume-uniform Poincare/Witten theorem",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound",
        "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
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
