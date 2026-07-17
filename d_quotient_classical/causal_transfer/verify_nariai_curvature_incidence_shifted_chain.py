#!/usr/bin/env python3
"""Independent exact replay of the Nariai shifted incidence chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _formal_adjoint,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import curvature_incidence
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _lc_adjoint_curvature,
    candidate,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import fixture as middle_fixture


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-shifted-chain-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    matrix = sp.zeros(rows, columns)
    for row, column, entry in value["entries"]:
        matrix[row, column] = sp.Rational(entry)
    digest = hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest()
    if digest != value["sha256"]:
        raise ValueError("sparse matrix digest drifted")
    return matrix


def _table(value: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    result = {tuple(item["word"]): _matrix(item["matrix"]) for item in value["entries"]}
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(result[word]))}"
        for word in sorted(result)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value["sha256"]:
        raise ValueError("operator table digest drifted")
    return result


def verify() -> dict[str, object]:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    for name, dependency in value["dependency_refs"].items():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency drifted: {name}")

    strict = candidate()
    middle = middle_fixture()
    algebraic = middle["algebraic"]
    background = NariaiBackground()
    parent_pbw = FibrePBW(
        _tensor_product_curvature(background, _lc_adjoint_curvature(), 1),
        background,
        "Nariai-C1-independent-shifted-chain",
    )
    l1 = _add(middle["inclusion1"], _algebraic(strict["correction1"]))
    incidence = _algebraic(curvature_incidence()["incidence"])
    parent = middle["yang_mills_middle"]
    phi = middle["pbw_h1"].compose(parent, l1)
    mi = middle["pbw_h0"].compose(parent, incidence)
    phik = middle["pbw_h0"].compose(phi, middle["first_bgg"])
    if mi != _scale(phik, -1):
        raise ValueError("independent shifted-chain replay failed")
    l1_sharp = _formal_adjoint(
        l1,
        algebraic.endpoint_field_pairing,
        algebraic.one_form_pairing,
        parent_pbw,
    )
    saddle = middle["pbw_h1"].compose(l1_sharp, phi)
    upper = _add(
        middle["pbw_h0"].compose(saddle, middle["first_bgg"]),
        middle["pbw_h0"].compose(l1_sharp, mi),
    )
    if upper:
        raise ValueError("independent factorized upper saddle replay failed")
    parent_sharp = _formal_adjoint(
        parent,
        algebraic.one_form_pairing,
        algebraic.one_form_pairing,
        parent_pbw,
    )
    adjoint_defect = _add(parent_sharp, _scale(parent, -1))
    if set(adjoint_defect) != {()} or adjoint_defect[()].rank() != 60:
        raise ValueError("PBW adjoint replay diagnostic drifted")
    if sum(entry != 0 for entry in adjoint_defect[()]) != 60 or adjoint_defect[()][0, 0] != 1:
        raise ValueError("PBW adjoint replay witness drifted")

    data = value["exact_data"]
    expected = {
        "corrected_L1": l1,
        "curvature_incidence": incidence,
        "shifted_equation_map": phi,
        "M_on_incidence": mi,
        "Phi1_on_K": phik,
        "shifted_chain_defect": {},
        "factorized_endpoint_saddle": saddle,
        "factorized_saddle_lower_defect": {},
        "factorized_saddle_upper_defect": {},
        "pbw_parent_adjoint_replay_defect": adjoint_defect,
    }
    for name, table in expected.items():
        if _table(data[name]) != table:
            raise ValueError(f"portable table drifted: {name}")
    if value["flags"]["CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE"] is not False:
        raise ValueError("cyclic mapping cone was overpromoted")
    print("NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
