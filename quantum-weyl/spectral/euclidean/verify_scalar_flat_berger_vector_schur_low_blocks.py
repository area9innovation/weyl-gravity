#!/usr/bin/env python3
"""Independent exact replay of the scalar-flat Berger vector Schur low blocks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator, ValidationError


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json"
ORACLE = HERE / "generated/scalar_flat_berger_vector_schur_low_blocks_v1/blocks.json"
CERTIFICATE_SCHEMA = HERE / "schema/scalar-flat-berger-vector-schur-low-blocks-v1.schema.json"
ORACLE_SCHEMA = HERE / "schema/scalar-flat-berger-vector-schur-low-block-oracle-v1.schema.json"
I = sp.I
T = sp.symbols("t", real=True)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"t": T, "I": I, "sqrt": sp.sqrt})


def _matrix(value: list[list[str]]) -> sp.Matrix:
    if not value:
        return sp.zeros(0)
    return sp.Matrix([[_parse(entry) for entry in row] for row in value])


def _explicit_generators(twice_j: int) -> list[sp.Matrix]:
    if twice_j == 1:
        return [
            sp.Matrix([[0, 1], [1, 0]]) / 2,
            sp.Matrix([[0, -I], [I, 0]]) / 2,
            sp.diag(sp.Rational(1, 2), sp.Rational(-1, 2)),
        ]
    if twice_j == 2:
        root = sp.sqrt(2)
        return [
            sp.Matrix([[0, 1, 0], [1, 0, 1], [0, 1, 0]]) / root,
            sp.Matrix([[0, -I, 0], [I, 0, -I], [0, I, 0]]) / root,
            sp.diag(1, 0, -1),
        ]
    raise ValueError("independent rail covers j=1/2 and j=1")


def _hardcoded_covector_connection() -> list[sp.Matrix]:
    c0 = sp.zeros(4)
    c1 = sp.zeros(4)
    c1[2, 3] = -1
    c1[3, 2] = 1
    c2 = sp.zeros(4)
    c2[1, 3] = 1
    c2[3, 1] = -1
    c3 = sp.zeros(4)
    c3[1, 2] = sp.Rational(1, 2)
    c3[2, 1] = sp.Rational(-1, 2)
    return [c0, c1, c2, c3]


def _independent_block(n: int, twice_j: int) -> dict[str, sp.Matrix]:
    angular = _explicit_generators(twice_j)
    dimension = twice_j + 1
    identity = sp.eye(dimension)
    derivatives = [I * n * identity, -I * angular[0], -I * angular[1], -I * angular[2] / 2]
    connection = _hardcoded_covector_connection()
    covariant = [
        sp.kronecker_product(sp.eye(4), derivatives[a])
        + sp.kronecker_product(connection[a], identity)
        for a in range(4)
    ]
    ricci = sp.kronecker_product(sp.diag(0, -1, -1, 2), identity)
    f_block = -sum((entry * entry for entry in covariant), sp.zeros(4 * dimension)) + ricci
    w_block = -2 * ricci
    a_block = sp.simplify(f_block + T * w_block)
    gradient = sp.Matrix.vstack(*derivatives)
    divergence = gradient.H
    delta0 = sp.simplify(divergence * gradient)
    schur = sp.simplify(sp.Rational(2, 3) * identity + sp.Rational(1, 3) * divergence * a_block.inv() * gradient)
    return {
        "d": gradient,
        "delta": divergence,
        "Delta_0": delta0,
        "F": f_block,
        "W": w_block,
        "A": a_block,
        "S": schur,
    }


def verify(certificate: dict | None = None, oracle: dict | None = None) -> None:
    if certificate is None:
        certificate = json.loads(CERTIFICATE.read_text())
    if oracle is None:
        oracle_bytes = ORACLE.read_bytes()
        oracle = json.loads(oracle_bytes)
    else:
        oracle_bytes = (json.dumps(oracle, indent=2, sort_keys=True) + "\n").encode()
    try:
        for schema_path, value in ((CERTIFICATE_SCHEMA, certificate), (ORACLE_SCHEMA, oracle)):
            schema = json.loads(schema_path.read_text())
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(value)
    except ValidationError as exc:
        raise ValueError("low-block schema rejected payload") from exc
    assert certificate["oracle"]["sha256"] == _sha256_bytes(oracle_bytes)
    assert certificate["oracle"]["block_count"] == 9

    indexed = {(row["n"], row["twice_j"]): row for row in oracle["blocks"]}
    for twice_j in (1, 2):
        for n in (-1, 0, 1):
            stored = indexed[(n, twice_j)]
            direct = _independent_block(n, twice_j)
            for stored_name, direct_name in (
                ("d_matrix", "d"),
                ("delta_matrix", "delta"),
                ("Delta_0_matrix", "Delta_0"),
                ("F_matrix", "F"),
                ("W_matrix", "W"),
                ("A_t_matrix", "A"),
                ("S_L_t_matrix", "S"),
            ):
                assert sp.simplify(_matrix(stored[stored_name]) - direct[direct_name]) == sp.zeros(*direct[direct_name].shape), (n, twice_j, stored_name)
            assert sp.simplify(direct["F"] * direct["d"] - direct["d"] * direct["Delta_0"]) == sp.zeros(4 * (twice_j + 1), twice_j + 1)
            assert direct["A"].H == direct["A"]
            assert sp.simplify(
                sp.factor(direct["A"].det()) - _parse(stored["det_A_t"])
            ) == 0
            assert sp.simplify(
                sp.factor(direct["S"].det()) - _parse(stored["det_S_L_t"])
            ) == 0
            derivative = sp.simplify(direct["S"].diff(T).subs(T, 0))
            assert derivative == _matrix(stored["S_L_first_derivative_at_zero"])

    first = indexed[(0, 1)]
    assert _matrix(first["S_L_first_derivative_at_zero"]) == sp.diag(sp.Rational(-64, 81), sp.Rational(-64, 81))

    total_a_one_kernel = 0
    for row in oracle["blocks"]:
        a_one = _matrix(row["A_t_matrix"]).subs(T, 1)
        delta = _matrix(row["delta_matrix"])
        projector = _matrix(row["A_at_one_kernel"]["orthogonal_projector"])
        assert sp.simplify(projector.H - projector) == sp.zeros(projector.rows)
        assert sp.simplify(projector * projector - projector) == sp.zeros(projector.rows)
        assert sp.simplify(a_one * projector) == sp.zeros(projector.rows)
        assert sp.simplify(delta * projector) == sp.zeros(delta.rows, projector.cols)
        rank = int(projector.rank())
        assert rank == row["A_at_one_kernel"]["dimension"]
        total_a_one_kernel += row["left_multiplicity"] * rank
        if row["scalar_primed_in_block"]:
            det_a = _parse(row["det_A_t"])
            det_s = _parse(row["det_S_L_t"])
            det_f = sp.factor(_matrix(row["F_matrix"]).det())
            assert sp.simplify(
                sp.factor(det_a * det_s / det_f)
                - _parse(row["paired_relative_factor"])
            ) == 0
    assert total_a_one_kernel == 5
    assert oracle["priming"]["A_at_one_zero_dimension_with_left_multiplicity"] == 5

    flags = certificate["claim_flags"]
    true_flags = {"LOW_VECTOR_SCHUR_BLOCKS_COMPUTED", "HODGE_WARD_AND_SELF_ADJOINTNESS_VERIFIED", "LOW_MODE_PRIMING_AND_ZERO_POLE_POLICY_COMPUTED"}
    for name, flag in flags.items():
        assert flag is (name in true_flags)
    print("Scalar-flat Berger vector Schur low blocks: PASS")


if __name__ == "__main__":
    verify()
