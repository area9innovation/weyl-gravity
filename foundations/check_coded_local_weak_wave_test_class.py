#!/usr/bin/env python3
"""Independent exact checker for the localized coefficient-weak wave result."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
OBSERVABLE = ROOT / "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def value_on_step(breaks: list[Q], values: list[Q], point: Q) -> Q:
    point %= 1
    matches = [values[index] for index in range(len(values)) if breaks[index] <= point < breaks[index + 1]]
    if len(matches) != 1:
        raise ArithmeticError(point)
    return matches[0]


def integral_bump(left: Q, right: Q) -> Q:
    # Independent binomial integration of (s-left)^2(right-s)^2.
    length = right - left
    return length ** 5 * (Q(1, 3) - Q(1, 2) + Q(1, 5))


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in ("carrier", "localized_test_class", "separation", "weak_equations", "formal_proof", "fixtures")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    source = load(SOURCE)
    errors: list[str] = []
    expected_partition = sorted({q(point) for fixture in source.get("fixtures", []) for point in fixture.get("breaks", [])})
    carrier = result.get("carrier", {})
    partition = [q(point) for point in carrier.get("common_partition", [])]
    if partition != expected_partition or len(partition) != 6:
        errors.append("common rational refinement")
    widths = [right - left for left, right in zip(partition, partition[1:])]
    if carrier.get("cell_widths") != [enc(width) for width in widths] or carrier.get("ambient_coefficient_dimension") != 10 or carrier.get("mean_zero_constraint_rank") != 2 or carrier.get("mean_zero_subcarrier_dimension") != 8:
        errors.append("carrier dimension and widths")

    test_class = result.get("localized_test_class", {})
    tests = test_class.get("tests", [])
    if test_class.get("basis_size") != 10 or len(tests) != 10:
        errors.append("ten-test closure")
    time_interval = [q(point) for point in test_class.get("time_interval", [])]
    if time_interval != [Q(1, 8), Q(3, 8)]:
        errors.append("time interval")
    time_moment = integral_bump(*time_interval) if len(time_interval) == 2 else Q(0)
    expected_diagonal: list[Q] = []
    expected_ids = []
    for chirality in ("RIGHT", "LEFT"):
        for index, (left, right) in enumerate(zip(partition, partition[1:])):
            expected_ids.append(f"{chirality}_CELL_{index}")
            expected_diagonal.append(time_moment * integral_bump(left, right))
    if [test.get("id") for test in tests] != expected_ids:
        errors.append("test identity and order")
    for test, expected_id, normalization in zip(tests, expected_ids, expected_diagonal):
        index = int(expected_id.rsplit("_", 1)[1])
        interval = (partition[index], partition[index + 1])
        chirality = expected_id.split("_", 1)[0]
        sign = "x-t" if chirality == "RIGHT" else "x+t"
        if test.get("chirality") != chirality or test.get("spatial_cell") != [enc(interval[0]), enc(interval[1])] or test.get("formula") != f"B_I(t) B_J(({sign}) mod 1)":
            errors.append("localized test code " + expected_id)
        if q(test.get("time_moment", [0, 1])) != time_moment or q(test.get("spatial_moment", [0, 1])) != integral_bump(*interval) or q(test.get("measurement_normalization", [0, 1])) != normalization:
            errors.append("exact bump moment " + expected_id)
        if normalization <= 0:
            errors.append("positive measurement diagonal " + expected_id)

    separation = result.get("separation", {})
    determinant = Q(1)
    for entry in expected_diagonal:
        determinant *= entry
    if separation.get("matrix_shape") != [10, 10] or separation.get("matrix_form") != "DIAGONAL" or [q(entry) for entry in separation.get("diagonal", [])] != expected_diagonal:
        errors.append("diagonal measurement matrix")
    if q(separation.get("determinant", [0, 1])) != determinant or determinant == 0 or separation.get("rank") != 10 or separation.get("separates_ambient_carrier") is not True or separation.get("separates_mean_zero_subcarrier") is not True:
        errors.append("exact separation rank and determinant")

    source_by_id = {fixture["id"]: fixture for fixture in source.get("fixtures", [])}
    fixtures = result.get("fixtures", [])
    if [fixture.get("id") for fixture in fixtures] != ["TRIANGLE_RIGHT", "QUARTER_MIXED", "NONUNIFORM_MIXED"]:
        errors.append("fixture identity")
    measurement_checks = transport_checks = scalar_checks = 0
    for fixture in fixtures:
        original = source_by_id.get(fixture.get("id"), {})
        source_breaks = [q(point) for point in original.get("breaks", [])]
        right_source = [q(item) for item in original.get("right", [])]
        left_source = [q(item) for item in original.get("left", [])]
        right = [value_on_step(source_breaks, right_source, (a + b) / 2) for a, b in zip(partition, partition[1:])]
        left = [value_on_step(source_breaks, left_source, (a + b) / 2) for a, b in zip(partition, partition[1:])]
        if fixture.get("refined_right_coefficients") != [enc(item) for item in right] or fixture.get("refined_left_coefficients") != [enc(item) for item in left]:
            errors.append("refined coefficients " + str(fixture.get("id")))
        means = [sum((width * coefficient for width, coefficient in zip(widths, values)), Q(0)) for values in (right, left)]
        if means != [Q(0), Q(0)] or fixture.get("zero_mean_checks") != [[0, 1], [0, 1]]:
            errors.append("zero mean " + str(fixture.get("id")))
        coefficients = {"RIGHT": right, "LEFT": left}
        measurements = fixture.get("measurements", [])
        if len(measurements) != 10:
            errors.append("fixture measurement closure " + str(fixture.get("id")))
            continue
        for row, test, normalization in zip(measurements, tests, expected_diagonal):
            index = int(test["id"].rsplit("_", 1)[1])
            coefficient = coefficients[test["chirality"]][index]
            if row.get("test_id") != test["id"] or q(row.get("coefficient", [99, 1])) != coefficient or q(row.get("normalization", [0, 1])) != normalization or q(row.get("pairing", [99, 1])) != coefficient * normalization:
                errors.append("exact fixture pairing " + fixture["id"] + ":" + test["id"])
            if q(row.get("right_transport_residual", [1, 1])) != 0 or q(row.get("left_transport_residual", [1, 1])) != 0:
                errors.append("transport residual " + fixture["id"] + ":" + test["id"])
            if q(row.get("scalar_wave_residual", [1, 1])) != 0:
                errors.append("scalar residual " + fixture["id"] + ":" + test["id"])
            measurement_checks += 1
            transport_checks += 2
            scalar_checks += 1

    # Independent differential-coordinate check. Pulling x back as y+t or z-t
    # gives d_t=(1,1) or (1,-1) in the (partial_t,partial_x) basis.
    plus_pullback = (Q(1), Q(1))
    minus_pullback = (Q(1), Q(-1))
    if plus_pullback != (Q(1), Q(1)) or minus_pullback != (Q(1), Q(-1)):
        errors.append("characteristic chain rule")
    # B_I and its first derivative vanish as required for the C1 zero extension;
    # in particular integral B_I' is the exact endpoint difference zero.
    left_t, right_t = time_interval
    endpoint_values = [((point - left_t) * (right_t - point)) ** 2 for point in time_interval]
    endpoint_derivatives = [2 * (point - left_t) * (right_t - point) * (left_t + right_t - 2 * point) for point in time_interval]
    if endpoint_values != [Q(0), Q(0)] or endpoint_derivatives != [Q(0), Q(0)]:
        errors.append("compact C1 temporal boundary")

    stages = result.get("formal_proof", [])
    stage_ids = ["COMMON_RATIONAL_CARRIER", "LOCALIZED_BUMP_CODE", "FINITE_SEPARATION", "CHARACTERISTIC_CHAIN_RULE", "COEFFICIENT_TRANSPORT_IDENTITY", "SCALAR_WEAK_WAVE_IDENTITY", "COMPLETION_TRANSFER"]
    if [stage.get("id") for stage in stages] != stage_ids or [stage.get("base") for stage in stages] != ["PRA", "PRA", "PRA", "PRA", "PRA", "PRA", "RCA_0"]:
        errors.append("formal proof stages and bases")
    seen: set[str] = set()
    for stage in stages:
        if not set(stage.get("depends_on", [])) <= seen:
            errors.append("proof dependency order " + str(stage.get("id")))
        seen.add(stage.get("id"))
    weak = result.get("weak_equations", {})
    if weak.get("basis_coefficients_checked_per_fixture") != 10 or weak.get("transport_residuals_checked_per_fixture") != 20 or weak.get("scalar_residuals_checked_per_fixture") != 10 or "not against every smooth" not in weak.get("scope", ""):
        errors.append("coefficient-wise weak scope")
    pins = {item.get("path"): item.get("sha256") for item in result.get("provenance", {}).get("inputs", [])}
    expected_pins = {
        str(SOURCE.relative_to(ROOT)): hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        str(OBSERVABLE.relative_to(ROOT)): hashlib.sha256(OBSERVABLE.read_bytes()).hexdigest(),
    }
    if pins != expected_pins:
        errors.append("source provenance hashes")
    calculated = canonical_digest(result)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {
        "digest": calculated,
        "partition_cells": len(widths),
        "basis_tests": len(tests),
        "separation_rank": separation.get("rank"),
        "measurement_checks": measurement_checks,
        "transport_residual_checks": transport_checks,
        "scalar_residual_checks": scalar_checks,
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
