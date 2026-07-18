#!/usr/bin/env python3
"""Jet-aware first variation of the transverse Nariai BGG/YM middle."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _algebraic,
    _induced_harmonic_curvature,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.first_variation_pbw import (
    FirstVariationPBW,
    LinearizedOperator,
    lin_add,
    lin_scale,
    zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    curvature_incidence,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _derivative_rows,
    _load,
)
from d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation import (
    exact_variation,
)
from d_quotient_classical.causal_transfer.nariai_transverse_pbw_curvature_jet_gate import (
    _PerturbedBackground,
    _lc_adjoint_curvature,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-jet-aware-middle-schur-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-jet-aware-middle-schur-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_jet_aware_middle_schur_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_jet_aware_middle_schur_variation.py"
PBW_GATE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json"
ALGEBRAIC_GATE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
AUTOMORPHISM_CERT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1.json"
PBW_LINEAR_SOURCE = HERE / "first_variation_pbw.py"


Table = dict[tuple[int, ...], sp.Matrix]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean(table: Table) -> Table:
    return {
        word: expanded
        for word, matrix in table.items()
        if (expanded := matrix.applyfunc(sp.expand)) != sp.zeros(*matrix.shape)
    }


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [[r, c, str(v)] for (r, c), v in sorted(matrix.todok().items())],
        "sha256": hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest(),
    }


def _table(table: Table) -> dict[str, Any]:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return {
        "orders": sorted({len(word) for word in table}),
        "nonzero_coefficients": sum(v != 0 for matrix in table.values() for v in matrix),
        "entries": [
            {"word": list(word), "matrix": _sparse(table[word])}
            for word in sorted(table)
        ],
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def _coefficient(matrix: sp.Matrix, symbol: sp.Symbol, order: int) -> sp.Matrix:
    return matrix.applyfunc(lambda value: sp.expand(value).coeff(symbol, order))


def _curvature_coefficients(curvature, symbol: sp.Symbol, order: int):
    return tuple(
        tuple(_coefficient(curvature[left][right], symbol, order) for right in range(4))
        for left in range(4)
    )


def _deserialize(record: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(*record["shape"])
    for row, column, value in record["entries"]:
        matrix[row, column] = sp.sympify(value)
    return matrix


def _right(table: LinearizedOperator, matrix: sp.Matrix) -> LinearizedOperator:
    return (
        _clean({word: value * matrix for word, value in table[0].items()}),
        _clean({word: value * matrix for word, value in table[1].items()}),
    )


def _jet_factor(word: tuple[int, ...]) -> sp.Expr:
    if any(axis != 0 for axis in word):
        return sp.Integer(0)
    return sp.Integer(1) if len(word) % 2 == 0 else sp.sqrt(2)


def _spin_connection_variation() -> tuple[sp.Matrix, ...]:
    coefficients = (sp.Integer(0), -2 * sp.sqrt(2) / 3, sp.sqrt(2), sp.sqrt(2))
    output = []
    for axis, coefficient in enumerate(coefficients):
        matrix = sp.zeros(4)
        if axis:
            matrix[0, axis] = coefficient
            matrix[axis, 0] = coefficient
        if matrix.T * NariaiBackground.metric + NariaiBackground.metric * matrix != sp.zeros(4):
            raise AssertionError("spin variation left so(1,3)")
        output.append(matrix)
    return tuple(output)


def _adjoint_action(matrix4: sp.Matrix) -> sp.Matrix:
    _, basis = _adjoint_basis()
    from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
        _coordinate_map,
    )

    embedded, left_inverse = _coordinate_map(basis)
    standard = sp.zeros(6)
    standard[1:5, 1:5] = matrix4
    columns = []
    for generator in basis:
        commutator = standard * generator - generator * standard
        coordinates = left_inverse * commutator.reshape(36, 1)
        if embedded * coordinates != commutator.reshape(36, 1):
            raise AssertionError("spin variation escaped adjoint tractor representation")
        columns.append(coordinates)
    return sp.Matrix.hstack(*columns)


def _bundle_connection_variation(
    form_degree: int,
    spin: tuple[sp.Matrix, ...],
) -> tuple[sp.Matrix, ...]:
    pairs = tuple((left, right) for left in range(4) for right in range(left + 1, 4))
    if form_degree == 0:
        form_components = ((),)
    elif form_degree == 1:
        form_components = tuple((axis,) for axis in range(4))
    elif form_degree == 2:
        form_components = pairs
    else:
        raise ValueError(form_degree)
    lookup = {component: index for index, component in enumerate(form_components)}
    rank = len(form_components) * 15
    output = []
    for derivative in range(4):
        matrix = sp.zeros(rank)
        adjoint = _adjoint_action(spin[derivative])
        covector = -spin[derivative].T
        for form_index, slots in enumerate(form_components):
            for adjoint_input in range(15):
                for adjoint_output in range(15):
                    value = adjoint[adjoint_output, adjoint_input]
                    if value:
                        matrix[15 * form_index + adjoint_output, 15 * form_index + adjoint_input] += value
                for position, old_axis in enumerate(slots):
                    for new_axis in range(4):
                        value = covector[old_axis, new_axis]
                        if not value:
                            continue
                        changed = list(slots)
                        changed[position] = new_axis
                        if len(set(changed)) != len(changed):
                            continue
                        inversions = sum(
                            changed[a] > changed[b]
                            for a in range(len(changed))
                            for b in range(a + 1, len(changed))
                        )
                        input_form = lookup[tuple(sorted(changed))]
                        matrix[15 * form_index + adjoint_input, 15 * input_form + adjoint_input] += (-1) ** inversions * value
        output.append(matrix)
    return tuple(output)


def _first_curvature_jet(
    base_curvature,
    delta_curvature,
    bundle_connection: tuple[sp.Matrix, ...],
    spin: tuple[sp.Matrix, ...],
    derivative: int,
    left: int,
    right: int,
) -> sp.Matrix:
    partial = sp.sqrt(2) * delta_curvature[left][right] if derivative == 0 else sp.zeros(*delta_curvature[left][right].shape)
    connection = bundle_connection[derivative]
    value = partial + connection * base_curvature[left][right] - base_curvature[left][right] * connection
    for changed in range(4):
        value -= spin[derivative][changed, left] * base_curvature[changed][right]
        value -= spin[derivative][changed, right] * base_curvature[left][changed]
    return value.applyfunc(sp.expand)


def _pbw_layers() -> dict[str, FirstVariationPBW]:
    base = middle_fixture()
    algebraic = base["algebraic"]
    screen = base["screen"]
    epsilon = _PerturbedBackground.epsilon
    perturbed_lc = _lc_adjoint_curvature(_PerturbedBackground)
    perturbed = {
        "C0": _tensor_product_curvature(_PerturbedBackground, perturbed_lc, 0),
        "C1": _tensor_product_curvature(_PerturbedBackground, perturbed_lc, 1),
        "C2": _tensor_product_curvature(_PerturbedBackground, perturbed_lc, 2),
    }
    perturbed["H0"] = _induced_harmonic_curvature(
        perturbed["C0"], algebraic.i0, screen.harmonic_p0
    )
    perturbed["H1"] = _induced_harmonic_curvature(
        perturbed["C1"], algebraic.i1, screen.harmonic_p1
    )
    base_pbw = {
        "C0": base["pbw_h0"].__class__(
            _curvature_coefficients(perturbed["C0"], epsilon, 0),
            NariaiBackground(),
            "base-C0-jet-aware",
        ),
        "C1": FibrePBW(
            _curvature_coefficients(perturbed["C1"], epsilon, 0),
            NariaiBackground(),
            "base-C1-jet-aware",
        ),
        "C2": FibrePBW(
            _curvature_coefficients(perturbed["C2"], epsilon, 0),
            NariaiBackground(),
            "base-C2-jet-aware",
        ),
        "H0": base["pbw_h0"],
        "H1": base["pbw_h1"],
    }
    # Check that rebuilding the parent base curvatures did not change the
    # already certified locally symmetric PBW representation.
    if base_pbw["C0"].curvature != _curvature_coefficients(perturbed["C0"], epsilon, 0):
        raise AssertionError("C0 base curvature reconstruction failed")
    base_covector = tuple(
        tuple(NariaiBackground.covector_commutator(left, right) for right in range(4))
        for left in range(4)
    )
    delta_covector = tuple(
        tuple(
            _coefficient(_PerturbedBackground.covector_commutator(left, right), epsilon, 1)
            for right in range(4)
        )
        for left in range(4)
    )
    spin = _spin_connection_variation()
    bundle_connections = {
        "C0": _bundle_connection_variation(0, spin),
        "C1": _bundle_connection_variation(1, spin),
        "C2": _bundle_connection_variation(2, spin),
    }
    bundle_connections["H0"] = tuple(
        screen.harmonic_p0 * bundle_connections["C0"][axis] * algebraic.i0
        for axis in range(4)
    )
    bundle_connections["H1"] = tuple(
        screen.harmonic_p1 * bundle_connections["C1"][axis] * algebraic.i1
        for axis in range(4)
    )
    covector_connection = tuple(-matrix.T for matrix in spin)

    def jet_callback(base_curvature, delta_curvature, connection):
        def value(left: int, right: int, word: tuple[int, ...]) -> sp.Matrix:
            if not word:
                return delta_curvature[left][right]
            if len(word) == 1:
                return _first_curvature_jet(
                    base_curvature, delta_curvature, connection, spin,
                    word[0], left, right,
                )
            if all(axis == 0 for axis in word):
                return _jet_factor(word) * delta_curvature[left][right]
            return sp.zeros(*delta_curvature[left][right].shape)
        return value

    covector_jet = jet_callback(base_covector, delta_covector, covector_connection)
    return {
        name: FirstVariationPBW(
            base_pbw[name],
            _curvature_coefficients(perturbed[name], epsilon, 1),
            delta_covector,
            _jet_factor,
            f"Nariai-transverse-{name}",
            delta_fibre_jet=jet_callback(
                _curvature_coefficients(perturbed[name], epsilon, 0),
                _curvature_coefficients(perturbed[name], epsilon, 1),
                bundle_connections[name],
            ),
            delta_covector_jet=covector_jet,
        )
        for name in ("C0", "C1", "C2", "H0", "H1")
    }


def _algebraic_lin(matrix: sp.Matrix, delta: sp.Matrix | None = None) -> LinearizedOperator:
    return _algebraic(matrix), ({} if delta is None or delta == sp.zeros(*delta.shape) else _algebraic(delta))


def _curvature_action_from_square(square: LinearizedOperator) -> LinearizedOperator:
    eta = NariaiBackground.metric
    pairs = tuple((left, right) for left in range(4) for right in range(left + 1, 4))

    def build(table: Table) -> sp.Matrix:
        raw = table.get((), sp.zeros(90, 15))
        blocks = {
            pair: raw[15 * index : 15 * (index + 1), :]
            for index, pair in enumerate(pairs)
        }

        def curvature(left: int, right: int) -> sp.Matrix:
            if left == right:
                return sp.zeros(15)
            return blocks[(left, right)] if left < right else -blocks[(right, left)]

        return sp.Matrix.vstack(*(
            sp.Matrix.hstack(*(
                eta[source, source] * curvature(target, source)
                for source in range(4)
            ))
            for target in range(4)
        ))

    return _algebraic(build(square[0])), _algebraic(build(square[1]))


def _solve_splitting_variation(
    defect: Table,
    d_aut_base: Table,
    first_bgg_base: Table,
    projection0: sp.Matrix,
    projection1: sp.Matrix,
) -> tuple[sp.Matrix, sp.Matrix, dict[str, Any]]:
    """Solve ``defect+d_aut c0-c1 K=0`` for algebraic ``c0,c1``."""

    correction1 = sp.zeros(60, 9)
    correction0_candidates: dict[int, list[sp.Matrix]] = {
        adjoint: [] for adjoint in range(15)
    }
    parameter_counts = []
    inconsistent_rows = []
    for row in range(60):
        form = row // 15
        adjoint = row % 15
        transverse = [axis for axis in range(4) if axis != form]
        k_stack = sp.Matrix.hstack(*(
            first_bgg_base.get((axis,), sp.zeros(9, 4))
            for axis in transverse
        ))
        defect_stack = sp.Matrix.hstack(*(
            defect.get((axis,), sp.zeros(60, 4))[row, :]
            for axis in transverse
        ))
        try:
            solution, parameters = k_stack.T.gauss_jordan_solve(defect_stack.T)
        except ValueError:
            inconsistent_rows.append(row)
            continue
        parameter_counts.append(parameters.rows)
        if parameters.rows:
            solution = solution.subs({parameter: 0 for parameter in parameters})
        correction1[row, :] = solution.T
        correction0_candidates[adjoint].append(
            correction1[row, :]
            * first_bgg_base.get((form,), sp.zeros(9, 4))
            - defect.get((form,), sp.zeros(60, 4))[row, :]
        )
    if inconsistent_rows:
        raise AssertionError(f"splitting variation inconsistent in rows {inconsistent_rows}")
    correction0 = sp.zeros(15, 4)
    cross_form_defects = []
    for adjoint, candidates in correction0_candidates.items():
        correction0[adjoint, :] = candidates[0]
        for form, candidate in enumerate(candidates[1:], start=1):
            difference = candidate - candidates[0]
            for column, value in enumerate(difference):
                if value != 0:
                    cross_form_defects.append([adjoint, form, column, str(value)])
    if cross_form_defects:
        raise AssertionError(f"splitting variation has cross-form defects: {cross_form_defects[:5]}")
    algebraic_defect = (
        defect.get((), sp.zeros(60, 4))
        + d_aut_base.get((), sp.zeros(60, 15)) * correction0
        - correction1 * first_bgg_base.get((), sp.zeros(9, 4))
    )
    projection0_defect = projection0 * correction0
    projection1_defect = projection1 * correction1
    if projection0_defect != sp.zeros(4) or projection1_defect != sp.zeros(9):
        raise AssertionError("splitting variation violates normalized projection")
    return correction0, correction1, {
        "parameter_counts": parameter_counts,
        "inconsistent_rows": inconsistent_rows,
        "cross_form_defects": cross_form_defects,
        "algebraic_residual": _sparse(algebraic_defect),
        "projection0_defect": _sparse(projection0_defect),
        "projection1_defect": _sparse(projection1_defect),
    }


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    middle = middle_fixture()
    automorphism = automorphism_fixture()
    algebraic = middle["algebraic"]
    screen = middle["screen"]
    pbw = _pbw_layers()

    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    rho = tuple(NariaiBackground.metric[axis, axis] * k_actions[axis] / 6 for axis in range(4))
    rho0 = sp.Matrix.vstack(*rho)
    rho1_rows = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = rho[left]
            block[:, 15 * left : 15 * (left + 1)] = -rho[right]
            rho1_rows.append(block)
    rho1 = sp.Matrix.vstack(*rho1_rows)
    derivative0, derivative1 = _derivative_rows()
    delta0 = lin_add(_algebraic_lin(rho0), zero_variation(derivative0))
    delta1 = lin_add(_algebraic_lin(rho1), zero_variation(derivative1))
    total0 = lin_add(_algebraic_lin(screen.cohomology_d0), delta0)
    total1 = lin_add(_algebraic_lin(screen.cohomology_d1), delta1)

    n0 = pbw["C0"].compose(_algebraic_lin(screen.q1), delta0)
    n1 = pbw["C1"].compose(_algebraic_lin(screen.q2), delta1)
    i0_alg = _algebraic_lin(algebraic.i0)
    i1_alg = _algebraic_lin(algebraic.i1)
    n0_i0 = pbw["H0"].compose(n0, i0_alg)
    n1_i1 = pbw["H1"].compose(n1, i1_alg)
    inclusion0 = lin_add(
        i0_alg,
        lin_scale(n0_i0, -1),
        pbw["H0"].compose(n0, n0_i0),
    )
    inclusion1 = lin_add(
        i1_alg,
        lin_scale(n1_i1, -1),
        pbw["H1"].compose(n1, n1_i1),
    )
    corrected_l0 = lin_add(inclusion0, _algebraic_lin(
        automorphism["corrected_l0"].get((), sp.zeros(15, 4))
        - middle["inclusion0"].get((), sp.zeros(15, 4))
    ))
    corrected_l1 = lin_add(inclusion1, _algebraic_lin(
        automorphism["corrected_l1"].get((), sp.zeros(60, 9))
        - middle["inclusion1"].get((), sp.zeros(60, 9))
    ))
    first_bgg = pbw["H0"].compose(
        _algebraic_lin(screen.harmonic_p1),
        pbw["H0"].compose(total0, inclusion0),
    )

    incidence0 = curvature_incidence()["incidence"]
    incidence1 = _deserialize(exact_variation()["delta_curvature_incidence"])
    p0 = screen.harmonic_p0
    incidence_projected = _algebraic_lin(incidence0 * p0, incidence1 * p0)
    d_aut = lin_add(total0, lin_scale(incidence_projected, -1))
    k_p0 = _right(first_bgg, p0)
    preliminary_first_square = lin_add(
        pbw["H0"].compose(d_aut, corrected_l0),
        lin_scale(pbw["H0"].compose(corrected_l1, first_bgg), -1),
    )
    if preliminary_first_square[0]:
        raise AssertionError("base corrected first square drifted")
    splitting_dot0, splitting_dot1, splitting_solve = _solve_splitting_variation(
        preliminary_first_square[1],
        d_aut[0],
        first_bgg[0],
        screen.harmonic_p0,
        screen.harmonic_p1,
    )
    corrected_l0 = lin_add(corrected_l0, ({}, _algebraic(splitting_dot0)))
    corrected_l1 = lin_add(corrected_l1, ({}, _algebraic(splitting_dot1)))
    splitting_residual = _deserialize(splitting_solve["algebraic_residual"])
    automorphism_jet_correction = -splitting_residual * p0
    d_aut = lin_add(d_aut, ({}, _algebraic(automorphism_jet_correction)))
    first_square = lin_add(
        pbw["H0"].compose(d_aut, corrected_l0),
        lin_scale(pbw["H0"].compose(corrected_l1, first_bgg), -1),
    )

    normal_square = pbw["C0"].compose(total1, total0)
    curvature_action = _curvature_action_from_square(normal_square)
    eta = NariaiBackground.metric
    pairs = tuple((left, right) for left in range(4) for right in range(left + 1, 4))
    two_form_metric = sp.diag(*(eta[left, left] * eta[right, right] for left, right in pairs))
    two_form_pairing = sp.kronecker_product(two_form_metric, algebraic.adjoint_pairing)
    total1_sharp = pbw["C2"].formal_adjoint(
        total1, algebraic.one_form_pairing, two_form_pairing
    )
    rough_middle = pbw["C1"].compose(total1_sharp, total1)
    yang_mills_middle = lin_add(rough_middle, lin_scale(curvature_action, -1))
    parent_yang_mills_identity = pbw["C0"].compose(yang_mills_middle, total0)
    parent_requested = {
        name: sorted(layer.requested_jet_words)
        for name, layer in pbw.items()
    }
    phi = pbw["H1"].compose(yang_mills_middle, corrected_l1)
    shifted_chain = lin_add(
        pbw["C0"].compose(yang_mills_middle, d_aut),
        lin_scale(pbw["C0"].compose(phi, k_p0), -1),
    )

    inclusion1_sharp = pbw["C1"].formal_adjoint(
        inclusion1,
        algebraic.endpoint_field_pairing,
        algebraic.one_form_pairing,
    )
    compressed_middle = pbw["H1"].compose(
        inclusion1_sharp,
        pbw["H1"].compose(yang_mills_middle, inclusion1),
    )

    for name, operator in (
        ("first_square", first_square),
        ("parent_yang_mills_identity", parent_yang_mills_identity),
    ):
        if operator[0] or operator[1]:
            by_word = {
                str(word): sum(value != 0 for value in matrix)
                for word, matrix in operator[1].items()
            }
            raise AssertionError(
                f"jet-aware {name} failed: base={sum(v != 0 for m in operator[0].values() for v in m)}, "
                f"delta={sum(v != 0 for m in operator[1].values() for v in m)}, words={by_word}"
            )

    frozen = json.loads(PBW_GATE.read_text())["exact_data"]["frozen_parallel_PBW_audit"]["variations"]
    frozen_compressed_hash = frozen["compressed_middle"]["sha256"]
    true_compressed_hash = _table(compressed_middle[1])["sha256"]
    if true_compressed_hash == frozen_compressed_hash:
        raise AssertionError("curvature-jet Leibniz terms did not change the compressed middle")

    # The existing base Schur correction remains exact at epsilon=0.  Audit the
    # differentiated gauge equation before choosing an ansatz for Q-dot.  A
    # purely algebraic Q-dot can change only first-order terms in Q-dot K, so
    # any surviving word of length other than one is an exact obstruction to
    # that ansatz (not to a differential Schur correction).
    q0 = middle["endpoint_correction"]
    schur_without_qdot = lin_add(compressed_middle, _algebraic_lin(q0))
    gauge_without_qdot = pbw["H0"].compose(schur_without_qdot, first_bgg)
    if gauge_without_qdot[0]:
        raise AssertionError("base Schur gauge identity drifted")
    non_algebraic_orders = sorted(
        word for word in gauge_without_qdot[1] if len(word) != 1
    )
    if not non_algebraic_orders:
        raise AssertionError("expected differential Schur obstruction disappeared")

    requested = {
        name: sorted(layer.requested_jet_words)
        for name, layer in pbw.items()
    }
    unsupported_requested = {
        name: [word for word in words if len(word) > 1 and any(axis != 0 for axis in word)]
        for name, words in requested.items()
    }
    unsupported_requested = {
        name: words for name, words in unsupported_requested.items() if words
    }
    unsupported_parent_requested = {
        name: [word for word in words if len(word) > 1 and any(axis != 0 for axis in word)]
        for name, words in parent_requested.items()
    }
    unsupported_parent_requested = {
        name: words for name, words in unsupported_parent_requested.items() if words
    }
    if unsupported_parent_requested:
        raise AssertionError(
            f"parent identity requested unsupported curvature jets: {unsupported_parent_requested}"
        )

    return {
        "jet_model": {
            "curvature_variation": "exact first covariant jets from the moving-frame variation; repeated time jets from delta R(t)=sinh(t) delta R(t_star)",
            "accepted_covariant_jet_words": "empty word, every length-one word, and repeated time-axis words",
            "jet_factor_even": "1",
            "jet_factor_odd": "sqrt(2)",
            "maximum_jet_order_used": 3,
        },
        "operator_variations": {
            "requested_curvature_jet_words": {
                name: [list(word) for word in words]
                for name, words in requested.items()
            },
            "parent_identity_requested_curvature_jet_words": {
                name: [list(word) for word in words]
                for name, words in parent_requested.items()
            },
            "unsupported_parent_identity_curvature_jet_words": {},
            "unsupported_requested_curvature_jet_words": {
                name: [list(word) for word in words]
                for name, words in unsupported_requested.items()
            },
            "splitting_correction0": _sparse(splitting_dot0),
            "splitting_correction1": _sparse(splitting_dot1),
            "splitting_solve": splitting_solve,
            "automorphism_curvature_jet_correction": _sparse(automorphism_jet_correction),
            "corrected_L0": _table(corrected_l0[1]),
            "corrected_L1": _table(corrected_l1[1]),
            "first_BGG": _table(first_bgg[1]),
            "normal_tractor_square": _table(normal_square[1]),
            "Yang_Mills_middle": _table(yang_mills_middle[1]),
            "Phi": _table(phi[1]),
            "compressed_middle": _table(compressed_middle[1]),
        },
        "identity_defects": {
            "corrected_first_square_base": _table(first_square[0]),
            "corrected_first_square_variation": _table(first_square[1]),
            "parent_YM_base": _table(parent_yang_mills_identity[0]),
            "parent_YM_variation": _table(parent_yang_mills_identity[1]),
            "shifted_chain_base": _table(shifted_chain[0]),
            "shifted_chain_variation": _table(shifted_chain[1]),
        },
        "frozen_parallel_comparison": {
            "frozen_compressed_sha256": frozen_compressed_hash,
            "jet_aware_compressed_sha256": true_compressed_hash,
            "coefficients_differ": True,
            "frozen_nonzero_coefficients": frozen["compressed_middle"]["nonzero_coefficients"],
            "jet_aware_nonzero_coefficients": _table(compressed_middle[1])["nonzero_coefficients"],
        },
        "differential_schur_gate": {
            "unrepaired_gauge_defect": _table(gauge_without_qdot[1]),
            "non_algebraically_repairable_orders": [
                list(word) for word in non_algebraic_orders
            ],
            "algebraic_qdot_sufficient": False,
            "required_correction_order_lower_bound": 1,
            "action_derived_equality_checked": False,
            "cyclicity_checked_with_authoritative_Hom_adjoint": False,
        },
    }


def build() -> dict[str, Any]:
    dependencies = {}
    for name, path, expected in (
        ("curvature_jet_gate", PBW_GATE, "NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1"),
        ("algebraic_pairing_gate", ALGEBRAIC_GATE, "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1"),
        ("base_automorphism_complex", AUTOMORPHISM_CERT, "NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise AssertionError(f"dependency drifted: {name}")
        dependencies[name] = {"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": _sha(path)}
    exact = exact_data()
    checks = {
        "jet_aware_first_square_variation_zero": exact["identity_defects"]["corrected_first_square_variation"]["nonzero_coefficients"] == 0,
        "jet_aware_parent_YM_variation_zero": exact["identity_defects"]["parent_YM_variation"]["nonzero_coefficients"] == 0,
        "jet_aware_shifted_chain_variation_nonzero": exact["identity_defects"]["shifted_chain_variation"]["nonzero_coefficients"] > 0,
        "jet_terms_change_compressed_middle": exact["frozen_parallel_comparison"]["coefficients_differ"],
        "parent_curvature_jet_coverage_complete": not exact["operator_variations"]["unsupported_parent_identity_curvature_jet_words"],
        "compressed_curvature_jet_coverage_incomplete": bool(exact["operator_variations"]["unsupported_requested_curvature_jet_words"]),
        "algebraic_schur_variation_rejected": not exact["differential_schur_gate"]["algebraic_qdot_sufficient"],
        "action_schur_not_promoted": not exact["differential_schur_gate"]["action_derived_equality_checked"],
    }
    return {
        "schema": "nariai-transverse-jet-aware-middle-schur-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1",
        "result_state": "JET_AWARE_BGG_AND_PARENT_YM_MIDDLE_EXACT_SHIFTED_CHAIN_AND_DIFFERENTIAL_SCHUR_OPEN",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "exact_data": exact,
        "exact_checks": checks,
        "flags": {
            "TRANSVERSE_JET_AWARE_PBW_VARIATION": True,
            "TRANSVERSE_BGG_FIRST_SQUARE_VARIATION": True,
            "TRANSVERSE_YANG_MILLS_MIDDLE_VARIATION": True,
            "TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE": False,
            "TRANSVERSE_SHIFTED_CHAIN_VARIATION": False,
            "TRANSVERSE_ALGEBRAIC_SCHUR_VARIATION": False,
            "TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION": False,
            "TRANSVERSE_CYCLIC_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_DIFFERENTIAL_SCHUR_AND_RANK_310_SDR_VARIATION",
        "claim_boundary": "This certificate implements the first-variation PBW Leibniz rule with complete curvature-jet coverage for the corrected BGG first square and Yang-Mills parent identity at first order along the transverse Nariai tangent. The later compressed endpoint calculation requests mixed spatial curvature jets of orders two and three that are not yet derived, so its coefficients are diagnostic only. Within that diagnostic truncation the shifted-chain identity retains a defect and a purely algebraic Schur correction is insufficient. A complete higher-jet calculation, differential action-derived cyclic Schur correction, rank-310 SDR variation, and transverse causal transfer remain open.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (
                Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA,
                PBW_LINEAR_SOURCE,
            )
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_jet_aware_middle_schur_variation.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_jet_aware_middle_schur_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-jet-aware-middle-schur-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    comparison = data["frozen_parallel_comparison"]
    return f"""# Transverse Nariai jet-aware middle/Schur variation

