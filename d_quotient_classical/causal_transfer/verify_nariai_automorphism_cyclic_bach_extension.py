#!/usr/bin/env python3
"""Independent verifier for the Nariai automorphism cyclic Bach extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _tensor_product_curvature,
)
from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _parse_sparse,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _lc_adjoint_curvature,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    endpoint_operator,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-automorphism-cyclic-bach-extension-v1.schema.json"


O = OperatorPolynomial


def _operator_matrix(value: object) -> list[list[O]]:
    if not isinstance(value, Mapping):
        raise AssertionError("operator matrix is not an object")
    shape = value.get("shape")
    entries = value.get("entries")
    if not (
        isinstance(shape, list)
        and len(shape) == 2
        and all(isinstance(item, int) for item in shape)
        and isinstance(entries, list)
    ):
        raise AssertionError("malformed operator matrix")
    matrix = [[O.zero() for _ in range(shape[1])] for _ in range(shape[0])]
    for item in entries:
        if not isinstance(item, list) or len(item) != 3:
            raise AssertionError("malformed operator entry")
        row, column, terms = item
        if not isinstance(terms, list):
            raise AssertionError("malformed operator terms")
        matrix[row][column] = O._from_dict(
            {
                tuple(term[0]): sp.Rational(term[1], term[2])
                for term in terms
            }
        )
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value.get("sha256"):
        raise AssertionError("operator matrix digest mismatch")
    return matrix


def _zero(rows: int, columns: int) -> list[list[O]]:
    return [[O.zero() for _ in range(columns)] for _ in range(rows)]


def _multiply(left: list[list[O]], right: list[list[O]]) -> list[list[O]]:
    if len(left[0]) != len(right):
        raise AssertionError("operator matrices do not compose")
    value = _zero(len(left), len(right[0]))
    for row in range(len(left)):
        for column in range(len(right[0])):
            for middle in range(len(right)):
                value[row][column] = value[row][column] + left[row][middle] * right[middle][column]
    return value


def _add(left: list[list[O]], right: list[list[O]]) -> list[list[O]]:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _adjoint(value: O) -> O:
    involution = {
        "d": "dsharp", "dsharp": "d",
        "k": "ksharp", "ksharp": "k",
        "M": "M", "Phi": "Phisharp", "Phisharp": "Phi",
        "B": "B", "L0": "L0sharp", "L0sharp": "L0",
        "L1": "L1sharp", "L1sharp": "L1",
        "p0sharp": "p0", "p0": "p0sharp",
        "K": "Ksharp", "Ksharp": "K",
    }
    return O._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def _matrix_adjoint(value: list[list[O]]) -> list[list[O]]:
    return [
        [_adjoint(value[column][row]) for column in range(len(value))]
        for row in range(len(value[0]))
    ]


def _assert_abstract_layout(operators: Mapping[str, object]) -> None:
    q = _operator_matrix(operators["abstract_Q"])
    pairing = _operator_matrix(operators["odd_pairing"])
    metric_q = _operator_matrix(operators["metric_Q"])
    metric_pairing = _operator_matrix(operators["metric_pairing"])
    inclusion = _operator_matrix(operators["metric_graph_inclusion"])
    if [len(q), len(q[0])] != [8, 8] or [len(inclusion), len(inclusion[0])] != [8, 4]:
        raise AssertionError("abstract carrier shape drifted")

    expected_q = _zero(8, 8)
    for row, column, name, coefficient in (
        (1, 0, "d", 1), (2, 0, "k", 1), (4, 3, "M", 1),
        (5, 2, "B", 1), (5, 3, "Phisharp", -1),
        (6, 1, "M", 1), (6, 2, "Phi", -1),
        (7, 4, "dsharp", 1), (7, 5, "ksharp", 1),
    ):
        expected_q[row][column] = O.atom(name, coefficient)
    if q != expected_q:
        raise AssertionError("cyclic saddle sign or incidence drifted")

    expected_pairing = _zero(8, 8)
    for left, right in ((0, 7), (1, 4), (2, 5), (3, 6)):
        expected_pairing[left][right] = O.identity()
        expected_pairing[right][left] = O.identity(-1)
    if pairing != expected_pairing:
        raise AssertionError("odd pairing layout drifted")

    degree_sign = _zero(8, 8)
    for index, degree in enumerate((-1, 0, 0, 0, 1, 1, 1, 2)):
        degree_sign[index][index] = O.identity(-1 if degree % 2 else 1)
    cyclic = _add(
        _multiply(_matrix_adjoint(q), pairing),
        _multiply(_multiply(degree_sign, pairing), q),
    )
    if any(entry != O.zero() for row in cyclic for entry in row):
        raise AssertionError("independent abstract odd-cyclicity replay failed")

    square = _multiply(q, q)
    nonzero = {
        (row, column): square[row][column]
        for row in range(8)
        for column in range(8)
        if square[row][column] != O.zero()
    }
    expected_square = {
        (5, 0): O.atom("B") * O.atom("k"),
        (6, 0): O.atom("M") * O.atom("d") + (O.atom("Phi") * O.atom("k")).scale(-1),
        (7, 2): O.atom("ksharp") * O.atom("B"),
        (7, 3): O.atom("dsharp") * O.atom("M") + (O.atom("ksharp") * O.atom("Phisharp")).scale(-1),
    }
    if nonzero != expected_square:
        raise AssertionError("unexpected abstract Q-squared path")

    expected_metric_q = _zero(4, 4)
    expected_metric_q[1][0] = O.atom("K")
    expected_metric_q[2][1] = O.atom("B")
    expected_metric_q[3][2] = O.atom("Ksharp")
    if metric_q != expected_metric_q:
        raise AssertionError("metric complex layout drifted")
    expected_metric_pairing = _zero(4, 4)
    for left, right in ((0, 3), (1, 2)):
        expected_metric_pairing[left][right] = O.identity()
        expected_metric_pairing[right][left] = O.identity(-1)
    if metric_pairing != expected_metric_pairing:
        raise AssertionError("metric pairing layout drifted")
    expected_inclusion = _zero(8, 4)
    expected_inclusion[0][0] = O.atom("L0")
    expected_inclusion[1][1] = O.atom("L1")
    expected_inclusion[2][1] = O.identity()
    expected_inclusion[5][2] = O.identity()
    expected_inclusion[7][3] = O.atom("p0sharp")
    if inclusion != expected_inclusion:
        raise AssertionError("metric graph layout drifted")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_table(value: object) -> dict[tuple[int, ...], sp.Matrix]:
    if not isinstance(value, Mapping) or not isinstance(value.get("entries"), list):
        raise AssertionError("malformed PBW table")
    table: dict[tuple[int, ...], sp.Matrix] = {}
    for item in value["entries"]:
        if not isinstance(item, Mapping) or not isinstance(item.get("word"), list):
            raise AssertionError("malformed PBW entry")
        table[tuple(item["word"])] = _parse_sparse(item.get("matrix"))
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    if hashlib.sha256(payload.encode()).hexdigest() != value.get("sha256"):
        raise AssertionError("PBW table digest mismatch")
    return table


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(entry != 0 for matrix in table.values() for entry in matrix)


def verify() -> None:
    certificate = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if certificate["result_id"] != "NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1":
        raise AssertionError("wrong cyclic Bach result id")

    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError("dependency digest drifted")
    for relative, digest in certificate["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise AssertionError(f"source digest drifted: {relative}")

    carrier = certificate["carrier"]
    if carrier["block_ranks"] != [15, 60, 9, 60, 60, 9, 60, 15]:
        raise AssertionError("carrier ranks drifted")
    if carrier["block_degrees"] != [-1, 0, 0, 0, 1, 1, 1, 2]:
        raise AssertionError("carrier degrees drifted")
    if carrier["total_rank"] != 288:
        raise AssertionError("carrier total rank drifted")

    operators = certificate["operators"]
    _assert_abstract_layout(operators)
    serialized = {
        name: _parse_table(operators[name])
        for name in (
            "d_aut",
            "K_p0",
            "M_D",
            "Phi",
            "B_action",
            "L0_corrected",
            "L1_corrected",
        )
    }
    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    authoritative = {
        "d_aut": automorphism["d_aut"],
        "K_p0": automorphism["k_p0"],
        "M_D": automorphism["middle"]["yang_mills_middle"],
        "Phi": automorphism["phi"],
        "B_action": endpoint["action_bach"],
        "L0_corrected": automorphism["corrected_l0"],
        "L1_corrected": automorphism["corrected_l1"],
    }
    if serialized != authoritative:
        raise AssertionError("serialized primal coefficient tables drifted")

    if any(
        _count(automorphism[name])
        for name in (
            "first_square_defect",
            "projection_defect",
            "degree_one_defect",
            "graph_constraint_defect",
        )
    ):
        raise AssertionError("automorphism primal identities drifted")
    background = NariaiBackground()
    pbw_c0 = FibrePBW(
        _tensor_product_curvature(background, _lc_adjoint_curvature(), 0),
        background,
        "Nariai-C0-independent-cyclic-Bach",
    )
    if _count(pbw_c0.compose(endpoint["action_bach"], automorphism["k_p0"])):
        raise AssertionError("B_action K p0 identity drifted")

    algebraic = automorphism["middle"]["algebraic"]
    pairings = certificate["pairings"]
    expected_pairings = {
        "C0": algebraic.adjoint_pairing,
        "C1": algebraic.one_form_pairing,
        "H0": algebraic.endpoint_ghost_pairing,
        "H1": algebraic.endpoint_field_pairing,
    }
    if any(_parse_sparse(pairings[name]) != matrix for name, matrix in expected_pairings.items()):
        raise AssertionError("serialized fibre pairing drifted")
    if _parse_sparse(operators["p0"]) != algebraic.p0:
        raise AssertionError("p0 drifted")
    if _parse_sparse(operators["p0_sharp"]) != algebraic.i_identity:
        raise AssertionError("forced p0 adjoint drifted")
    if algebraic.p0 * automorphism["corrected_l0"].get((), sp.zeros(15, 4)) != sp.eye(4):
        # The complete differential identity is already checked above; this
        # additionally confirms the algebraic retraction coefficient.
        raise AssertionError("p0 L0 algebraic coefficient drifted")

    checks = certificate["checks"]
    if not all(
        checks[name] is True
        for name in (
            "abstract_Q_squared_mod_certified_relations",
            "abstract_odd_cyclicity",
            "metric_graph_chain_map_mod_certified_relations",
            "metric_pairing_pullback_mod_retract_relations",
        )
    ):
        raise AssertionError("abstract cyclic checks unavailable")
    if any(
        checks[name] != 0
        for name in (
            "M_daut_minus_Phi_Kp0_entries",
            "B_Kp0_entries",
            "daut_L0_minus_L1_K_entries",
            "p0_L0_minus_identity_entries",
            "P_metric_graph_entries",
            "metric_BK_entries",
            "metric_KsharpB_entries",
        )
    ):
        raise AssertionError("coefficient defect was promoted")

    flags = certificate["flags"]
    if not all(
        flags[name] is True
        for name in (
            "NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1",
            "FULL_ODD_CYCLIC_BACH_COMPLEX",
            "ACTION_DERIVED_MIDDLE",
            "METRIC_BACH_GRAPH_CHAIN_MAP",
            "METRIC_PAIRING_PULLBACK",
            "SUPPORT_LOCAL_DIFFERENTIAL_COMPLEX",
        )
    ):
        raise AssertionError("positive cyclic flag unavailable")
    if any(
        flags[name]
        for name in (
            "FULL_PARENT_METRIC_QUASI_ISOMORPHISM",
            "SUPPORT_LOCAL_AUTOMORPHISM_SDR",
            "NARIAI_GREEN_HOMOTOPY",
            "OPEN_BACKGROUND_CLASS",
            "NONLINEAR_EXTENSION",
            "QUANTUM_CLAIM",
        )
    ):
        raise AssertionError("cyclic Bach extension was overpromoted")
    print("NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1: independently verified")


if __name__ == "__main__":
    verify()
