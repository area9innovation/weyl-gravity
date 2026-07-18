#!/usr/bin/env python3
"""Independent coefficient consumer for the Nariai metric Green theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add, _algebraic, _scale,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    coefficient_kernel, _entry_count,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-metric-biwave-green-homotopy-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    result = sp.zeros(rows, columns)
    for row, column, coefficient in value["entries"]:
        result[row, column] = sp.Rational(coefficient)
    return result


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    return {
        tuple(item["word"]): _matrix(item["matrix"])
        for item in value["entries"]
    }


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for dependency in value["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    coefficient = coefficient_kernel()
    middle = coefficient["automorphism"]["middle"]
    pbw_h0 = middle["pbw_h0"]
    pbw_h1 = middle["pbw_h1"]
    metric = pbw_h0.background.metric
    companion = _table(value["companion"]["coefficient_table"])
    k = middle["first_bgg"]
    box0 = {(axis, axis): metric[axis, axis] * sp.eye(4) for axis in range(4)}
    box1 = {(axis, axis): metric[axis, axis] * sp.eye(9) for axis in range(4)}

    ghost = pbw_h0.compose(companion, k)
    expected_ghost = pbw_h0.compose(
        _add(box0, _algebraic(sp.eye(4))),
        _add(box0, _algebraic(sp.Rational(1, 3) * sp.eye(4))),
    )
    if _entry_count(_add(ghost, _scale(expected_ghost, -1))):
        raise AssertionError("serialized companion lost the ghost factorization")

    gram = coefficient["endpoint"]["tensor_gram"]
    bach = {word: gram.inv() * matrix for word, matrix in coefficient["b"].items()}
    metric_block = _add(
        bach, _scale(pbw_h1.compose(k, companion), sp.Rational(1, 2))
    )
    factor_a_matrix = _matrix(value["metric_factorization"]["factor_a_matrix"])
    factor_b_matrix = _matrix(value["metric_factorization"]["factor_b_matrix"])
    factors = _scale(
        pbw_h1.compose(
            _add(box1, _algebraic(factor_a_matrix)),
            _add(box1, _algebraic(factor_b_matrix)),
        ),
        sp.Rational(1, 2),
    )
    if _entry_count(_add(metric_block, _scale(factors, -1))):
        raise AssertionError("serialized metric factors do not reproduce the Bach witness")
    if gram * factor_a_matrix != factor_a_matrix.T * gram:
        raise AssertionError("factor A is not pairing self-adjoint")
    if gram * factor_b_matrix != factor_b_matrix.T * gram:
        raise AssertionError("factor B is not pairing self-adjoint")
    if factor_a_matrix * factor_b_matrix != factor_b_matrix * factor_a_matrix:
        raise AssertionError("metric factors do not commute")

    checks = value["exact_checks"]
    zero_checks = [
        number for name, number in checks.items()
        if name.endswith("_entries") or name.endswith("_rank") and name not in (
            "lower_order_linear_rank", "lower_order_augmented_rank"
        )
    ]
    if any(zero_checks):
        raise AssertionError("certificate contains a nonzero factorization defect")
    if checks["projector_ranks"] != [4, 1, 4]:
        raise AssertionError("curvature-channel ranks drifted")
    if value["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("metric causal theorem was not promoted")
    if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not False:
        raise AssertionError("rank-310 theorem was overpromoted")
    print("NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1: independently verified")


if __name__ == "__main__":
    verify()
