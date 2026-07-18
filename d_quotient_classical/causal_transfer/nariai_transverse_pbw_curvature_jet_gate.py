#!/usr/bin/env python3
"""Audit the nonparallel curvature jet in the transverse Nariai PBW gate."""

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
    _coordinate_map,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _formal_adjoint,
    _induced_harmonic_curvature,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _derivative_rows,
    _load,
)
from d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation import (
    _variation_riemann,
    exact_variation,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-pbw-curvature-jet-gate.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-pbw-curvature-jet-gate-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_pbw_curvature_jet_gate.py"
TESTS = HERE / "tests/test_nariai_transverse_pbw_curvature_jet_gate.py"
WITNESS = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
INCIDENCE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1.json"
ALGEBRAIC = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [[r, c, str(v)] for (r, c), v in sorted(matrix.todok().items())],
        "sha256": hashlib.sha256(sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()).hexdigest(),
    }


def _table(table: dict[tuple[int, ...], sp.Matrix]) -> dict[str, Any]:
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


def _first(table: dict[tuple[int, ...], sp.Matrix], epsilon: sp.Symbol) -> dict[tuple[int, ...], sp.Matrix]:
    result = {}
    for word, matrix in table.items():
        derivative = matrix.applyfunc(lambda value: sp.expand(value).coeff(epsilon, 1))
        if derivative != sp.zeros(*derivative.shape):
            result[word] = derivative
    return result


