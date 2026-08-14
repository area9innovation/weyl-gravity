#!/usr/bin/env python3
"""Independent exact checker for coded-wave observable reconstruction."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def step_value(breaks: list[Q], values: list[Q], point: Q) -> Q:
    point %= 1
    for index in range(len(values)):
        if breaks[index] <= point < breaks[index + 1]:
            return values[index]
    raise ArithmeticError(point)


def shifted_step(breaks: list[Q], values: list[Q], shift: Q) -> tuple[list[Q], list[Q]]:
    shifted = sorted({Q(0), Q(1), *((point + shift) % 1 for point in breaks[:-1])})
    values_out = [step_value(breaks, values, (left + right) / 2 - shift) for left, right in zip(shifted, shifted[1:])]
    return shifted, values_out


def linear_value(breaks: list[Q], values: list[Q], point: Q) -> Q:
    if point == 1:
        return values[-1]
    point %= 1
    for index in range(len(values) - 1):
        left, right = breaks[index], breaks[index + 1]
        if left <= point < right:
            return values[index] + (point - left) * (values[index + 1] - values[index]) / (right - left)
    raise ArithmeticError(point)


def pairing(test: tuple[list[Q], list[Q]], step: tuple[list[Q], list[Q]]) -> Q:
    partition = sorted(set(test[0] + step[0]))
    answer = Q(0)
    for left, right in zip(partition, partition[1:]):
        height = step_value(step[0], step[1], (left + right) / 2)
        answer += height * (right - left) * (linear_value(test[0], test[1], left) + linear_value(test[0], test[1], right)) / 2
    return answer


def observable(state: dict[str, Any], test: tuple[list[Q], list[Q]], time: Q) -> Q:
    breaks = [q(value) for value in state["breaks"]]
    right = [q(value) for value in state["right"]]
    left = [q(value) for value in state["left"]]
    return pairing(test, shifted_step(breaks, right, time)) + pairing(test, shifted_step(breaks, left, -time))


def norm_one(breaks: list[Q], values: list[Q]) -> Q:
    return sum(((right - left) * abs(value) for left, right, value in zip(breaks, breaks[1:], values)), Q(0))


def polygonal_lipschitz(breaks: list[Q], values: list[Q]) -> Q:
    return max(abs((values[index + 1] - values[index]) / (breaks[index + 1] - breaks[index])) for index in range(len(values) - 1))


def polygonal_square_integral(breaks: list[Q], values: list[Q]) -> Q:
    answer = Q(0)
    for left, right, left_value, right_value in zip(breaks, breaks[1:], values, values[1:]):
        answer += (right - left) * (left_value * left_value + left_value * right_value + right_value * right_value) / 3
    return answer


def ceiling_exponent(value: Q) -> int:
    exponent, bound = 0, Q(1)
    while bound < value:
        exponent, bound = exponent + 1, bound * 2
    return exponent


def exact_samples(state: dict[str, Any], test: tuple[list[Q], list[Q]], cutoff: int) -> list[Q]:
    denominator = 2 ** cutoff
    return [observable(state, test, Q(index, denominator)) for index in range(denominator + 1)]


def samples_hash(values: list[Q]) -> str:
    return hashlib.sha256(json.dumps([enc(value) for value in values], separators=(",", ":")).encode()).hexdigest()


def interpolate(values: list[Q], cutoff: int, time: Q) -> Q:
    phase = time % 1
    intervals = 2 ** cutoff
    scaled = phase * intervals
    index = scaled.numerator // scaled.denominator
    if index == intervals:
        return values[-1]
    weight = scaled - index
    return values[index] + weight * (values[index + 1] - values[index])


def canonical_digest(result: dict[str, Any]) -> str:
    projection = {key: result[key] for key in ("theorem", "declared_observable", "finite_approximant", "cutoff_theorem", "formal_proof", "fixtures")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    value = load(RESULT) if result is None else result
    source = load(SOURCE)
    errors: list[str] = []
    detector = value.get("declared_observable", {})
    test_breaks = [q(item) for item in detector.get("test_breaks", [])]
    test_values = [q(item) for item in detector.get("test_values", [])]
    if test_breaks != [Q(0), Q(1, 2), Q(1)] or test_values != [Q(0), Q(1), Q(0)] or test_values[0] != test_values[-1] or q(detector.get("test_l2_squared", [0, 1])) != polygonal_square_integral(test_breaks, test_values):
        errors.append("declared periodic tent detector")
        test = ([Q(0), Q(1)], [Q(0), Q(0)])
    else:
        test = (test_breaks, test_values)
    fixtures = value.get("fixtures", [])
    source_by_id = {item["id"]: item for item in source.get("fixtures", [])}
    if [item.get("id") for item in fixtures] != ["TRIANGLE_RIGHT", "QUARTER_MIXED", "NONUNIFORM_MIXED"]:
        errors.append("fixture closure")
    hash_checks = cutoff_checks = stress_checks = 0
    for fixture in fixtures:
        state = fixture.get("source_state", {})
        original = source_by_id.get(fixture.get("id"), {})
        if state != {key: original.get(key) for key in ("breaks", "right", "left")}:
            errors.append("source fixture identity " + str(fixture.get("id")))
            continue
        breaks = [q(item) for item in state["breaks"]]
        right = [q(item) for item in state["right"]]
        left = [q(item) for item in state["left"]]
        norms = [norm_one(breaks, right), norm_one(breaks, left)]
        lip_h = polygonal_lipschitz(*test)
        constant = lip_h * sum(norms, Q(0))
        exponent = ceiling_exponent(constant)
        if fixture.get("component_l1_norms") != [enc(item) for item in norms] or q(fixture.get("test_lipschitz_constant", [0, 1])) != lip_h or q(fixture.get("observable_lipschitz_constant", [0, 1])) != constant:
            errors.append("exact constants " + fixture["id"])
        if fixture.get("binary_ceiling_exponent") != exponent or fixture.get("cutoff_formula") != f"N(k)=k+{exponent + 1}":
            errors.append("cutoff formula " + fixture["id"])
        expected_anchors = [{"phase": enc(phase), "value": enc(observable(state, test, phase))} for phase in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4))]
        if fixture.get("anchor_values") != expected_anchors:
            errors.append("anchor values " + fixture["id"])
        rows = fixture.get("approximants", [])
        if [row.get("precision") for row in rows] != list(range(1, 7)):
            errors.append("precision closure " + fixture["id"])
            continue
        for row in rows:
            precision = row["precision"]
            cutoff = precision + exponent + 1
            values = exact_samples(state, test, cutoff)
            bound = constant / 2 ** cutoff
            if row.get("cutoff_index") != cutoff or row.get("grid_intervals") != 2 ** cutoff or row.get("sample_count") != len(values):
                errors.append("finite approximant dimensions " + fixture["id"] + ":" + str(precision))
            if q(row.get("uniform_error_bound", [99, 1])) != bound or q(row.get("requested_tolerance", [0, 1])) != Q(1, 2 ** precision) or not (bound <= Q(1, 2 ** (precision + 1)) < Q(1, 2 ** precision)):
                errors.append("uniform cutoff inequality " + fixture["id"] + ":" + str(precision))
            if row.get("sample_sha256") != samples_hash(values):
                errors.append("exact sample hash " + fixture["id"] + ":" + str(precision))
            hash_checks += 1
            cutoff_checks += 1
            if precision <= 3:
                fine_denominator = 2 ** (cutoff + 2)
                for index in range(fine_denominator):
                    time = Q(index, fine_denominator)
                    if abs(interpolate(values, cutoff, time) - observable(state, test, time)) > bound:
                        errors.append("fine-grid uniform stress " + fixture["id"] + ":" + str(precision))
                        break
                    stress_checks += 1
    stages = value.get("formal_proof", [])
    expected_ids = ["EXACT_RATIONAL_SAMPLES", "BOUNDED_LINEAR_OBSERVABLE", "OBSERVABLE_LIPSCHITZ_BOUND", "FINITE_DYADIC_INTERPOLANT", "UNIFORM_INTERPOLATION_BOUND", "EXPLICIT_CUTOFF", "UNIFORM_RECONSTRUCTION"]
    if [stage.get("id") for stage in stages] != expected_ids:
        errors.append("proof-stage closure")
    seen: set[str] = set()
    for stage in stages:
        if not set(stage.get("depends_on", [])) <= seen:
            errors.append("proof dependency order " + str(stage.get("id")))
        seen.add(stage.get("id"))
    if [stage.get("base") for stage in stages] != ["PRA", "RCA_0", "PRA", "PRA", "RCA_0", "PRA", "RCA_0"]:
        errors.append("named weak-base assignments")
    if canonical_digest(value) != value.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if value.get("provenance", {}).get("source_sha256") != source_hash or value.get("provenance", {}).get("source_result_id") != source.get("result_id"):
        errors.append("source provenance pin")
    return errors, {
        "digest": canonical_digest(value),
        "fixtures": len(fixtures),
        "exact_sample_hash_checks": hash_checks,
        "cutoff_checks": cutoff_checks,
        "fine_grid_stress_checks": stress_checks,
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
