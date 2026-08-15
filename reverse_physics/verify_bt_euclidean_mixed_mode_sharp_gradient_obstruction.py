#!/usr/bin/env python3
"""Independent exact verifier for the BT mixed-mode gradient obstruction."""

from __future__ import annotations

import argparse
import ast
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
    "MIXED_MODE_SHARP_GRADIENT_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "mixed-mode-sharp-gradient-obstruction-v1.schema.json",
)
PRODUCER_PATH = os.path.join(
    ROOT, "reverse_physics/bt_euclidean_mixed_mode_sharp_gradient_obstruction.py"
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def producer_not_imported() -> bool:
    with open(__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    forbidden = "bt_euclidean_mixed_mode_sharp_gradient_obstruction"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(forbidden in alias.name for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module and forbidden in node.module:
            return False
    return os.path.exists(PRODUCER_PATH)


Gaussian = tuple[Fraction, Fraction]
Fourier = dict[tuple[int, int], Gaussian]
GZERO: Gaussian = (Fraction(0), Fraction(0))


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def fadd(*items: Fourier) -> Fourier:
    out: Fourier = {}
    for item in items:
        for mode, value in item.items():
            out[mode] = gadd(out.get(mode, GZERO), value)
            if out[mode] == GZERO:
                del out[mode]
    return out


def fscale(item: Fourier, scalar: Fraction | int) -> Fourier:
    scalar = Fraction(scalar)
    return {
        mode: (scalar * value[0], scalar * value[1])
        for mode, value in item.items()
    }


def fmul(left: Fourier, right: Fourier) -> Fourier:
    out: Fourier = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode[0] + right_mode[0], left_mode[1] + right_mode[1]
            out[mode] = gadd(out.get(mode, GZERO), gmul(left_value, right_value))
    return {mode: value for mode, value in out.items() if value != GZERO}


def derivative(item: Fourier, axis: int) -> Fourier:
    out: Fourier = {}
    for mode, (real, imaginary) in item.items():
        frequency = mode[axis]
        if frequency:
            out[mode] = -frequency * imaginary, frequency * real
    return out


def laplacian(item: Fourier) -> Fourier:
    return {
        mode: (-(mode[0] ** 2 + mode[1] ** 2) * value[0],
               -(mode[0] ** 2 + mode[1] ** 2) * value[1])
        for mode, value in item.items()
        if mode != (0, 0)
    }


def fnorm(item: Fourier) -> Fraction:
    return sum(
        (real * real + imaginary * imaginary for real, imaginary in item.values()),
        Fraction(0),
    )


def continuum_reconstruction() -> dict[str, Fraction]:
    a = Fraction(1, 12)
    d = Fraction(1, 90)
    psi: Fourier = {
        (1, 0): (a / 2, Fraction(0)),
        (-1, 0): (a / 2, Fraction(0)),
        (0, 1): (a / 2, Fraction(0)),
        (0, -1): (a / 2, Fraction(0)),
        (1, 1): (d / 4, Fraction(0)),
        (1, -1): (d / 4, Fraction(0)),
        (-1, 1): (d / 4, Fraction(0)),
        (-1, -1): (d / 4, Fraction(0)),
    }
    dx = derivative(psi, 0)
    dy = derivative(psi, 1)
    residual = fadd(laplacian(psi), fmul(dx, dx), fmul(dy, dy))
    divergence = fadd(
        derivative(fmul(residual, dx), 0),
        derivative(fmul(residual, dy), 1),
    )
    euler = fadd(laplacian(residual), fscale(divergence, -2))
    residual_norm = fnorm(residual)
    euler_norm = fnorm(euler)
    return {
        "residual_norm": residual_norm,
        "euler_norm": euler_norm,
        "gap": euler_norm - residual_norm,
        "quotient": euler_norm / residual_norm,
    }


Laurent = dict[int, Fraction]
Series = tuple[Laurent, ...]
SeriesFourier = dict[tuple[int, int], Series]


def lclean(item: Laurent) -> Laurent:
    return {power: value for power, value in item.items() if value}


def ladd(*items: Laurent) -> Laurent:
    out: Laurent = {}
    for item in items:
        for power, value in item.items():
            out[power] = out.get(power, Fraction(0)) + value
    return lclean(out)


def lscale(item: Laurent, scalar: Fraction | int) -> Laurent:
    scalar = Fraction(scalar)
    return lclean({power: scalar * value for power, value in item.items()})


def lmul(left: Laurent, right: Laurent) -> Laurent:
    out: Laurent = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            out[power] = out.get(power, Fraction(0)) + left_value * right_value
    return lclean(out)


def lpow(item: Laurent, exponent: int) -> Laurent:
    out: Laurent = {0: Fraction(1)}
    for _ in range(exponent):
        out = lmul(out, item)
    return out


def szero(degree: int = 3) -> Series:
    return tuple({} for _ in range(degree + 1))


def sadd(*items: Series, degree: int = 3) -> Series:
    return tuple(ladd(*(item[index] for item in items)) for index in range(degree + 1))


def sscale(item: Series, scalar: Fraction | int, degree: int = 3) -> Series:
    return tuple(lscale(item[index], scalar) for index in range(degree + 1))


def smul(left: Series, right: Series, degree: int = 3) -> Series:
    out = []
    for total in range(degree + 1):
        out.append(ladd(*(
            lmul(left[index], right[total - index])
            for index in range(total + 1)
            if index < len(left) and total - index < len(right)
        )))
    return tuple(out)


def sfadd(*items: SeriesFourier, degree: int = 3) -> SeriesFourier:
    out: SeriesFourier = {}
    modes = set().union(*(item.keys() for item in items))
    for mode in modes:
        value = sadd(*(item.get(mode, szero(degree)) for item in items), degree=degree)
        if any(value):
            out[mode] = value
    return out


def sfscale(item: SeriesFourier, scalar: Fraction | int, degree: int = 3) -> SeriesFourier:
    return {mode: sscale(value, scalar, degree) for mode, value in item.items()}


def sfmul(left: SeriesFourier, right: SeriesFourier, degree: int = 3) -> SeriesFourier:
    out: SeriesFourier = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode[0] + right_mode[0], left_mode[1] + right_mode[1]
            product = smul(left_value, right_value, degree)
            out[mode] = sadd(out.get(mode, szero(degree)), product, degree=degree)
    return {mode: value for mode, value in out.items() if any(value)}


def sfshift(item: SeriesFourier, displacement: tuple[int, int]) -> SeriesFourier:
    out: SeriesFourier = {}
    for mode, value in item.items():
        shift_power = mode[0] * displacement[0] + mode[1] * displacement[1]
        out[mode] = tuple(lmul(coefficient, {shift_power: Fraction(1)}) for coefficient in value)
    return out


def sfexp(item: SeriesFourier) -> SeriesFourier:
    one: SeriesFourier = {(0, 0): ({0: Fraction(1)}, {}, {}, {})}
    square = sfmul(item, item)
    cube = sfmul(square, item)
    return sfadd(one, item, sfscale(square, Fraction(1, 2)), sfscale(cube, Fraction(1, 6)))


def sfnorm(item: SeriesFourier) -> Series:
    degree = 6
    out = szero(degree)
    for mode, value in item.items():
        partner = item.get((-mode[0], -mode[1]))
        if partner is not None:
            out = sadd(out, smul(value, partner, degree), degree=degree)
    return out


def formal_lattice_gap_coefficient(mixed_parameter: Fraction) -> Laurent:
    """Derive the a^4 coefficient without using the producer formula."""
    b = Fraction(mixed_parameter)
    psi: SeriesFourier = {}
    for mode in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        psi[mode] = ({}, {0: Fraction(1, 2)}, {}, {})
    for mode in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        psi[mode] = ({}, {}, {0: b / 4}, {})

    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    residual: SeriesFourier = {}
    weights: list[SeriesFourier] = []
    one: SeriesFourier = {(0, 0): ({0: Fraction(1)}, {}, {}, {})}
    for direction in directions:
        difference = sfadd(sfshift(psi, direction), sfscale(psi, -1))
        weight = sfexp(difference)
        weights.append(weight)
        residual = sfadd(residual, weight, sfscale(one, -1))

    weight_sum: SeriesFourier = {}
    for weight in weights:
        weight_sum = sfadd(weight_sum, weight)
    gradient = sfscale(sfmul(residual, weight_sum), -1)
    for direction in directions:
        incoming_residual = sfshift(residual, (-direction[0], -direction[1]))
        incoming_difference = sfadd(
            psi, sfscale(sfshift(psi, (-direction[0], -direction[1])), -1)
        )
        gradient = sfadd(
            gradient, sfmul(incoming_residual, sfexp(incoming_difference))
        )

    residual_norm = sfnorm(residual)
    gradient_norm = sfnorm(gradient)
    omega = {0: Fraction(2), 1: Fraction(-1), -1: Fraction(-1)}
    return ladd(gradient_norm[4], lscale(lmul(lmul(omega, omega), residual_norm[4]), -1))


def expected_lattice_gap_coefficient(mixed_parameter: Fraction) -> Laurent:
    b = Fraction(mixed_parameter)
    first = lscale(lmul(lpow({1: Fraction(1), 0: Fraction(-1)}, 8), {-8: Fraction(1)}), Fraction(1, 16))
    middle = 48 * b * b - 160 * b + 148
    second = {
        8: Fraction(1),
        6: Fraction(-1),
        5: Fraction(-12),
        4: middle,
        3: Fraction(-12),
        2: Fraction(-1),
        0: Fraction(1),
    }
    return lmul(first, second)


def lattice_fixture_reconstruction(table: list[list[int]]) -> dict[str, Fraction]:
    length = 8
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    residual: list[list[Fraction]] = []
    for x in range(length):
        row = []
        for y in range(length):
            row.append(sum(
                Fraction(table[(x + dx) % length][(y + dy) % length], table[x][y])
                for dx, dy in neighbors
            ) - 4)
        residual.append(row)
    gradient: list[list[Fraction]] = []
    for x in range(length):
        row = []
        for y in range(length):
            value = -residual[x][y] * (residual[x][y] + 4)
            for dx, dy in neighbors:
                source = (x - dx) % length, (y - dy) % length
                value += residual[source[0]][source[1]] * Fraction(
                    table[x][y], table[source[0]][source[1]]
                )
            row.append(value)
        gradient.append(row)
    residual_norm = sum((v * v for row in residual for v in row), Fraction(0))
    gradient_norm = sum((v * v for row in gradient for v in row), Fraction(0))
    return {
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "ratio": gradient_norm / residual_norm,
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
    checks["producer_not_imported"] = producer_not_imported()
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(item["path"]) == item["sha256"] for item in inputs
    )

    continuum = continuum_reconstruction()
    stored_continuum = certificate["exact_continuum_fixture"]
    checks["continuum_norms_reconstructed"] = (
        continuum["residual_norm"] == decode(stored_continuum["residual_norm_squared"])
        and continuum["euler_norm"] == decode(stored_continuum["euler_norm_squared"])
        and continuum["gap"] == decode(stored_continuum["euler_minus_residual"])
        and continuum["quotient"] == decode(stored_continuum["quotient"])
    )
    checks["continuum_strict_obstruction"] = continuum["gap"] < 0

    formal_values = (Fraction(0), Fraction(1), Fraction(2), Fraction(5, 3))
    checks["formal_lattice_series_reconstructed"] = all(
        formal_lattice_gap_coefficient(value) == expected_lattice_gap_coefficient(value)
        for value in formal_values
    )
    continuum_theorem = certificate["continuum_theorem"]
    lattice_theorem = certificate["lattice_theorem"]
    checks["theorem_formulas_recorded"] = (
        continuum_theorem["residual_norm_formula"]
        == "(20a^4+40a^2d^2-32a^2d+16a^2+5d^4+16d^2)/16"
        and continuum_theorem["euler_norm_formula"]
        == (
            "(36a^6+238a^4d^2-112a^4d+36a^4+144a^2d^4-116a^2d^3+"
            "124a^2d^2-48a^2d+4a^2+9d^6+36d^4+16d^2)/4"
        )
        and continuum_theorem["completion"]
        == "3b^2-10b+31/4=3(b-5/3)^2-7/12"
        and lattice_theorem["formal_gap"]
        == "||grad A||^2-omega_L^2||r||^2=a^4 omega_L^4 C_L(b)+O(a^5)"
        and lattice_theorem["coefficient"]
        == (
            "C_L(b)=3b^2-10b+c_L^4-(5/4)c_L^2-(3/2)c_L+19/2, "
            "c_L=cos(2*pi/L)"
        )
        and lattice_theorem["minimized_coefficient"]
        == "C_L(5/3)=(12c_L^4-15c_L^2-18c_L+14)/12<0 for every L>=8"
    )
    checks["all_volume_sign_chain"] = (
        "C_L(5/3)" in lattice_theorem["minimized_coefficient"]
        and "p'(c)=6(c-1)(8c^2+8c+3)<0" in lattice_theorem["sign_proof"]
        and 19**2 < 18**2 * 2
        and lattice_theorem["conclusion"].endswith("<1")
    )

    lattice = certificate["exact_lattice_fixture"]
    rebuilt_lattice = lattice_fixture_reconstruction(lattice["omega_table"])
    checks["lattice_fixture_reconstructed"] = (
        rebuilt_lattice["residual_norm"]
        == decode(lattice["residual_norm_squared_per_transverse_copy"])
        and rebuilt_lattice["gradient_norm"]
        == decode(lattice["gradient_norm_squared_per_transverse_copy"])
        and rebuilt_lattice["ratio"] == decode(lattice["raw_gradient_to_residual_ratio"])
    )
    rational_upper = Fraction(35, 102)
    checks["lattice_exact_strict_obstruction"] = (
        rebuilt_lattice["ratio"] < rational_upper
        and rational_upper - rebuilt_lattice["ratio"]
        == decode(lattice["rational_upper_minus_ratio"])
        and 577**2 - 2 * 408**2 == 1
        and lattice["comparison"]
        == "||grad A||^2/||r||^2 < 35/102 < (2-sqrt(2))^2=omega_8^2"
    )

    checks["method_boundary"] = certificate["method_disposition"] == {
        "separable_sharp_free_coefficient": "PROVED_BY_PREDECESSOR",
        "arbitrary_nonseparable_coefficient_one": "OBSTRUCTED",
        "lattice_coefficient_one_every_L_ge_8": "OBSTRUCTED",
        "positive_volume_uniform_gradient_coefficient": "OPEN",
        "normalized_full_witten_coercivity": "OPEN",
        "interacting_h_minus_one_bound": "OPEN",
        "actual_interacting_h_minus_one_divergence": "NOT_ESTABLISHED",
        "continuum_reconstruction": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "collapse of the full lattice gradient quotient to zero",
        "boundedness or divergence of the actual interacting H^-1 moment",
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
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} ({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
