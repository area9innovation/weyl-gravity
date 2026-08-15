#!/usr/bin/env python3
"""Independent verifier for BT corrector-slab cylinder suppression."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-cylinder-suppression-v1.schema.json")
ZERO = (0, 0, 0, 0, 0)
PATTERN = {
    time: ((0, 0, 1, -1) if time == 1 else (0, 1, 0, -1) if time == 2 else (0, 0, 0, 0))
    for time in range(-1, 5)
}
EDGES = (
    ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0)),
    ((0, -1, 0, 0, 0), (0, 0, 1, 0, 0)),
    ((0, 0, -1, 0, 0), (0, 0, 0, 1, 0)),
    ((0, 0, 0, -1, 0), (0, 0, 0, 0, 1)),
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


def interval_product(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    candidates = [x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1]]
    return min(candidates), max(candidates)


def accumulate(polynomial: dict, exponent: tuple[int, ...], bounds: tuple[Fraction, Fraction]) -> None:
    old = polynomial.get(exponent, (Fraction(0), Fraction(0)))
    polynomial[exponent] = old[0] + bounds[0], old[1] + bounds[1]


def multiply(left: dict, right: dict) -> dict:
    answer = {}
    for le, lc in left.items():
        for re, rc in right.items():
            accumulate(answer, tuple(a + b for a, b in zip(le, re)), interval_product(lc, rc))
    return answer


def reconstruct(edge: tuple[Fraction, Fraction]) -> dict:
    """Reconstruct via site polynomials, independently of the producer."""
    result = {}
    for time in range(4):
        left, right = EDGES[time]
        for space in range(4):
            residual = {ZERO: (Fraction(-8), Fraction(-8))}
            for exponent in (left, right, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO):
                accumulate(residual, exponent, edge)
            delta = {}
            current = PATTERN[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left),
                (time + 1, space, right),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = Fraction(2) ** (PATTERN[other_time][other_space] - current) - 1
                if factor:
                    accumulate(delta, exponent, interval_product(edge, (factor, factor)))
            twice_residual = {exponent: (2 * bounds[0], 2 * bounds[1]) for exponent, bounds in residual.items()}
            for product in (multiply(twice_residual, delta), multiply(delta, delta)):
                for exponent, bounds in product.items():
                    accumulate(result, exponent, bounds)
    return result


def decode_ledger(items: list[dict]) -> dict:
    return {
        tuple(item["exponents_A_B_C_D_E"]): (frac(item["lower"]), frac(item["upper"]))
        for item in items
    }


def evaluate_exact(polynomial: dict, variables: tuple[Fraction, ...]) -> Fraction:
    total = Fraction(0)
    for exponent, bounds in polynomial.items():
        require(bounds[0] == bounds[1], "attempted exact evaluation of an interval")
        monomial = Fraction(1)
        for variable, power in zip(variables, exponent):
            monomial *= variable ** power
        total += bounds[0] * monomial
    return total


def enumerate_unperturbed(variables: tuple[Fraction, ...]) -> Fraction:
    A, B, C, D, E = variables
    ratios = ((A, B), (1 / B, C), (1 / C, D), (1 / D, E))
    difference = Fraction(0)
    for time, (left, right) in enumerate(ratios):
        for space in range(4):
            base = Fraction(-2) + left + right
            slab = Fraction(-8)
            here = PATTERN[time][space]
            for other_time, other_space, factor in (
                (time - 1, space, left),
                (time + 1, space, right),
                (time, (space - 1) % 4, Fraction(1)),
                (time, (space + 1) % 4, Fraction(1)),
            ):
                slab += factor * Fraction(2) ** (PATTERN[other_time][other_space] - here)
            slab += 4
            difference += slab * slab - base * base
    return difference


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(len(cert["provenance"]["inputs"]) == 2, "input count drift")
        require(all(digest(item["path"]) == item["sha256"] for item in cert["provenance"]["inputs"]), "input hash drift")

        exact = reconstruct((Fraction(1), Fraction(1)))
        exact = {key: value for key, value in exact.items() if value != (Fraction(0), Fraction(0))}
        require(decode_ledger(cert["unperturbed_translation"]["coefficient_ledger"]) == exact, "exact Laurent polynomial drift")
        for fixture in (
            (Fraction(2), Fraction(3, 2), Fraction(4, 3), Fraction(5, 4), Fraction(7, 6)),
            (Fraction(1, 7), Fraction(9, 5), Fraction(2, 9), Fraction(11, 3), Fraction(5, 8)),
        ):
            require(evaluate_exact(exact, fixture) == enumerate_unperturbed(fixture), "direct residual enumeration mismatch")
        require(frac(cert["unperturbed_translation"]["coarse_gap"]) == Fraction(349, 144), "unperturbed gap drift")

        robust = reconstruct((Fraction(199, 200), Fraction(200, 199)))
        require(decode_ledger(cert["robust_interval_certificate"]["coefficient_ledger"]) == robust, "robust interval ledger drift")
        square = (0, 2, 0, 0, 0)
        inverse_square = (0, 0, 0, -2, 0)
        linear = (0, 1, 0, 0, 0)
        inverse_linear = (0, 0, 0, -1, 0)
        alpha = robust[square][0]
        beta = -robust[linear][0]
        constant = robust[ZERO][0]
        require(robust[inverse_square][0] == alpha and robust[inverse_linear][0] == -beta, "paired coefficient drift")
        for exponent, bounds in robust.items():
            if exponent not in (ZERO, square, inverse_square, linear, inverse_linear):
                require(bounds[0] >= 0, "discarded robust coefficient is negative")
        gap = constant - beta * beta / (2 * alpha)
        require(gap == Fraction(403338322161150510073, 354498257782024320000), "robust gap drift")
        require(frac(cert["robust_interval_certificate"]["residual_square_gap"]) == gap, "serialized robust gap drift")
        require(frac(cert["gibbs_cylinder_probability"]["action_gap_coefficient"]) == gap / 8, "action multiplicity drift")
        require(frac(cert["gibbs_cylinder_probability"]["lambda_point_four_exponent"]) == Fraction(25, 4) * gap / 8, "coupling exponent drift")

        disposition = cert["method_disposition"]
        require(disposition["localized_slab_positive_radius_cylinder_probability"] == "PROVED_EXPONENTIALLY_SUPPRESSED", "cylinder result omitted")
        require(disposition["all_large_corrector_backgrounds_contain_certified_cylinders"] == "OPEN", "one cylinder promoted to all correctors")
        require(disposition["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "corrector moment promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, ZeroDivisionError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT corrector-slab cylinder suppression: PASS" if ok else "BT corrector-slab cylinder suppression: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
