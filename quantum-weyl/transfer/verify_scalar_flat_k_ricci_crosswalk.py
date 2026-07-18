#!/usr/bin/env python3
"""Independent replay of the scalar-flat K/Ricci cubic crosswalk."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json

try:
    from .scalar_flat_k_ricci_crosswalk import OUTPUT, ROOT, build, validate
except ImportError:
    from scalar_flat_k_ricci_crosswalk import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _linearized_tt_fixture() -> None:
    dimension = 4
    k = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    h = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    h[1][1] = Fraction(1)
    h[2][2] = Fraction(-1)
    h[1][2] = h[2][1] = Fraction(2)
    trace_h = sum(h[index][index] for index in range(dimension))
    if trace_h != 0 or any(
        sum(k[a] * h[a][b] for a in range(dimension)) != 0
        for b in range(dimension)
    ):
        raise ValueError("linearized crosswalk fixture is not TT")

    riemann = [
        [
            [
                [
                    Fraction(1, 2)
                    * (
                        k[b] * k[m] * h[a][n]
                        + k[n] * k[a] * h[m][b]
                        - k[n] * k[m] * h[a][b]
                        - k[b] * k[a] * h[m][n]
                    )
                    for n in range(dimension)
                ]
                for b in range(dimension)
            ]
            for m in range(dimension)
        ]
        for a in range(dimension)
    ]
    k_squared = sum(component * component for component in k)
    ricci = [
        [
            Fraction(1, 2)
            * (
                sum(k[a] * k[m] * h[a][n] for a in range(dimension))
                + sum(k[n] * k[a] * h[m][a] for a in range(dimension))
                - k_squared * h[m][n]
                - k[m] * k[n] * trace_h
            )
            for n in range(dimension)
        ]
        for m in range(dimension)
    ]
    scalar = sum(ricci[index][index] for index in range(dimension))
    delta = lambda left, right: Fraction(int(left == right))
    weyl = [
        [
            [
                [
                    riemann[a][m][b][n]
                    - Fraction(1, 2)
                    * (
                        delta(a, b) * ricci[n][m]
                        - delta(a, n) * ricci[b][m]
                        - delta(m, b) * ricci[n][a]
                        + delta(m, n) * ricci[b][a]
                    )
                    + scalar
                    * Fraction(1, 6)
                    * (
                        delta(a, b) * delta(n, m)
                        - delta(a, n) * delta(b, m)
                    )
                    for n in range(dimension)
                ]
                for b in range(dimension)
            ]
            for m in range(dimension)
        ]
        for a in range(dimension)
    ]
    for m in range(dimension):
        for n in range(dimension):
            double_divergence = sum(
                k[a] * k[b] * weyl[a][m][b][n]
                for a in range(dimension)
                for b in range(dimension)
            )
            if double_divergence != Fraction(1, 2) * k_squared * ricci[m][n]:
                raise ValueError("linearized Weyl double-divergence sign fixture failed")


def verify() -> dict:
    stored = json.loads(OUTPUT.read_text())
    rebuilt = build()
    if stored != rebuilt:
        raise ValueError("stored scalar-flat K/Ricci crosswalk is stale")
    validate(stored)
    _linearized_tt_fixture()

    dimension = stored["linear_crosswalk"]["dimension"]
    divergence = Fraction(dimension - 3, dimension - 2)
    k_prefactor = Fraction(2)
    if divergence != Fraction(1, 2):
        raise ValueError("independent contracted-Weyl coefficient failed")
    if _fraction(stored["linear_crosswalk"]["Weyl_divergence_prefactor"]) != divergence:
        raise ValueError("stored Weyl divergence coefficient drifted")
    if _fraction(stored["linear_crosswalk"]["K_definition_prefactor"]) != k_prefactor:
        raise ValueError("stored K-definition coefficient drifted")
    if _fraction(stored["linear_crosswalk"]["normalized_linear_coefficient"]) != divergence * k_prefactor:
        raise ValueError("independent K/Ricci normalization failed")

    replacement_orders = [
        sum(orders)
        for orders in itertools.product((1, 2), repeat=3)
        if orders != (1, 1, 1)
    ]
    if min(replacement_orders) != 4:
        raise ValueError("independent cubic replacement order failed")
    if stored["cubic_order_counting"]["first_replacement_error_order"] != min(replacement_orders):
        raise ValueError("stored cubic replacement order drifted")

    dependencies = stored["dependencies"]
    values = {}
    for name, reference in dependencies.items():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
        values[name] = json.loads(path.read_text())
    manifest = values["carrier_manifest"]["carrier_manifest"]
    by_order: dict[int, list[str]] = {}
    for row in manifest:
        by_order.setdefault(row["explicit_derivative_order"], []).append(
            row["carrier_id"]
        )
    triangle = values["ghost_triangle"]
    projector_counts = sorted(
        {row["projector_count"] for row in triangle["projector_sector_expansion"]["sectors"]}
    )
    if projector_counts != [0, 1, 2, 3]:
        raise ValueError("triangle projector-count coverage drifted")
    expected_routing = []
    for count in projector_counts:
        orders = list(range(0, 2 * count + 1, 2))
        expected_routing.append(
            {
                "longitudinal_projector_count": count,
                "possible_external_derivative_orders": orders,
                "possible_repository_carriers": [
                    carrier for order in orders for carrier in by_order.get(order, [])
                ],
            }
        )
    if stored["five_carrier_target"]["triangle_sector_routing"] != expected_routing:
        raise ValueError("independent five-carrier routing failed")
    return stored


def main() -> int:
    verify()
    print("independent scalar-flat K/Ricci cubic crosswalk: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
