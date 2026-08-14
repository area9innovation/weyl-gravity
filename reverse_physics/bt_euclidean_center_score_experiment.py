#!/usr/bin/env python3
"""Finite-volume diagnostic for BT lowest-mode conditional centers.

This is a deterministic binary64 observation producer, not a certificate of
an annealed bound.  It uses the independent local Metropolis update already
audited by the lattice step-scaling preflight and solves the one-dimensional
fiber-mode equation by monotone bisection.
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
    action_gradient,
    periodic_neighbors,
    project_mean_zero,
    site_coordinates,
)
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    independent_residuals,
    local_proposal,
)


OUTPUT_REL = "reverse_physics/data/bt_euclidean_center_score_observations_v1.json"
OUTPUT_PATH = os.path.join(ROOT, OUTPUT_REL)


FIELDS = (
    "sum_t",
    "sum_t2",
    "sum_mode_center",
    "sum_mode_center2",
    "sum_recentered",
    "sum_recentered2",
    "sum_action_density",
    "sum_zero_fiber_score2",
)


def empty_block() -> dict[str, float | int]:
    return {"sample_count": 0, **{name: 0.0 for name in FIELDS}}


def lowest_cosine(length: int, dimensions: int) -> list[float]:
    momentum = 2.0 * math.pi / length
    volume = length**dimensions
    return [
        math.cos(momentum * site_coordinates(index, length, dimensions)[0])
        for index in range(volume)
    ]


def fiber_score(
    background: list[float], coordinate: float, mode: list[float],
    coupling: float, neighbors: list[tuple[int, ...]],
) -> float:
    field = [eta + coordinate * h for eta, h in zip(background, mode)]
    _, gradient, _ = action_gradient(field, coupling, neighbors)
    return math.fsum(g * h for g, h in zip(gradient, mode))


def fiber_mode(
    background: list[float], start: float, mode: list[float],
    coupling: float, neighbors: list[tuple[int, ...]],
) -> tuple[float, float, int]:
    """Find the unique score zero using only the certified monotonicity."""
    initial_score = fiber_score(background, start, mode, coupling, neighbors)
    evaluations = 1
    if abs(initial_score) <= 1.0e-12:
        return start, initial_score, evaluations
    step = 0.04
    if initial_score > 0.0:
        upper = start
        lower = start - step
        lower_score = fiber_score(
            background, lower, mode, coupling, neighbors
        )
        evaluations += 1
        while lower_score > 0.0:
            step *= 2.0
            lower = start - step
            lower_score = fiber_score(
                background, lower, mode, coupling, neighbors
            )
            evaluations += 1
    else:
        lower = start
        upper = start + step
        upper_score = fiber_score(
            background, upper, mode, coupling, neighbors
        )
        evaluations += 1
        while upper_score < 0.0:
            step *= 2.0
            upper = start + step
            upper_score = fiber_score(
                background, upper, mode, coupling, neighbors
            )
            evaluations += 1
    for _ in range(36):
        midpoint = (lower + upper) / 2.0
        midpoint_score = fiber_score(
            background, midpoint, mode, coupling, neighbors
        )
        evaluations += 1
        if midpoint_score < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    center = (lower + upper) / 2.0
    residual = fiber_score(background, center, mode, coupling, neighbors)
    return center, residual, evaluations + 1


def run(
    *, length: int, dimensions: int, coupling: float, seed: int,
    warmup: int, samples: int, thinning: int, proposal_width: float,
    blocks: int,
) -> dict:
    if samples % blocks:
        raise ValueError("samples must be divisible by blocks")
    neighbors = periodic_neighbors(length, dimensions)
    volume = length**dimensions
    mode = lowest_cosine(length, dimensions)
    mode_norm_squared = math.fsum(value * value for value in mode)
    omega = 4.0 * math.sin(math.pi / length) ** 2
    curvature = (2.0 / 9.0) * volume * omega * omega
    rng = random.Random(seed)
    field = [0.0] * volume
    residuals = independent_residuals(field, coupling, neighbors)
    action = action_from_residuals(residuals, coupling)
    output_blocks = [empty_block() for _ in range(blocks)]
    block_width = samples // blocks
    accepted = attempted = recorded = score_evaluations = 0
    maximum_mode_score_residual = 0.0
    maximum_center_score_inequality_residual = 0.0
    maximum_absolute_mode_center = 0.0
    started = time.monotonic()
    total_sweeps = warmup + samples * thinning
    for sweep in range(total_sweeps):
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
                delta_action <= 0.0
                or rng.random() < math.exp(-delta_action)
            ):
                field[site] += delta
                action += delta_action
                for vertex, value in proposed.items():
                    residuals[vertex] = value
                accepted += 1
        field = project_mean_zero(field)
        if sweep < warmup or (sweep - warmup) % thinning:
            continue
        coordinate = math.fsum(
            value * h for value, h in zip(field, mode)
        ) / mode_norm_squared
        background = [
            value - coordinate * h for value, h in zip(field, mode)
        ]
        zero_score = fiber_score(
            background, 0.0, mode, coupling, neighbors
        )
        center, center_score, evaluations = fiber_mode(
            background, coordinate, mode, coupling, neighbors
        )
        score_evaluations += evaluations + 1
        recentered = coordinate - center
        block = output_blocks[recorded // block_width]
        block["sample_count"] += 1
        values = {
            "sum_t": coordinate,
            "sum_t2": coordinate * coordinate,
            "sum_mode_center": center,
            "sum_mode_center2": center * center,
            "sum_recentered": recentered,
            "sum_recentered2": recentered * recentered,
            "sum_action_density": action / volume,
            "sum_zero_fiber_score2": zero_score * zero_score,
        }
        for name, value in values.items():
            block[name] += value
        maximum_mode_score_residual = max(
            maximum_mode_score_residual, abs(center_score)
        )
        maximum_center_score_inequality_residual = max(
            maximum_center_score_inequality_residual,
            center * center - zero_score * zero_score / (curvature * curvature),
        )
        maximum_absolute_mode_center = max(
            maximum_absolute_mode_center, abs(center)
        )
        recorded += 1
    recomputed_action = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    return {
        "algorithm": "independent local random-scan Metropolis plus monotone fiber-score bisection",
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
        "mode": {
            "axis": 0,
            "phase": "cosine",
            "omega": omega,
            "norm_squared": mode_norm_squared,
            "certified_curvature_lower_bound": curvature,
        },
        "root_diagnostic": {
            "score_evaluations": score_evaluations,
            "maximum_absolute_mode_score_residual": maximum_mode_score_residual,
            "maximum_center_score_inequality_residual": maximum_center_score_inequality_residual,
            "maximum_absolute_mode_center": maximum_absolute_mode_center,
        },
        "blocks": output_blocks,
    }


def experiment(smoke: bool = False) -> dict:
    dimensions = 4
    plans = (
        [(4, 10, 20, 1, 4, 0.08)]
        if smoke
        else [
            (4, 800, 400, 4, 10, 0.18),
            (6, 1500, 200, 4, 10, 0.18),
        ]
    )
    runs = []
    for length, warmup, samples, thinning, blocks, width in plans:
        run_data = run(
            length=length,
            dimensions=dimensions,
            coupling=0.4,
            seed=270814000 + length,
            warmup=warmup,
            samples=samples,
            thinning=thinning,
            proposal_width=width,
            blocks=blocks,
        )
        print(
            f"center diagnostic L={length}: "
            f"acceptance={run_data['acceptance_rate']:.4f}, "
            f"elapsed={run_data['elapsed_seconds']:.2f}s",
            flush=True,
        )
        runs.append(run_data)
    return {
        "schema_version": "bt-euclidean-center-score-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "coordinate": "phi=eta+t*h with eta orthogonal to h and h_x=cos(2*pi*x_0/L)",
        "center": "unique zero of d/dt S_lambda(eta+t*h), found by monotone bisection",
        "runs": runs,
        "does_not_establish": [
            "an annealed center theorem or a statistically precise scaling law",
            "a normalized lowest-mode or interacting H^-1 bound",
            "tightness, a continuum measure, Born, Krein, or LORENTZIAN-CAUSAL physics",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
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
