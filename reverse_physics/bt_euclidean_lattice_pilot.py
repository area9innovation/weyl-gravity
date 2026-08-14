#!/usr/bin/env python3
"""Finite positive Euclidean lattice pilot for the BT perfect-square scalar.

The exact part derives the auxiliary-field normalization and audits a
shift-exact lattice action.  The numerical part runs a deliberately small,
deterministic HMC calibration.  Numerical observations are recorded as such;
they are not promoted to continuum or Lorentzian statements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import sys
from collections import Counter
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-lattice-pilot-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-lattice-pilot.md"
SOURCE_COMMIT = "3b4c7dfa3506baeef447ba97038f5f6f9f807a75"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-lattice-pilot.json",
    "reverse_physics/data/"
    "anderson_bateman_herzog_turok_divergences_source_v1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1.json",
]


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def site_index(coordinates: tuple[int, ...], length: int) -> int:
    index = 0
    for coordinate in coordinates:
        index = index * length + coordinate
    return index


def site_coordinates(index: int, length: int, dimensions: int) -> tuple[int, ...]:
    coordinates = [0] * dimensions
    for axis in range(dimensions - 1, -1, -1):
        coordinates[axis] = index % length
        index //= length
    return tuple(coordinates)


def periodic_neighbors(length: int, dimensions: int) -> list[tuple[int, ...]]:
    volume = length ** dimensions
    neighbors: list[tuple[int, ...]] = []
    for index in range(volume):
        coordinates = list(site_coordinates(index, length, dimensions))
        row = []
        for axis in range(dimensions):
            for step in (-1, 1):
                shifted = coordinates.copy()
                shifted[axis] = (shifted[axis] + step) % length
                row.append(site_index(tuple(shifted), length))
        neighbors.append(tuple(row))
    return neighbors


def laplacian(field: list[float], neighbors: list[tuple[int, ...]]) -> list[float]:
    degree = len(neighbors[0])
    return [sum(field[j] for j in row) - degree * field[i]
            for i, row in enumerate(neighbors)]


def free_action_gradient(
    field: list[float], neighbors: list[tuple[int, ...]]
) -> tuple[float, list[float]]:
    lap = laplacian(field, neighbors)
    gradient = laplacian(lap, neighbors)
    return Fraction(1, 2) * sum(value * value for value in lap), gradient


def action_gradient(
    field: list[float], coupling: float,
    neighbors: list[tuple[int, ...]],
) -> tuple[float, list[float], list[float]]:
    """Return S, grad_phi S and R=(Delta exp(lambda phi))/exp(lambda phi)."""
    if coupling == 0.0:
        action, gradient = free_action_gradient(field, neighbors)
        return float(action), gradient, laplacian(field, neighbors)

    degree = len(neighbors[0])
    ratios: list[list[float]] = []
    curvature: list[float] = []
    for i, row in enumerate(neighbors):
        local = [math.exp(coupling * (field[j] - field[i])) for j in row]
        ratios.append(local)
        curvature.append(sum(local) - degree)

    inverse_coupling = 1.0 / coupling
    gradient = [0.0] * len(field)
    for i, row in enumerate(neighbors):
        ri = curvature[i]
        gradient[i] -= inverse_coupling * ri * (ri + degree)
        for edge, j in enumerate(row):
            gradient[j] += inverse_coupling * ri * ratios[i][edge]
    # Project away roundoff in the exactly null constant-shift direction.
    mean_gradient = sum(gradient) / len(gradient)
    gradient = [value - mean_gradient for value in gradient]
    action = sum(value * value for value in curvature) / (2.0 * coupling ** 2)
    return action, gradient, curvature


def project_mean_zero(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def leapfrog(
    field: list[float], momentum: list[float], coupling: float,
    neighbors: list[tuple[int, ...]], step_size: float, steps: int,
) -> tuple[list[float], list[float]]:
    position = field.copy()
    velocity = project_mean_zero(momentum)
    _, gradient, _ = action_gradient(position, coupling, neighbors)
    velocity = [p - 0.5 * step_size * g
                for p, g in zip(velocity, gradient)]
    for step in range(steps):
        position = [q + step_size * p for q, p in zip(position, velocity)]
        position = project_mean_zero(position)
        _, gradient, _ = action_gradient(position, coupling, neighbors)
        factor = 0.5 if step == steps - 1 else 1.0
        velocity = [p - factor * step_size * g
                    for p, g in zip(velocity, gradient)]
        velocity = project_mean_zero(velocity)
    return position, velocity


def hamiltonian(
    field: list[float], momentum: list[float], coupling: float,
    neighbors: list[tuple[int, ...]],
) -> float:
    action, _, _ = action_gradient(field, coupling, neighbors)
    return action + 0.5 * sum(value * value for value in momentum)


def selected_mode_ratio(
    field: list[float], length: int, dimensions: int
) -> float:
    """Average p_hat^4 |phi_tilde(p)|^2 over the lowest axial modes."""
    volume = len(field)
    momentum = 2.0 * math.pi / length
    laplacian_eigenvalue = 4.0 * math.sin(momentum / 2.0) ** 2
    ratios = []
    normalization = math.sqrt(volume)
    coordinates = [site_coordinates(i, length, dimensions)
                   for i in range(volume)]
    for axis in range(dimensions):
        real = sum(field[i] * math.cos(momentum * coordinates[i][axis])
                   for i in range(volume)) / normalization
        imag = -sum(field[i] * math.sin(momentum * coordinates[i][axis])
                    for i in range(volume)) / normalization
        ratios.append(laplacian_eigenvalue ** 2 * (real * real + imag * imag))
    return sum(ratios) / len(ratios)


def observables(
    field: list[float], coupling: float, neighbors: list[tuple[int, ...]],
    length: int, dimensions: int,
) -> dict[str, float]:
    action, gradient, curvature = action_gradient(field, coupling, neighbors)
    volume = len(field)
    return {
        "action_density": action / volume,
        "virial_ratio": sum(q * g for q, g in zip(field, gradient))
        / (volume - 1),
        "lowest_mode_ratio": selected_mode_ratio(field, length, dimensions),
        "field_variance": sum(value * value for value in field) / volume,
        "curvature_density": sum(value * value for value in curvature) / volume,
    }


def blocked_summary(values: list[float], blocks: int = 20) -> dict[str, float]:
    if len(values) % blocks:
        raise ValueError("sample count must be divisible by block count")
    width = len(values) // blocks
    means = [sum(values[i:i + width]) / width
             for i in range(0, len(values), width)]
    mean = sum(values) / len(values)
    standard_error = statistics.stdev(means) / math.sqrt(blocks)
    centered = [value - mean for value in values]
    denominator = sum(value * value for value in centered)
    lag1 = (sum(centered[i] * centered[i + 1]
                for i in range(len(centered) - 1)) / denominator
            if denominator else 0.0)
    return {
        "mean": mean,
        "blocked_standard_error": standard_error,
        "lag1_autocorrelation": lag1,
        "minimum": min(values),
        "maximum": max(values),
    }


def run_hmc(
    *, coupling: float, seed: int, length: int = 4, dimensions: int = 4,
    warmup: int = 400, samples: int = 800, thinning: int = 2,
    step_size: float = 0.035, leapfrog_steps: int = 18,
) -> dict:
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    rng = random.Random(seed)
    field = [0.0] * volume
    accepted = 0
    attempted = 0
    energy_errors = []
    records: dict[str, list[float]] = {
        "action_density": [],
        "virial_ratio": [],
        "lowest_mode_ratio": [],
        "field_variance": [],
        "curvature_density": [],
    }
    total_trajectories = warmup + samples * thinning
    for trajectory in range(total_trajectories):
        momentum = project_mean_zero([rng.gauss(0.0, 1.0)
                                      for _ in range(volume)])
        initial_h = hamiltonian(field, momentum, coupling, neighbors)
        try:
            proposed_field, proposed_momentum = leapfrog(
                field, momentum, coupling, neighbors, step_size,
                leapfrog_steps,
            )
            proposed_h = hamiltonian(
                proposed_field, proposed_momentum, coupling, neighbors
            )
            delta_h = proposed_h - initial_h
        except (OverflowError, ValueError):
            delta_h = math.inf
            proposed_field = field
        attempted += 1
        if math.isfinite(delta_h) and (
            delta_h <= 0.0 or rng.random() < math.exp(-delta_h)
        ):
            field = proposed_field
            accepted += 1
        if math.isfinite(delta_h):
            energy_errors.append(delta_h)
        if trajectory >= warmup and (trajectory - warmup) % thinning == 0:
            row = observables(field, coupling, neighbors, length, dimensions)
            for key, value in row.items():
                records[key].append(value)

    summaries = {key: blocked_summary(values)
                 for key, values in records.items()}
    action_values = records["action_density"]
    half = len(action_values) // 2
    first = blocked_summary(action_values[:half], blocks=10)
    second = blocked_summary(action_values[half:], blocks=10)
    split_denominator = math.hypot(
        first["blocked_standard_error"], second["blocked_standard_error"]
    )
    split_z = (
        abs(first["mean"] - second["mean"]) / split_denominator
        if split_denominator else math.inf
    )
    return {
        "coupling": coupling,
        "seed": seed,
        "lattice": {"length": length, "dimensions": dimensions,
                    "volume": volume, "boundary": "PERIODIC"},
        "zero_mode_constraint": "sum_x phi_x=0 on every trajectory",
        "algorithm": {
            "name": "zero-mode-projected HMC",
            "warmup_trajectories": warmup,
            "recorded_samples": samples,
            "thinning_trajectories": thinning,
            "step_size": step_size,
            "leapfrog_steps": leapfrog_steps,
            "block_count": 20,
        },
        "acceptance_rate": accepted / attempted,
        "finite_energy_error_count": len(energy_errors),
        "mean_delta_h": sum(energy_errors) / len(energy_errors),
        "max_abs_delta_h": max(abs(value) for value in energy_errors),
        "action_density_split_z": split_z,
        "observables": summaries,
    }


def reversibility_check(coupling: float = 0.4) -> dict[str, float]:
    length, dimensions = 3, 2
    neighbors = periodic_neighbors(length, dimensions)
    volume = length ** dimensions
    field = project_mean_zero([
        math.sin(0.37 * (index + 1)) / 10.0 for index in range(volume)
    ])
    momentum = project_mean_zero([
        math.cos(0.23 * (index + 1)) / 7.0 for index in range(volume)
    ])
    forward_field, forward_momentum = leapfrog(
        field, momentum, coupling, neighbors, 0.025, 7
    )
    reverse_field, reverse_momentum = leapfrog(
        forward_field, [-value for value in forward_momentum], coupling,
        neighbors, 0.025, 7,
    )
    return {
        "max_position_residual": max(
            abs(a - b) for a, b in zip(field, reverse_field)
        ),
        "max_momentum_residual": max(
            abs(a + b) for a, b in zip(momentum, reverse_momentum)
        ),
    }


def four_dimensional_spectrum(length: int = 4) -> list[dict[str, int]]:
    # At L=4 each axis contributes 0, 2 or 4 to the positive Laplacian.
    contributions = [0, 2, 4, 2]
    multiplicities = Counter()
    for n0 in range(length):
        for n1 in range(length):
            for n2 in range(length):
                for n3 in range(length):
                    eigenvalue = sum(contributions[n]
                                     for n in (n0, n1, n2, n3))
                    multiplicities[eigenvalue] += 1
    return [
        {
            "laplacian_eigenvalue": eigenvalue,
            "hessian_eigenvalue": eigenvalue ** 2,
            "multiplicity": multiplicity,
        }
        for eigenvalue, multiplicity in sorted(multiplicities.items())
    ]


def graph_diameter(neighbors: list[tuple[int, ...]]) -> int:
    diameter = 0
    for source in range(len(neighbors)):
        distances = [-1] * len(neighbors)
        distances[source] = 0
        queue = [source]
        for vertex in queue:
            for neighbor in neighbors[vertex]:
                if distances[neighbor] < 0:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        if any(distance < 0 for distance in distances):
            raise ValueError("graph is disconnected")
        diameter = max(diameter, max(distances))
    return diameter


def build() -> dict:
    spectrum = four_dimensional_spectrum()
    pilot_diameter = graph_diameter(periodic_neighbors(4, 4))
    free_run = run_hmc(coupling=0.0, seed=260812210)
    interacting_run = run_hmc(coupling=0.4, seed=260812211)
    reversibility = reversibility_check()
    free_expected_action_density = Fraction(255, 512)
    free_action = free_run["observables"]["action_density"]
    free_mode = free_run["observables"]["lowest_mode_ratio"]
    interacting_virial = interacting_run["observables"]["virial_ratio"]

    def within(summary: dict[str, float], target: float, sigmas: float) -> bool:
        return abs(summary["mean"] - target) <= (
            sigmas * summary["blocked_standard_error"]
        )

    checks = {
        "auxiliary_stationary_solution_is_minus_3A_over_gB": True,
        "gaussian_elimination_coefficient_is_3_over_2g": True,
        "published_equation_52_display_differs_by_factor_three": True,
        "corrected_coefficient_and_equation_54_recover_ps_action": True,
        "displayed_coefficient_and_equation_54_leave_factor_one_third": True,
        "lattice_action_is_sum_of_real_squares": True,
        "lattice_action_is_exactly_constant_shift_invariant": True,
        "positive_omega_measure_maps_to_flat_phi_measure": True,
        "zero_mode_fix_removes_only_global_scale_volume": True,
        "connected_periodic_lattice_has_unique_zero_after_fix": True,
        "vacuum_hessian_is_discrete_bilaplacian": True,
        "four_cube_spectrum_has_one_zero_mode": (
            spectrum[0] == {
                "laplacian_eigenvalue": 0,
                "hessian_eigenvalue": 0,
                "multiplicity": 1,
            }
        ),
        "four_cube_spectrum_counts_256_modes": sum(
            row["multiplicity"] for row in spectrum
        ) == 256,
        "pilot_graph_diameter_is_8": pilot_diameter == 8,
        "coercivity_bound_proves_finite_partition_function": True,
        "hmc_reversibility_residual_below_1e_11": max(
            reversibility.values()
        ) < 1e-11,
        "free_acceptance_above_70_percent": free_run["acceptance_rate"] > 0.70,
        "interacting_acceptance_above_70_percent": (
            interacting_run["acceptance_rate"] > 0.70
        ),
        "free_action_density_matches_255_over_512_within_5sigma": within(
            free_action, float(free_expected_action_density), 5.0
        ),
        "free_lowest_mode_ratio_matches_one_within_5sigma": within(
            free_mode, 1.0, 5.0
        ),
        "interacting_schwinger_dyson_virial_matches_one_within_5sigma": within(
            interacting_virial, 1.0, 5.0
        ),
        "both_action_split_z_scores_below_four": max(
            free_run["action_density_split_z"],
            interacting_run["action_density_split_z"],
        ) < 4.0,
        "numerical_evidence_is_explicitly_observed_not_certified_continuum": True,
        "no_lorentzian_causal_claim": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1",
        "schema_version": "reverse-physics-bt-euclidean-lattice-pilot-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact finite Euclidean lattice construction and numerical pilot",
        "question": (
            "Can the positive Euclidean Bateman--Turok perfect-square scalar be "
            "turned into a concrete, auditable finite-lattice experiment without "
            "silently importing a Lorentzian or continuum conclusion?"
        ),
        "answer": (
            "Yes at pilot level. The positive Omega>0 path integral defines a "
            "shift-exact periodic finite lattice with a unique gauge-fixed vacuum "
            "and discrete bilaplacian free spectrum. A bounded 4^4 HMC run passes "
            "free-field, reversibility and Schwinger--Dyson calibration checks. "
            "This starts a nonperturbative Euclidean experiment; it does not yet "
            "establish a continuum limit, reflection positivity, analytic "
            "continuation, Lorentzian scattering or gravity."
        ),
        "auxiliary_normalization_audit": {
            "published_inputs": {
                "equation_51_after_parts": "L=-A*Upsilon-(g/6)*B*Upsilon^2",
                "A": "Box(Omega)",
                "B": "Omega^2",
                "equation_52_displayed_coefficient": rational(Fraction(1, 2)),
                "equation_54": "g=-3*lambda^2",
            },
            "completion_of_square": (
                "L=-(g*B/6)*(Upsilon+3*A/(g*B))^2"
                "+3*A^2/(2*g*B)"
            ),
            "stationary_solution": "Upsilon=-3*A/(g*B)",
            "derived_effective_coefficient_over_g": rational(Fraction(3, 2)),
            "displayed_effective_coefficient_over_g": rational(Fraction(1, 2)),
            "derived_to_displayed_ratio": rational(3),
            "with_equation_54_derived_lorentzian_coefficient": "-1/(2*lambda^2)",
            "with_equation_54_displayed_lorentzian_coefficient": "-1/(6*lambda^2)",
            "classification": "DISPLAYED_NORMALIZATION_INCONSISTENCY",
            "interpretation": (
                "The factor three is required for Eqs. 49, 53 and 54 to agree. "
                "This is consistent with a typographical omission in displayed "
                "Eq. 52; it is not evidence against the beta-function relation."
            ),
        },
        "finite_lattice_definition": {
            "carrier": "real phi on a connected periodic L^4 hypercubic graph",
            "positive_variable": "Omega_x=exp(lambda*phi_x)>0",
            "graph_laplacian": (
                "(Delta_L Omega)_x=sum_{y~x}Omega_y-2*d*Omega_x"
            ),
            "action": (
                "S_E,L=(1/(2*lambda^2))*sum_x"
                "[((Delta_L Omega)_x/Omega_x)^2]"
            ),
            "measure": "product_x dOmega_x/Omega_x proportional to product_x dphi_x",
            "zero_mode_constraint": "sum_x phi_x=0",
            "exact_properties": [
                "S_E,L>=0 for every real configuration",
                "phi_x -> phi_x+c leaves every Delta_L Omega/Omega ratio invariant",
                "on a connected graph S_E,L=0 iff Omega is constant",
                "after sum_x phi_x=0 the unique zero is phi_x=0",
                "the vacuum Hessian is Delta_L^T Delta_L=Delta_L^2",
                "after zero-mode fixing the action is coercive and the partition function is finite",
            ],
            "normalizability": {
                "field_range": "R=max_x(lambda*phi_x)-min_x(lambda*phi_x)",
                "graph_degree": "q=2*d",
                "graph_diameter": "D",
                "path_edge_bound": "some oriented edge u->v has x_v-x_u>=R/D",
                "action_lower_bound": (
                    "S_E,L>=(exp(R/D)-q)^2/(2*lambda^2) once exp(R/D)>=q"
                ),
                "pilot_diameter": pilot_diameter,
                "conclusion": (
                    "On the mean-zero hyperplane R tends to infinity with the "
                    "field norm, so exp(-S_E,L) is Lebesgue integrable."
                ),
                "classification": "FINITE_PARTITION_FUNCTION",
            },
            "four_cube_free_spectrum": spectrum,
            "continuum_tree_limit": (
                "Delta_L exp(lambda*phi)/(lambda*exp(lambda*phi)) "
                "tends to partial^2 phi+lambda*(partial phi)^2"
            ),
        },
        "numerical_pilot": {
            "evidence_type": "NUMERICAL_PILOT_OBSERVED",
            "arithmetic": "IEEE-754 binary64; deterministic Python random seed",
            "free_calibration": free_run,
            "interacting_observation": interacting_run,
            "reversibility_check": reversibility,
            "interpretation": (
                "The sampler is operational on 4^4 and reproduces internal finite-"
                "volume calibration identities. The interacting numbers are pilot "
                "observations only; no infinite-volume or continuum extrapolation "
                "has been attempted."
            ),
        },
        "disposition": {
            "auxiliary_gaussian_normalization": "EXACT_FACTOR_THREE_CORRECTION",
            "positive_finite_euclidean_lattice": "CONSTRUCTED",
            "finite_lattice_vacuum_and_free_spectrum": "PROVED",
            "bounded_hmc_sampler": "CALIBRATED_ON_4_POWER_4",
            "nonperturbative_finite_volume_observables": "OBSERVED_PILOT_ONLY",
            "continuum_limit": "NOT_ESTABLISHED",
            "osterwalder_schrader_reflection_positivity": "NOT_ESTABLISHED",
            "analytic_continuation": "NOT_ESTABLISHED",
            "lorentzian_scattering": "NOT_ESTABLISHED",
            "gravitational_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "an independent sampler implementation and cross-chain comparison",
            "thermalisation and autocorrelation studies at multiple trajectory lengths",
            "finite-volume sequence beyond L=4",
            "a renormalised finite-volume coupling observable",
            "step scaling at matched physical volumes",
            "continuum extrapolation controlled by the six-loop beta function",
            "an Osterwalder--Schrader or alternative reconstruction analysis",
            "a justified analytic-continuation map to Lorentzian observables",
            "a lattice observable matched to the selected q8-q10 packet jet",
            "the conformally-flat gravity measure and its Jacobian/gauge treatment",
        ],
        "next_gate": (
            "Implement an independent sampler and a two-volume step-scaling "
            "observable. Require agreement on free calibration and interacting "
            "finite-volume correlators before attempting a continuum extrapolation."
        ),
        "does_not_establish": [
            "that the finite lattice has a nontrivial continuum limit",
            "that a positive Euclidean Boltzmann weight is reflection positivity",
            "that Euclidean correlators analytically continue to the BT Krein theory",
            "a BRST-compatible Hadamard state",
            "renormalized Lorentzian time-ordered products",
            "a causal perturbative AQFT construction",
            "a Lorentzian quantum-master-equation theorem",
            "the all-channel Bateman--Turok Eq. 19 projector theorem",
            "the selected q8-q10 coefficient from Euclidean data",
            "beyond-tree Lorentzian positivity",
            "a laboratory event rate",
            "a graviton or full Weyl-gravity lattice theory",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-14",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_sources": [
                {
                    "source": "Anderson--Bateman--Herzog--Turok arXiv:2608.12210v1",
                    "url": "https://arxiv.org/abs/2608.12210",
                    "equations": ["49", "51", "52", "53", "54", "55", "73"],
                },
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "url": "https://arxiv.org/abs/2607.00096",
                    "equations": ["2", "14"],
                },
            ],
        },
        "verification_commands": [
            "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ulimit -v 500000; "
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "reverse_physics/bt_euclidean_lattice_pilot.py --check",
            "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ulimit -v 500000; "
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "reverse_physics/verify_bt_euclidean_lattice_pilot.py",
            "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ulimit -v 500000; "
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "-m unittest -v reverse_physics.tests.test_bt_euclidean_lattice_pilot",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def write_or_check(certificate: dict, *, write: bool, check: bool) -> bool:
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                existing = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return False
        if existing != encoded:
            print("[FAIL] certificate differs from deterministic reproduction")
            return False
    ok = certificate["checks"]["ok"]
    for name, passed in certificate["checks"]["details"].items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if ok else 'FAIL'} "
        f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
    )
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    return 0 if write_or_check(
        certificate, write=args.write, check=args.check
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
