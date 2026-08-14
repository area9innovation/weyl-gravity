#!/usr/bin/env python3
"""Independent-sampler finite-volume experiment for the BT Euclidean lattice.

This is the expensive observation producer.  It deliberately keeps the local
Metropolis action-difference implementation separate from the HMC force used
by ``bt_euclidean_lattice_pilot``.  The emitted block sufficient statistics
can be audited without rerunning either Markov chain.

All outputs are finite-volume binary64 observations.  Nothing here certifies
a continuum limit or a Lorentzian theory.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from reverse_physics.bt_euclidean_lattice_pilot import (
    action_gradient,
    hamiltonian,
    leapfrog,
    periodic_neighbors,
    project_mean_zero,
    site_coordinates,
)


OUTPUT_REL = (
    "reverse_physics/data/"
    "bt_euclidean_lattice_step_scaling_observations_v1.json"
)
OUTPUT_PATH = os.path.join(REPO_ROOT, OUTPUT_REL)


def independent_residuals(
    field: list[float], coupling: float, neighbors: list[tuple[int, ...]]
) -> list[float]:
    """Residuals computed without the HMC action/gradient implementation."""
    degree = len(neighbors[0])
    if coupling == 0.0:
        return [
            sum(field[j] for j in row) - degree * field[i]
            for i, row in enumerate(neighbors)
        ]
    return [
        sum(math.exp(coupling * (field[j] - field[i])) for j in row) - degree
        for i, row in enumerate(neighbors)
    ]


def action_from_residuals(residuals: list[float], coupling: float) -> float:
    scale = 1.0 if coupling == 0.0 else coupling
    return sum(value * value for value in residuals) / (2.0 * scale * scale)


def local_proposal(
    field: list[float],
    residuals: list[float],
    site: int,
    delta: float,
    coupling: float,
    neighbors: list[tuple[int, ...]],
) -> tuple[float, dict[int, float]]:
    """Return the exact local action change and proposed affected residuals.

    The formula is independently derived from
      r_i=sum_(j~i) exp(lambda*(phi_j-phi_i))-q.
    It does not call the global HMC action.  Duplicate periodic edges are
    counted, so the routine also works on very small smoke lattices.
    """
    degree = len(neighbors[0])
    incoming = Counter(neighbors[site])
    proposed: dict[int, float] = {}
    if coupling == 0.0:
        proposed[site] = residuals[site] - degree * delta
        for vertex, multiplicity in incoming.items():
            proposed[vertex] = residuals[vertex] + multiplicity * delta
        scale = 1.0
    else:
        up = math.exp(coupling * delta)
        down = 1.0 / up
        proposed[site] = (residuals[site] + degree) * down - degree
        for vertex, multiplicity in incoming.items():
            edge = math.exp(coupling * (field[site] - field[vertex]))
            proposed[vertex] = (
                residuals[vertex] + multiplicity * edge * (up - 1.0)
            )
        scale = coupling
    old = sum(residuals[index] ** 2 for index in proposed)
    new = sum(value * value for value in proposed.values())
    return (new - old) / (2.0 * scale * scale), proposed


def direct_local_delta_check(
    *, length: int = 3, dimensions: int = 2, coupling: float = 0.4
) -> float:
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    field = project_mean_zero([
        math.sin(0.31 * (index + 1)) / 7.0 for index in range(volume)
    ])
    residuals = independent_residuals(field, coupling, neighbors)
    worst = 0.0
    for site, delta in ((0, 0.037), (volume // 2, -0.052), (volume - 1, 0.019)):
        predicted, _ = local_proposal(
            field, residuals, site, delta, coupling, neighbors
        )
        proposed_field = field.copy()
        proposed_field[site] += delta
        direct = (
            action_from_residuals(
                independent_residuals(proposed_field, coupling, neighbors),
                coupling,
            )
            - action_from_residuals(residuals, coupling)
        )
        worst = max(worst, abs(predicted - direct))
    return worst


def mode_powers(
    field: list[float], length: int, dimensions: int
) -> tuple[float, float]:
    """Axis-pooled second and fourth powers of the lowest complex mode."""
    volume = len(field)
    momentum = 2.0 * math.pi / length
    normalization = math.sqrt(volume)
    coordinates = [site_coordinates(i, length, dimensions)
                   for i in range(volume)]
    squares = []
    for axis in range(dimensions):
        real = sum(
            field[i] * math.cos(momentum * coordinates[i][axis])
            for i in range(volume)
        ) / normalization
        imaginary = -sum(
            field[i] * math.sin(momentum * coordinates[i][axis])
            for i in range(volume)
        ) / normalization
        squares.append(real * real + imaginary * imaginary)
    second = sum(squares) / dimensions
    fourth = sum(value * value for value in squares) / dimensions
    return second, fourth


def empty_block() -> dict[str, float | int]:
    return {
        "sample_count": 0,
        "axis_count": 0,
        "sum_action_density": 0.0,
        "sum_field_variance": 0.0,
        "sum_mode2": 0.0,
        "sum_mode4": 0.0,
    }


def add_measurement(
    block: dict[str, float | int], field: list[float], action: float,
    length: int, dimensions: int,
) -> None:
    volume = len(field)
    centered = project_mean_zero(field)
    mode2, mode4 = mode_powers(centered, length, dimensions)
    block["sample_count"] += 1
    block["axis_count"] += dimensions
    block["sum_action_density"] += action / volume
    block["sum_field_variance"] += sum(q * q for q in centered) / volume
    block["sum_mode2"] += dimensions * mode2
    block["sum_mode4"] += dimensions * mode4


def run_local_metropolis(
    *, coupling: float, seed: int, length: int, dimensions: int,
    warmup: int, samples: int, thinning: int, proposal_width: float,
    blocks: int,
) -> dict:
    if samples % blocks:
        raise ValueError("samples must be divisible by blocks")
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    residuals = independent_residuals(field, coupling, neighbors)
    action = action_from_residuals(residuals, coupling)
    accepted = attempted = 0
    output_blocks = [empty_block() for _ in range(blocks)]
    block_width = samples // blocks
    total_sweeps = warmup + samples * thinning
    recorded = 0
    started = time.monotonic()
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
                delta_action <= 0.0 or rng.random() < math.exp(-delta_action)
            ):
                field[site] += delta
                for vertex, value in proposed.items():
                    residuals[vertex] = value
                action += delta_action
                accepted += 1
        # Exact shift invariance makes this recentering action-neutral.
        field = project_mean_zero(field)
        if sweep >= warmup and (sweep - warmup) % thinning == 0:
            block = output_blocks[recorded // block_width]
            add_measurement(block, field, action, length, dimensions)
            recorded += 1
    recomputed_action = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    return {
        "algorithm": "independent local random-scan Metropolis",
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
        "final_action_recompute_residual": abs(action - recomputed_action),
        "elapsed_seconds": time.monotonic() - started,
        "blocks": output_blocks,
    }


def run_hmc_blocks(
    *, coupling: float, seed: int, length: int, dimensions: int,
    warmup: int, samples: int, thinning: int, step_size: float,
    leapfrog_steps: int, blocks: int,
) -> dict:
    if samples % blocks:
        raise ValueError("samples must be divisible by blocks")
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    accepted = attempted = 0
    output_blocks = [empty_block() for _ in range(blocks)]
    block_width = samples // blocks
    total = warmup + samples * thinning
    recorded = 0
    started = time.monotonic()
    for trajectory in range(total):
        momentum = project_mean_zero([
            rng.gauss(0.0, 1.0) for _ in range(volume)
        ])
        initial = hamiltonian(field, momentum, coupling, neighbors)
        try:
            proposed_field, proposed_momentum = leapfrog(
                field, momentum, coupling, neighbors, step_size,
                leapfrog_steps,
            )
            delta_h = hamiltonian(
                proposed_field, proposed_momentum, coupling, neighbors
            ) - initial
        except (OverflowError, ValueError):
            proposed_field, delta_h = field, math.inf
        attempted += 1
        if math.isfinite(delta_h) and (
            delta_h <= 0.0 or rng.random() < math.exp(-delta_h)
        ):
            field = proposed_field
            accepted += 1
        if trajectory >= warmup and (trajectory - warmup) % thinning == 0:
            action, _, _ = action_gradient(field, coupling, neighbors)
            block = output_blocks[recorded // block_width]
            add_measurement(block, field, action, length, dimensions)
            recorded += 1
    return {
        "algorithm": "zero-mode-projected HMC",
        "seed": seed,
        "lattice": {
            "length": length,
            "dimensions": dimensions,
            "volume": volume,
            "boundary": "PERIODIC",
        },
        "coupling": coupling,
        "warmup_trajectories": warmup,
        "recorded_samples": samples,
        "thinning_trajectories": thinning,
        "step_size": step_size,
        "leapfrog_steps": leapfrog_steps,
        "block_count": blocks,
        "acceptance_rate": accepted / attempted,
        "elapsed_seconds": time.monotonic() - started,
        "blocks": output_blocks,
    }


def experiment(smoke: bool = False) -> dict:
    if smoke:
        plans = [
            ("metropolis", 3, 20, 40, 1, 0.08, 0, 4),
            ("hmc", 3, 20, 40, 1, 0.025, 5, 4),
        ]
        dimensions = 2
    else:
        # The production statistics are intentionally moderate: the purpose is
        # sampler reproduction and a two-volume preflight, not extrapolation.
        plans = [
            ("metropolis-free", 4, 1600, 1600, 4, 0.18, 0, 20),
            ("metropolis", 4, 1600, 1600, 4, 0.18, 0, 20),
            ("hmc", 4, 300, 600, 2, 0.035, 18, 20),
            ("metropolis", 6, 3000, 2000, 4, 0.18, 0, 20),
            ("hmc", 6, 300, 600, 2, 0.018, 24, 20),
        ]
        dimensions = 4
    runs = []
    for algorithm, length, warmup, samples, thinning, scale, steps, blocks in plans:
        seed = 260814000 + length * 100 + {
            "metropolis-free": 0,
            "metropolis": 1,
            "hmc": 2,
        }[algorithm]
        if algorithm.startswith("metropolis"):
            run = run_local_metropolis(
                coupling=0.0 if algorithm == "metropolis-free" else 0.4,
                seed=seed, length=length,
                dimensions=dimensions, warmup=warmup, samples=samples,
                thinning=thinning, proposal_width=scale, blocks=blocks,
            )
        else:
            run = run_hmc_blocks(
                coupling=0.4, seed=seed, length=length,
                dimensions=dimensions, warmup=warmup, samples=samples,
                thinning=thinning, step_size=scale,
                leapfrog_steps=steps, blocks=blocks,
            )
        print(
            f"{algorithm} L={length}: acceptance={run['acceptance_rate']:.4f}, "
            f"elapsed={run['elapsed_seconds']:.2f}s",
            flush=True,
        )
        runs.append(run)
    return {
        "schema_version": "bt-euclidean-step-scaling-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "action": (
            "S_E,L=(2*lambda^2)^-1 sum_x "
            "[sum_(y~x) exp(lambda*(phi_y-phi_x))-2*d]^2 for lambda!=0; "
            "the lambda=0 calibration uses its continuous limit "
            "S_E,L=(1/2) sum_x (Delta_L phi_x)^2"
        ),
        "mode_scheme": {
            "z_mu": (
                "V^-1/2 sum_x phi_x exp(-2*pi*i*x_mu/L), "
                "mu=1,...,d"
            ),
            "M2": "ensemble-and-axis average of |z_mu|^2",
            "M4": "ensemble-and-axis average of |z_mu|^4",
            "u_L": "2-M4/M2^2",
            "gaussian_reference": "u_L=0 for a centered complex Gaussian mode",
        },
        "smoke": smoke,
        "local_delta_direct_check_max_residual": direct_local_delta_check(),
        "runs": runs,
        "does_not_establish": [
            "a renormalized continuum coupling",
            "matched physical volumes",
            "a continuum or infinite-volume limit",
            "Osterwalder--Schrader reflection positivity",
            "analytic continuation or Lorentzian scattering",
            "a q8-q10 observable or Weyl-gravity transfer",
        ],
    }


def add_free_calibration(result: dict) -> dict:
    """Add or replace the independent L=4 free-field calibration."""
    result["runs"] = [run for run in result["runs"] if run["coupling"] != 0.0]
    free_run = run_local_metropolis(
        coupling=0.0,
        seed=260814400,
        length=4,
        dimensions=4,
        warmup=1600,
        samples=1600,
        thinning=4,
        proposal_width=0.18,
        blocks=20,
    )
    print(
        f"metropolis-free L=4: acceptance={free_run['acceptance_rate']:.4f}, "
        f"elapsed={free_run['elapsed_seconds']:.2f}s",
        flush=True,
    )
    result["runs"].insert(0, free_run)
    return result


def load_production_observations() -> dict:
    with open(OUTPUT_PATH, encoding="utf-8") as handle:
        result = json.load(handle)
    if result.get("smoke") or len(result.get("runs", [])) not in (4, 5):
        raise ValueError("production observation file is missing or malformed")
    return result


def refresh_metropolis() -> dict:
    """Replace only local chains in an existing production observation file."""
    result = load_production_observations()
    replacements = {}
    for length, warmup, samples in ((4, 1600, 1600), (6, 3000, 2000)):
        run = run_local_metropolis(
            coupling=0.4,
            seed=260814000 + length * 100 + 1,
            length=length,
            dimensions=4,
            warmup=warmup,
            samples=samples,
            thinning=4,
            proposal_width=0.18,
            blocks=20,
        )
        print(
            f"metropolis L={length}: acceptance={run['acceptance_rate']:.4f}, "
            f"elapsed={run['elapsed_seconds']:.2f}s",
            flush=True,
        )
        replacements[length] = run
    result["runs"] = [
        replacements.get(run["lattice"]["length"], run)
        if run["algorithm"] == "independent local random-scan Metropolis"
        else run
        for run in result["runs"]
        if run["coupling"] != 0.0
    ]
    result = add_free_calibration(result)
    result["local_delta_direct_check_max_residual"] = direct_local_delta_check()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-metropolis", action="store_true")
    parser.add_argument("--add-free-calibration", action="store_true")
    args = parser.parse_args(argv)
    modes = sum((args.smoke, args.refresh_metropolis, args.add_free_calibration))
    if modes > 1:
        raise SystemExit("choose only one run mode")
    if args.refresh_metropolis:
        result = refresh_metropolis()
    elif args.add_free_calibration:
        result = add_free_calibration(load_production_observations())
    else:
        result = experiment(smoke=args.smoke)
    if args.write:
        if args.smoke:
            raise SystemExit("refusing to overwrite production observations with smoke data")
        with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"wrote {OUTPUT_REL}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
