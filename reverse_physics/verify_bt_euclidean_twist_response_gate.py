#!/usr/bin/env python3
"""Non-importing verifier for the BT uniform-twist response gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TWIST_RESPONSE_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-twist-response-gate-v1.schema.json",
)
OBSERVATION_REL = (
    "reverse_physics/data/bt_euclidean_twist_response_observations_v1.json"
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_EXPECTED_HESSIAN_AXIAL_SYMBOL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    OBSERVATION_REL,
]


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_fixture() -> tuple[list[Fraction], list[Fraction], Fraction]:
    length = 6
    dimensions = 2
    points = list(product(range(length), repeat=dimensions))
    profile = tuple(Fraction(value) for value in (1, 2, 1, Fraction(1, 2), 1, 1))
    omega = {point: profile[point[0]] for point in points}

    def move(point, axis, step):
        result = list(point)
        result[axis] = (result[axis] + step) % length
        return tuple(result)

    residual = {
        point: sum(
            (
                omega[move(point, axis, step)] / omega[point]
                for axis in range(dimensions) for step in (-1, 1)
            ),
            Fraction(),
        ) - 2 * dimensions
        for point in points
    }
    currents = []
    densities = []
    for axis in range(dimensions):
        current = curvature = Fraction()
        for point in points:
            plus = omega[move(point, axis, 1)] / omega[point]
            minus = omega[move(point, axis, -1)] / omega[point]
            current += residual[point] * (plus - minus)
            curvature += (
                (plus - minus) ** 2
                + residual[point] * (plus + minus)
            )
        currents.append(current)
        densities.append(curvature / len(points))
    return currents, densities, sum(densities, Fraction()) / dimensions


def reduce_run(run: dict, omitted: int | None = None) -> dict[str, float]:
    blocks = [
        block for number, block in enumerate(run["blocks"])
        if number != omitted
    ]
    axes = math.fsum(block["axis_count"] for block in blocks)
    samples = math.fsum(block["sample_count"] for block in blocks)
    alpha = math.fsum(
        block["sum_twist_curvature_density"] for block in blocks
    ) / axes
    current = math.fsum(
        block["sum_integrated_current"] for block in blocks
    ) / axes
    current2 = math.fsum(
        block["sum_integrated_current2"] for block in blocks
    ) / axes
    variance = current2 - current * current
    chi = variance / (
        run["lattice"]["volume"] * run["coupling"] ** 2
    )
    response = alpha - chi
    return {
        "action_density": math.fsum(
            block["sum_action_density"] for block in blocks
        ) / samples,
        "alpha": alpha,
        "mean_integrated_current": current,
        "integrated_current_variance": variance,
        "scaled_current_susceptibility": chi,
        "scaled_twist_response": response,
        "free_energy_curvature": response / run["coupling"] ** 2,
    }


def jackknife(run: dict, key: str) -> float:
    deleted = [
        reduce_run(run, omitted=number)[key]
        for number in range(len(run["blocks"]))
    ]
    center = math.fsum(deleted) / len(deleted)
    return math.sqrt(
        (len(deleted) - 1) / len(deleted)
        * math.fsum((value - center) ** 2 for value in deleted)
    )


def independent_observations() -> list[dict]:
    with open(os.path.join(ROOT, OBSERVATION_REL), encoding="utf-8") as handle:
        observations = json.load(handle)
    rows = []
    for run in observations["runs"]:
        reduced = reduce_run(run)
        rows.append({
            "length": run["lattice"]["length"],
            **reduced,
            "alpha_jackknife_error": jackknife(run, "alpha"),
            "susceptibility_jackknife_error": jackknife(
                run, "scaled_current_susceptibility"
            ),
            "response_jackknife_error": jackknife(
                run, "scaled_twist_response"
            ),
        })
    return rows


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False
    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes_current"] = (
        [item.get("path") for item in inputs] == EXPECTED_INPUTS
        and all(item.get("sha256") == file_hash(item["path"]) for item in inputs)
    )

    currents, densities, average = independent_fixture()
    public = cert.get("exact_fixture", {})
    checks["independent_exact_twist_fixture"] = (
        currents == [0, 0]
        and densities == [Fraction(7, 3), Fraction(2, 3)]
        and average == Fraction(3, 2)
        and [dec(value) for value in public.get("integrated_currents", [])]
        == currents
        and [dec(value) for value in public.get("axis_curvature_densities", [])]
        == densities
        and dec(public.get("axis_average_curvature", {})) == average
        and dec(public.get("expected_hessian_fixture_alpha", {})) == average
    )

    identity = cert.get("exact_uniform_twist_identity", {})
    checks["exact_response_identity_and_boundary"] = (
        identity.get("reflection_ward") == "E_mu[I_mu]=0"
        and "alpha_L-chi_L" in identity.get("response", "")
        and identity.get("susceptibility")
        == "chi_L=Var_mu(I_mu)/(N*lambda^2)>=0"
        and "D^(-1)*sum_mu D_mu/N equals alpha_L"
        in identity.get("axis_average_identity", "")
        and identity.get("orbit_relation")
        == "q*E[t_+]+R=U+V+(2D-2)*W from s=q+r=sum_neighbors t"
        and identity.get("alpha_before_relation")
        == "alpha=2q*E[t_+]+4R-4V-4(D-1)W"
        and identity.get("alpha_after_relation")
        == "alpha=2U-2V+2R=E[D_mu]/N"
        and tuple(
            left + right for left, right in zip(
                (2, 2, 12, -2), (0, -4, -12, 4)
            )
        ) == (2, -2, 0, 2)
        and "no lower sign" in identity.get("one_sided_consequence", "")
        and identity.get("status") == "PROVED_FINITE_VOLUME"
    )

    observed = independent_observations()
    public_rows = cert.get("finite_volume_diagnostic", {}).get("summaries", [])
    numeric_match = len(observed) == len(public_rows) == 2
    keys = (
        "action_density", "alpha", "mean_integrated_current",
        "integrated_current_variance", "scaled_current_susceptibility",
        "scaled_twist_response", "free_energy_curvature",
        "alpha_jackknife_error", "susceptibility_jackknife_error",
        "response_jackknife_error",
    )
    if numeric_match:
        for expected, recorded in zip(observed, public_rows):
            numeric_match &= expected["length"] == recorded.get("length")
            for key in keys:
                numeric_match &= abs(
                    expected[key] - recorded.get(key, math.inf)
                ) < 1.0e-14
    checks["observation_reduction_and_hash"] = (
        numeric_match
        and cert.get("finite_volume_diagnostic", {}).get("observation_sha256")
        == file_hash(OBSERVATION_REL)
        and all(row["scaled_twist_response"] > 0.09 for row in observed)
        and all(
            row["scaled_current_susceptibility"] / row["alpha"] < 1 / 400
            for row in observed
        )
    )

    obstruction = cert.get("witten_nontransfer_obstruction", {})
    checks["independent_nontransfer_fixture"] = (
        dec(obstruction.get("uniform_twist_rayleigh", {})) == 1
        and dec(obstruction.get("fixture_epsilon", {})) == Fraction(1, 100)
        and dec(obstruction.get("orthogonal_inverse_response", {})) == 100
        and obstruction.get("scope")
        == "logical non-transfer witness only; not a BT counterexample"
        and obstruction.get("status") == "OBSTRUCTION_TO_INFERENCE"
    )

    disposition = cert.get("method_disposition", {})
    checks["claim_boundary"] = (
        disposition.get("positive_L6_L8_complete_twist_response")
        == "OBSERVED_NOT_CERTIFIED"
        and disposition.get("positive_thermodynamic_twist_modulus") == "OPEN"
        and disposition.get("inhomogeneous_low_momentum_response_kernel") == "OPEN"
        and disposition.get("response_to_witten_coercivity_transfer") == "OPEN"
        and disposition.get("actual_interacting_h_minus_one_second_moment") == "OPEN"
        and any(
            "LORENTZIAN-CAUSAL" in item
            for item in cert.get("does_not_establish", [])
        )
    )
    published = cert.get("checks", {})
    checks["producer_checks_consistent"] = (
        published.get("ok") is True
        and published.get("passed") == published.get("total") == 20
        and published.get("failures") == []
        and all(published.get("details", {}).values())
    )
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    ok = all(checks.values())
    print(
        "BT twist response independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
