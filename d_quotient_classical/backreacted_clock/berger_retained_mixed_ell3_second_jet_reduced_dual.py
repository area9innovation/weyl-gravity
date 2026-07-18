#!/usr/bin/env python3
"""Exact reduced dual search on second-jet-untouched Euler coordinates.

The full second-jet image misses sixteen target coordinates.  Individually
they can be moved by lower-page affine directions.  This module asks the exact
coupled question: is there a linear combination of those sixteen coordinates
whose first-jet rows lie in row(C), and whose resulting zero-jet row lies in
the row space of the certified lower Schur system?  Such a combination is a
dual witness for the complete physical order-two affine system because every
second-jet column vanishes on its order-two support.
"""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
import time

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)


K = sp.QQ.algebraic_field(sp.sqrt(10))
CACHE = Path("/tmp/berger_retained_mixed_ell3_second_jet_reduced_dual_inputs.pkl")


def _solve_transpose(square: sp.Matrix, rhs: sp.Matrix) -> sp.Matrix:
    numerator, denominator = DomainMatrix.from_Matrix(square.T).convert_to(K).solve_den(
        DomainMatrix.from_Matrix(rhs).convert_to(K)
    )
    return numerator.to_Matrix() / K.to_sympy(denominator)


def _nullspace(matrix: sp.Matrix) -> tuple[sp.Matrix, ...]:
    return tuple(matrix.nullspace())


def _first_label(axis: int, label: tuple[str, int, tuple[int, ...], int]) -> second.FLabel:
    arity, output, inputs, derivative_field = label
    atoms = []
    used = False
    for field in inputs:
        differentiated = field == derivative_field and not used
        atoms.append((field, (axis,) if differentiated else ()))
        used = used or differentiated
    return arity, output, tuple(sorted(atoms))


