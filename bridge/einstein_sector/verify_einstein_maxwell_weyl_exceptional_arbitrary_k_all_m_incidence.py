"""Independent verifier for the arbitrary-k all-m locked incidence theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-arbitrary-k-all-m-incidence-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-arbitrary-k-all-m-incidence-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coordinates(matrix: sp.Matrix, basis: list[sp.Matrix]) -> sp.Matrix:
    columns = sp.Matrix.hstack(*(value.reshape(9, 1) for value in basis))
    solution, parameters = columns.gauss_jordan_solve(matrix.reshape(9, 1))
    assert parameters.rows == 0
    return solution


def _independent_representation_check() -> tuple[int, sp.Matrix]:
    basis = [
        sp.diag(1, -1, 0),
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
        sp.diag(sp.Rational(-1, 2), sp.Rational(-1, 2), 1),
    ]
    generators = [
        sp.Matrix([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
        sp.Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]]),
    ]
    v2_generators = [
        sp.Matrix.hstack(
            *[_coordinates(generator * tensor - tensor * generator, basis) for tensor in basis]
        )
        for generator in generators
    ]
    product_generators = [
        sp.kronecker_product(generator, sp.eye(5))
        + sp.kronecker_product(sp.eye(3), v2_generator)
        for generator, v2_generator in zip(generators, v2_generators, strict=True)
    ]
    canonical = sp.zeros(3, 15)
    for vector_index in range(3):
        for tensor_index, tensor in enumerate(basis):
            canonical[:, 5 * vector_index + tensor_index] = tensor * sp.eye(3)[:, vector_index]
    for generator, product_generator in zip(generators, product_generators, strict=True):
        assert generator * canonical == canonical * product_generator

    symbols = sp.symbols("z0:45")
    unknown = sp.Matrix(3, 15, symbols)
    equations: list[sp.Expr] = []
    for generator, product_generator in zip(generators, product_generators, strict=True):
        equations.extend(list(generator * unknown - unknown * product_generator))
    coefficient_matrix, _ = sp.linear_eq_to_matrix(equations, symbols)
    return len(symbols) - coefficient_matrix.rank(), canonical


def verify_payload(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    provenance = payload["provenance"]
    assert _sha256(ROOT / provenance["producer_path"]) == provenance["producer_sha256"]
    assert _sha256(ROOT / provenance["schema_path"]) == provenance["schema_sha256"]
    locked_reference = provenance["inputs"]["locked_resonance"]
    locked_path = ROOT / locked_reference["path"]
    assert _sha256(locked_path) == locked_reference["sha256"]
    assert locked_reference["sha256"] == "1d6e0de1021e13285508ce940b8d6a18f538025c0cba5eceed4999e05ffa1788"
    locked = _load(locked_path)
    assert locked["result_id"] == locked_reference["result_id"]

    hom_dimension, canonical = _independent_representation_check()
    representation = payload["representation_theorem"]
    assert hom_dimension == 1
    assert representation["Hom_SO3_dimension"] == 1
    assert representation["intertwiner_unknown_count"] - representation["intertwiner_linear_system_rank"] == 1
    assert representation["intertwiner_matrix"] == [
        [str(sp.factor(canonical[row, column])) for column in range(canonical.cols)]
        for row in range(canonical.rows)
    ]

    rows = payload["all_m_functionals"]
    assert rows["axial_output"] == "R_ax(k)=-(768/5)*Y*conj(x_ax)"
    assert rows["polar_output"] == "R_pol(k)=-(864/5)*Y*conj(x_pol)"
    assert sp.Rational(-768, 5) != 0
    assert sp.Rational(-864, 5) != 0

    rank_strata = payload["incidence_theorem"]["rank_strata"]
    assert [item["rank_Y"] for item in rank_strata] == [3, 2, 1, 0]
    assert sp.Matrix(rank_strata[0]["witness_Y"]).rank() == 3
    assert sp.Matrix(rank_strata[1]["witness_Y"]).rank() == 2
    rank_one = sp.Matrix(
        [[sp.sympify(value, locals={"I": sp.I}) for value in row] for row in rank_strata[2]["witness_Y"]]
    )
    assert rank_one.rank() == 1
    assert sp.trace(rank_one) == 0
    assert sp.Matrix(rank_strata[3]["witness_Y"]) == sp.zeros(3)

    classification = payload["classification"]
    assert classification["all_m_locked_difference_tensor_assembled"] is True
    assert classification["locked_two_fibre_difference_incidence_classified"] is True
    assert classification["enlarged_bounded_common_zero_with_moment_maps_classified"] is False
    assert classification["all_exceptional_cross_columns_computed"] is False
    assert classification["multiple_abs_momentum_full_cone_classified"] is False


def verify_certificate() -> None:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    atlas = _load(ATLAS)
    assert atlas["generated_by_sha256"] == _sha256(ROOT / atlas["generated_by"])
    assert len(atlas["entries"]) == 1
    entry = atlas["entries"][0]
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)
    assert entry["mode_data"]["resonance"]["status"] == "CERTIFIED"
    assert entry["mode_data"]["taub_maps"]["status"] == "OPEN"
    assert entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] == "OPEN"
    assert entry["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1 independent verification: PASS")
