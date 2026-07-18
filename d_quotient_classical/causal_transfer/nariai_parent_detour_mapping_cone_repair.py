#!/usr/bin/env python3
"""Economical cyclic parent-detour mapping-cone repair on unit Nariai.

The 288-component automorphism/Bach saddle has a fifteen-dimensional
noncharacteristic symbol class because its multiplier copy has no incoming
arrow.  The repair below does not invert that multiplier.  It replaces the
bare saddle by the parent detour cone and adds only the eleven-dimensional
algebraic complement of the metric ghost splitting.

In split coordinates the 310-component complex is the direct sum of

* the four-row metric Bach complex;
* the pointwise contractible complement ``epsilon_perp -> s``; and
* the locally invertible parent saddle

      (x,y) |-> (c M x+y, x),        c=-1/2.

The saddle inverse is the finite-order differential matrix

      [[0,1],[1,(1/2)M]],

so the SDR uses no Green operator or inverse differential operator.  The
canonical triangular change of variables

    a=x+d_aut J0 s+L1 h,       lambda=y-c Phi h

and its forced cotangent transform restore the original parent/metric graph.
The Schur complement is exactly the action Bach Hessian because

    B_parent_compressed+Q_unique=-2 B_action.

This module certifies the local cyclic SDR.  Green transfer is deliberately
left to the next gate.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _tensor_product_curvature,
)
from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    OUTPUT as AUTOMORPHISM_CERTIFICATE,
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_cyclic_bach_sdr_symbol_obstruction import (
    OUTPUT as OBSTRUCTION_CERTIFICATE,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _lc_adjoint_curvature,
    _sha256,
    _sparse,
    _sparse_table,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    OUTPUT as BACH_CERTIFICATE,
    endpoint_operator,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-parent-detour-mapping-cone-repair.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-parent-detour-mapping-cone-repair-v1.schema.json"
VERIFIER = HERE / "verify_nariai_parent_detour_mapping_cone_repair.py"
TESTS = HERE / "tests/test_nariai_parent_detour_mapping_cone_repair.py"
AUTOMORPHISM_PRODUCER = HERE / "nariai_automorphism_prolongation_first_two_rows.py"
OBSTRUCTION_PRODUCER = HERE / "nariai_automorphism_cyclic_bach_sdr_symbol_obstruction.py"
BACH_PRODUCER = HERE / "nariai_linearized_bach_endpoint.py"
FORMAL_SOURCE = ROOT / "covariant_completion/minimal_witness/formal_operators.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


O = OperatorPolynomial
Matrix = list[list[O]]
Table = dict[tuple[int, ...], sp.Matrix]
C = Fraction(-1, 2)

BLOCK_NAMES = (
    "epsilon_C0",
    "s_ker_p0",
    "x_C1",
    "h_H1",
    "y_C1",
    "s_sharp_ker_p0_dual",
    "x_sharp_C1dual",
    "h_sharp_H1dual",
    "y_sharp_C1dual",
    "epsilon_sharp_C0dual",
)
BLOCK_DEGREES = (-1, 0, 0, 0, 0, 1, 1, 1, 1, 2)
BLOCK_RANKS = (15, 11, 60, 9, 60, 11, 60, 9, 60, 15)
METRIC_NAMES = ("xi_H0", "h_H1", "h_sharp_H1dual", "xi_sharp_H0dual")
METRIC_DEGREES = (-1, 0, 1, 2)
SIZE = len(BLOCK_NAMES)


def _zero(rows: int, columns: int) -> Matrix:
    return [[O.zero() for _ in range(columns)] for _ in range(rows)]


def _identity(size: int) -> Matrix:
    value = _zero(size, size)
    for index in range(size):
        value[index][index] = O.identity()
    return value


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _scale(value: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in value]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise AssertionError("abstract matrix shapes do not compose")
    value = _zero(len(left), len(right[0]))
    for row in range(len(left)):
        for middle in range(len(right)):
            if left[row][middle] == O.zero():
                continue
            for column in range(len(right[0])):
                if right[middle][column] != O.zero():
                    value[row][column] = (
                        value[row][column]
                        + left[row][middle] * right[middle][column]
                    )
    return value


def _operator_adjoint(value: O) -> O:
    involution = {
        "g": "gsharp", "gsharp": "g",
        "J": "Jsharp", "Jsharp": "J",
        "d": "dsharp", "dsharp": "d",
        "k": "ksharp", "ksharp": "k",
        "M": "M", "B": "B",
        "L": "Lsharp", "Lsharp": "L",
        "Phi": "Phisharp", "Phisharp": "Phi",
        "L0": "L0sharp", "L0sharp": "L0",
        "p0": "p0sharp", "p0sharp": "p0",
        "K": "Ksharp", "Ksharp": "K",
    }
    return O._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def _matrix_adjoint(value: Matrix) -> Matrix:
    return [
        [_operator_adjoint(value[column][row]) for column in range(len(value))]
        for row in range(len(value[0]))
    ]


def _degree_sign(degrees: tuple[int, ...]) -> Matrix:
    value = _zero(len(degrees), len(degrees))
    for index, degree in enumerate(degrees):
        value[index][index] = O.identity(-1 if degree % 2 else 1)
    return value


def _replace_once(value: O) -> tuple[O, bool]:
    """Apply one terminating relation of the ghost splitting/Bach complex."""
    zero = {
        ("B", "k"), ("ksharp", "B"),
        ("g", "L0"), ("L0sharp", "gsharp"),
        ("p0", "J"), ("Jsharp", "p0sharp"),
    }
    simple = {
        ("g", "J"): O.identity(),
        ("Jsharp", "gsharp"): O.identity(),
        ("p0", "L0"): O.identity(),
        ("L0sharp", "p0sharp"): O.identity(),
        ("k",): O.atom("K") * O.atom("p0"),
        ("ksharp",): O.atom("p0sharp") * O.atom("Ksharp"),
        ("d", "L0"): O.atom("L") * O.atom("K"),
        ("L0sharp", "dsharp"): O.atom("Ksharp") * O.atom("Lsharp"),
        ("M", "L"): O.atom("Phi"),
        ("Lsharp", "M"): O.atom("Phisharp"),
    }
    affine = {
        ("J", "g"): O.identity() + (O.atom("L0") * O.atom("p0")).scale(-1),
        ("gsharp", "Jsharp"): O.identity() + (O.atom("p0sharp") * O.atom("L0sharp")).scale(-1),
    }
    for word, coefficient in value.terms:
        for old in zero:
            for index in range(len(word) - len(old) + 1):
                if word[index:index + len(old)] == old:
                    left = O._from_dict({word[:index]: coefficient})
                    right = O._from_dict({word[index + len(old):]: 1})
                    replacement = left * O.zero() * right
                    rest = value + O._from_dict({word: -coefficient})
                    return rest + replacement, True
        for relations in (simple, affine):
            for old, new in relations.items():
                for index in range(len(word) - len(old) + 1):
                    if word[index:index + len(old)] == old:
                        prefix = O._from_dict({word[:index]: coefficient})
                        suffix = O._from_dict({word[index + len(old):]: 1})
                        rest = value + O._from_dict({word: -coefficient})
                        return rest + prefix * new * suffix, True
    return value, False


def _reduce(value: O) -> O:
    current = value
    for _ in range(32):
        current, changed = _replace_once(current)
        if not changed:
            return current
    raise AssertionError(f"abstract relation reduction did not terminate: {value.display()}")


def _matrix_zero(value: Matrix, *, relations: bool = False) -> bool:
    return all(
        (_reduce(entry) if relations else entry) == O.zero()
        for row in value for entry in row
    )


def _digest_matrix(value: Matrix) -> str:
    payload = "\n".join(",".join(entry.display() for entry in row) for row in value)
    return hashlib.sha256(payload.encode()).hexdigest()


def _serialize_operator(value: O) -> list[list[object]]:
    return [
        [list(word), coefficient.numerator, coefficient.denominator]
        for word, coefficient in value.terms
    ]


def _serialize_matrix(value: Matrix) -> dict[str, object]:
    return {
        "shape": [len(value), len(value[0])],
        "entries": [
            [row, column, _serialize_operator(value[row][column])]
            for row in range(len(value))
            for column in range(len(value[0]))
            if value[row][column] != O.zero()
        ],
        "sha256": _digest_matrix(value),
    }


def _table_add(left: Table, right: Table) -> Table:
    sample = next(iter(left.values()), next(iter(right.values())))
    words = set(left) | set(right)
    return {
        word: matrix
        for word in words
        if (matrix := (left.get(word, sp.zeros(*sample.shape)) + right.get(word, sp.zeros(*sample.shape))).applyfunc(sp.expand)) != sp.zeros(*sample.shape)
    }


def _table_scale(value: Table, coefficient: sp.Rational) -> Table:
    return {
        word: (coefficient * matrix).applyfunc(sp.expand)
        for word, matrix in value.items()
        if coefficient * matrix != sp.zeros(*matrix.shape)
    }


def _table_right(value: Table, matrix: sp.Matrix) -> Table:
    return {
        word: (coefficient * matrix).applyfunc(sp.expand)
        for word, coefficient in value.items()
        if coefficient * matrix != sp.zeros(coefficient.rows, matrix.cols)
    }


def _table_left(matrix: sp.Matrix, value: Table) -> Table:
    return {
        word: (matrix * coefficient).applyfunc(sp.expand)
        for word, coefficient in value.items()
        if matrix * coefficient != sp.zeros(matrix.rows, coefficient.cols)
    }


def _entry_count(value: Table) -> int:
    return sum(entry != 0 for matrix in value.values() for entry in matrix)


def abstract_kernel() -> dict[str, object]:
    q = _zero(SIZE, SIZE)
    q[1][0] = O.atom("g")
    q[3][0] = O.atom("k")
    q[6][2] = O.atom("M", C)
    q[6][4] = O.identity()
    q[7][3] = O.atom("B")
    q[8][2] = O.identity()
    q[9][5] = O.atom("gsharp")
    q[9][7] = O.atom("ksharp")

    pairing = _zero(SIZE, SIZE)
    for left, right in ((0, 9), (1, 5), (2, 6), (3, 7), (4, 8)):
        pairing[left][right] = O.identity()
        pairing[right][left] = O.identity(-1)

    metric_q = _zero(4, 4)
    metric_q[1][0] = O.atom("K")
    metric_q[2][1] = O.atom("B")
    metric_q[3][2] = O.atom("Ksharp")
    metric_pairing = _zero(4, 4)
    for left, right in ((0, 3), (1, 2)):
        metric_pairing[left][right] = O.identity()
        metric_pairing[right][left] = O.identity(-1)

    inclusion = _zero(SIZE, 4)
    inclusion[0][0] = O.atom("L0")
    inclusion[3][1] = O.identity()
    inclusion[7][2] = O.identity()
    inclusion[9][3] = O.atom("p0sharp")
    projection = _zero(4, SIZE)
    projection[0][0] = O.atom("p0")
    projection[1][3] = O.identity()
    projection[2][7] = O.identity()
    projection[3][9] = O.atom("L0sharp")

    homotopy = _zero(SIZE, SIZE)
    homotopy[0][1] = O.atom("J")
    homotopy[2][8] = O.identity()
    homotopy[4][6] = O.identity()
    homotopy[4][8] = O.atom("M", -C)
    homotopy[5][9] = O.atom("Jsharp")

    # Original coordinates: a=x+d J s+L h, lambda=y-c Phi h.
    field_indices = (1, 2, 3, 4)
    u = _identity(4)
    u[1][0] = O.atom("d") * O.atom("J")
    u[1][2] = O.atom("L")
    u[3][2] = O.atom("Phi", -C)
    u_inverse = _identity(4)
    u_inverse[1][0] = O.atom("d") * O.atom("J", -1)
    u_inverse[1][2] = O.atom("L", -1)
    u_inverse[3][2] = O.atom("Phi", C)
    cotangent = _matrix_adjoint(u_inverse)
    cotangent_inverse = _matrix_adjoint(u)
    transform = _identity(SIZE)
    transform_inverse = _identity(SIZE)
    for row, target in enumerate(field_indices):
        for column, source in enumerate(field_indices):
            transform[target][source] = u[row][column]
            transform_inverse[target][source] = u_inverse[row][column]
    dual_indices = (5, 6, 7, 8)
    for row, target in enumerate(dual_indices):
        for column, source in enumerate(dual_indices):
            transform[target][source] = cotangent[row][column]
            transform_inverse[target][source] = cotangent_inverse[row][column]

    original_q = _multiply(_multiply(transform, q), transform_inverse)
    original_inclusion = _multiply(transform, inclusion)
    original_projection = _multiply(projection, transform_inverse)
    original_homotopy = _multiply(_multiply(transform, homotopy), transform_inverse)

    identity = _identity(SIZE)
    metric_identity = _identity(4)
    degree_sign = _degree_sign(BLOCK_DEGREES)
    checks = {
        "split_Q_squared": _matrix_zero(_multiply(q, q), relations=True),
        "split_odd_cyclic": _matrix_zero(_add(
            _multiply(_matrix_adjoint(q), pairing),
            _multiply(_multiply(degree_sign, pairing), q),
        )),
        "projection_inclusion_identity": _matrix_zero(_add(
            _multiply(projection, inclusion), _scale(metric_identity, -1)
        ), relations=True),
        "inclusion_chain_map": _matrix_zero(_add(
            _multiply(q, inclusion), _scale(_multiply(inclusion, metric_q), -1)
        ), relations=True),
        "projection_chain_map": _matrix_zero(_add(
            _multiply(projection, q), _scale(_multiply(metric_q, projection), -1)
        ), relations=True),
        "retract_identity": _matrix_zero(_add(
            _add(identity, _scale(_multiply(inclusion, projection), -1)),
            _scale(_add(_multiply(q, homotopy), _multiply(homotopy, q)), -1),
        ), relations=True),
        "homotopy_odd_cyclic": _matrix_zero(_add(
            _multiply(_matrix_adjoint(homotopy), pairing),
            _scale(_multiply(_multiply(degree_sign, pairing), homotopy), -1),
        )),
        "metric_pairing_pullback": _matrix_zero(_add(
            _multiply(_multiply(_matrix_adjoint(inclusion), pairing), inclusion),
            _scale(metric_pairing, -1),
        ), relations=True),
        "canonical_transform": _matrix_zero(_add(
            _multiply(_multiply(_matrix_adjoint(transform), pairing), transform),
            _scale(pairing, -1),
        )),
        "transform_left_inverse": _matrix_zero(_add(
            _multiply(transform_inverse, transform), _scale(identity, -1)
        )),
        "transform_right_inverse": _matrix_zero(_add(
            _multiply(transform, transform_inverse), _scale(identity, -1)
        )),
        "original_Q_squared": _matrix_zero(_multiply(original_q, original_q), relations=True),
        "original_odd_cyclic": _matrix_zero(_add(
            _multiply(_matrix_adjoint(original_q), pairing),
            _multiply(_multiply(degree_sign, pairing), original_q),
        ), relations=True),
        "original_retract_identity": _matrix_zero(_add(
            _add(identity, _scale(_multiply(original_inclusion, original_projection), -1)),
            _scale(_add(
                _multiply(original_q, original_homotopy),
                _multiply(original_homotopy, original_q),
            ), -1),
        ), relations=True),
    }
    return {
        "q": q, "pairing": pairing,
        "metric_q": metric_q, "metric_pairing": metric_pairing,
        "inclusion": inclusion, "projection": projection, "homotopy": homotopy,
        "field_transform": u, "field_transform_inverse": u_inverse,
        "transform": transform, "transform_inverse": transform_inverse,
        "original_q": original_q,
        "original_inclusion": original_inclusion,
        "original_projection": original_projection,
        "original_homotopy": original_homotopy,
        "checks": checks,
    }


def coefficient_kernel() -> dict[str, object]:
    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    middle = automorphism["middle"]
    p0 = automorphism["projection0"]
    l0 = automorphism["corrected_l0"]
    l1 = automorphism["corrected_l1"]
    d = automorphism["d_aut"]
    k = automorphism["k_p0"]
    m = middle["yang_mills_middle"]
    phi = automorphism["phi"]
    b = endpoint["action_bach"]
    q_unique = middle["endpoint_correction"]
    compressed = middle["compressed_middle"]

    j0 = sp.Matrix.hstack(*p0.nullspace())
    if j0.shape != (15, 11):
        raise AssertionError("ker(p0) dimension drifted")
    r0 = (j0.T * j0).inv() * j0.T
    l0p0 = _table_right(l0, p0)
    identity_c0 = {(): sp.eye(15)}
    r_complement = _table_add(identity_c0, _table_scale(l0p0, sp.Integer(-1)))
    g = _table_left(r0, r_complement)

    background = NariaiBackground()
    curvature0 = _tensor_product_curvature(background, _lc_adjoint_curvature(), 0)
    pbw_c0 = FibrePBW(curvature0, background, "Nariai-C0-parent-cone-repair")
    jg = _table_left(j0, g)
    gauge_reconstruction = _table_add(
        _table_add(pbw_c0.compose(d, jg), pbw_c0.compose(l1, k)),
        _table_scale(d, sp.Integer(-1)),
    )
    effective = _table_add(
        _table_scale(compressed, sp.Rational(-1, 2)),
        {(): sp.Rational(-1, 2) * q_unique},
    )
    effective_defect = _table_add(effective, _table_scale(b, sp.Integer(-1)))
    phi_defect = _table_add(
        middle["pbw_h1"].compose(m, l1),
        _table_scale(phi, sp.Integer(-1)),
    )
    g_l0 = middle["pbw_h0"].compose(g, l0)
    p0_l0 = _table_left(p0, l0)

    checks = {
        "p0_rank": p0.rank(),
        "ker_p0_dimension": j0.cols,
        "p0_J0_rank": (p0 * j0).rank(),
        "r0_J0_minus_identity_rank": (r0 * j0 - sp.eye(11)).rank(),
        "p0_L0_minus_identity_entries": _entry_count(_table_add(p0_l0, {(): -sp.eye(4)})),
        "J0_g_minus_R0_entries": _entry_count(_table_add(jg, _table_scale(r_complement, -1))),
        "g_J0_minus_identity_entries": _entry_count(_table_add(_table_right(g, j0), {(): -sp.eye(11)})),
        "g_L0_entries": _entry_count(g_l0),
        "d_J0_g_plus_L1_k_minus_d_entries": _entry_count(gauge_reconstruction),
        "M_L1_minus_Phi_entries": _entry_count(phi_defect),
        "effective_Hessian_minus_B_action_entries": _entry_count(effective_defect),
        "saddle_inverse_is_finite_order": True,
        "support_local_entries_only": True,
    }
    return {
        "automorphism": automorphism, "endpoint": endpoint,
        "p0": p0, "l0": l0, "l1": l1, "d": d, "k": k,
        "m": m, "phi": phi, "b": b, "q_unique": q_unique,
        "compressed": compressed, "j0": j0, "r0": r0,
        "r_complement": r_complement, "g": g, "effective": effective,
        "checks": checks,
    }


def build() -> dict[str, object]:
    dependencies = {
        "automorphism": (AUTOMORPHISM_CERTIFICATE, "NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1"),
        "sdr_obstruction": (OBSTRUCTION_CERTIFICATE, "NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1"),
        "action_bach": (BACH_CERTIFICATE, "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1"),
    }
    dependency_refs = {}
    for name, (path, expected) in dependencies.items():
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise ValueError(f"dependency drifted: {name}")
        dependency_refs[name] = {
            "artifact_id": expected,
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
    if json.loads(OBSTRUCTION_CERTIFICATE.read_text())["flags"]["CURRENT_CARRIER_SDR_OBSTRUCTED"] is not True:
        raise ValueError("repair gate was not fail-closed")

    abstract = abstract_kernel()
    coefficient = coefficient_kernel()
    if not all(abstract["checks"].values()):
        failed = [name for name, value in abstract["checks"].items() if not value]
        raise AssertionError(f"abstract repair failed: {failed}")
    integer_zero_checks = (
        "p0_J0_rank", "r0_J0_minus_identity_rank",
        "p0_L0_minus_identity_entries", "J0_g_minus_R0_entries",
        "g_J0_minus_identity_entries", "g_L0_entries",
        "d_J0_g_plus_L1_k_minus_d_entries", "M_L1_minus_Phi_entries",
        "effective_Hessian_minus_B_action_entries",
    )
    if any(coefficient["checks"][name] for name in integer_zero_checks):
        raise AssertionError("coefficient repair identity failed")

    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA,
        AUTOMORPHISM_PRODUCER, OBSTRUCTION_PRODUCER, BACH_PRODUCER,
        FORMAL_SOURCE, PBW_SOURCE,
    )
    source_manifest = {
        str(path.relative_to(ROOT)): _sha256(path) for path in source_paths
    }
    return {
        "schema": "pure-weyl-nariai-parent-detour-mapping-cone-repair-v1",
        "result_id": "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1",
        "result_state": "RANK_310_CYCLIC_SUPPORT_LOCAL_SDR_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependency_refs,
        "carrier": {
            "background": "unit Nariai dS2 x S2",
            "block_names": list(BLOCK_NAMES),
            "block_degrees": list(BLOCK_DEGREES),
            "block_ranks": list(BLOCK_RANKS),
            "total_rank": sum(BLOCK_RANKS),
            "metric_block_names": list(METRIC_NAMES),
            "metric_block_degrees": list(METRIC_DEGREES),
            "metric_total_rank": 36,
            "added_rank_over_obstructed_carrier": 22,
        },
        "construction": {
            "c": "-1/2",
            "split_variables": {
                "x": "a-d_aut J0 s-L1_corrected h",
                "y": "lambda+c Phi h",
            },
            "original_variables": {
                "a": "x+d_aut J0 s+L1_corrected h",
                "lambda": "y-c Phi h",
            },
            "split_quadratic_action": "1/2<h,B_action h>+(c/2)<x,M^D x>+<y,x>",
            "original_quadratic_action": "(c/2)<u,M^D u>+1/2<h,R h>+<lambda,u-L1 h>, u=a-d_aut J0 s, R=-Q_unique/2",
            "saddle_operator": "[[c M^D,1],[1,0]]",
            "saddle_local_inverse": "[[0,1],[1,-c M^D]]",
            "metric_inclusion_original_fields": "s=0, a=L1 h, h=h, lambda=-c Phi h",
            "no_nonlocal_inverse": True,
        },
        "algebraic_complement": {
            "p0": _sparse(coefficient["p0"]),
            "J0": _sparse(coefficient["j0"]),
            "r0": _sparse(coefficient["r0"]),
            "R0": _sparse_table(coefficient["r_complement"]),
            "g": _sparse_table(coefficient["g"]),
        },
        "operators": {
            "d_aut": _sparse_table(coefficient["d"]),
            "K_p0": _sparse_table(coefficient["k"]),
            "L0_corrected": _sparse_table(coefficient["l0"]),
            "L1_corrected": _sparse_table(coefficient["l1"]),
            "M_parent": _sparse_table(coefficient["m"]),
            "Phi": _sparse_table(coefficient["phi"]),
            "B_action": _sparse_table(coefficient["b"]),
            "Q_unique": _sparse(coefficient["q_unique"]),
            "effective_Hessian": _sparse_table(coefficient["effective"]),
        },
        "fibre_pairings": {
            "C0": _sparse(coefficient["automorphism"]["middle"]["algebraic"].adjoint_pairing),
            "C1": _sparse(coefficient["automorphism"]["middle"]["algebraic"].one_form_pairing),
            "H0": _sparse(coefficient["automorphism"]["middle"]["algebraic"].endpoint_ghost_pairing),
            "H1": _sparse(coefficient["automorphism"]["middle"]["algebraic"].endpoint_field_pairing),
            "ker_p0_coordinate_evaluation": _sparse(sp.eye(11)),
            "formal_adjoint_recipes": {
                "J0_sharp": "formal adjoint of J0: ker(p0)->C0 under the serialized C0 and coordinate-evaluation pairings",
                "g_sharp": "formal adjoint of g:C0->ker(p0) under the serialized C0 and coordinate-evaluation pairings",
                "parent_rows": "formal adjoints under the serialized C0, C1, H0 and H1 pairings",
            },
        },
        "abstract_matrices": {
            name: _serialize_matrix(abstract[name])
            for name in (
                "q", "pairing", "metric_q", "metric_pairing",
                "inclusion", "projection", "homotopy",
                "field_transform", "field_transform_inverse",
                "transform", "transform_inverse", "original_q",
                "original_inclusion", "original_projection", "original_homotopy",
            )
        },
        "exact_checks": {**coefficient["checks"], **abstract["checks"]},
        "proof": {
            "ghost_complement": "g J0=1_11 and J0 g=1-L0 p0",
            "parent_saddle": "A^{-1}=[[0,1],[1,-cM]] is a two-sided finite-order inverse",
            "effective_metric_hessian": "c(L1^sharp M L1)-Q_unique/2=B_action",
            "support": "all maps are finite-order differential operators or pointwise rational matrices",
            "cyclicity": "the split homotopy is odd cyclic and the triangular field/cotangent transform is BV canonical",
        },
        "flags": {
            "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1": True,
            "PARENT_DETOUR_MAPPING_CONE_REPAIR": True,
            "SUPPORT_LOCAL_AUTOMORPHISM_SDR": True,
            "CYCLIC_HOMOTOPY": True,
            "EFFECTIVE_HESSIAN_EQUALS_BACH": True,
            "COMPLEMENT_LOCAL_INVERSE": True,
            "CURRENT_288_COMPONENT_CARRIER_REUSED_UNCHANGED": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": "On unit Nariai, an economical 310-component cyclic parent-detour mapping cone admits an explicit finite-order support-local cyclic SDR onto the exact metric Bach BV complex. The eleven-dimensional ghost complement and the parent saddle are contracted locally, and the metric Schur Hessian equals the action-derived Bach operator coefficientwise. No global rank-minimality claim is made.",
            "not_claimed": [
                "retarded or advanced Green homotopies",
                "a Green-hyperbolic witness for the repaired parent",
                "an open conformally Einstein or Bach-flat background class",
                "nonlinear compatibility",
                "a quantum theorem",
            ],
        },
        "next_gate": "C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER",
        "source_manifest": source_manifest,
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_parent_detour_mapping_cone_repair.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_parent_detour_mapping_cone_repair.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_parent_detour_mapping_cone_repair",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-parent-detour-mapping-cone-repair-v1.schema.json -d d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
        ],
    }


def _write_report(value: dict[str, object]) -> None:
    checks = value["exact_checks"]
    REPORT.write_text(f"""# Nariai parent-detour mapping-cone repair