def exact_reduced_dual(*, progress: bool = True) -> dict[str, object]:
    started = time.time()
    source = second.exact_data()
    lower = first.exact_matrices()
    certificate = second.zero._load(first.OUTPUT)
    C = lower["C"]
    positive_labels = first._positive_labels()
    if CACHE.exists():
        with CACHE.open("rb") as handle:
            keys, E = pickle.load(handle)
        if progress:
            print(
                json.dumps({"stage": "input_cache", "status": "loaded", "elapsed": round(time.time() - started, 2)}),
                flush=True,
            )
    else:
        keys = second.untouched_second_jet_target_coordinates(source["euler"])
        if len(keys) != 16:
            raise ValueError(f"second-jet untouched-coordinate count drifted: {len(keys)}")
        key_index = {key: index for index, key in enumerate(keys)}
        if progress:
            print(json.dumps({"stage": "untouched", "count": len(keys), "elapsed": round(time.time() - started, 2)}), flush=True)
        E = []
        for axis in range(4):
            entries = {}
            for column, label in enumerate(positive_labels):
                image = second.redefinition_column(_first_label(axis, label), 2)
                for key in set(image).intersection(key_index):
                    entries[(key_index[key], column)] = image[key]
            E.append(sp.MutableSparseMatrix(len(keys), len(positive_labels), entries))
            if progress:
                print(
                    json.dumps({"stage": f"E_axis_{axis}", "nnz": len(entries), "elapsed": round(time.time() - started, 2)}),
                    flush=True,
                )
        with CACHE.open("wb") as handle:
            pickle.dump((keys, E), handle, protocol=pickle.HIGHEST_PROTOCOL)
    key_index = {key: index for index, key in enumerate(keys)}

    C_rows = certificate["rank_receipts"]["C_independent_rows"]
    C_columns = certificate["rank_receipts"]["C_basis_columns"]
    C_square = C[C_rows, C_columns]
    combined_rhs = sp.Matrix.hstack(*(E[axis][:, C_columns].T for axis in range(4)))
    combined_lambda = _solve_transpose(C_square, combined_rhs)
    lambdas = [
        combined_lambda[:, axis * len(keys) : (axis + 1) * len(keys)]
        for axis in range(4)
    ]
    defects = []
    for axis in range(4):
        defects.append(E[axis] - lambdas[axis].T * C[C_rows, :])
    first_constraints = sp.Matrix.vstack(*(defect.T for defect in defects))
    alpha_basis = _nullspace(first_constraints)
    first_rank = len(keys) - len(alpha_basis)
    if progress:
        print(
            json.dumps({"stage": "C_cokernel", "rank": first_rank, "kernel_dimension": len(alpha_basis), "elapsed": round(time.time() - started, 2)}),
            flush=True,
        )
    if not alpha_basis:
        return {
            "untouched_coordinate_count": len(keys),
            "C_cokernel_constraint_rank": first_rank,
            "C_compatible_combination_dimension": 0,
            "reduced_dual_exists": False,
            "elapsed_seconds": round(time.time() - started, 3),
        }

    D_entries = {}
    for column, (arity, output, inputs) in enumerate(second.zero._labels()):
        label = arity, output, tuple((field, ()) for field in inputs)
        image = second.redefinition_column(label, 2)
        for key in set(image).intersection(key_index):
            D_entries[(key_index[key], column)] = image[key]
    D = sp.MutableSparseMatrix(len(keys), len(second.zero._labels()), D_entries)
    effective = D
    for axis in range(4):
        effective = effective - lambdas[axis].T * lower["B"][axis][C_rows, :]
    alpha_matrix = sp.Matrix.hstack(*alpha_basis)
    effective_basis = alpha_matrix.T * effective

    C_left = sp.Matrix.hstack(*C.T.nullspace()).T
    H = lower["A"]
    for axis in range(4):
        H = H.col_join(C_left * lower["B"][axis])
    H_rows = certificate["rank_receipts"]["Schur_independent_rows"]
    H_columns = certificate["rank_receipts"]["Schur_basis_columns"]
    H_square = H[H_rows, H_columns]
    mu = _solve_transpose(H_square, effective_basis[:, H_columns].T)
    Schur_defect = effective_basis - mu.T * H[H_rows, :]
    beta_basis = _nullspace(Schur_defect.T)
    Schur_rank = len(alpha_basis) - len(beta_basis)
    if progress:
        print(
            json.dumps({"stage": "Schur", "constraint_rank": Schur_rank, "kernel_dimension": len(beta_basis), "elapsed": round(time.time() - started, 2)}),
            flush=True,
        )
    candidates = []
    target = sp.Matrix([source["euler"][key] for key in keys])
    for beta in beta_basis:
        alpha = alpha_matrix * beta
        evaluation = sp.factor((alpha.T * target)[0])
        if evaluation != 0:
            candidates.append((alpha / evaluation, evaluation))
    if not candidates:
        return {
            "untouched_coordinate_count": len(keys),
            "C_cokernel_constraint_rank": first_rank,
            "C_compatible_combination_dimension": len(alpha_basis),
            "Schur_compatible_combination_dimension": len(beta_basis),
            "nonzero_target_evaluation_dimension": 0,
            "reduced_dual_exists": False,
            "elapsed_seconds": round(time.time() - started, 3),
        }

    alpha, unnormalized_evaluation = candidates[0]
    normalized_evaluation = sp.factor((alpha.T * target)[0])
    if normalized_evaluation != 1:
        raise AssertionError("reduced dual normalization failed")
    support = [
        {
            "coordinate": second._euler_records({keys[index]: source["euler"][keys[index]]})[0],
            "dual_coefficient": str(sp.factor(alpha[index])),
        }
        for index in range(len(keys))
        if alpha[index] != 0
    ]
    return {
        "untouched_coordinate_count": len(keys),
        "C_cokernel_constraint_rank": first_rank,
        "C_compatible_combination_dimension": len(alpha_basis),
        "Schur_constraint_rank": Schur_rank,
        "Schur_compatible_combination_dimension": len(beta_basis),
        "nonzero_target_evaluation_dimension": len(candidates),
        "reduced_dual_exists": True,
        "normalized_target_evaluation": str(normalized_evaluation),
        "unnormalized_target_evaluation": str(unnormalized_evaluation),
        "order_two_support": support,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def main() -> None:
    argparse.ArgumentParser().parse_args()
    print(json.dumps(exact_reduced_dual(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
