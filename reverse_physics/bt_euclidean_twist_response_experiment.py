#!/usr/bin/env python3
"""Memory-bounded full-Gibbs diagnostic for the BT twist response.

This binary64 observer measures the diamagnetic uniform-twist curvature and
the subtractive integrated-current susceptibility.  It is finite-volume
evidence, not a certificate of a positive thermodynamic helicity modulus.
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

from reverse_physics.bt_euclidean_hessian_symbol_experiment import shift
from reverse_physics.bt_euclidean_lattice_pilot import (
    periodic_neighbors,
    project_mean_zero,
)
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    independent_residuals,
    local_proposal,
)


OUTPUT_REL = (
    "reverse_physics/data/bt_euclidean_twist_response_observations_v1.json"
)
OUTPUT_PATH = os.path.join(ROOT, OUTPUT_REL)


def twist_observables(
    field: list[float], residuals: list[float], coupling: float,
    length: int, dimensions: int,
) -> tuple[list[float], list[float]]:
    """Return I_mu=A'_mu(0) and D_mu=A''_mu(0) for every uniform twist."""
    volume = len(field)
    currents = []
    curvatures = []
    for selected in range(dimensions):
        forward = tuple(
            int(axis == selected) for axis in range(dimensions)
        )
        backward = tuple(-value for value in forward)
        current = curvature = 0.0
        for x in range(volume):
            plus = shift(x, forward, length, dimensions)
            minus = shift(x, backward, length, dimensions)
            t_plus = math.exp(coupling * (field[plus] - field[x]))
            t_minus = math.exp(coupling * (field[minus] - field[x]))
            difference = t_plus - t_minus
            current += residuals[x] * difference
            curvature += (
                difference * difference
                + residuals[x] * (t_plus + t_minus)
            )
        currents.append(current)
        curvatures.append(curvature)
    return currents, curvatures


def empty_block() -> dict[str, float | int]:
    return {
        "sample_count": 0,
        "axis_count": 0,
        "sum_action_density": 0.0,
        "sum_twist_curvature_density": 0.0,
        "sum_integrated_current": 0.0,
        "sum_integrated_current2": 0.0,
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
    output_blocks = [empty_block() for _ in range(blocks)]
    block_width = samples // blocks
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
        currents, curvatures = twist_observables(
            field, residuals, coupling, length, dimensions
        )
        block = output_blocks[recorded // block_width]
        block["sample_count"] += 1
        block["axis_count"] += dimensions
        block["sum_action_density"] += action / volume
        block["sum_twist_curvature_density"] += math.fsum(
            value / volume for value in curvatures
        )
        block["sum_integrated_current"] += math.fsum(currents)
        block["sum_integrated_current2"] += math.fsum(
            value * value for value in currents
        )
        recorded += 1
    recomputed_action = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    return {
        "algorithm": "independent local random-scan Metropolis plus exact uniform-twist derivatives",
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
        "definitions": {
            "twisted_residual": "r_x(theta)=t_(x,x+e)*exp(theta)+t_(x,x-e)*exp(-theta)+sum_transverse t_xy-2D",
            "integrated_current": "I_mu=partial_theta A_theta at zero",
            "twist_curvature": "D_mu=partial_theta^2 A_theta at zero",
            "scaled_response": "lambda^2*f_L''(0)=E[D_mu]/N-Var(I_mu)/(N*lambda^2)",
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
        "schema_version": "bt-euclidean-twist-response-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "runs": runs,
        "does_not_establish": [
            "a positive thermodynamic twist modulus",
            "inhomogeneous current-response control or Witten coercivity",
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