def _connection_difference() -> dict[str, Any]:
    """Return the fixed-coordinate LC variation and moving-frame spin variation."""

    t, theta, epsilon = sp.symbols("t theta epsilon", real=True)
    alpha = -sp.sinh(2 * t) / 3
    beta = sp.sinh(t)
    a = sp.cosh(t) + epsilon * alpha
    b = 1 + epsilon * beta
    metric = sp.diag(-1, a**2, b**2, b**2 * sp.sin(theta) ** 2)
    inverse = metric.inv()
    coordinates = (t, sp.Symbol("chi"), theta, sp.Symbol("phi"))
    gamma = [[[
        sp.simplify(sum(
            inverse[rho, sigma]
            * (
                sp.diff(metric[sigma, nu], coordinates[mu])
                + sp.diff(metric[sigma, mu], coordinates[nu])
                - sp.diff(metric[mu, nu], coordinates[sigma])
            )
            for sigma in range(4)
        ) / 2)
        for nu in range(4)] for mu in range(4)] for rho in range(4)]
    delta_gamma = [[[
        sp.simplify(sp.diff(gamma[rho][mu][nu], epsilon).subs(epsilon, 0))
        for nu in range(4)] for mu in range(4)] for rho in range(4)]
    coframe = (1, sp.cosh(t), 1, sp.sin(theta))
    frame = tuple(1 / value for value in coframe)
    substitutions = {
        sp.sinh(t): 1,
        sp.cosh(t): sp.sqrt(2),
        sp.sin(theta): 1,
        sp.cos(theta): 0,
    }
    tensor = sp.MutableDenseNDimArray.zeros(4, 4, 4)
    for output in range(4):
        for derivative in range(4):
            for source in range(4):
                value = sp.expand_trig(
                    coframe[output]
                    * frame[derivative]
                    * frame[source]
                    * delta_gamma[output][derivative][source]
                ).subs(substitutions)
                tensor[output, derivative, source] = sp.simplify(value)
    flattened = sp.Matrix(4, 16, lambda output, column: tensor[output, column // 4, column % 4])

    delta_hubble = {
        1: sp.simplify(sp.diff(alpha / sp.cosh(t), t)).subs(substitutions),
        2: sp.diff(beta, t).subs(substitutions),
        3: sp.diff(beta, t).subs(substitutions),
    }
    spin = {}
    for axis, coefficient in delta_hubble.items():
        matrix = sp.zeros(4)
        matrix[0, axis] = coefficient
        matrix[axis, 0] = coefficient
        if matrix.T * NariaiBackground.metric + NariaiBackground.metric * matrix != sp.zeros(4):
            raise AssertionError("moving-frame spin variation left so(1,3)")
        spin[str(axis)] = _sparse(matrix)
    return {
        "evaluation_point": "t=asinh(1), theta=pi/2",
        "fixed_coordinate_connection_difference_in_background_orthonormal_components": _sparse(flattened),
        "moving_coframe_spin_connection_variation": spin,
        "nonzero_spin_axes": sorted(spin),
    }


class _PerturbedBackground:
    epsilon = sp.Symbol("epsilon")
    metric = NariaiBackground.metric
    inverse_metric = metric
    delta_riemann = _variation_riemann()

    @classmethod
    def riemann(cls, a: int, b: int, c: int, d: int) -> sp.Expr:
        return NariaiBackground.riemann(a, b, c, d) + cls.epsilon * cls.delta_riemann[a, b, c, d]

    @classmethod
    def covector_commutator(cls, a: int, b: int) -> sp.Matrix:
        return sp.Matrix(4, 4, lambda output, source: -sum(
            cls.inverse_metric[source, raised] * cls.riemann(raised, output, a, b)
            for raised in range(4)
        ))

    @classmethod
    def vector_commutator(cls, a: int, b: int) -> sp.Matrix:
        return -cls.covector_commutator(a, b).T


def _lc_adjoint_curvature(background: type[_PerturbedBackground]) -> tuple[tuple[sp.Matrix, ...], ...]:
    _, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    output = []
    for left in range(4):
        row = []
        for right in range(4):
            standard = sp.zeros(6)
            standard[1:5, 1:5] = background.vector_commutator(left, right)
            columns = []
            for generator in basis:
                commutator = standard * generator - generator * standard
                coordinates = left_inverse * commutator.reshape(36, 1)
                if embedded * coordinates != commutator.reshape(36, 1):
                    raise AssertionError("perturbed LC curvature escaped so(4,2)")
                columns.append(coordinates)
            row.append(sp.Matrix.hstack(*columns))
        output.append(tuple(row))
    return tuple(output)


@lru_cache(maxsize=1)
def frozen_parallel_pbw_audit() -> dict[str, Any]:
    """Differentiate the old parallel-curvature PBW engine as a scoped audit."""

    epsilon = _PerturbedBackground.epsilon
    background = _PerturbedBackground
    algebraic, screen = _load()
    lc_adjoint = _lc_adjoint_curvature(background)
    curvature0 = _tensor_product_curvature(background, lc_adjoint, 0)
    curvature1 = _tensor_product_curvature(background, lc_adjoint, 1)
    curvature2 = _tensor_product_curvature(background, lc_adjoint, 2)
    harmonic0 = _induced_harmonic_curvature(curvature0, algebraic.i0, screen.harmonic_p0)
    harmonic1 = _induced_harmonic_curvature(curvature1, algebraic.i1, screen.harmonic_p1)
    pbw0 = FibrePBW(curvature0, background, "transverse-C0")
    pbw1 = FibrePBW(curvature1, background, "transverse-C1")
    pbw2 = FibrePBW(curvature2, background, "transverse-C2")
    pbw_h0 = FibrePBW(harmonic0, background, "transverse-H0")
    pbw_h1 = FibrePBW(harmonic1, background, "transverse-H1")

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
    delta0 = _add(_algebraic(rho0), derivative0)
    delta1 = _add(_algebraic(rho1), derivative1)
    total0 = _add(_algebraic(screen.cohomology_d0), delta0)
    total1 = _add(_algebraic(screen.cohomology_d1), delta1)

    n0 = pbw0.compose(_algebraic(screen.q1), delta0)
    n1 = pbw1.compose(_algebraic(screen.q2), delta1)
    i0_alg = _algebraic(algebraic.i0)
    i1_alg = _algebraic(algebraic.i1)
    n0_i0 = pbw_h0.compose(n0, i0_alg)
    n1_i1 = pbw_h1.compose(n1, i1_alg)
    inclusion0 = _add(i0_alg, _scale(n0_i0, -1), pbw_h0.compose(n0, n0_i0))
    inclusion1 = _add(i1_alg, _scale(n1_i1, -1), pbw_h1.compose(n1, n1_i1))
    first_bgg = pbw_h0.compose(
        _algebraic(screen.harmonic_p1),
        pbw_h0.compose(total0, inclusion0),
    )
    square = pbw0.compose(total1, total0)

    pairs = tuple((left, right) for left in range(4) for right in range(left + 1, 4))
    curvature_pairs = {
        pair: square[()][15 * index : 15 * (index + 1), :]
        for index, pair in enumerate(pairs)
    }

    def curvature(left: int, right: int) -> sp.Matrix:
        if left == right:
            return sp.zeros(15)
        return curvature_pairs[(left, right)] if left < right else -curvature_pairs[(right, left)]

    eta = NariaiBackground.metric
    curvature_action = sp.Matrix.vstack(*(
        sp.Matrix.hstack(*(eta[source, source] * curvature(target, source) for source in range(4)))
        for target in range(4)
    ))
    two_form_metric = sp.diag(*(eta[left, left] * eta[right, right] for left, right in pairs))
    two_form_pairing = sp.kronecker_product(two_form_metric, algebraic.adjoint_pairing)
    total1_sharp = _formal_adjoint(total1, algebraic.one_form_pairing, two_form_pairing, pbw2)
    rough_middle = pbw1.compose(total1_sharp, total1)
    middle = _add(rough_middle, _scale(_algebraic(curvature_action), -1))
    inclusion1_sharp = _formal_adjoint(
        inclusion1,
        algebraic.endpoint_field_pairing,
        algebraic.one_form_pairing,
        pbw1,
    )
    compressed = pbw_h1.compose(inclusion1_sharp, pbw_h1.compose(middle, inclusion1))

    variations = {
        "inclusion0": _first(inclusion0, epsilon),
        "inclusion1": _first(inclusion1, epsilon),
        "first_bgg": _first(first_bgg, epsilon),
        "normal_tractor_square": _first(square, epsilon),
        "yang_mills_middle": _first(middle, epsilon),
        "compressed_middle": _first(compressed, epsilon),
    }

    # The varied square must equal the adjoint action of the independently
    # reconstructed normal-tractor curvature variation.
    incidence = exact_variation()["delta_normal_tractor_curvature"]
    embedded, left_inverse = _coordinate_map(basis)
    expected_blocks = []
    for pair in pairs:
        record = incidence[f"{pair[0]}{pair[1]}"]
        coordinates = sp.zeros(15, 1)
        for row, column, value in record["entries"]:
            coordinates[row, column] = sp.Rational(value)
        standard = sp.Matrix(6, 6, embedded * coordinates)
        columns = []
        for generator in basis:
            commutator = standard * generator - generator * standard
            columns.append(left_inverse * commutator.reshape(36, 1))
        expected_blocks.append(sp.Matrix.hstack(*columns))
    expected_square = sp.Matrix.vstack(*expected_blocks)
    actual_square = variations["normal_tractor_square"].get((), sp.zeros(90, 15))
    square_defect = actual_square - expected_square
    if square_defect != sp.zeros(90, 15):
        raise AssertionError("varied normal-tractor square disagrees with incidence curvature")

    return {
        "assumption": "delta curvature is frozen parallel at the evaluation point; derivatives of delta curvature are omitted",
        "variations": {name: _table(table) for name, table in variations.items()},
        "square_matches_independent_curvature_action": True,
        "square_comparison_defect": _sparse(square_defect),
        "authoritative_for_true_transverse_middle": False,
    }


def curvature_jet() -> dict[str, Any]:
    base = _variation_riemann()
    first_time = sp.sqrt(2) * base
    second_time = base
    flattened = lambda tensor: sp.Matrix(16, 16, lambda row, column: tensor[row // 4, row % 4, column // 4, column % 4])
    return {
        "sectional_function": {
            "01": "2 sinh(t)", "02": "-sinh(t)", "03": "-sinh(t)",
            "12": "sinh(t)", "13": "sinh(t)", "23": "-2 sinh(t)",
        },
        "delta_R_at_t_star": _sparse(flattened(base)),
        "covariant_time_jet_order_1_at_t_star": _sparse(flattened(first_time)),
        "covariant_time_jet_order_2_at_t_star": _sparse(flattened(second_time)),
        "nonparallel_witness": {
            "component": "nabla_0 delta C_0202",
            "value": str(-sp.sqrt(2)),
        },
    }


def build() -> dict[str, Any]:
    dependencies = {}
    for name, path, expected in (
        ("transverse_witness", WITNESS, "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1"),
        ("incidence_variation", INCIDENCE, "NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1"),
        ("algebraic_pairing", ALGEBRAIC, "NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != expected:
            raise AssertionError(f"dependency drifted: {name}")
        dependencies[name] = {"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": _sha(path)}
    exact = {
        "connection": _connection_difference(),
        "curvature_jet": curvature_jet(),
        "frozen_parallel_PBW_audit": frozen_parallel_pbw_audit(),
    }
    return {
        "schema": "nariai-transverse-pbw-curvature-jet-gate-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1",
        "result_state": "NONPARALLEL_CURVATURE_JET_EXACT_PARALLEL_PBW_SHORTCUT_OBSTRUCTED",
        "lifecycle_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "exact_data": exact,
        "exact_checks": {
            "ordinary_connection_variation_nonzero": exact["connection"]["fixed_coordinate_connection_difference_in_background_orthonormal_components"]["rank"] > 0,
            "moving_spin_connection_variation_nonzero": len(exact["connection"]["moving_coframe_spin_connection_variation"]) == 3,
            "curvature_time_jet_nonzero": exact["curvature_jet"]["covariant_time_jet_order_1_at_t_star"]["rank"] > 0,
            "parallel_PBW_square_matches_independent_curvature_action": exact["frozen_parallel_PBW_audit"]["square_matches_independent_curvature_action"],
            "parallel_PBW_middle_not_promoted": not exact["frozen_parallel_PBW_audit"]["authoritative_for_true_transverse_middle"],
        },
        "flags": {
            "TRANSVERSE_CONNECTION_VARIATION_EXACT": True,
            "TRANSVERSE_CURVATURE_JET_EXACT": True,
            "FROZEN_PARALLEL_PBW_RESPONSE_EXACT": True,
            "PARALLEL_CURVATURE_PBW_SUFFICIENT": False,
            "TRANSVERSE_JET_AWARE_PBW_VARIATION": False,
            "TRANSVERSE_MIDDLE_SCHUR_VARIATION": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_JET_AWARE_PBW_LEIBNIZ_AND_MIDDLE_SCHUR_VARIATION",
        "claim_boundary": "This certificate computes the exact nonzero Levi-Civita/spin-connection variation and the nonparallel curvature time jet along the certified transverse tangent. It also differentiates the old locally symmetric PBW engine under the explicitly false frozen-parallel substitution and checks its normal-tractor square against the independent curvature incidence. Because nabla_0 delta C is nonzero, that frozen response is not the true middle/Schur variation. The result obstructs only reuse of the parallel-curvature PBW backend; it is not an obstruction to a jet-aware PBW repair, the rank-310 SDR, or transverse causal transfer.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PBW_SOURCE)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_pbw_curvature_jet_gate --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_pbw_curvature_jet_gate.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_pbw_curvature_jet_gate",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-pbw-curvature-jet-gate-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    frozen = payload["exact_data"]["frozen_parallel_PBW_audit"]["variations"]
    return f"""# Transverse Nariai PBW curvature-jet gate

The transverse Kantowski--Sachs tangent changes the Levi--Civita connection
and the normal-tractor curvature.  At the normalized point the fixed-frame
connection-difference tensor is nonzero, while the moving coframe has three
nonzero boost-connection variations.  More decisively,

\\[
(\\nabla_0\\,\\delta C)_{{0202}}=-\\sqrt2.
\\]

Thus the tangent is not a parallel-curvature perturbation.  The existing
`FibrePBW` backend was designed for locally symmetric backgrounds and omits
Leibniz terms in which outer derivatives hit the varied curvature.

As a diagnostic, freezing the curvature variation at the point gives exact
first responses with `{frozen['inclusion0']['nonzero_coefficients']}` BGG-0,
`{frozen['inclusion1']['nonzero_coefficients']}` BGG-1,
`{frozen['yang_mills_middle']['nonzero_coefficients']}` parent-middle, and
`{frozen['compressed_middle']['nonzero_coefficients']}` compressed-middle
coefficients.  Its varied normal-tractor square agrees exactly with the
independent curvature-incidence reconstruction.  Those middle coefficients
are deliberately **not** promoted: the nonzero curvature jet proves that the
parallel substitution omits required terms.

The next implementation gate is a jet-aware PBW normal form carrying
covariant derivatives of curvature through the Leibniz rule, followed by the
middle/Schur and full rank-310 SDR variations.  This is a scoped backend
obstruction, not a no-go theorem for transverse causal transfer.
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
        raise AssertionError("transverse PBW curvature-jet gate artifact is stale")
    print("NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1: PASS")


if __name__ == "__main__":
    main()
