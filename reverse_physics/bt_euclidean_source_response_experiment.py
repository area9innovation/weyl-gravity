#!/usr/bin/env python3
"""Memory-bounded BT source-response and whole-mode-mixing diagnostic.

The local update is the independently audited random-scan Metropolis kernel.
The optional whole-mode update proposes a symmetric displacement along one
complete lowest cosine/sine phase and accepts it using a full action
recomputation.  Stored results are binary64 observations, not uniform bounds.
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
)
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    independent_residuals,
    local_proposal,
)


OUTPUT_REL = "reverse_physics/data/bt_euclidean_source_response_observations_v1.json"
OUTPUT_PATH = os.path.join(ROOT, OUTPUT_REL)
FIELDS = ("action_density", "mode2", "mode2_square")


def lowest_phases(length: int, dimensions: int) -> list[list[float]]:
    """Cosine then sine for each axis, all mean zero for length >= 3."""
    volume = length**dimensions
    coordinates = [
        site_coordinates(index, length, dimensions)
        for index in range(volume)
    ]
    phases: list[list[float]] = []
    for axis in range(dimensions):
        phases.append(
            [
                math.cos(2.0 * math.pi * point[axis] / length)
                for point in coordinates
            ]
        )
        phases.append(
            [
                math.sin(2.0 * math.pi * point[axis] / length)
                for point in coordinates
            ]
        )
    return phases


def source_mode2(field: list[float], phases: list[list[float]]) -> float:
    """Axis average of |N^-1/2 sum phi exp(-ipx)|^2."""
    volume = len(field)
    dimensions = len(phases) // 2
    total = 0.0
    for axis in range(dimensions):
        real = math.fsum(
            value * phase
            for value, phase in zip(field, phases[2 * axis])
        ) / math.sqrt(volume)
        imag = math.fsum(
            value * phase
            for value, phase in zip(field, phases[2 * axis + 1])
        ) / math.sqrt(volume)
        total += real * real + imag * imag
    return total / dimensions


def empty_block() -> dict[str, float | int]:
    return {
        "sample_count": 0,
        **{f"sum_{field}": 0.0 for field in FIELDS},
    }


def run(
    *,
    length: int,
    dimensions: int,
    coupling: float,
    seed: int,
    warmup: int,
    samples: int,
    thinning: int,
    local_width: float,
    blocks: int,
    mode_width: float | None,
) -> dict:
    if samples % blocks:
        raise ValueError("samples must be divisible by blocks")
    neighbors = periodic_neighbors(length, dimensions)
    phases = lowest_phases(length, dimensions)
    volume = length**dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    residuals = independent_residuals(field, coupling, neighbors)
    action = action_from_residuals(residuals, coupling)
    output_blocks = [empty_block() for _ in range(blocks)]
    block_width = samples // blocks
    local_accepted = local_attempted = 0
    mode_accepted = mode_attempted = recorded = 0
    started = time.monotonic()

    for sweep in range(warmup + samples * thinning):
        order = list(range(volume))
        rng.shuffle(order)
        for site in order:
            delta = rng.uniform(-local_width, local_width)
            try:
                delta_action, proposed = local_proposal(
                    field,
                    residuals,
                    site,
                    delta,
                    coupling,
                    neighbors,
                )
            except OverflowError:
                delta_action, proposed = math.inf, {}
            local_attempted += 1
            if math.isfinite(delta_action) and (
                delta_action <= 0.0
                or rng.random() < math.exp(-delta_action)
            ):
                field[site] += delta
                action += delta_action
                for vertex, value in proposed.items():
                    residuals[vertex] = value
                local_accepted += 1
        field = project_mean_zero(field)

        if mode_width is not None:
            phase = phases[rng.randrange(len(phases))]
            delta = rng.uniform(-mode_width, mode_width)
            proposed_field = [
                value + delta * component
                for value, component in zip(field, phase)
            ]
            proposed_residuals = independent_residuals(
                proposed_field, coupling, neighbors
            )
            proposed_action = action_from_residuals(
                proposed_residuals, coupling
            )
            delta_action = proposed_action - action
            mode_attempted += 1
            if delta_action <= 0.0 or rng.random() < math.exp(-delta_action):
                field = proposed_field
                residuals = proposed_residuals
                action = proposed_action
                mode_accepted += 1

        if sweep < warmup or (sweep - warmup) % thinning:
            continue
        mode2 = source_mode2(field, phases)
        values = {
            "action_density": action / volume,
            "mode2": mode2,
            "mode2_square": mode2 * mode2,
        }
        block = output_blocks[recorded // block_width]
        block["sample_count"] += 1
        for name, value in values.items():
            block[f"sum_{name}"] += value
        recorded += 1

    recomputed_action = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    omega = 4.0 * math.sin(math.pi / length) ** 2
    return {
        "algorithm": (
            "local random-scan Metropolis"
            if mode_width is None
            else "local random-scan Metropolis plus symmetric whole-lowest-mode Metropolis"
        ),
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
        "local_proposal_width": local_width,
        "whole_mode_proposal_width": mode_width,
        "whole_mode_proposals_per_sweep": int(mode_width is not None),
        "block_count": blocks,
        "local_acceptance_rate": local_accepted / local_attempted,
        "whole_mode_acceptance_rate": (
            mode_accepted / mode_attempted if mode_attempted else None
        ),
        "elapsed_seconds": time.monotonic() - started,
        "final_action_recompute_residual": abs(action - recomputed_action),
        "mode": {
            "axis_average": True,
            "phase_pair": "complete lowest cosine-sine pair",
            "field_coordinate": "phi with psi=lambda*phi",
            "omega": omega,
            "free_mode2": 1.0 / (omega * omega),
            "bilaplacian_ratio": "omega^2*M2",
            "tension_ratio": "omega*M2",
        },
        "blocks": output_blocks,
    }


def experiment(smoke: bool = False) -> dict:
    if smoke:
        plans = [
            (4, 10, 20, 1, 4, 0.08, None, 150826004),
            (4, 10, 20, 1, 4, 0.08, 0.05, 150826104),
        ]
    else:
        plans = [
            (6, 300, 100, 2, 10, 0.18, 0.05, 150826106),
            (8, 300, 100, 2, 10, 0.18, None, 150826008),
            (8, 300, 100, 2, 10, 0.18, 0.035, 150826108),
        ]
    runs = [
        run(
            length=length,
            dimensions=4,
            coupling=0.4,
            seed=seed,
            warmup=warmup,
            samples=samples,
            thinning=thinning,
            local_width=local_width,
            blocks=blocks,
            mode_width=mode_width,
        )
        for (
            length,
            warmup,
            samples,
            thinning,
            blocks,
            local_width,
            mode_width,
            seed,
        ) in plans
    ]
    return {
        "schema_version": "bt-euclidean-source-response-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "per_configuration_fields": {
            "mode2": "axis average of the complete lowest complex-mode modulus squared",
            "mode2_square": "square of that axis-averaged mode2; not the axis average of individual fourth powers",
        },
        "runs": runs,
        "does_not_establish": [
            "an equilibrated L=8 source susceptibility or scaling law",
            "a volume-uniform lowest-mode or interacting H^-1 estimate",
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
