#!/usr/bin/env python3
"""Nonimporting Laurent-Fourier verifier for separable BT coercivity."""

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
    "SEPARABLE_PRODUCT_GRADIENT_COERCIVITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "separable-product-gradient-coercivity-v1.schema.json",
)
Gaussian = tuple[Fraction, Fraction]
Polynomial = dict[tuple[int, int], Gaussian]
ZERO: Gaussian = (Fraction(0), Fraction(0))


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return (left[0] + right[0], left[1] + right[1])


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def add(*polynomials: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for polynomial in polynomials:
        for mode, value in polynomial.items():
            out[mode] = gadd(out.get(mode, ZERO), value)
            if out[mode] == ZERO:
                del out[mode]
    return out


def scale(polynomial: Polynomial, scalar: Fraction | int) -> Polynomial:
    scalar = Fraction(scalar)
    return {
        mode: (scalar * value[0], scalar * value[1])
        for mode, value in polynomial.items()
        if value != ZERO
    }


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = (left_mode[0] + right_mode[0], left_mode[1] + right_mode[1])
            out[mode] = gadd(out.get(mode, ZERO), gmul(left_value, right_value))
    return {mode: value for mode, value in out.items() if value != ZERO}


def derivative(polynomial: Polynomial, axis: int) -> Polynomial:
    out: Polynomial = {}
    for mode, (real, imaginary) in polynomial.items():
        frequency = mode[axis]
        if frequency:
            out[mode] = (-frequency * imaginary, frequency * real)
    return out


def norm_squared(polynomial: Polynomial) -> Fraction:
    return sum(
        (real * real + imaginary * imaginary for real, imaginary in polynomial.values()),
        Fraction(0),
    )


def sine(axis: int, amplitude: int) -> Polynomial:
    plus = [0, 0]
    minus = [0, 0]
    plus[axis] = 1
    minus[axis] = -1
    return {
        tuple(plus): (Fraction(0), Fraction(-amplitude, 2)),
        tuple(minus): (Fraction(0), Fraction(amplitude, 2)),
    }


def independently_reconstruct_fixture() -> dict[str, Fraction]:
    u_one = sine(0, 1)
    u_two = sine(1, 2)
    r_one = add(derivative(u_one, 0), multiply(u_one, u_one))
    r_two = add(derivative(u_two, 1), multiply(u_two, u_two))
    residual = add(r_one, r_two)
    laplacian_residual = add(
        derivative(derivative(residual, 0), 0),
        derivative(derivative(residual, 1), 1),
    )
    divergence = add(
        derivative(multiply(residual, u_one), 0),
        derivative(multiply(residual, u_two), 1),
    )
    euler = add(laplacian_residual, scale(divergence, -2))

    z_one = Fraction(1, 2)
    z_two = Fraction(2)
    e_one = add(
        derivative(derivative(r_one, 0), 0),
        scale(derivative(multiply(r_one, u_one), 0), -2),
        scale(derivative(u_one, 0), -2 * z_two),
    )
    e_two = add(
        derivative(derivative(r_two, 1), 1),
        scale(derivative(multiply(r_two, u_two), 1), -2),
        scale(derivative(u_two, 1), -2 * z_one),
    )
    centered_r_one = add(r_one, {(0, 0): (-z_one, Fraction(0))})
    centered_r_two = add(r_two, {(0, 0): (-z_two, Fraction(0))})
    pair = scale(
        add(multiply(derivative(u_one, 0), centered_r_two),
            multiply(derivative(u_two, 1), centered_r_one)),
        -2,
    )
    return {
        "residual_norm": norm_squared(residual),
        "euler_norm": norm_squared(euler),
        "first_one_body_norm": norm_squared(e_one),
        "second_one_body_norm": norm_squared(e_two),
        "pair_norm": norm_squared(pair),
        "decomposition_difference_norm": norm_squared(add(euler, scale(e_one, -1), scale(e_two, -1), scale(pair, -1))),
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
        file_hash(item["path"]) == item["sha256"] for item in inputs
    )
    fixture = certificate["exact_fixture"]
    rebuilt = independently_reconstruct_fixture()
    checks["residual_norm_reconstructed"] = (
        rebuilt["residual_norm"] == decode(fixture["total_residual_norm_squared"])
        == Fraction(87, 8)
    )
    checks["euler_norm_reconstructed"] = (
        rebuilt["euler_norm"] == decode(fixture["total_euler_norm_squared"])
        == Fraction(973, 4)
    )
    checks["anova_decomposition_reconstructed"] = (
        rebuilt["first_one_body_norm"] == decode(fixture["one_body_euler_norms_squared"][0])
        and rebuilt["second_one_body_norm"] == decode(fixture["one_body_euler_norms_squared"][1])
        and rebuilt["pair_norm"] == decode(fixture["two_body_euler_norm_squared"])
        and rebuilt["decomposition_difference_norm"] == 0
    )
    checks["sharp_gap_reconstructed"] = (
        rebuilt["euler_norm"] - rebuilt["residual_norm"]
        == decode(fixture["sharp_bound_slack"])
        and rebuilt["euler_norm"] > rebuilt["residual_norm"]
    )
    theorem = certificate["theorem"]
    proof = certificate["proof_chain"]
    checks["proof_chain_recorded"] = (
        theorem["conclusion"] == "||E||_2^2>=k_1^4||R||_2^2"
        and "Q_i^2/Z_i" in proof["poincare_cauchy"]
        and "S+2S^2+X+2Y" in proof["mean_control_unit_scale"]
        and "scaling restores k_1^4" in proof["closure"]
    )
    checks["method_boundary"] = certificate["method_disposition"] == {
        "coordinate_separable_continuum_gradient_collapse": "RULED_OUT",
        "sharp_free_coefficient_in_separable_class": "PROVED",
        "nonseparable_continuum_gradient_collapse": "OPEN",
        "lattice_all_field_gradient_bound": "OPEN",
        "background_marginal_hyperuniformity": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "a theorem for arbitrary nonseparable fields",
        "the all-field lattice gradient constant",
        "a Poincare inequality, Witten coercivity, or interacting H^-1 bound",
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