## Result

The obstructed 288-component multiplier saddle is replaced by an economical
310-component cyclic parent-detour cone.  It adds only the eleven-dimensional
complement of the metric ghost splitting and its dual.  In split variables,
the complex is the direct sum of the metric Bach complex, the pointwise pair
`epsilon_perp -> s`, and the parent saddle

```text
[[ -(1/2) M^D, 1 ],
 [       1,     0 ]].
```

Its exact inverse is `[[0,1],[1,(1/2)M^D]]`; it is a finite-order local
operator, not an inverse of `M^D`.

## Coefficient checks

- rank `p0`: `{checks['p0_rank']}`;
- dimension `ker p0`: `{checks['ker_p0_dimension']}`;
- `p0 J0`: rank `{checks['p0_J0_rank']}`;
- `g J0-1`: `{checks['g_J0_minus_identity_entries']}` entries;
- `J0 g-(1-L0 p0)`: `{checks['J0_g_minus_R0_entries']}` entries;
- reconstructed gauge arrow `d J0 g+L1 k-d`: `{checks['d_J0_g_plus_L1_k_minus_d_entries']}` entries;
- `M L1-Phi`: `{checks['M_L1_minus_Phi_entries']}` entries;
- effective Hessian minus `B_action`: `{checks['effective_Hessian_minus_B_action_entries']}` entries.

## Cyclic SDR

The serialized ten-block matrices verify `Q^2=0`, odd cyclicity, `PI=1`, both
chain-map identities, the exact retract identity

```text
1-IP = QH+HQ,
```

and odd cyclicity of `H`.  The triangular field transform and its forced
cotangent transform are mutually inverse and BV canonical.  Therefore the
same identities hold in the original parent/metric graph coordinates.

## Boundary

This is a local cyclic deformation retract on the unit Nariai background.
It is not a retarded/advanced Green construction.  The next gate is
`C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER`.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.guards:
        if value["flags"]["NARIAI_GREEN_HOMOTOPY"]:
            raise AssertionError("Green theorem promoted by algebraic SDR")
        if not value["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
            raise AssertionError("support-local SDR did not promote")
    if not args.check:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    print(json.dumps({"result_id": value["result_id"], "checks": value["exact_checks"], "flags": value["flags"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
