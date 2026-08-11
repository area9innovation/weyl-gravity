#!/usr/bin/env python3
"""Dependency-minimal checker for the fixed energy-2 free-BV SDR witness.

This rail deliberately does not import the source BV implementation or a
linear-algebra package.  It expands four interval maps into sparse integer
matrices and checks the displayed identities by bounded dictionary arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json"
Sparse = dict[tuple[int, int], int]


def load_result(path: Path = RESULT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def identity(size: int) -> Sparse:
    return {(index, index): 1 for index in range(size)}


def normalize(matrix: Sparse) -> Sparse:
    return {key: value for key, value in matrix.items() if value != 0}


def add(*matrices: Sparse) -> Sparse:
    result: Sparse = {}
    for matrix in matrices:
        for key, value in matrix.items():
            result[key] = result.get(key, 0) + value
    return normalize(result)


def scale(matrix: Sparse, coefficient: int) -> Sparse:
    return normalize({key: coefficient * value for key, value in matrix.items()})


def compose(left: Sparse, right: Sparse) -> Sparse:
    """Return left*right using exact sparse integer arithmetic."""

    right_by_row: dict[int, list[tuple[int, int]]] = {}
    for (middle, column), value in right.items():
        right_by_row.setdefault(middle, []).append((column, value))
    result: Sparse = {}
    for (row, middle), left_value in left.items():
        for column, right_value in right_by_row.get(middle, []):
            key = (row, column)
            result[key] = result.get(key, 0) + left_value * right_value
    return normalize(result)


def matrix_digest(matrices: dict[str, Sparse]) -> str:
    canonical = {
        name: [[row, column, value] for (row, column), value in sorted(matrix.items())]
        for name, matrix in sorted(matrices.items())
    }
    payload = json.dumps(canonical, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def expand(data: dict[str, Any]) -> tuple[dict[str, Sparse], list[str]]:
    errors: list[str] = []
    module = data.get("module", {})
    full = module.get("full_dimension")
    reduced = module.get("reduced_dimension")
    if not isinstance(full, int) or not isinstance(reduced, int):
        return {}, ["module dimensions are not integers"]

    fields = module.get("field_slices", [])
    cursor = 0
    for field in fields:
        start, stop, dimension = field.get("start"), field.get("stop"), field.get("dimension")
        if start != cursor or not isinstance(stop, int) or stop < start:
            errors.append(f"field slice {field.get('name')} is not contiguous")
            break
        if dimension != stop - start:
            errors.append(f"field slice {field.get('name')} has wrong dimension")
        cursor = stop
    if cursor != full:
        errors.append("field slices do not exhaust the full module")

    q: Sparse = {}
    h: Sparse = {}
    occupied_sources: set[int] = set()
    occupied_targets: set[int] = set()
    for pair in module.get("contractible_pairs", []):
        source_start = pair.get("source_start")
        source_stop = pair.get("source_stop")
        target_start = pair.get("target_start")
        target_stop = pair.get("target_stop")
        if not all(isinstance(value, int) for value in (source_start, source_stop, target_start, target_stop)):
            errors.append(f"pair {pair.get('name')} has noninteger endpoint")
            continue
        if source_stop - source_start != target_stop - target_start:
            errors.append(f"pair {pair.get('name')} has unequal interval lengths")
            continue
        if pair.get("q_coefficient") != 1 or pair.get("h_coefficient") != 1:
            errors.append(f"pair {pair.get('name')} is not integral unit-normalized")
        for offset in range(source_stop - source_start):
            source = source_start + offset
            target = target_start + offset
            if not 0 <= source < full or not 0 <= target < full:
                errors.append(f"pair {pair.get('name')} has out-of-range coordinate")
                continue
            if source in occupied_sources or target in occupied_targets:
                errors.append(f"pair {pair.get('name')} overlaps a like-role interval")
            occupied_sources.add(source)
            occupied_targets.add(target)
            q[(target, source)] = 1
            h[(source, target)] = 1

    physical = module.get("physical_slice", {})
    full_start, full_stop = physical.get("full_start"), physical.get("full_stop")
    reduced_start, reduced_stop = physical.get("reduced_start"), physical.get("reduced_stop")
    if not all(isinstance(value, int) for value in (full_start, full_stop, reduced_start, reduced_stop)):
        errors.append("physical slice has noninteger endpoint")
        return {}, errors
    if full_stop - full_start != reduced or reduced_start != 0 or reduced_stop != reduced:
        errors.append("physical and reduced intervals disagree")
    physical_coordinates = set(range(full_start, full_stop))
    partition = occupied_sources | occupied_targets | physical_coordinates
    if occupied_sources & occupied_targets:
        errors.append("source and target intervals overlap")
    if occupied_sources & physical_coordinates or occupied_targets & physical_coordinates:
        errors.append("contractible and physical intervals overlap")
    if partition != set(range(full)):
        errors.append("source-target-physical intervals do not partition the full basis")

    j = {(full_start + offset, offset): 1 for offset in range(reduced)}
    p = {(offset, full_start + offset): 1 for offset in range(reduced)}
    return {"q": q, "h": h, "j": j, "p": p}, errors


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    if data is None:
        data = load_result()
    matrices, errors = expand(data)
    if errors:
        return errors, {}

    q, h, j, p = (matrices[name] for name in ("q", "h", "j", "p"))
    module = data["module"]
    full = module["full_dimension"]
    reduced = module["reduced_dimension"]
    zero: Sparse = {}
    claims = {
        "q_squared_zero": compose(q, q) == zero,
        "h_squared_zero": compose(h, h) == zero,
        "p_j_identity": compose(p, j) == identity(reduced),
        "j_p_contraction": compose(j, p)
        == add(identity(full), scale(compose(q, h), -1), scale(compose(h, q), -1)),
        "q_j_zero": compose(q, j) == zero,
        "p_q_zero": compose(p, q) == zero,
        "h_j_zero": compose(h, j) == zero,
        "p_h_zero": compose(p, h) == zero,
    }
    for name, passed in claims.items():
        if not passed:
            errors.append(f"identity failed: {name}")

    counts = module.get("partition_counts", {})
    actual_counts = {
        "contractible_sources": len(h),
        "contractible_targets": len(q),
        "physical": len(j),
        "total": full,
    }
    if counts != actual_counts:
        errors.append("declared partition counts disagree with expanded matrices")

    summary = {
        "passed": len(errors) == 0,
        "identity_checks": claims,
        "expanded_nonzero_entries": {name: len(matrix) for name, matrix in matrices.items()},
        "matrix_digest": matrix_digest(matrices),
        "cohomology_rank_from_explicit_sdr": reduced,
        "arithmetic": "exact integers only",
    }
    return errors, summary


def main() -> int:
    errors, summary = check()
    if errors:
        print("FOUNDATIONAL_FREE_BV_ENERGY2_PRIMITIVE_CHECKER: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("FOUNDATIONAL_FREE_BV_ENERGY2_PRIMITIVE_CHECKER: PASS")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
