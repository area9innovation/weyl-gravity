#!/usr/bin/env python3
"""Independent verifier for BT corrector-slab fiber stability."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-fiber-stability-v1.schema.json")
MATRIX = (
    (0, 0, 0, 0),
    (0, 0, 1, -1),
    (0, 1, 0, -1),
    (0, 0, 0, 0),
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def reconstruct_row(time: int) -> tuple[list[Fraction], list[Fraction], list[Fraction]]:
    base = []
    left = []
    right = []
    for space in range(4):
        exponent = MATRIX[time][space]
        base.append(Fraction(-4) + p2(MATRIX[time][(space - 1) % 4] - exponent) + p2(MATRIX[time][(space + 1) % 4] - exponent))
        left.append(p2(MATRIX[time - 1][space] - exponent))
        right.append(p2(MATRIX[time + 1][space] - exponent))
    return base, left, right


def row_square(vectors: tuple[list[Fraction], list[Fraction], list[Fraction]], left_factor: Fraction, right_factor: Fraction) -> Fraction:
    base, left, right = vectors
    return sum((base[index] + left_factor * left[index] + right_factor * right[index]) ** 2 for index in range(4))


def quadratic(x: Fraction, y: Fraction) -> Fraction:
    return Fraction(25, 4) * x * x + Fraction(21, 2) * x * y + Fraction(25, 4) * y * y


def direct_coefficients(vectors: tuple[list[Fraction], list[Fraction], list[Fraction]]) -> tuple[Fraction, ...]:
    base, left, right = vectors
    dot = lambda x, y: sum((a * b for a, b in zip(x, y)), Fraction(0))
    return (dot(base, base), 2 * dot(base, left), 2 * dot(base, right), dot(left, left), 2 * dot(left, right), dot(right, right))


def enumerate_relaxed_slab(length: int, row_factors: list[Fraction]) -> Fraction:
    """Enumerate the full 2D residual action and multiply the inert L^2 sites."""
    def omega(time: int, space: int) -> Fraction:
        exponent = MATRIX[time][space % 4] if time < 4 else 0
        return row_factors[time] * p2(exponent)

    residual_square = Fraction(0)
    for time in range(length):
        for space in range(length):
            here = omega(time, space)
            residual = Fraction(-4)
            residual += omega((time - 1) % length, space) / here
            residual += omega((time + 1) % length, space) / here
            residual += omega(time, (space - 1) % length) / here
            residual += omega(time, (space + 1) % length) / here
            residual_square += residual * residual
    return Fraction(length * length, 2) * residual_square


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        inputs = cert["provenance"]["inputs"]
        require(len(inputs) == 3 and all(digest(item["path"]) == item["sha256"] for item in inputs), "input hash drift")
        row_one = reconstruct_row(1)
        row_two = reconstruct_row(2)
        section = cert["row_cone_coercivity"]
        require([[frac(value) for value in section["row_one"][name]] for name in ("base", "left", "right")] == [list(values) for values in row_one], "row-one vectors drift")
        require([[frac(value) for value in section["row_two"][name]] for name in ("base", "left", "right")] == [list(values) for values in row_two], "row-two vectors drift")
        row_one_completed = (
            Fraction(1909, 100) + Fraction(25, 4) * Fraction(33, 50) ** 2,
            Fraction(117, 25) - Fraction(21, 2) * Fraction(33, 50),
            -Fraction(25, 2) * Fraction(33, 50),
            Fraction(25, 4), Fraction(21, 2), Fraction(25, 4),
        )
        row_two_completed = (
            Fraction(387, 50) + Fraction(25, 4) * Fraction(24, 25) ** 2,
            -Fraction(25, 2) * Fraction(24, 25),
            Fraction(27, 25) - Fraction(21, 2) * Fraction(24, 25),
            Fraction(25, 4), Fraction(21, 2), Fraction(25, 4),
        )
        require(direct_coefficients(row_one) == row_one_completed, "row-one polynomial completion failed")
        require(direct_coefficients(row_two) == row_two_completed, "row-two polynomial completion failed")
        require(Fraction(25, 4) - Fraction(21, 4) == 1 and Fraction(25, 4) + Fraction(21, 4) == Fraction(23, 2), "quadratic eigenvalues failed")
        fixtures = [(Fraction(1, 7), Fraction(33, 50)), (Fraction(2, 3), Fraction(5, 4)), (Fraction(7, 2), Fraction(1, 9))]
        for left_factor, right_factor in fixtures:
            direct_one = row_square(row_one, left_factor, right_factor)
            decomposed_one = Fraction(1909, 100) + Fraction(117, 25) * left_factor + quadratic(left_factor, right_factor - Fraction(33, 50))
            require(direct_one == decomposed_one >= Fraction(1909, 100), "row-one completion failed")
            direct_two = row_square(row_two, left_factor, right_factor)
            decomposed_two = Fraction(387, 50) + Fraction(27, 25) * right_factor + quadratic(left_factor - Fraction(24, 25), right_factor)
            require(direct_two == decomposed_two >= Fraction(387, 50), "row-two completion failed")
        require(frac(section["combined_residual_square_lower_bound"]) == Fraction(2683, 100), "combined row gap drift")
        for length in (8, 12):
            factors = [Fraction(((3 * time + 2) % 11) + 1, ((5 * time + 1) % 7) + 1) for time in range(length)]
            action = enumerate_relaxed_slab(length, factors)
            require(action >= Fraction(2683, 800) * length**3, f"full relaxed slab lower bound failed at L={length}")
        fiber = cert["fiber_action_lower_bound"]
        require(frac(fiber["coefficient"]) == Fraction(2683, 800), "fiber coefficient drift")
        density = cert["integrated_background_density"]
        require(frac(density["lambda_point_four_prefactor"]) == Fraction(99, 5600), "density prefactor drift")
        require(frac(density["lambda_point_four_action_exponent"]) == Fraction(2683, 128), "density exponent drift")
        require(frac(density["lambda_point_four_zero_constant"]) == Fraction(96800, 49), "zero-background constant drift")
        require(Fraction(2, 9) * 256 == Fraction(512, 9), "curvature floor algebra failed")
        require(Fraction(8) * Fraction(1936, 49) == Fraction(15488, 49), "small-square action algebra failed")
        disposition = cert["method_disposition"]
        require(disposition["localized_slab_two_mode_fiber_action_escape"] == "OBSTRUCTED", "fiber escape no-go weakened")
        require(disposition["localized_slab_integrated_marginal_point_density_escape"] == "OBSTRUCTED", "density suppression weakened")
        require(disposition["localized_slab_neighborhood_probability_bound"] == "OPEN", "point density promoted to neighborhood probability")
        require(disposition["all_large_corrector_backgrounds_fiber_stable"] == "OPEN", "single family promoted to all backgrounds")
        require(disposition["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "Gibbs corrector promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born rule promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT corrector-slab fiber stability: PASS" if ok else "BT corrector-slab fiber stability: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
