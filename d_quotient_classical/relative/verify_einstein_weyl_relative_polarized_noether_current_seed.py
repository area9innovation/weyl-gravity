#!/usr/bin/env python3
"""Independent consumer for the polarized relative-current seed."""

from __future__ import annotations

import hashlib
import json

import sympy as sp

from d_quotient_classical.relative import einstein_weyl_relative_polarized_noether_current_seed as producer
from d_quotient_classical.relative.einstein_weyl_relative_noether_current import (
    gauge_covariant_lie_derivative_potential,
    polarized_relative_noether_current_component,
)


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    for name, dependency in value["dependencies"].items():
        path = producer.ROOT / dependency["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")

    coordinates = sp.symbols("t x y z")
    t, x, y, z = coordinates
    metric = sp.diag(-1, 1, 1, 1)
    field = sp.zeros(4)
    generator = sp.Matrix([1, 0, 0, 0])
    zero_potential = sp.zeros(4, 1)
    first_metric = sp.zeros(4)
    second_metric = sp.zeros(4)
    first_metric[1, 2] = first_metric[2, 1] = t * x
    second_metric[1, 2] = second_metric[2, 1] = t**2 * x
    first = (first_metric, zero_potential)
    second = (second_metric, zero_potential)
    forward = polarized_relative_noether_current_component(
        metric, field, first, second, generator, coordinates, 1
    )
    reverse = polarized_relative_noether_current_component(
        metric, field, second, first, generator, coordinates, 1
    )
    if sp.simplify(forward - 3 * x / 8) != 0:
        raise AssertionError("nonzero spatial fixture failed")
    if sp.simplify(forward - reverse) != 0:
        raise AssertionError("polarization symmetry failed")

    potential = sp.Matrix([t * x, t**2 + y, x * z, t * y])
    covariant = gauge_covariant_lie_derivative_potential(potential, generator, coordinates)
    ordinary = potential.applyfunc(lambda entry: sp.diff(entry, t))
    exact = sp.Matrix([sp.diff(potential[0], coordinate) for coordinate in coordinates])
    if (covariant - ordinary + exact).applyfunc(sp.simplify) != sp.zeros(4, 1):
        raise AssertionError("Cartan lift identity failed")

    classification = value["classification"]
    if not all(
        classification[key]
        for key in (
            "all_four_action_current_components_exported",
            "bundle_covariant_stabilizer_action",
            "polarized_relative_current_exported",
            "finite_order_support_local",
        )
    ):
        raise AssertionError("positive current-seed flags are not closed")
    if any(
        classification[key]
        for key in (
            "off_shell_divergence_cone_certified",
            "slice_integral_matches_complete_five_charge_q2",
            "cyclic_dual_rows_certified",
            "direct_f2_repaired",
            "arity_three_authorized",
            "causal_observable_particle_or_quantum_claim",
        )
    ):
        raise AssertionError("downstream claim was promoted")
    return {"status": "PASS", "spatial_fixture": str(sp.factor(forward)), "divergence_cone": False}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
