#!/usr/bin/env python3
"""Bounded independent-sampler experiment for the BT reflected witness."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

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
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    independent_residuals,
    local_proposal,
)


DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_os_witness_observations_v1.json"
)
DATA_PATH = os.path.join(REPO_ROOT, DATA_REL)


def reflected_observable(
    field: list[float], length: int, dimensions: int
) -> tuple[float, float, float]:
    if length != 6 or dimensions != 4:
        raise ValueError("the certified witness is defined on the 6^4 lattice")
    spatial_volume = length ** (dimensions - 1)
    slices = [0.0] * length
    for site, value in enumerate(field):
        time_coordinate = site_coordinates(site, length, dimensions)[0]
        slices[time_coordinate] += value
    slices = [value / spatial_volume for value in slices]
    positive = -slices[1] + 2.0 * slices[2] - slices[3]
    reflected = -slices[0] + 2.0 * slices[5] - slices[4]
    return positive, reflected, positive * reflected


def run_local(
    *, seed: int, warmup: int, samples: int, thinning: int,
    proposal_width: float,
) -> dict:
    length, dimensions, coupling = 6, 4, 0.4
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    residuals = independent_residuals(field, coupling, neighbors)
    action = action_from_residuals(residuals, coupling)
    accepted = attempted = recorded = 0
    measurements = []
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
                for vertex, value in proposed.items():
                    residuals[vertex] = value
                action += delta_action
                accepted += 1
        field = project_mean_zero(field)
        if sweep >= warmup and (sweep - warmup) % thinning == 0:
            positive, reflected, product = reflected_observable(
                field, length, dimensions
            )
            measurements.append({
                "positive_F": positive,
                "reflected_F": reflected,
                "reflected_product": product,
            })
            recorded += 1
    recomputed = action_from_residuals(
        independent_residuals(field, coupling, neighbors), coupling
    )
    return {
        "algorithm": "independent local random-scan Metropolis",
        "seed": seed,
        "coupling": coupling,
        "lattice": {"length": length, "dimensions": dimensions, "volume": volume},
        "warmup_sweeps": warmup,
        "recorded_samples": recorded,
        "thinning_sweeps": thinning,
        "proposal_width": proposal_width,
        "acceptance_rate": accepted / attempted,
        "final_action_recompute_residual": abs(action - recomputed),
        "elapsed_seconds_observed": time.monotonic() - started,
        "measurements": measurements,
    }


def run_hmc(
    *, seed: int, warmup: int, samples: int, thinning: int,
    step_size: float, leapfrog_steps: int,
) -> dict:
    length, dimensions, coupling = 6, 4, 0.4
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    accepted = attempted = recorded = 0
    measurements = []
    started = time.monotonic()
    for trajectory in range(warmup + samples * thinning):
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
            positive, reflected, product = reflected_observable(
                field, length, dimensions
            )
            measurements.append({
                "positive_F": positive,
                "reflected_F": reflected,
                "reflected_product": product,
            })
            recorded += 1
    action, _, _ = action_gradient(field, coupling, neighbors)
    return {
        "algorithm": "zero-mode-projected HMC",
        "seed": seed,
        "coupling": coupling,
        "lattice": {"length": length, "dimensions": dimensions, "volume": volume},
        "warmup_trajectories": warmup,
        "recorded_samples": recorded,
        "thinning_trajectories": thinning,
        "step_size": step_size,
        "leapfrog_steps": leapfrog_steps,
        "acceptance_rate": accepted / attempted,
        "final_action_density": action / volume,
        "elapsed_seconds_observed": time.monotonic() - started,
        "measurements": measurements,
    }


def experiment(smoke: bool = False) -> dict:
    if smoke:
        plans = [
            ("metropolis", 2608146101, 8, 8, 1),
            ("hmc", 2608146201, 4, 8, 1),
        ]
    else:
        plans = [
            (algorithm, base + replica, 3000 if algorithm == "metropolis" else 300,
             1600 if algorithm == "metropolis" else 800,
             4 if algorithm == "metropolis" else 2)
            for algorithm, base in (
                ("metropolis", 2608146100),
                ("hmc", 2608146200),
            )
            for replica in range(1, 5)
        ]
    runs = []
    for algorithm, seed, warmup, samples, thinning in plans:
        if algorithm == "metropolis":
            run = run_local(
                seed=seed,
                warmup=warmup,
                samples=samples,
                thinning=thinning,
                proposal_width=0.18,
            )
        else:
            run = run_hmc(
                seed=seed,
                warmup=warmup,
                samples=samples,
                thinning=thinning,
                step_size=0.018,
                leapfrog_steps=24,
            )
        print(
            f"{algorithm} seed={seed}: acceptance={run['acceptance_rate']:.4f}, "
            f"elapsed={run['elapsed_seconds_observed']:.2f}s",
            flush=True,
        )
        runs.append(run)
    return {
        "schema_version": "bt-euclidean-os-witness-observations-v1",
        "evidence_type": "NUMERICAL_FINITE_VOLUME_OBSERVED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "arithmetic": "IEEE-754 binary64; Python random.Random deterministic seeds",
        "smoke": smoke,
        "question": (
            "What sign does the exact free OS witness have under the interacting "
            "positive BT measure at lambda=0.4 on 6^4?"
        ),
        "observable": {
            "reflection": "theta(t,x)=(1-t mod 6,x)",
            "positive_half": [1, 2, 3],
            "F": "-A_1+2*A_2-A_3 with A_t the spatial slice average",
            "theta_F": "-A_0+2*A_5-A_4",
            "measurement": "theta_F*F for every retained configuration",
            "exact_free_expectation": {"numerator": -1, "denominator": 1296},
        },
        "runs": runs,
        "does_not_establish": [
            "an exact sign at lambda=0.4",
            "ordinary reflection positivity or its failure for all observables",
            "a continuum or infinite-volume limit",
            "a Krein-compatible reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = experiment(smoke=args.smoke)
    if args.write:
        if args.smoke:
            raise SystemExit("refusing to write smoke observations")
        with open(DATA_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"wrote {DATA_REL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
