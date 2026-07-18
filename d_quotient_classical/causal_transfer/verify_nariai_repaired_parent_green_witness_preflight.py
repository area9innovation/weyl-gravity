#!/usr/bin/env python3
"""Independent consumer for the Nariai metric-witness symbol preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.principal_symbols import (
    MinimalWitnessPrincipalSymbols,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    coefficient_kernel,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-repaired-parent-green-witness-preflight-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    result = sp.zeros(rows, columns)
    for row, column, coefficient in value["entries"]:
        result[row, column] = sp.Rational(coefficient)
    digest = hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(result)).encode()).hexdigest()
    if digest != value["sha256"]:
        raise AssertionError("serialized matrix digest mismatch")
    return result


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode()).hexdigest()


def _principal(
    table: dict[tuple[int, ...], sp.Matrix], order: int, zeta: sp.Matrix
) -> sp.Matrix:
    sample = next(iter(table.values()))
    result = sp.zeros(sample.rows, sample.cols)
    for word, matrix in table.items():
        if len(word) == order:
            result += sp.prod(zeta[axis] for axis in word) * matrix
    return result.applyfunc(sp.expand)


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for dependency in value["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    coordinates = value["typed_coordinates"]
    coordinate_map = _matrix(coordinates["metric_coordinate_map"])
    ghost_map = _matrix(coordinates["ghost_to_covector_map"])
    pairing = _matrix(coordinates["metric_fibre_pairing"])
    if coordinate_map.det() == 0 or ghost_map.det() == 0 or pairing.det() == 0:
        raise AssertionError("typed fibre map became degenerate")

    universal = MinimalWitnessPrincipalSymbols.build()
    universal.verify()
    k_symbol = (
        coordinate_map.inv() * universal.conformal_killing * ghost_map
    ).applyfunc(sp.expand)
    t_symbol = (
        ghost_map.inv() * universal.companion * coordinate_map
    ).applyfunc(sp.expand)
    bach = (
        coordinate_map.inv() * universal.bach * coordinate_map
    ).applyfunc(sp.expand)
    q4 = universal.covector_square**2
    coefficient = coefficient_kernel()
    actual_k = _principal(
        coefficient["automorphism"]["middle"]["first_bgg"],
        1,
        universal.covector,
    )
    actual_bach = _principal(coefficient["b"], 4, universal.covector)
    if actual_k != k_symbol.applyfunc(sp.expand):
        raise AssertionError("authoritative Nariai K does not match the typed symbol")
    if actual_bach != (pairing * bach).applyfunc(sp.expand):
        raise AssertionError("authoritative Nariai Bach row lost evaluation-dual typing")
    stored = value["principal_witness"]
    expected_digests = {
        "K_sha256": _digest(k_symbol),
        "T_pr_sha256": _digest(t_symbol),
        "B_operator_sha256": _digest(bach),
        "B_action_covector_sha256": _digest(actual_bach),
    }
    for name, digest in expected_digests.items():
        if stored[name] != digest:
            raise AssertionError(f"principal-symbol digest drifted: {name}")
    if sp.simplify(t_symbol * k_symbol - q4 * sp.eye(4)) != sp.zeros(4):
        raise AssertionError("ghost biwave identity failed")
    if sp.simplify(
        pairing * bach
        + sp.Rational(1, 2) * pairing * k_symbol * t_symbol
        - sp.Rational(1, 2) * q4 * pairing
    ) != sp.zeros(9):
        raise AssertionError("field biwave identity failed")

    checks = value["exact_checks"]
    boolean_checks = {
        name: item for name, item in checks.items() if not name.endswith("_rank")
    }
    if not all(isinstance(item, bool) and item for item in boolean_checks.values()):
        raise AssertionError("preflight contains a failed exact check")
    if checks["ghost_completed_symbol_rank"] != 0 or checks["field_completed_symbol_rank"] != 0:
        raise AssertionError("completed null symbol did not vanish")
    if value["rejected_candidate"]["cubic_symbol_rank"] != 0:
        raise AssertionError("parent-divergence screen drifted")
    if value["flags"]["NARIAI_METRIC_SCALAR_BIWAVE_PRINCIPAL_SYMBOL"] is not True:
        raise AssertionError("metric principal gate was not promoted")
    if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not False:
        raise AssertionError("rank-310 Green theorem was overpromoted")
    print("NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1: independently verified")


if __name__ == "__main__":
    verify()