The PBW rewrite rule is differentiated with covariant curvature jets.  At
first order, every prefix derivative that lands on the varied curvature
contributes its Leibniz term.  The certified parent operators satisfy
coefficientwise

\\[
\\dot(d_{{aut}}L_0-L_1K)=0,
\\qquad
\\dot(M^D d^D)=0.
\\]

The provisional compressed-middle variation has
`{comparison['jet_aware_nonzero_coefficients']}` coefficients, compared with
`{comparison['frozen_nonzero_coefficients']}` in the rejected frozen-parallel
shortcut, and the coefficient hashes differ.  Mixed spatial curvature jets of
orders two and three are still missing from this endpoint calculation, so
these compressed coefficients are a diagnostic rather than a theorem.

The shifted-chain variation retains an exact defect.  More decisively, the
endpoint gauge defect contains zeroth- and second-order PBW words.  Since an
algebraic `Qdot` times the first-order BGG gauge map can change only first-order
words, the algebraic Schur ansatz is obstructed.  The required next object is a
differential, action-derived and cyclic Schur correction.  The complete
rank-310 SDR and transverse causal transfer are not promoted.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    text = report(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
        REPORT.write_text(text)
    elif json.loads(OUTPUT.read_text()) != payload or REPORT.read_text() != text:
        raise AssertionError("jet-aware transverse middle/Schur artifact is stale")
    print("NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()
