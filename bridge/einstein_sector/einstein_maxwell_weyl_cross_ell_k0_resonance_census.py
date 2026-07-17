"""Exact bounded cross-ell k=0 Weyl--Maxwell resonance census."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_resonance_census.schema.json"
ELL_MAX = 96
BRANCHES = ("Einstein_minus", "extra", "Einstein_plus")


class CrossEllK0ResonanceCensusError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossEllK0ResonanceCensusError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _squarefree_split(value: int) -> tuple[int, int]:
    outside = 1
    inside = 1
    remainder = value
    prime = 2
    while prime * prime <= remainder:
        exponent = 0
        while remainder % prime == 0:
            remainder //= prime
            exponent += 1
        outside *= prime ** (exponent // 2)
        if exponent % 2:
            inside *= prime
        prime += 1
    if remainder > 1:
        inside *= remainder
    return outside, inside


Radical = dict[int, Fraction]


def _add(left: Radical, right: Radical) -> Radical:
    result = dict(left)
    for radicand, coefficient in right.items():
        result[radicand] = result.get(radicand, Fraction(0)) + coefficient
        if result[radicand] == 0:
            del result[radicand]
    return result


def _negate(value: Radical) -> Radical:
    return {radicand: -coefficient for radicand, coefficient in value.items()}


def _scale(value: Radical, coefficient: Fraction) -> Radical:
    return {
        radicand: coefficient * entry
        for radicand, entry in value.items()
        if coefficient * entry != 0
    }


def _multiply(left: Radical, right: Radical) -> Radical:
    result: Radical = {}
    for radicand_left, coefficient_left in left.items():
        for radicand_right, coefficient_right in right.items():
            common = math.gcd(radicand_left, radicand_right)
            radicand = radicand_left * radicand_right // common**2
            coefficient = coefficient_left * coefficient_right * common
            result[radicand] = result.get(radicand, Fraction(0)) + coefficient
            if result[radicand] == 0:
                del result[radicand]
    return result


def _shell_squared(ell: int, branch: str) -> Radical:
    lam = ell * (ell + 1)
    if branch == "extra":
        return {1: Fraction(lam) - Fraction(2, 3)}
    outside, inside = _squarefree_split(2 * lam)
    sign = -1 if branch == "Einstein_minus" else 1
    return _add({1: Fraction(lam)}, {inside: Fraction(sign * outside)})


def _evaluate(value: Radical) -> float:
    return sum(float(coefficient) * math.sqrt(radicand) for radicand, coefficient in value.items())


def _serialize(value: Radical) -> list[dict[str, str | int]]:
    return [
        {"radicand": radicand, "coefficient": str(coefficient)}
        for radicand, coefficient in sorted(value.items())
    ]


def _resonance_polynomial(first: Radical, second: Radical, target: Radical) -> Radical:
    """Return (target-first-second)^2-4*first*second exactly."""

    delta = _add(_add(target, _negate(first)), _negate(second))
    return _add(_multiply(delta, delta), _negate(_scale(_multiply(first, second), Fraction(4))))


def _candidate_outputs(ell_first: int, ell_second: int) -> dict[str, tuple[int, ...]]:
    total = ell_first + ell_second
    difference = ell_second - ell_first
    return {
        "sum": tuple(range(total - 2, total + 1)),
        "difference": tuple(range(difference, difference + 3)),
    }


def _exact_census() -> dict[str, Any]:
    shell_cache = {
        (ell, branch): _shell_squared(ell, branch)
        for ell in range(1, 2 * ELL_MAX + 1)
        for branch in BRANCHES
    }
    transcript = hashlib.sha256()
    squared_resonance_checks = 0
    frequency_collision_checks = 0
    exact_squared_candidates: list[dict[str, Any]] = []
    exact_frequency_collisions: list[dict[str, Any]] = []
    nearest: tuple[float, tuple[int, int, str, str, str, int, str], Radical] | None = None

    for ell_first in range(2, ELL_MAX + 1):
        for ell_second in range(ell_first + 1, ELL_MAX + 1):
            outputs = _candidate_outputs(ell_first, ell_second)
            for branch_first in BRANCHES:
                first = shell_cache[(ell_first, branch_first)]
                omega_first = math.sqrt(_evaluate(first))
                for branch_second in BRANCHES:
                    second = shell_cache[(ell_second, branch_second)]
                    omega_second = math.sqrt(_evaluate(second))
                    collision = _add(first, _negate(second))
                    frequency_collision_checks += 1
                    transcript.update(
                        f"C|{ell_first}|{ell_second}|{branch_first}|{branch_second}|{_serialize(collision)}\n".encode()
                    )
                    if not collision:
                        exact_frequency_collisions.append(
                            {
                                "ell_first": ell_first,
                                "ell_second": ell_second,
                                "branch_first": branch_first,
                                "branch_second": branch_second,
                            }
                        )

                    for temporal_channel, output_ells in outputs.items():
                        omega = (
                            omega_first + omega_second
                            if temporal_channel == "sum"
                            else abs(omega_second - omega_first)
                        )
                        for output_ell in output_ells:
                            for target_branch in BRANCHES:
                                target = shell_cache[(output_ell, target_branch)]
                                polynomial = _resonance_polynomial(first, second, target)
                                squared_resonance_checks += 1
                                label = (
                                    ell_first,
                                    ell_second,
                                    branch_first,
                                    branch_second,
                                    temporal_channel,
                                    output_ell,
                                    target_branch,
                                )
                                transcript.update(f"R|{label}|{_serialize(polynomial)}\n".encode())
                                if not polynomial:
                                    exact_squared_candidates.append(
                                        {
                                            "ell_first": ell_first,
                                            "ell_second": ell_second,
                                            "branch_first": branch_first,
                                            "branch_second": branch_second,
                                            "temporal_channel": temporal_channel,
                                            "output_ell": output_ell,
                                            "target_branch": target_branch,
                                        }
                                    )
                                numerical_defect = abs(omega - math.sqrt(max(0.0, _evaluate(target))))
                                if nearest is None or numerical_defect < nearest[0]:
                                    nearest = (numerical_defect, label, polynomial)

    _require(not exact_frequency_collisions, "a distinct-ell frequency collision entered the census")
    _require(not exact_squared_candidates, "an exact cross-ell output resonance entered the census")
    _require(squared_resonance_checks == 723330, "resonance census cardinality changed")
    _require(frequency_collision_checks == 40185, "collision census cardinality changed")
    assert nearest is not None
    expected_nearest = (5, 34, "extra", "Einstein_plus", "difference", 30, "Einstein_minus")
    _require(nearest[1] == expected_nearest, f"nearest channel changed: {nearest[1]}")
    _require(nearest[2], "nearest channel became exactly resonant")
    return {
        "ell_window": {"minimum": 2, "maximum": ELL_MAX, "distinct_inputs_only": True},
        "candidate_reduction": {
            "uniform_branch_bound": "ell-1/2 < omega_branch(ell) < ell+3/2 for ell>=2",
            "target_bound": "L-1 <= omega_target(L) < L+2 for L>=1",
            "sum_candidates": "L=ell_1+ell_2-2, ell_1+ell_2-1, ell_1+ell_2",
            "difference_candidates": "L=ell_2-ell_1, ell_2-ell_1+1, ell_2-ell_1+2",
            "angular_statement": "these are a superset of every triangle-allowed output across both input parity choices",
        },
        "exact_method": "canonical Q-linear expansion in square roots of distinct squarefree positive integers of (C-A-B)^2-4AB; those radicals are Q-linearly independent",
        "frequency_collision_checks": frequency_collision_checks,
        "exact_frequency_collisions": exact_frequency_collisions,
        "squared_resonance_checks": squared_resonance_checks,
        "exact_squared_resonance_candidates": exact_squared_candidates,
        "audit_sha256": transcript.hexdigest(),
        "nearest_nonresonant_channel": {
            "label_order": [
                "ell_first",
                "ell_second",
                "branch_first",
                "branch_second",
                "temporal_channel",
                "output_ell",
                "target_branch",
            ],
            "labels": list(nearest[1]),
            "numerical_frequency_defect": repr(nearest[0]),
            "exact_squared_resonance_polynomial": _serialize(nearest[2]),
            "exact_nonzero": True,
        },
    }


def build_certificate() -> dict[str, Any]:
    census = _exact_census()
    return {
        "schema": "einstein-maxwell-weyl-cross-ell-k0-resonance-census-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CROSS_ELL_K0_RESONANCE_CENSUS",
        "result_state": "EXACT_NO_RESONANCE_THROUGH_ELL_96",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_EXACT_FINITE_CROSS_ELL_WINDOW",
        "domain": "all distinct generic input ells 2<=ell_1<ell_2<=96 at k=0, all three primary branches on each input, both temporal sum/difference channels, and every angularly possible target branch in either parity",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "census": census,
        "classification": {
            "no_distinct_ell_frequency_collision_in_window": True,
            "no_cross_ell_nonzero_output_resonance_in_window": True,
            "all_input_and_target_primary_branches_covered": True,
            "both_input_parity_choices_covered_by_angular_superset": True,
            "unbounded_cross_ell_theorem_proved": False,
            "cross_ell_quadratic_source_solved": False,
        },
        "interpretation": "No cross-ell superposition with input ell at most 96 fails second-order inversion through a kinematic target-shell resonance. The closest channel is an exact nonzero near-miss. Any obstruction in this window must come from an adjoint-cokernel projection or an angular/source identity, not from the nonzero-frequency determinant.",
        "next_gate": "turn the six boundary-offset channel families into an unbounded Diophantine/nonresonance proof, then compute the mixed cross-ell zero/exceptional source projections on the common stabilizer-moment-map cone",
        "claim_boundary": "This is an exact finite-window resonance census, not an unbounded cross-ell theorem and not a second-order extension theorem. Cross-ell source coefficients, opposite momenta and their phases, exceptional/global inputs, all-orders integration, causal propagation, and quantum claims remain open.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {
                "status": "PASS",
                "elapsed_seconds": 0.06,
                "commands": [
                    "python3 -m py_compile <scoped Python paths>",
                    "python3 -m json.tool bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json",
                    "git diff --check -- <scoped paths>",
                ],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 51.0,
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_resonance_census --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_resonance_census.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_resonance_census",
                ],
                "scope": "full 763,515-case exact producer replay, separately implemented full exact verifier, and four fast certificate-contract tests",
            },
            "tier_2": {
                "status": "NOT_RUN",
                "reason": "the census introduces no shared operator or upstream mathematical input and promotes only a fail-closed G2 finite window",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "the unbounded cross-ell theorem and the mixed quadratic source remain explicitly open",
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_resonance_census --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_resonance_census.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_resonance_census",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "cross-ell census certificate is stale")


if __name__ == "__main__":
    main()
