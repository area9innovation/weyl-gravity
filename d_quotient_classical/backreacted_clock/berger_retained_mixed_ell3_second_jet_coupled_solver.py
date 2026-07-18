#!/usr/bin/env python3
"""Sparse coupled solver for the retained mixed-ell3 order-two page.

This is a basis-selection consumer, not a scientific certificate.  It builds
the complete affine correction system around the frozen order-one primitive:

    A dx = 0,
    B_a dx + C dy_a = 0,
    D dx + sum_a E_a dy_a + Z z = r_2.

The floating-point pass is used only to measure compatibility and select a
candidate exact support.  No result from this module is promotable until the
selected support is replayed over QQ(sqrt(10)).
"""

from __future__ import annotations

import argparse
from array import array
import json
import pickle
from pathlib import Path
import time

import numpy as np
import sympy as sp
from scipy.sparse import coo_matrix, csr_matrix, diags, load_npz, save_npz
from scipy.sparse.linalg import lsmr

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)


ZERO_COLUMNS = 2690
FIRST_COLUMNS_PER_AXIS = 6560
FIRST_COLUMNS = 4 * FIRST_COLUMNS_PER_AXIS
SECOND_COLUMNS = 155640
TOTAL_COLUMNS = ZERO_COLUMNS + FIRST_COLUMNS + SECOND_COLUMNS
LOWER_ROWS = 550 + 4 * 1330
DEFAULT_CACHE = Path("/tmp/berger_retained_mixed_ell3_second_jet_coupled")


def _float(value: object) -> float:
    return float(second.sp.N(value, 17))


def _first_label(axis: int, label: tuple[str, int, tuple[int, ...], int]) -> second.FLabel:
    arity, output, inputs, derivative_field = label
    atoms = []
    used = False
    for field in inputs:
        differentiated = field == derivative_field and not used
        atoms.append((field, (axis,) if differentiated else ()))
        used = used or differentiated
    return arity, output, tuple(sorted(atoms))


