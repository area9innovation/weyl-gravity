#!/usr/bin/env python3
"""Memory-bounded diagnostic for the local BT expected-Hessian symbol.

This is a deterministic binary64 observation, not a certificate of an
infinite-volume estimate.  On a hypercubic torus of side at least six, the
range-two Hessian kernel has four symmetry orbits.  The axial symbol is

    H_hat(p) = alpha * omega(p) + c * omega(p)^2,
    alpha = -(b + 4*c + 6*d).

The observer estimates the local orbit coefficients with the independent
Metropolis implementation used by the lattice step-scaling preflight.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_lattice_pilot import (
    periodic_neighbors,
    project_mean_zero,
    site_coordinates,
    site_index,
)
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    independent_residuals,
    local_proposal,
)


OUTPUT_REL = (
    "reverse_physics/data/bt_euclidean_hessian_symbol_observations_v1.json"
)
OUTPUT_PATH = os.path.join(ROOT, OUTPUT_REL)


FIELDS = ("b", "c", "d", "alpha", "action_density")


def shift(
    index: int, displacement: tuple[int, ...], length: int, dimensions: int
) -> int:
    coordinates = site_coordinates(index, length, dimensions)
    return site_index(
        tuple(
            (coordinates[axis] + displacement[axis]) % length
            for axis in range(dimensions)
        ),
        length,
    )


def local_orbit_coefficients(
    field: list[float], residuals: list[float], coupling: float,
    length: int, dimensions: int,
) -> dict[str, float]:
    """Return translation/hypercubic averages of b, c, and d.

    The formulas independently differentiate
      A=(1/2)*sum_x r_x^2,
      r_x=sum_(y~x) exp(psi_y-psi_x)-2D,
    with psi=coupling*field.  Length >= 6 prevents range-two orbit aliasing.
    """
    if length < 6:
        raise ValueError("length must be at least six to avoid orbit aliasing")
    volume = len(field)
    degree = 2 * dimensions
    b_sum = c_sum = d_sum = 0.0
    b_count = c_count = d_count = 0
    unit = [
        tuple(int(axis == selected) for axis in range(dimensions))
        for selected in range(dimensions)
    ]
    for x in range(volume):
        psi_x = coupling * field[x]
        for axis in range(dimensions):
            y = shift(x, unit[axis], length, dimensions)
            t_xy = math.exp(coupling * (field[y] - field[x]))
            b_sum += -(
                (degree + 2.0 * residuals[x]) * t_xy
                + (degree + 2.0 * residuals[y]) / t_xy
            )
            b_count += 1

            displacement = tuple(2 * value for value in unit[axis])
            z = shift(x, displacement, length, dimensions)
            c_sum += math.exp(
                psi_x + coupling * field[z] - 2.0 * coupling * field[y]
            )
            c_count += 1

        for first in range(dimensions):
            for second in range(first + 1, dimensions):
                for first_sign in (-1, 1):
                    for second_sign in (-1, 1):
                        first_step = tuple(
                            first_sign * int(axis == first)
                            for axis in range(dimensions)
                        )
                        second_step = tuple(
                            second_sign * int(axis == second)
                            for axis in range(dimensions)
                        )
                        diagonal = tuple(
                            left + right
                            for left, right in zip(first_step, second_step)
                        )
                        middle_first = shift(
                            x, first_step, length, dimensions
                        )
                        middle_second = shift(
                            x, second_step, length, dimensions
                        )
                        z = shift(x, diagonal, length, dimensions)
                        psi_z = coupling * field[z]
                        d_sum += (
                            math.exp(
                                psi_x + psi_z
                                - 2.0 * coupling * field[middle_first]
                            )
                            + math.exp(
                                psi_x + psi_z
                                - 2.0 * coupling * field[middle_second]
                            )
                        )
                        d_count += 1
    b = b_sum / b_count
    c = c_sum / c_count
    d = d_sum / d_count
    return {
        "b": b,
        "c": c,
        "d": d,
        "alpha": -(b + 4.0 * c + 2.0 * (dimensions - 1) * d),
    }


def run(
    *, length: int, dimensions: int, coupling: float, seed: int,
    warmup: int, samples: int, thinning: int, proposal_width: float,
    blocks: int,
) -> dict:
    if samples % blocks:
        raise ValueError("samples must be divisible by blocks")
    neighbors = periodic_neighbors(length, dimensions)
    volume = length**dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    residuals = independent_residuals(field, coupling, neighbors)
    action = action_from_residuals(residuals, coupling)
    width = samples // blocks
    output_blocks = [
        {"sample_count": 0, **{f"sum_{name}": 0.0 for name in FIELDS}}
        for _ in range(blocks)
    ]
    accepted = attempted = recorded = 0
    started = time.monotonic()
    for sweep in range(warmup + samples * thinning):
        order = list(range(volume))
        rng.shuffle(order)
        for site in order:
            delta = rng.uniform(-proposal_width, proposal_width)
            try:
                delta_action, proposed = local_proposal(
                    field, residuals, site, delta, coupling, neighbors
                )
            except OverflowError:
                delta_action, proposed = math.inf, {}
            attempted += 1
            if math.isfinite(delta_action) and (
                delta_action <= 0.0 or rng.random() < math.exp(-delta_action)
            ):
                field[site] += delta
                action += delta_action
                for vertex, value in proposed.items():
                    residuals[vertex] = value
                accepted += 1
        field = project_mean_zero(field)
        if sweep < warmup or (sweep - warmup) % thinning:
            continue
        values = local_orbit_coefficients(
            field, residuals, coupling, length, dimensions
        )
        values["action_density"] = action / volume
        block = output_blocks[recorded // width]
        block["sample_count"] += 1
        for name in FIELDS:
            block[f"sum_{name}"] += values[name]
        recorded += 1
    recomputed_action = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    return {
        "dependency_tags": ["REDUCED-MODE", "EUCLIDEAN-SPECTRAL"],
        "result_kind": "FINITE_VOLUME_BINARY64_OBSERVATION",
        "does_not_establish": [
            "uniform interacting H^-1 estimate",
            "infinite-volume alpha limit",
            "continuum measure",
            "LORENTZIAN-CAUSAL claim",
        ],
        "algorithm": "independent local random-scan Metropolis plus local Hessian-orbit averages",
        "seed": seed,
        "lattice": {
            "length": length,
            "dimensions": dimensions,
            "volume": volume,
            "boundary": "PERIODIC",
        },
        "coupling": coupling,
        "warmup_sweeps": warmup,
        "recorded_samples": samples,
        "thinning_sweeps": thinning,
        "proposal_width": proposal_width,
        "block_count": blocks,
        "acceptance_rate": accepted / attempted,
        "elapsed_seconds": time.monotonic() - started,
        "final_action_recompute_residual": abs(action - recomputed_action),
        "symbol_identity": {
            "axial": "H_hat(p)=alpha_L*omega(p)+c_L*omega(p)^2",
            "alpha": "-(b_L+4*c_L+6*d_L)",
            "omega": "2*(1-cos(p))",
        },
        "blocks": output_blocks,
    }


def experiment(smoke: bool = False) -> dict:
    plans = (
        [(6, 20, 10, 1, 2)]
        if smoke
        else [(6, 600, 200, 3, 10), (8, 300, 100, 2, 10)]
    )
    runs = [
        run(
            length=length,
            dimensions=4,
            coupling=0.4,
            seed=270815000 + length,
            warmup=warmup,
            samples=samples,
            thinning=thinning,
            proposal_width=0.18,
            blocks=blocks,
        )
        for length, warmup, samples, thinning, blocks in plans
    ]
    return {
        "schema_version": "bt-euclidean-hessian-symbol-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "runs": runs,
        "does_not_establish": [
            "a nonzero infinite-volume helicity coefficient",
            "a conditioned-background score estimate",
            "a uniform interacting H^-1 estimate or divergence",
            "a continuum measure, Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL claim",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if not args.smoke and not args.reproduce:
        parser.error("choose --smoke or --reproduce")
    payload = experiment(smoke=args.smoke)
    target = args.output or (None if args.smoke else OUTPUT_PATH)
    if target:
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"wrote {target}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
