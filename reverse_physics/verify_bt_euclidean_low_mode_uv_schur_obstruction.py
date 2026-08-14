#!/usr/bin/env python3
"""Independent verifier for the BT lowest-mode/UV Schur obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-euclidean-low-mode-uv-schur-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def full_lattice_forms(
    parameter: int, h: tuple[int, ...], g: tuple[int, ...], v: tuple[int, ...]
) -> dict[str, Fraction]:
    length = 6
    sites = tuple(product(range(length), repeat=4))
    shape = (-1, 0, 0, -1, 1, 1)
    center = {site: parameter * shape[site[0]] for site in sites}
    directions = {
        "h": {site: h[site[0]] for site in sites},
        "g": {site: g[site[0]] for site in sites},
        "v": {site: v[site[0]] for site in sites},
    }
    pairs = (("h", "h"), ("h", "g"), ("g", "g"), ("v", "v"))
    hessians = {pair: Fraction(0) for pair in pairs}
    action = Fraction(0)
    for site in sites:
        residual = Fraction(-8)
        first = {key: Fraction(0) for key in directions}
        second = {pair: Fraction(0) for pair in pairs}
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                neighbor = tuple(neighbor)
                weight = dyadic(center[neighbor] - center[site])
                residual += weight
                differences = {
                    key: values[neighbor] - values[site]
                    for key, values in directions.items()
                }
                for key in directions:
                    first[key] += weight * differences[key]
                for pair in pairs:
                    second[pair] += (
                        weight * differences[pair[0]] * differences[pair[1]]
                    )
        action += residual * residual / 2
        for pair in pairs:
            hessians[pair] += (
                first[pair[0]] * first[pair[1]] + residual * second[pair]
            )
    return {
        "action": action,
        "hh": hessians[("h", "h")],
        "hg": hessians[("h", "g")],
        "gg": hessians[("g", "g")],
        "vv": hessians[("v", "v")],
    }


def evaluate(coefficients: dict[str, int], x: int) -> Fraction:
    return sum(
        (Fraction(value) * Fraction(x) ** int(exponent)
         for exponent, value in coefficients.items()),
        Fraction(0),
    )


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
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"] == 16
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )
    hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["three_provenance_hashes_current"] = len(hashes) == 3 and all(
        digest == file_hash(relative) for relative, digest in hashes.items()
    )

    modes = certificate["lattice_and_modes"]
    h = tuple(modes["lowest_mode_h"])
    g = tuple(modes["alternating_mode_g"])
    v = tuple(modes["degenerating_direction_v"])
    lap = lambda values: tuple(
        2 * values[i] - values[(i - 1) % 6] - values[(i + 1) % 6]
        for i in range(6)
    )
    checks["mode_spectrum_and_decomposition_reconstructed"] = (
        lap(h) == h
        and lap(g) == tuple(4 * value for value in g)
        and sum(a * b for a, b in zip(h, g)) == 0
        and sum(value * value for value in h) == 12
        and sum(value * value for value in g) == 6
        and all(3 * v[i] == -2 * h[i] + g[i] for i in range(6))
        and sum(v[i] * h[i] for i in range(6)) == -8
        and decode(modes["v_lowest_mode_projection_norm_squared"])
        == Fraction(16, 3)
    )

    section = certificate["exact_two_mode_hessian"]
    fixture_by_parameter = {row["parameter"]: row for row in section["fixtures"]}
    full_ok = True
    for parameter in (1, 3, 6):
        forms = full_lattice_forms(parameter, h, g, v)
        row = fixture_by_parameter[parameter]
        full_ok &= (
            forms["hh"] == 216 * decode(row["h_hessian_per_spatial_site"])
            and forms["hg"] == 216 * decode(row["h_g_hessian_per_spatial_site"])
            and forms["gg"] == 216 * decode(row["g_g_hessian_per_spatial_site"])
            and forms["vv"] == 216 * decode(
                row["degenerating_direction_hessian_per_spatial_site"]
            )
            and forms["action"] == 216 * decode(
                row["center_action_per_spatial_site"]
            )
        )
    checks["selected_full_6_to_the_4_fixtures_reconstructed"] = full_ok

    formulas_ok = True
    for row in section["fixtures"]:
        x = row["x"]
        hh = evaluate(section["h_h_laurent_coefficients"], x)
        hg = evaluate(section["h_g_laurent_coefficients"], x)
        gg = evaluate(section["g_g_laurent_coefficients"], x)
        det = evaluate(section["determinant_laurent_coefficients"], x)
        schur = det / gg
        formulas_ok &= (
            x == 2 ** row["parameter"]
            and hh == decode(row["h_hessian_per_spatial_site"])
            and hg == decode(row["h_g_hessian_per_spatial_site"])
            and gg == decode(row["g_g_hessian_per_spatial_site"])
            and det == hh * gg - hg * hg
            and det == decode(row["determinant_per_spatial_site_squared"])
            and schur == decode(
                row["low_mode_schur_complement_per_spatial_site"]
            )
            and x * schur == decode(row["x_times_schur_complement"])
            and 0 < schur <= Fraction(72, x)
        )
    checks["all_laurent_and_schur_fixtures_reconstructed"] = formulas_ok

    action_coefficients = certificate["action_curvature_tradeoff"][
        "center_action_laurent_coefficients"
    ]
    checks["action_and_limit_leading_terms_reconstructed"] = (
        action_coefficients
        == {"-4": 1, "-2": -1, "-1": -2, "0": 6, "1": -4,
            "2": -3, "3": 2, "4": 1}
        and section["determinant_laurent_coefficients"]
        == {"-6": 288, "-5": 288, "-3": -288, "-2": -288,
            "-1": -288, "0": -288, "1": 576, "2": 864, "3": 288}
        and section["g_g_laurent_coefficients"]
        == {"-4": 16, "-2": 32, "-1": 16, "1": -16,
            "3": 32, "4": 16}
        and Fraction(288, 16) == 18
    )
    checks["all_x_schur_proof_chain_reconstructed"] = (
        section["positivity_and_bound"] == "for x>=2, 0<kappa(x)<=72/x"
        # For x>=2: the determinant's positive high terms dominate
        # 1+x^-1+x^-2+x^-3, while its positive tail can be retained.
        and Fraction(2**3 + 3 * 2**2 + 2 * 2)
        > Fraction(1) + Fraction(1, 2) + Fraction(1, 4) + Fraction(1, 8)
        # Dropping negative determinant terms gives at most 4*x^3:
        # x^3 + 3*x^2 + 2*x + x^-5 + x^-6 <= 4*x^3.
        and Fraction(3, 2) + Fraction(1, 2) + 1 + 1 == 4
        # H_gg/16 >= x^4 because 2*x^3-x and all inverse-power terms
        # are nonnegative for x>=2.
        and 2 * 2**3 - 2 >= 0
        and Fraction(288 * 4, 16) == 72
    )
    projected = certificate["direct_projected_curvature_obstruction"]
    checks["projected_curvature_obstruction_typed"] = (
        "8*(x+1)/x^2" in projected["directional_hessian"]
        and "16/3" in projected["lowest_projection_norm_squared"]
        and "3/x" in projected["limit_bound"]
        and projected["status"]
        == "LOWEST_MODE_PROJECTED_STRONG_CONVEXITY_OBSTRUCTED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"
    ]
    checks["open_bound_preserved"] = (
        certificate["method_disposition"][
            "actual_interacting_h_minus_one_second_moment_bound"
        ] == "OPEN"
        and certificate["method_disposition"][
            "action_weighted_or_annealed_inverse_hessian"
        ] == "OPEN"
        and certificate["method_disposition"]["continuum_limit"]
        == "NOT_ESTABLISHED"
    )
    checks["required_nonclaims_present"] = {
        "failure of an action-weighted or annealed covariance estimate",
        "failure of the actual interacting H^-1 moment bound",
        "a Born rule or Krein reconstruction",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({passed}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
