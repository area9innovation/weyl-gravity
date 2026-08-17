#!/usr/bin/env python3
"""Numerically scout hyperoctahedral BT profiles on four-tori.

This is a hypothesis-generation tool, not a certificate.  It evaluates the
complete nonlinear residual-gradient quotient, uses its analytic derivative,
and restricts only by coordinate permutations and reflections.  A small-torus
profile can be continued to an adjacent side length by periodic multilinear
interpolation.  Floating-point minima produced here establish no theorem.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from collections import Counter
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class QuotientGeometry:
    side: int
    orbits: tuple[tuple[int, int, int, int], ...]
    multiplicities: tuple[int, ...]
    transitions: tuple[tuple[tuple[int, int], ...], ...]


def orbit_key(point: tuple[int, int, int, int], side: int) -> tuple[int, int, int, int]:
    return tuple(sorted(min(value % side, (-value) % side) for value in point))  # type: ignore[return-value]


def build_geometry(side: int) -> QuotientGeometry:
    if side < 3:
        raise ValueError("side must be at least 3")
    radius = side // 2
    orbits = tuple(
        (a, b, c, d)
        for a in range(radius + 1)
        for b in range(a, radius + 1)
        for c in range(b, radius + 1)
        for d in range(c, radius + 1)
    )
    lookup = {key: index for index, key in enumerate(orbits)}
    multiplicities: list[int] = []
    transitions: list[tuple[tuple[int, int], ...]] = []
    for key in orbits:
        repetitions = Counter(key)
        permutation_count = math.factorial(4)
        for count in repetitions.values():
            permutation_count //= math.factorial(count)
        sign_count = 1
        for value in key:
            if value != 0 and not (side % 2 == 0 and value == radius):
                sign_count *= 2
        multiplicities.append(permutation_count * sign_count)

        adjacent: Counter[int] = Counter()
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(key)
                neighbor[axis] = (neighbor[axis] + step) % side
                adjacent[lookup[orbit_key(tuple(neighbor), side)]] += 1
        transitions.append(tuple(sorted(adjacent.items())))
    if sum(multiplicities) != side**4:
        raise AssertionError("orbit multiplicities do not cover the torus")
    for adjacent in transitions:
        if sum(count for _, count in adjacent) != 8:
            raise AssertionError("orbit transition row is not 8-regular")
    return QuotientGeometry(side, orbits, tuple(multiplicities), tuple(transitions))


def residual_gradient_hessian_vector(
    geometry: QuotientGeometry,
    psi: list[float],
    vector: list[float] | None = None,
) -> tuple[list[float], list[float], list[float] | None]:
    count = len(psi)
    residual = [0.0] * count
    for source, adjacent in enumerate(geometry.transitions):
        residual[source] = sum(
            edge_count * math.exp(psi[target] - psi[source])
            for target, edge_count in adjacent
        ) - 8.0

    gradient = [0.0] * count
    for source, adjacent in enumerate(geometry.transitions):
        gradient[source] = sum(
            edge_count
            * (
                residual[target] * math.exp(psi[source] - psi[target])
                - residual[source] * math.exp(psi[target] - psi[source])
            )
            for target, edge_count in adjacent
        )
    if vector is None:
        return residual, gradient, None

    residual_variation = [0.0] * count
    for source, adjacent in enumerate(geometry.transitions):
        residual_variation[source] = sum(
            edge_count
            * math.exp(psi[target] - psi[source])
            * (vector[target] - vector[source])
            for target, edge_count in adjacent
        )
    hessian_vector = [0.0] * count
    for source, adjacent in enumerate(geometry.transitions):
        total = 0.0
        for target, edge_count in adjacent:
            forward = math.exp(psi[target] - psi[source])
            backward = 1.0 / forward
            difference = vector[target] - vector[source]
            total += edge_count * (
                residual_variation[target] * backward
                - residual[target] * backward * difference
                - residual_variation[source] * forward
                - residual[source] * forward * difference
            )
        hessian_vector[source] = total
    return residual, gradient, hessian_vector


def metrics_and_log_gradient(
    geometry: QuotientGeometry, psi: list[float]
) -> tuple[dict[str, float], list[float]]:
    residual, gradient, hessian_gradient = residual_gradient_hessian_vector(
        geometry, psi, None
    )
    residual_norm = sum(
        multiplicity * value * value
        for multiplicity, value in zip(geometry.multiplicities, residual)
    )
    gradient_norm = sum(
        multiplicity * value * value
        for multiplicity, value in zip(geometry.multiplicities, gradient)
    )
    if residual_norm <= 0.0 or gradient_norm <= 0.0:
        raise ArithmeticError("the quotient derivative is singular at a constant field")
    _, _, hessian_gradient = residual_gradient_hessian_vector(
        geometry, psi, gradient
    )
    assert hessian_gradient is not None
    log_gradient = [
        2.0 * hessian_value / gradient_norm - 2.0 * gradient_value / residual_norm
        for hessian_value, gradient_value in zip(hessian_gradient, gradient)
    ]
    omega = 4.0 * math.sin(math.pi / geometry.side) ** 2
    quotient = gradient_norm / residual_norm
    return (
        {
            "side": float(geometry.side),
            "vertices": float(geometry.side**4),
            "orbit_variables": float(len(psi)),
            "action_density": residual_norm / (2.0 * geometry.side**4),
            "quotient": quotient,
            "free_bilaplacian_scale": omega * omega,
            "normalized_quotient": quotient / (omega * omega),
            "log_contrast": max(psi) - min(psi),
            "gradient_rms": math.sqrt(
                sum(
                    multiplicity * value * value
                    for multiplicity, value in zip(
                        geometry.multiplicities, log_gradient
                    )
                )
                / geometry.side**4
            ),
        },
        log_gradient,
    )


def weighted_center(geometry: QuotientGeometry, values: list[float]) -> None:
    mean = sum(
        multiplicity * value
        for multiplicity, value in zip(geometry.multiplicities, values)
    ) / geometry.side**4
    for index in range(len(values)):
        values[index] -= mean


def lowest_mode_seed(geometry: QuotientGeometry, amplitude: float) -> list[float]:
    values = [
        amplitude
        * sum(math.cos(2.0 * math.pi * coordinate / geometry.side) for coordinate in key)
        for key in geometry.orbits
    ]
    weighted_center(geometry, values)
    return values


def full_field(geometry: QuotientGeometry, values: list[float]) -> list[float]:
    lookup = {key: index for index, key in enumerate(geometry.orbits)}
    return [
        values[lookup[orbit_key(point, geometry.side)]]
        for point in product(range(geometry.side), repeat=4)
    ]


def fourier_coefficients(
    side: int, field: list[float], tolerance: float = 1.0e-12
) -> list[tuple[tuple[int, int, int, int], complex]]:
    coefficients: list[tuple[tuple[int, int, int, int], complex]] = []
    points = tuple(product(range(side), repeat=4))
    volume = side**4
    for raw_mode in points:
        coefficient = sum(
            value
            * cmath.exp(
                -2j
                * math.pi
                * sum(mode * coordinate for mode, coordinate in zip(raw_mode, point))
                / side
            )
            for point, value in zip(points, field)
        ) / volume
        if abs(coefficient) > tolerance:
            # On an even grid the Nyquist characters +L/2 and -L/2 agree.
            # Split that coefficient evenly between the two frequencies so
            # continuation to a different grid remains real and reflection
            # symmetric.
            choices: list[tuple[tuple[int, float], ...]] = []
            for mode in raw_mode:
                if side % 2 == 0 and mode == side // 2:
                    choices.append(((mode, 0.5), (-mode, 0.5)))
                else:
                    choices.append(((mode if mode <= side // 2 else mode - side, 1.0),))
            for expanded in product(*choices):
                signed_mode = tuple(value for value, _ in expanded)
                weight = math.prod(factor for _, factor in expanded)
                coefficients.append((signed_mode, coefficient * weight))  # type: ignore[arg-type]
    return coefficients


def spectral_continue(
    source_geometry: QuotientGeometry,
    source_values: list[float],
    target_geometry: QuotientGeometry,
) -> list[float]:
    coefficients = fourier_coefficients(
        source_geometry.side, full_field(source_geometry, source_values)
    )
    values = []
    for point in target_geometry.orbits:
        value = sum(
            coefficient
            * cmath.exp(
                2j
                * math.pi
                * sum(mode * coordinate for mode, coordinate in zip(signed_mode, point))
                / target_geometry.side
            )
            for signed_mode, coefficient in coefficients
        )
        if abs(value.imag) > 1.0e-9:
            raise ArithmeticError("continued real field acquired an imaginary part")
        values.append(value.real)
    weighted_center(target_geometry, values)
    return values


def linear_continue(
    source_geometry: QuotientGeometry,
    source_values: list[float],
    target_geometry: QuotientGeometry,
) -> list[float]:
    """Periodically multilinear-interpolate one orbit field to another grid."""
    lookup = {key: index for index, key in enumerate(source_geometry.orbits)}
    values: list[float] = []
    for target_point in target_geometry.orbits:
        choices: list[tuple[tuple[int, float], ...]] = []
        for coordinate in target_point:
            scaled = coordinate * source_geometry.side / target_geometry.side
            lower = math.floor(scaled)
            fraction = scaled - lower
            if fraction < 1.0e-15:
                choices.append(((lower % source_geometry.side, 1.0),))
            else:
                choices.append(
                    (
                        (lower % source_geometry.side, 1.0 - fraction),
                        ((lower + 1) % source_geometry.side, fraction),
                    )
                )
        value = 0.0
        for corner in product(*choices):
            point = tuple(coordinate for coordinate, _ in corner)
            weight = math.prod(factor for _, factor in corner)
            value += weight * source_values[
                lookup[orbit_key(point, source_geometry.side)]
            ]
        values.append(value)
    weighted_center(target_geometry, values)
    return values


def optimize(
    geometry: QuotientGeometry,
    initial: list[float],
    iterations: int,
    learning_rate: float,
) -> tuple[list[float], dict[str, float]]:
    psi = initial[:]
    first_moment = [0.0] * len(psi)
    second_moment = [0.0] * len(psi)
    best = psi[:]
    best_metrics, _ = metrics_and_log_gradient(geometry, psi)
    for iteration in range(1, iterations + 1):
        _, derivative = metrics_and_log_gradient(geometry, psi)
        for index, value in enumerate(derivative):
            first_moment[index] = 0.9 * first_moment[index] + 0.1 * value
            second_moment[index] = 0.999 * second_moment[index] + 0.001 * value * value
            corrected_first = first_moment[index] / (1.0 - 0.9**iteration)
            corrected_second = second_moment[index] / (1.0 - 0.999**iteration)
            psi[index] -= learning_rate * corrected_first / (
                math.sqrt(corrected_second) + 1.0e-10
            )
        weighted_center(geometry, psi)
        metrics, _ = metrics_and_log_gradient(geometry, psi)
        if metrics["normalized_quotient"] < best_metrics["normalized_quotient"]:
            best = psi[:]
            best_metrics = metrics
    # Fixed-rate Adam is useful for finding the basin but not for certifying a
    # stationary numerical profile.  Finish with an Armijo descent in the
    # positive diagonal orbit metric.  This is still only reconnaissance.
    psi = best
    step_size = learning_rate
    for _ in range(iterations):
        metrics, derivative = metrics_and_log_gradient(geometry, psi)
        objective = math.log(metrics["quotient"])
        squared_slope = sum(
            multiplicity * value * value
            for multiplicity, value in zip(geometry.multiplicities, derivative)
        )
        if squared_slope / geometry.side**4 < 1.0e-18:
            break
        trial_step = step_size
        accepted = False
        while trial_step >= 1.0e-12:
            trial = [
                value - trial_step * slope
                for value, slope in zip(psi, derivative)
            ]
            weighted_center(geometry, trial)
            trial_metrics, _ = metrics_and_log_gradient(geometry, trial)
            if math.log(trial_metrics["quotient"]) <= (
                objective - 1.0e-4 * trial_step * squared_slope
            ):
                psi = trial
                step_size = min(0.05, 1.25 * trial_step)
                accepted = True
                break
            trial_step *= 0.5
        if not accepted:
            break
    final_metrics, _ = metrics_and_log_gradient(geometry, psi)
    if final_metrics["normalized_quotient"] < best_metrics["normalized_quotient"]:
        return psi, final_metrics
    return best, best_metrics


def derivative_check() -> dict[str, float]:
    geometry = build_geometry(5)
    psi = [
        0.17 * math.sin(1.7 * (index + 1))
        for index in range(len(geometry.orbits))
    ]
    direction = [
        math.cos(0.9 * (index + 2)) for index in range(len(geometry.orbits))
    ]
    weighted_center(geometry, psi)
    weighted_center(geometry, direction)
    _, derivative = metrics_and_log_gradient(geometry, psi)
    analytic = sum(
        multiplicity * slope * tangent
        for multiplicity, slope, tangent in zip(
            geometry.multiplicities, derivative, direction
        )
    )
    step = 1.0e-6
    plus, _ = metrics_and_log_gradient(
        geometry, [value + step * tangent for value, tangent in zip(psi, direction)]
    )
    minus, _ = metrics_and_log_gradient(
        geometry, [value - step * tangent for value, tangent in zip(psi, direction)]
    )
    numeric = (
        math.log(plus["quotient"]) - math.log(minus["quotient"])
    ) / (2.0 * step)
    return {
        "analytic_directional_derivative": analytic,
        "central_difference": numeric,
        "absolute_error": abs(analytic - numeric),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-side", type=int, default=5)
    parser.add_argument("--max-side", type=int, default=12)
    parser.add_argument("--iterations", type=int, default=2500)
    parser.add_argument("--learning-rate", type=float, default=0.004)
    parser.add_argument("--amplitude", type=float, default=0.1)
    parser.add_argument("--output")
    arguments = parser.parse_args()

    check = derivative_check()
    if check["absolute_error"] > 1.0e-6:
        raise AssertionError(f"analytic derivative check failed: {check}")

    source_geometry = build_geometry(arguments.source_side)
    source, source_metrics = optimize(
        source_geometry,
        lowest_mode_seed(source_geometry, arguments.amplitude),
        arguments.iterations,
        arguments.learning_rate,
    )
    records = [source_metrics]
    for side in range(arguments.source_side + 1, arguments.max_side + 1):
        target_geometry = build_geometry(side)
        continued = linear_continue(source_geometry, source, target_geometry)
        optimized, metrics = optimize(
            target_geometry,
            continued,
            arguments.iterations,
            arguments.learning_rate * arguments.source_side / side,
        )
        records.append(metrics)
        # Continue from the newly optimized adjacent-side profile.  Keeping
        # adjacent sides makes the interpolation a branch tracker, not a
        # collection of unrelated restarts.
        source_geometry, source = target_geometry, optimized

    result = {
        "status": "NUMERICAL_SCOUT_ONLY_NOT_A_CERTIFICATE",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "derivative_check": check,
        "settings": vars(arguments),
        "profiles": records,
        "does_not_establish": [
            "a lower bound for arbitrary fields",
            "a counterexample family",
            "global or asymptotic optimality in the symmetry class",
            "anything LORENTZIAN-CAUSAL",
        ],
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    print(encoded)
    if arguments.output:
        with open(arguments.output, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
