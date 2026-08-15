#!/usr/bin/env python3
"""Independent verifier for the BT pair-block response one-loop result."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-one-loop-v1.schema.json",
)
Coord = tuple[int, int, int, int]
CountMonomial = tuple[tuple[Coord, int], ...]
CountPoly = dict[CountMonomial, Fraction]
Power = tuple[int, int, int, int]
ORIGIN: Coord = (0, 0, 0, 0)
EDGE: Coord = (1, 0, 0, 0)
INSIDE = (ORIGIN, EDGE)
INSIDE_SET = set(INSIDE)
STEPS = tuple(
    tuple(sign if j == axis else 0 for j in range(4))
    for axis in range(4)
    for sign in (-1, 1)
)
CB = (
    (Fraction(9, 616), Fraction(1, 308)),
    (Fraction(1, 308), Fraction(9, 616)),
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value: Fraction) -> str:
    return hashlib.sha256(
        f"{value.numerator}/{value.denominator}".encode("ascii")
    ).hexdigest()


def mapping_hash(mapping: dict[tuple[int, ...], Fraction]) -> str:
    rows = [
        [list(key), value.numerator, value.denominator]
        for key, value in sorted(mapping.items())
    ]
    return hashlib.sha256(
        json.dumps(rows, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def plus(left: Coord, right: Coord) -> Coord:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def minus(left: Coord, right: Coord) -> Coord:
    return tuple(a - b for a, b in zip(left, right))  # type: ignore[return-value]


def opposite(value: Coord) -> Coord:
    return tuple(-entry for entry in value)  # type: ignore[return-value]


def normalized_difference(left: Coord, right: Coord) -> Coord:
    value = minus(left, right)
    return min(value, opposite(value))


def canonical_monomial(entries: list[Coord]) -> CountMonomial:
    return tuple(sorted(Counter(entries).items()))


def poly_add(*polys: CountPoly) -> CountPoly:
    result: dict[CountMonomial, Fraction] = defaultdict(Fraction)
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] += coefficient
    return {key: value for key, value in result.items() if value}


def poly_scale(poly: CountPoly, scalar: Fraction | int) -> CountPoly:
    scalar = Fraction(scalar)
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in poly.items()
        if scalar * coefficient
    }


def poly_multiply(left: CountPoly, right: CountPoly) -> CountPoly:
    result: dict[CountMonomial, Fraction] = defaultdict(Fraction)
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            counts: Counter[Coord] = Counter(dict(left_monomial))
            counts.update(dict(right_monomial))
            result[tuple(sorted(counts.items()))] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value}


def poly_power(poly: CountPoly, exponent: int) -> CountPoly:
    result: CountPoly = {(): Fraction(1)}
    for _ in range(exponent):
        result = poly_multiply(result, poly)
    return result


def linear(entries: list[tuple[Coord, int]]) -> CountPoly:
    result: dict[CountMonomial, Fraction] = defaultdict(Fraction)
    for coord, coefficient in entries:
        result[((coord, 1),)] += coefficient
    return {key: value for key, value in result.items() if value}


def differentiate(poly: CountPoly, axis: int) -> CountPoly:
    result: dict[CountMonomial, Fraction] = defaultdict(Fraction)
    for monomial, coefficient in poly.items():
        counts = dict(monomial)
        for coord, multiplicity in monomial:
            direction = coord[axis] ** 2
            if not direction:
                continue
            changed = dict(counts)
            if multiplicity == 1:
                del changed[coord]
            else:
                changed[coord] = multiplicity - 1
            result[tuple(sorted(changed.items()))] += (
                coefficient * multiplicity * direction
            )
    return {key: value for key, value in result.items() if value}


def independent_interactions() -> tuple[CountPoly, CountPoly, int]:
    neighbourhood = set(INSIDE)
    for coord in INSIDE:
        for step in STEPS:
            neighbourhood.add(plus(coord, step))

    def make(zero_inside: bool) -> tuple[CountPoly, CountPoly]:
        cubic: CountPoly = {}
        quartic: CountPoly = {}
        for vertex in neighbourhood:
            first: CountPoly = {}
            second: CountPoly = {}
            third: CountPoly = {}
            for step in STEPS:
                neighbour = plus(vertex, step)
                entries: list[tuple[Coord, int]] = []
                if not (zero_inside and neighbour in INSIDE_SET):
                    entries.append((neighbour, 1))
                if not (zero_inside and vertex in INSIDE_SET):
                    entries.append((vertex, -1))
                difference = linear(entries)
                first = poly_add(first, difference)
                second = poly_add(second, poly_power(difference, 2))
                third = poly_add(third, poly_power(difference, 3))
            cubic = poly_add(
                cubic,
                poly_scale(poly_multiply(first, second), Fraction(1, 2)),
            )
            quartic = poly_add(
                quartic,
                poly_scale(poly_multiply(second, second), Fraction(1, 8)),
                poly_scale(poly_multiply(first, third), Fraction(1, 6)),
            )
        return cubic, quartic

    full_cubic, full_quartic = make(False)
    base_cubic, base_quartic = make(True)
    return (
        poly_add(full_cubic, poly_scale(base_cubic, -1)),
        poly_add(full_quartic, poly_scale(base_quartic, -1)),
        len(neighbourhood),
    )


class FirstLoop:
    """Constant plus one occurrence of an abstract Green value."""

    __slots__ = ("constant", "coefficients")

    def __init__(
        self,
        constant: Fraction | int = 0,
        coefficients: dict[Coord, Fraction] | None = None,
    ) -> None:
        self.constant = Fraction(constant)
        self.coefficients = {
            key: Fraction(value)
            for key, value in (coefficients or {}).items()
            if value
        }

    def add(self, other: FirstLoop) -> FirstLoop:
        result: dict[Coord, Fraction] = defaultdict(Fraction, self.coefficients)
        for key, value in other.coefficients.items():
            result[key] += value
        return FirstLoop(self.constant + other.constant, result)

    def scale(self, scalar: Fraction | int) -> FirstLoop:
        scalar = Fraction(scalar)
        return FirstLoop(
            scalar * self.constant,
            {key: scalar * value for key, value in self.coefficients.items()},
        )

    def multiply(self, other: FirstLoop) -> FirstLoop:
        result: dict[Coord, Fraction] = defaultdict(Fraction)
        for key, value in self.coefficients.items():
            result[key] += value * other.constant
        for key, value in other.coefficients.items():
            result[key] += value * self.constant
        return FirstLoop(self.constant * other.constant, result)


Label = tuple[str, int, int | Coord]


def inside_index(coord: Coord) -> int | None:
    return 0 if coord == ORIGIN else 1 if coord == EDGE else None


def covariance(left: Label, right: Label) -> FirstLoop:
    if left[0] == "innovation" and right[0] == "innovation":
        return FirstLoop(CB[int(left[2])][int(right[2])])
    if right[0] == "innovation":
        return covariance(right, left)
    if left[0] == "innovation":
        if right[0] == "field" and right[1] == 0:
            index = inside_index(right[2])  # type: ignore[arg-type]
            if index is not None:
                return FirstLoop(CB[int(left[2])][index])
        return FirstLoop()

    left_replica, left_coord = left[1], left[2]
    right_replica, right_coord = right[1], right[2]
    displacement = normalized_difference(
        left_coord, right_coord  # type: ignore[arg-type]
    )
    result = FirstLoop(0, {displacement: Fraction(1)})
    if left_replica == right_replica:
        return result
    left_index = inside_index(left_coord)  # type: ignore[arg-type]
    right_index = inside_index(right_coord)  # type: ignore[arg-type]
    if left_index is not None and right_index is not None:
        return result.add(FirstLoop(-CB[left_index][right_index]))
    return result


@lru_cache(maxsize=None)
def wick(labels: tuple[Label, ...]) -> FirstLoop:
    if not labels:
        return FirstLoop(1)
    if len(labels) % 2:
        return FirstLoop()
    first = labels[0]
    result = FirstLoop()
    for index in range(1, len(labels)):
        result = result.add(
            covariance(first, labels[index]).multiply(
                wick(labels[1:index] + labels[index + 1 :])
            )
        )
    return result


def expanded_labels(monomial: CountMonomial, replica: int) -> list[Label]:
    result = []
    for coord, multiplicity in monomial:
        result.extend(("field", replica, coord) for _ in range(multiplicity))
    return result


def expectation(parts: list[tuple[CountPoly, int]]) -> FirstLoop:
    result = FirstLoop()
    rows = [list(poly.items()) for poly, _ in parts]
    for combination in itertools.product(*rows):
        coefficient = Fraction(1)
        labels: list[Label] = [("innovation", 0, 0)]
        for (monomial, value), (_, replica) in zip(combination, parts):
            coefficient *= value
            labels.extend(expanded_labels(monomial, replica))
        result = result.add(wick(tuple(labels)).scale(coefficient))
    return result


def response_moment(cubic: CountPoly, quartic: CountPoly, axis: int) -> FirstLoop:
    derivative_cubic = differentiate(cubic, axis)
    derivative_quartic = differentiate(quartic, axis)
    return (
        expectation([(cubic, 0), (derivative_cubic, 0)])
        .add(expectation([(derivative_quartic, 0)]).scale(-1))
        .add(expectation([(derivative_cubic, 0), (cubic, 1)]).scale(-1))
        .add(expectation([(cubic, 0), (derivative_cubic, 1)]).scale(-1))
    )


@lru_cache(maxsize=1)
def raw_pair_kernel() -> tuple[FirstLoop, int, int, int]:
    cubic, quartic, affected = independent_interactions()
    longitudinal = response_moment(cubic, quartic, 0)
    transverse = response_moment(cubic, quartic, 1)
    averaged = longitudinal.scale(Fraction(1, 8)).add(
        transverse.scale(Fraction(3, 8))
    )
    return averaged, len(cubic), len(quartic), affected


def laurent_from_raw(kernel: dict[Coord, Fraction]) -> dict[Coord, Fraction]:
    signed: dict[Coord, Fraction] = defaultdict(Fraction)
    for displacement, coefficient in kernel.items():
        if displacement == ORIGIN:
            signed[displacement] += coefficient
        else:
            signed[displacement] += coefficient / 2
            signed[opposite(displacement)] += coefficient / 2
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    permutations = tuple(itertools.permutations(range(4)))
    for exponent, coefficient in signed.items():
        for permutation in permutations:
            result[tuple(exponent[permutation[i]] for i in range(4))] += (
                coefficient / len(permutations)
            )
    return {key: value for key, value in result.items() if value}


def laurent_multiply(
    left: dict[Coord, Fraction], right: dict[Coord, Fraction]
) -> dict[Coord, Fraction]:
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            result[plus(left_power, right_power)] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value}


def laurent_power(poly: dict[Coord, Fraction], exponent: int) -> dict[Coord, Fraction]:
    result = {ORIGIN: Fraction(1)}
    for _ in range(exponent):
        result = laurent_multiply(result, poly)
    return result


def compact_numerator_laurent() -> dict[Coord, Fraction]:
    axes = []
    for axis in range(4):
        positive = tuple(1 if i == axis else 0 for i in range(4))
        negative = opposite(positive)
        axes.append(
            {
                ORIGIN: Fraction(2),
                positive: Fraction(-1),
                negative: Fraction(-1),
            }
        )
    e1: dict[Coord, Fraction] = defaultdict(Fraction)
    e2: dict[Coord, Fraction] = defaultdict(Fraction)
    for variable in axes:
        for monomial, coefficient in variable.items():
            e1[monomial] += coefficient
    for left in range(4):
        for right in range(left + 1, 4):
            for monomial, coefficient in laurent_multiply(
                axes[left], axes[right]
            ).items():
                e2[monomial] += coefficient
    powers = {degree: laurent_power(dict(e1), degree) for degree in range(1, 6)}
    rows = [
        (powers[1], Fraction(3, 56)),
        (powers[2], Fraction(-39, 1568)),
        (dict(e2), Fraction(1, 112)),
        (powers[3], Fraction(-97, 137984)),
        (laurent_multiply(dict(e1), dict(e2)), Fraction(572, 137984)),
        (powers[4], Fraction(51, 551936)),
        (laurent_multiply(powers[2], dict(e2)), Fraction(-126, 551936)),
        (powers[5], Fraction(-1, 551936)),
        (laurent_multiply(powers[3], dict(e2)), Fraction(2, 551936)),
    ]
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for poly, scalar in rows:
        for monomial, coefficient in poly.items():
            result[monomial] += scalar * coefficient
    return {key: value for key, value in result.items() if value}


def power_multiply(
    left: dict[Power, Fraction], right: dict[Power, Fraction]
) -> dict[Power, Fraction]:
    result: dict[Power, Fraction] = defaultdict(Fraction)
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            result[plus(left_power, right_power)] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value}


def compact_numerator_power() -> dict[Power, Fraction]:
    variables = [
        {tuple(1 if i == axis else 0 for i in range(4)): Fraction(1)}
        for axis in range(4)
    ]
    e1: dict[Power, Fraction] = defaultdict(Fraction)
    e2: dict[Power, Fraction] = defaultdict(Fraction)
    for variable in variables:
        for monomial, coefficient in variable.items():
            e1[monomial] += coefficient
    for left in range(4):
        for right in range(left + 1, 4):
            for monomial, coefficient in power_multiply(
                variables[left], variables[right]
            ).items():
                e2[monomial] += coefficient
    powers = {1: dict(e1)}
    for degree in range(2, 6):
        powers[degree] = power_multiply(powers[degree - 1], dict(e1))
    rows = [
        (powers[1], Fraction(3, 56)),
        (powers[2], Fraction(-39, 1568)),
        (dict(e2), Fraction(1, 112)),
        (powers[3], Fraction(-97, 137984)),
        (power_multiply(dict(e1), dict(e2)), Fraction(572, 137984)),
        (powers[4], Fraction(51, 551936)),
        (power_multiply(powers[2], dict(e2)), Fraction(-126, 551936)),
        (powers[5], Fraction(-1, 551936)),
        (power_multiply(powers[3], dict(e2)), Fraction(2, 551936)),
    ]
    result: dict[Power, Fraction] = defaultdict(Fraction)
    for poly, scalar in rows:
        for monomial, coefficient in poly.items():
            result[monomial] += scalar * coefficient
    return {key: value for key, value in result.items() if value}


def q_value(values: tuple[Fraction, ...]) -> Fraction:
    omega = sum(values, Fraction())
    e2 = sum(
        (
            values[i] * values[j]
            for i in range(4)
            for j in range(i + 1, 4)
        ),
        Fraction(),
    )
    return (
        Fraction(3, 56) * omega
        - Fraction(39, 1568) * omega**2
        + e2 / 112
        - Fraction(97, 137984) * omega**3
        + Fraction(572, 137984) * omega * e2
        + Fraction(51, 551936) * omega**4
        - Fraction(126, 551936) * omega**2 * e2
        - omega**5 / 551936
        + Fraction(2, 551936) * omega**3 * e2
    )


def exact_l6() -> Fraction:
    row = (Fraction(0), Fraction(1), Fraction(3), Fraction(4), Fraction(3), Fraction(1))
    total = Fraction()
    for momentum in itertools.product(range(6), repeat=4):
        values = tuple(row[index] for index in momentum)
        omega = sum(values, Fraction())
        if omega:
            total += q_value(values) / omega**2
    return Fraction(12493, 1517824) + total / 6**4


@lru_cache(maxsize=1)
def multinomial_returns(limit: int) -> tuple[int, ...]:
    counts = []
    for n in range(limit + 1):
        counts.append(
            math.comb(2 * n, n)
            * sum(
                math.comb(n, k) ** 2
                * math.comb(2 * k, k)
                * math.comb(2 * n - 2 * k, n - k)
                for k in range(n + 1)
            )
        )
    return tuple(counts)


@lru_cache(maxsize=None)
def direct_endpoint(n: int) -> int:
    if n == 0:
        return 0
    factorials = [math.factorial(value) for value in range(2 * n + 1)]
    numerator = factorials[2 * n]
    total = 0
    for first in range(n):
        for second in range(n - first):
            for third in range(n - first - second):
                fourth = n - 1 - first - second - third
                denominator = (
                    factorials[first]
                    * factorials[first + 1]
                    * factorials[second]
                    * factorials[second + 1]
                    * factorials[third] ** 2
                    * factorials[fourth] ** 2
                )
                total += numerator // denominator
    return total


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

    checks["strict_schema"] = (
        set(certificate) == set(schema["required"])
        and not list(Draft202012Validator(schema).iter_errors(certificate))
    )
    with open(__file__, encoding="utf-8") as handle:
        verifier_tree = ast.parse(handle.read())
    checks["nonimporting_verifier"] = not any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        and any(
            alias.name.endswith("bt_euclidean_pair_block_response_one_loop")
            for alias in node.names
        )
        for node in ast.walk(verifier_tree)
    )

    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 1 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )

    raw, cubic_terms, quartic_terms, affected = raw_pair_kernel()
    derivation = certificate["conditional_one_loop_derivation"]
    checks["independent_action_jet_reconstruction"] = (
        affected == derivation["affected_residual_sites"] == 16
        and cubic_terms == derivation["cubic_term_count"] == 314
        and quartic_terms == derivation["quartic_term_count"] == 701
        and "at most two external-background legs"
        in derivation["connected_degree_bound"]
    )
    checks["independent_affine_wick_kernel"] = (
        raw.constant == decode(derivation["green_independent_constant"])
        == Fraction(12493, 1517824)
        and len(raw.coefficients) == derivation["raw_green_kernel_term_count"]
        == 202
        and sum(raw.coefficients.values(), Fraction()) == 0
        and mapping_hash(raw.coefficients)
        == derivation["raw_green_kernel_sha256"]
    )
    checks["independent_laurent_identity"] = (
        laurent_from_raw(raw.coefficients) == compact_numerator_laurent()
    )

    pair = certificate["pair_block_definition"]
    checks["free_pair_symbol"] = (
        decode(pair["free_low_momentum_coefficient"]) == Fraction(1, 56)
        and pair["free_relaxation_symbol"]
        == "R_pair,0(k)=omega(k)^2*(44-omega(k))/2464"
    )
    vacuum = certificate["vacuum_pair_diagnostic"]
    checks["vacuum_coefficients"] = (
        decode(vacuum["longitudinal_second_moment_coefficient"])
        == Fraction(-7349, 379456)
        and decode(vacuum["transverse_second_moment_coefficient"])
        == Fraction(-7979, 379456)
        and decode(vacuum["beta_pair_vacuum_lambda2"])
        == Fraction(-15643, 1517824)
        and vacuum["sign"] == "STRICTLY_NEGATIVE"
    )

    finite = certificate["all_volume_formula"]
    l6 = exact_l6()
    checks["independent_exact_l6_sum"] = (
        l6 == Fraction(956585197, 10069092633600)
        and decode(finite["exact_l6"]) == l6
        and finite["exact_l6_sign"] == "STRICTLY_POSITIVE"
        and finite["expanded_term_count"] == 125
    )
    expanded = compact_numerator_power()
    checks["independent_expanded_numerator_hash"] = (
        len(expanded) == finite["expanded_term_count"] == 125
        and mapping_hash(expanded) == finite["expanded_sha256"]
    )

    reduced_constant = (
        Fraction(12493, 1517824)
        - Fraction(39, 1568)
        - Fraction(97 * 8, 137984)
        + Fraction(51 * 72 - 126 * 24, 551936)
        + Fraction(-704 + 2 * 240, 551936)
    )
    reduced_watson = Fraction(3, 56) + Fraction(2, 112)
    reduced_derivative = Fraction(572 * 6, 137984)
    checks["independent_large_volume_moment_reduction"] = (
        reduced_constant == Fraction(-32629, 1517824)
        and reduced_watson == Fraction(1, 14)
        and reduced_derivative == Fraction(39, 1568)
    )

    counts = multinomial_returns(100)
    endpoints = tuple(direct_endpoint(n) for n in range(101))
    watson = sum(
        (Fraction(counts[n], 8 * 64**n) for n in range(101)), Fraction()
    )
    potential = sum(
        (
            Fraction(counts[n] - endpoints[n], 8 * 64**n)
            for n in range(101)
        ),
        Fraction(),
    )
    tail = Fraction(121, 78400)
    i_lower = 1 - 4 * (potential + tail)
    beta_lower = (
        Fraction(-32629, 1517824)
        + watson / 14
        + Fraction(39, 1568) * i_lower
    )
    limit = certificate["large_volume_decision"]
    checks["independent_walk_lower_bounds"] = (
        decode(limit["watson_partial"]) == watson
        and fraction_hash(watson) == limit["watson_partial_sha256"]
        and decode(limit["potential_partial"]) == potential
        and fraction_hash(potential) == limit["potential_partial_sha256"]
        and decode(limit["potential_tail_upper"]) == tail
        and decode(limit["i4_strict_lower"]) == i_lower
    )
    checks["exact_positive_limit_decision"] = (
        decode(limit["substituted_strict_lower"]) == beta_lower
        and decode(limit["simple_strict_lower"]) == Fraction(1, 10000)
        and beta_lower > Fraction(1, 10000)
        and limit["sign"] == "STRICTLY_POSITIVE"
        and limit["status"]
        == "LARGE_VOLUME_PAIR_BLOCK_ONE_LOOP_SIGN_CERTIFIED"
    )

    disposition = certificate["method_disposition"]
    checks["claim_boundary"] = (
        disposition["annealed_pair_block_response_one_loop"]
        == "POSITIVE_AT_L6_AND_LARGE_VOLUME"
        and disposition["uniform_higher_order_pair_response"] == "OPEN"
        and disposition["nonperturbative_pair_response_at_lambda_0_4"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    required_nonclaims = {
        "a positive pair-block response at lambda=0.4 or any fixed nonzero coupling",
        "a uniform bound on the perturbative remainder or convergence of its series",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound",
        "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }
    checks["required_nonclaims"] = required_nonclaims.issubset(
        set(certificate["does_not_establish"])
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