def build_numeric_system(
    *,
    progress: bool = True,
    cache_prefix: Path | None = DEFAULT_CACHE,
) -> dict[str, object]:
    started = time.time()
    if cache_prefix is not None:
        matrix_path = cache_prefix.with_suffix(".npz")
        rhs_path = cache_prefix.with_suffix(".rhs.npy")
        rows_path = cache_prefix.with_suffix(".rows.pkl")
        if matrix_path.exists() and rhs_path.exists() and rows_path.exists():
            with rows_path.open("rb") as handle:
                order_rows = pickle.load(handle)
            return {
                "matrix": load_npz(matrix_path).tocsr(),
                "rhs": np.load(rhs_path),
                "order_rows": order_rows,
                "source": None,
                "build_seconds": time.time() - started,
                "cache_status": "loaded",
            }
    lower = first.exact_matrices()
    source = second.exact_data()
    rows = array("i")
    columns = array("i")
    values = array("d")

    def add(row: int, column: int, coefficient: object) -> None:
        numeric = _float(coefficient)
        if numeric:
            rows.append(row)
            columns.append(column)
            values.append(numeric)

    for (row, column), coefficient in lower["A"].todok().items():
        add(row, column, coefficient)
    for axis in range(4):
        row_offset = 550 + axis * 1330
        column_offset = ZERO_COLUMNS + axis * FIRST_COLUMNS_PER_AXIS
        for (row, column), coefficient in lower["B"][axis].todok().items():
            add(row_offset + row, column, coefficient)
        for (row, column), coefficient in lower["C"].todok().items():
            add(row_offset + row, column_offset + column, coefficient)

    target_keys = sorted(source["euler"])
    order_rows = {key: LOWER_ROWS + index for index, key in enumerate(target_keys)}
    rhs = [0.0] * (LOWER_ROWS + len(target_keys))
    for key, coefficient in source["euler"].items():
        rhs[order_rows[key]] = _float(coefficient)

    def add_order_column(column: int, image: second.EulerImage) -> None:
        for key, coefficient in image.items():
            row = order_rows.get(key)
            if row is None:
                row = LOWER_ROWS + len(order_rows)
                order_rows[key] = row
                rhs.append(0.0)
            add(row, column, coefficient)

    checkpoint = time.time()
    for column, (arity, output, inputs) in enumerate(second.zero._labels()):
        label = arity, output, tuple((field, ()) for field in inputs)
        add_order_column(column, second.redefinition_column(label, 2))
    if progress:
        print(json.dumps({"stage": "zero_columns", "elapsed": round(time.time() - checkpoint, 2)}), flush=True)

    checkpoint = time.time()
    positive_labels = first._positive_labels()
    for axis in range(4):
        offset = ZERO_COLUMNS + axis * FIRST_COLUMNS_PER_AXIS
        for local_column, label in enumerate(positive_labels):
            add_order_column(offset + local_column, second.redefinition_column(_first_label(axis, label), 2))
        if progress:
            print(
                json.dumps({"stage": f"first_axis_{axis}", "elapsed": round(time.time() - checkpoint, 2)}),
                flush=True,
            )

    checkpoint = time.time()
    second_offset = ZERO_COLUMNS + FIRST_COLUMNS
    for local_column, label in enumerate(second.second_jet_labels()):
        add_order_column(second_offset + local_column, second.second_jet_column(label))
        if progress and local_column and local_column % 25000 == 0:
            print(
                json.dumps({"stage": "second_columns", "completed": local_column, "elapsed": round(time.time() - checkpoint, 2)}),
                flush=True,
            )

    matrix = coo_matrix(
        (
            np.frombuffer(values, dtype=np.float64),
            (
                np.frombuffer(rows, dtype=np.int32),
                np.frombuffer(columns, dtype=np.int32),
            ),
        ),
        shape=(len(rhs), TOTAL_COLUMNS),
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    if cache_prefix is not None:
        save_npz(cache_prefix.with_suffix(".npz"), matrix, compressed=True)
        np.save(cache_prefix.with_suffix(".rhs.npy"), np.asarray(rhs, dtype=np.float64))
        with cache_prefix.with_suffix(".rows.pkl").open("wb") as handle:
            pickle.dump(order_rows, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return {
        "matrix": matrix,
        "rhs": np.asarray(rhs, dtype=np.float64),
        "order_rows": order_rows,
        "source": source,
        "build_seconds": time.time() - started,
        "cache_status": "written" if cache_prefix is not None else "disabled",
    }


def _row_record(row: int, inverse_order_rows: dict[int, second.EulerKey]) -> dict[str, object]:
    if row < 550:
        return {"row": row, "sector": "zero_constraint", "local_row": row}
    if row < LOWER_ROWS:
        offset = row - 550
        return {
            "row": row,
            "sector": "first_constraint",
            "axis": offset // 1330,
            "local_row": offset % 1330,
        }
    key = inverse_order_rows[row]
    return {
        "row": row,
        "sector": "order_two_Euler",
        "coordinate": second._euler_records({key: sp.Integer(1)})[0],
    }


def numerical_compatibility(*, maxiter: int = 5000) -> dict[str, object]:
    data = build_numeric_system()
    matrix: csr_matrix = data["matrix"]
    rhs: np.ndarray = data["rhs"]
    row_norms = np.sqrt(np.asarray(matrix.power(2).sum(axis=1)).ravel())
    unsupported = np.flatnonzero((row_norms == 0) & (rhs != 0))
    if unsupported.size:
        return {
            "shape": list(matrix.shape),
            "nnz": int(matrix.nnz),
            "unsupported_nonzero_rows": unsupported.tolist(),
            "compatible_numerically": False,
            "build_seconds": round(data["build_seconds"], 3),
        }
    row_norms[row_norms == 0] = 1.0
    column_norms = np.sqrt(np.asarray(matrix.power(2).sum(axis=0)).ravel())
    column_norms[column_norms == 0] = 1.0
    scaled = diags(1.0 / row_norms) @ matrix @ diags(1.0 / column_norms)
    scaled_rhs = rhs / row_norms
    started = time.time()
    result = lsmr(scaled, scaled_rhs, atol=1e-12, btol=1e-12, maxiter=maxiter)
    scaled_solution = result[0]
    solution = scaled_solution / column_norms
    residual = matrix @ solution - rhs
    scaled_residual = scaled @ scaled_solution - scaled_rhs
    original_left = scaled_residual / row_norms
    inverse_order_rows = {row: key for key, row in data["order_rows"].items()}
    top = np.argsort(np.abs(original_left))[-20:][::-1]
    top_records = []
    for row in top:
        record = _row_record(int(row), inverse_order_rows)
        record["left_weight"] = float(original_left[row])
        record["scaled_residual"] = float(scaled_residual[row])
        top_records.append(record)
    return {
        "shape": list(matrix.shape),
        "nnz": int(matrix.nnz),
        "order_two_Euler_rows": matrix.shape[0] - LOWER_ROWS,
        "zero_columns": ZERO_COLUMNS,
        "first_columns": FIRST_COLUMNS,
        "second_columns": SECOND_COLUMNS,
        "build_seconds": round(data["build_seconds"], 3),
        "cache_status": data["cache_status"],
        "solve_seconds": round(time.time() - started, 3),
        "lsmr_stop_code": int(result[1]),
        "iterations": int(result[2]),
        "scaled_residual_norm": float(result[3]),
        "normal_equation_residual_norm": float(result[4]),
        "condition_estimate": float(result[6]),
        "unscaled_residual_norm": float(np.linalg.norm(residual)),
        "unscaled_rhs_norm": float(np.linalg.norm(rhs)),
        "maximum_absolute_residual": float(np.max(np.abs(residual))),
        "solution_entries_above_1e_10": int(np.count_nonzero(np.abs(solution) > 1e-10)),
        "left_residual_entries_above_1e_8": int(np.count_nonzero(np.abs(original_left) > 1e-8)),
        "top_left_residual_rows": top_records,
        "compatible_numerically": bool(
            np.linalg.norm(residual) <= 1e-8 * max(1.0, np.linalg.norm(rhs))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maxiter", type=int, default=5000)
    args = parser.parse_args()
    print(json.dumps(numerical_compatibility(maxiter=args.maxiter), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
