#!/usr/bin/env python3
"""Exhaustively replay the positive-jet full-BV dual against native columns."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from typing import Mapping

import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_full_bv_coderivation_redefinition as zero,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_order_two_full_bv_redefinition as core,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_positive_jet_full_bv_obstruction as result,
)


def _weights(value: Mapping[str, object]) -> tuple[dict, dict, list[dict]]:
    page0 = {}
    page1 = {}
    normalized = [dict() for _ in range(4)]
    for record in value["obstruction_witness"]["weights"]:
        coefficient = result._coefficient(str(record["coefficient"]))
        if int(record["page"]) == 0:
            page0[(int(record["output"]), tuple(int(row) for row in record["inputs"]))] = coefficient
            continue
        key = result._actual_first_key(record)
        page1[key] = coefficient
        normalized[int(record["axis"])][(int(record["output"]), tuple(
            (0,) if value in ((0,), (1,), (2,), (3,)) else value
            for value in key[1]
        ))] = coefficient
    return page0, page1, normalized


def _pair(functional: Mapping, vector: Mapping) -> sp.Expr:
    return sp.factor(sum((coefficient * vector.get(key, 0) for key, coefficient in functional.items()), sp.S(0)))


def _zero_segment(bounds: tuple[int, int]) -> tuple[int, list[tuple[int, str]]]:
    start, stop = bounds
    value = json.loads(result.OUTPUT.read_text())
    page0, page1, _ = _weights(value)
    labels = [("F2", output, inputs) for output, inputs in zero.LABELS2] + [
        ("F3", output, inputs) for output, inputs in zero.LABELS3
    ]
    q10, q20, _ = zero.retained_maps_zero()
    q11, q21 = core.homogeneous_lower_operations(1)
    defects = []
    for index in range(start, min(stop, len(labels))):
        kind, output, inputs = labels[index]
        lifted0 = zero.cotangent_column(output, inputs)
        column0 = zero.coboundary(
            q10,
            q20,
            lifted0 if kind == "F2" else {},
            lifted0 if kind == "F3" else {},
        )
        zero_pairing = _pair(page0, column0)

        lifted1 = core.lift.cotangent_column(output, tuple((field, ()) for field in inputs))
        f2, f3 = core.jet_taylor_vectors(
            lifted1 if kind == "F2" else {},
            lifted1 if kind == "F3" else {},
        )
        column1 = core.coderivation_coboundary_page_streaming(f2, f3, 1, q1=q11, q2=q21)
        pairing = sp.factor(zero_pairing + _pair(page1, column1))
        if pairing:
            defects.append((index, str(pairing)))
    return min(stop, len(labels)) - start, defects


def _first_segment(bounds: tuple[int, int]) -> tuple[int, list[list[tuple[int, str]]]]:
    start, stop = bounds
    value = json.loads(result.OUTPUT.read_text())
    _, _, functionals = _weights(value)
    labels = core.first_jet_labels(0)
    defects = [[] for _ in range(4)]
    for index in range(start, min(stop, len(labels))):
        column = core.first_jet_column(labels[index])
        for axis, functional in enumerate(functionals):
            pairing = _pair(functional, column)
            if pairing:
                defects[axis].append((index, str(pairing)))
    return min(stop, len(labels)) - start, defects


def _bounds(length: int, workers: int) -> list[tuple[int, int]]:
    size = (length + workers - 1) // workers
    return [(start, min(start + size, length)) for start in range(0, length, size)]


def verify(workers: int) -> dict[str, object]:
    value = json.loads(result.OUTPUT.read_text())
    result.validate(value)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        zero_results = list(pool.map(_zero_segment, _bounds(5984, workers)))
        first_results = list(pool.map(_first_segment, _bounds(14998, workers)))
    zero_defects = [defect for _, defects in zero_results for defect in defects]
    first_defects = [
        [defect for _, defects in first_results for defect in defects[axis]]
        for axis in range(4)
    ]
    replay = {
        "zero_label_columns_checked": sum(count for count, _ in zero_results),
        "first_label_columns_checked_per_axis": sum(count for count, _ in first_results),
        "zero_column_defects": len(zero_defects),
        "first_column_defects_per_axis": [len(defects) for defects in first_defects],
        "target_pairing": str(result.target_pairing(value)),
    }
    if replay != value["obstruction_witness"]["exhaustive_transpose_replay"]:
        raise ValueError(f"exhaustive transpose replay drifted: {replay}")
    print(f"{value['result_id']} exhaustive transpose verification: PASS")
    return replay


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    verify(args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
