#!/usr/bin/env python3
"""Action-derived trace-free linearized Bach operator on unit Nariai.

Unlike the cylinder implementation, this calculation retains the variation
of the Levi--Civita connection acting on the nonzero parallel background Weyl
tensor.  All coefficients are built in a normal orthonormal frame and reduced
to the exact curved PBW normal form on the nine-dimensional trace-free metric
bundle.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Iterable
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add as table_add,
    _formal_adjoint,
    _scale as table_scale,
)
from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import (
    _nariai_weyl,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _sha256,
    _sparse_table,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


Expr = dict[tuple[int, ...], sp.Matrix]
TensorTable = dict[tuple[int, ...], sp.Matrix]

HERE = ROOT / "d_quotient_classical/causal_transfer"
OLD_OBSTRUCTION = ROOT / "d_quotient_classical/certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json"
CYLINDER_BACH = ROOT / "covariant_completion/certificates/linearized_bach.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-action-derived-bach-endpoint.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-action-derived-bach-endpoint-v1.schema.json"
VERIFIER = HERE / "verify_nariai_linearized_bach_endpoint.py"
TESTS = HERE / "tests/test_nariai_linearized_bach_endpoint.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"
INCIDENCE_SOURCE = HERE / "nariai_curvature_incidence_first_square.py"
BGG_SOURCE = HERE / "nariai_first_differential_bgg_correction.py"
MIDDLE_SOURCE = HERE / "nariai_yang_mills_middle_compression.py"


def _clean(value: Expr) -> Expr:
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in value.items()
        if matrix != sp.zeros(*matrix.shape)
    }


def _expr_add(*values: Expr) -> Expr:
    output: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(1, 9))
    for value in values:
        for word, matrix in value.items():
            output[word] += matrix
    return _clean(output)


def _expr_scale(value: Expr, coefficient: sp.Expr) -> Expr:
    if coefficient == 0:
        return {}
    return _clean({word: coefficient * matrix for word, matrix in value.items()})


def _derivative(value: Expr, axis: int, pbw) -> Expr:
    if not value:
        return {}
    return pbw.compose({(axis,): sp.eye(1)}, value)


def _sum_expr(values: Iterable[Expr]) -> Expr:
    return _expr_add(*tuple(values))


def _h_basis(algebraic) -> tuple[list[list[Expr]], sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return the covariant STF tensor basis and its contraction dual."""

    eta = NariaiBackground.metric
    carrier = sp.zeros(16, 9)
    tensor: list[list[Expr]] = [[{} for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            row = sp.Matrix(
                1,
                9,
                lambda _, column: eta[b, b] * algebraic.i1[15 * a + b, column],
            )
            carrier[4 * a + b, :] = row
            tensor[a][b] = {(): row} if row != sp.zeros(1, 9) else {}
    tensor_metric = sp.diag(
        *(eta[a, a] * eta[b, b] for a in range(4) for b in range(4))
    )
    gram = (carrier.T * tensor_metric * carrier).applyfunc(sp.expand)
    left_inverse = (gram.inv() * carrier.T * tensor_metric).applyfunc(sp.expand)
    if left_inverse * carrier != sp.eye(9):
        raise AssertionError("Nariai STF tensor carrier is singular")
    return tensor, carrier, gram, left_inverse


def _connection_variation(h, pbw):
    eta = NariaiBackground.metric
    output = [[[
        {} for _ in range(4)
    ] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        sign = eta[rho, rho]
        for mu in range(4):
            for nu in range(4):
                output[rho][mu][nu] = _expr_scale(
                    _expr_add(
                        _derivative(h[nu][rho], mu, pbw),
                        _derivative(h[mu][rho], nu, pbw),
                        _expr_scale(_derivative(h[mu][nu], rho, pbw), -1),
                    ),
                    sp.Rational(1, 2) * sign,
                )
    return output


def _linearized_curvatures(h, pbw):
    eta = NariaiBackground.metric
    gamma = _connection_variation(h, pbw)
    riemann_mixed = [[[[{} for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    riemann_mixed[rho][sigma][mu][nu] = _expr_add(
                        _derivative(gamma[rho][nu][sigma], mu, pbw),
                        _expr_scale(_derivative(gamma[rho][mu][sigma], nu, pbw), -1),
                    )

    riemann_lower = [[[[{} for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    riemann_lower[a][b][c][d] = _expr_add(
                        *(
                            _expr_scale(
                                h[a][rho],
                                eta[rho, rho] * NariaiBackground.riemann(rho, b, c, d),
                            )
                            for rho in range(4)
                        ),
                        _expr_scale(riemann_mixed[a][b][c][d], eta[a, a]),
                    )

    ricci = [[{} for _ in range(4)] for _ in range(4)]
    for b in range(4):
        for d in range(4):
            ricci[b][d] = _sum_expr(
                riemann_mixed[rho][b][rho][d] for rho in range(4)
            )
    scalar = _sum_expr(
        _expr_scale(ricci[a][a], eta[a, a]) for a in range(4)
    )
    schouten = [[{} for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            schouten[a][b] = _expr_scale(
                _expr_add(
                    ricci[a][b],
                    _expr_scale(scalar, -sp.Rational(1, 6) * eta[a, b]),
                    _expr_scale(h[a][b], -sp.Rational(2, 3)),
                ),
                sp.Rational(1, 2),
            )

    background_schouten = sp.Rational(1, 6) * eta
    weyl = [[[[{} for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    variation_wedge = _expr_add(
                        _expr_scale(h[a][c], background_schouten[d, b]),
                        _expr_scale(schouten[d][b], eta[a, c]),
                        _expr_scale(h[a][d], -background_schouten[c, b]),
                        _expr_scale(schouten[c][b], -eta[a, d]),
                        _expr_scale(h[b][c], -background_schouten[d, a]),
                        _expr_scale(schouten[d][a], -eta[b, c]),
                        _expr_scale(h[b][d], background_schouten[c, a]),
                        _expr_scale(schouten[c][a], eta[b, d]),
                    )
                    weyl[a][b][c][d] = _expr_add(
                        riemann_lower[a][b][c][d],
                        _expr_scale(variation_wedge, -1),
                    )
    return gamma, ricci, scalar, weyl


def _linearized_bach_tensor(h, pbw):
    eta = NariaiBackground.metric
    gamma, ricci, _, weyl_one = _linearized_curvatures(h, pbw)

    # U_f = delta(nabla_f C).  Nariai is locally symmetric, so nabla C=0,
    # but the four connection-variation actions on the nonzero C remain.
    def u(f: int, a: int, c: int, b: int, d: int) -> Expr:
        return _expr_add(
            _derivative(weyl_one[a][c][b][d], f, pbw),
            *(
                _expr_scale(gamma[p][f][a], -_nariai_weyl(p, c, b, d))
                for p in range(4)
            ),
            *(
                _expr_scale(gamma[p][f][c], -_nariai_weyl(a, p, b, d))
                for p in range(4)
            ),
            *(
                _expr_scale(gamma[p][f][b], -_nariai_weyl(a, c, p, d))
                for p in range(4)
            ),
            *(
                _expr_scale(gamma[p][f][d], -_nariai_weyl(a, c, b, p))
                for p in range(4)
            ),
        )

    output = [[{} for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            double_divergence = _sum_expr(
                _expr_scale(
                    _derivative(u(d, a, c, b, d), c, pbw),
                    eta[c, c] * eta[d, d],
                )
                for c in range(4)
                for d in range(4)
            )
            ricci_variation_term = _sum_expr(
                _expr_scale(
                    _expr_add(
                        ricci[c][d],
                        _expr_scale(h[c][d], -2),
                    ),
                    sp.Rational(1, 2)
                    * eta[c, c]
                    * eta[d, d]
                    * _nariai_weyl(a, c, b, d),
                )
                for c in range(4)
                for d in range(4)
            )
            background_ricci_term = _sum_expr(
                _expr_scale(
                    weyl_one[a][c][b][d],
                    sp.Rational(1, 2) * eta[c, d],
                )
                for c in range(4)
                for d in range(4)
            )
            output[a][b] = _expr_add(
                double_divergence,
                ricci_variation_term,
                background_ricci_term,
            )
    return output


def endpoint_operator() -> dict[str, object]:
    middle = middle_fixture()
    algebraic = middle["algebraic"]
    pbw_h1 = middle["pbw_h1"]
    h, tensor_carrier, tensor_gram, tensor_left_inverse = _h_basis(algebraic)
    bach_tensor = _linearized_bach_tensor(h, pbw_h1)

    # Verify tensor symmetry and trace before projecting to H1 coordinates.
    symmetry_defects = []
    for a in range(4):
        for b in range(4):
            defect = _expr_add(bach_tensor[a][b], _expr_scale(bach_tensor[b][a], -1))
            if defect:
                symmetry_defects.append((a, b, defect))
    trace = _sum_expr(
        _expr_scale(bach_tensor[a][a], NariaiBackground.metric[a, a])
        for a in range(4)
    )
    divergence = tuple(
        _sum_expr(
            _expr_scale(
                _derivative(bach_tensor[a][b], a, pbw_h1),
                NariaiBackground.metric[a, a],
            )
            for a in range(4)
        )
        for b in range(4)
    )

    coordinate_table: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(9))
    for output_coordinate in range(9):
        for a in range(4):
            for b in range(4):
                coefficient = tensor_left_inverse[output_coordinate, 4 * a + b]
                if coefficient == 0:
                    continue
                for word, row in bach_tensor[a][b].items():
                    coordinate_table[word][output_coordinate, :] += coefficient * row
    coordinate_table = {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in coordinate_table.items()
        if matrix != sp.zeros(9)
    }

    # Three natural paired-coordinate presentations are retained until the
    # parent principal symbol fixes the action normalization.
    candidates = {
        "tensor_coordinates": coordinate_table,
        "tensor_covector_coordinates": {
            word: (tensor_gram * matrix).applyfunc(sp.expand)
            for word, matrix in coordinate_table.items()
        },
    }
    diagnostics = {}
    for name, table in candidates.items():
        gauge_defect = middle["pbw_h0"].compose(table, middle["first_bgg"])
        adjoint = _formal_adjoint(
            table,
            algebraic.endpoint_field_pairing,
            algebraic.endpoint_field_pairing,
            pbw_h1,
        )
        adjoint_defect = table_add(adjoint, table_scale(table, -1))
        diagnostics[name] = {
            "table": table,
            "gauge_defect": gauge_defect,
            "adjoint_defect": adjoint_defect,
        }

    standard_covector = candidates["tensor_covector_coordinates"]
    action_bach = {
        word: (-2 * matrix).applyfunc(sp.expand)
        for word, matrix in standard_covector.items()
    }
    parent_corrected = table_add(
        middle["compressed_middle"],
        {(): middle["endpoint_correction"]},
    )
    compression_defect = table_add(
        parent_corrected,
        table_scale(action_bach, 2),
    )
    raw_compression_defect = table_add(
        middle["compressed_middle"],
        table_scale(action_bach, 2),
    )
    gauge_defect = middle["pbw_h0"].compose(
        action_bach, middle["first_bgg"]
    )

    return {
        "middle": middle,
        "tensor_gram": tensor_gram,
        "tensor_carrier": tensor_carrier,
        "tensor_left_inverse": tensor_left_inverse,
        "bach_tensor": bach_tensor,
        "symmetry_defects": symmetry_defects,
        "trace_defect": trace,
        "divergence_defects": divergence,
        "candidates": diagnostics,
        "standard_bach_covector": standard_covector,
        "action_bach": action_bach,
        "parent_corrected": parent_corrected,
        "compression_defect": compression_defect,
        "raw_compression_defect": raw_compression_defect,
        "action_gauge_defect": gauge_defect,
    }


def _entry_count(table: TensorTable) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _table_digest(table: TensorTable) -> str:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _product_scaling_fixture(value: dict[str, object]) -> dict[str, object]:
    """Independent finite product-family check of the algebraic coefficient."""

    x, y = sp.symbols("x y", positive=True)
    metric = sp.diag(-x, x, y, y)
    inverse = metric.inv()
    base = sp.diag(-1, 1, 1, 1)
    riemann = [[[[sp.Integer(0) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    same_factor = all(index < 2 for index in (a, b, c, d)) or all(
                        index >= 2 for index in (a, b, c, d)
                    )
                    if same_factor:
                        scale = x if a < 2 else y
                        riemann[a][b][c][d] = scale * (
                            base[a, c] * base[b, d]
                            - base[a, d] * base[b, c]
                        )
    ricci = sp.zeros(4)
    for b in range(4):
        for d in range(4):
            ricci[b, d] = sum(
                inverse[a, c] * riemann[c][b][a][d]
                for a in range(4)
                for c in range(4)
            )
    scalar = sum(
        inverse[a, b] * ricci[a, b]
        for a in range(4)
        for b in range(4)
    )
    schouten = sp.Rational(1, 2) * (
        ricci - sp.Rational(1, 6) * scalar * metric
    )
    weyl = [[[[sp.Integer(0) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    weyl[a][b][c][d] = sp.simplify(
                        riemann[a][b][c][d]
                        - (
                            metric[a, c] * schouten[d, b]
                            - metric[a, d] * schouten[c, b]
                            - metric[b, c] * schouten[d, a]
                            + metric[b, d] * schouten[c, a]
                        )
                    )
    bach = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            bach[a, b] = sp.simplify(
                sp.Rational(1, 2)
                * sum(
                    inverse[c, e]
                    * inverse[d, f]
                    * ricci[e, f]
                    * weyl[a][c][b][d]
                    for c in range(4)
                    for d in range(4)
                    for e in range(4)
                    for f in range(4)
                )
            )
    standard_variation = bach.applyfunc(
        lambda entry: sp.simplify(
            (sp.diff(entry, x) - sp.diff(entry, y)).subs({x: 1, y: 1})
        )
    )
    expected_standard = sp.diag(
        sp.Rational(2, 3),
        -sp.Rational(2, 3),
        sp.Rational(2, 3),
        sp.Rational(2, 3),
    )
    if standard_variation != expected_standard:
        raise AssertionError("product-family standard Bach variation drifted")

    carrier = value["tensor_carrier"]
    metric_variation = sp.Matrix(
        [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1]
    )
    coordinates, parameters = carrier.gauss_jordan_solve(metric_variation)
    if parameters.rows:
        raise AssertionError("product scaling escaped the STF carrier")
    action_covector = value["action_bach"].get((), sp.zeros(9)) * coordinates
    action_tensor_coordinates = value["tensor_gram"].inv() * action_covector
    action_tensor = (carrier * action_tensor_coordinates).reshape(4, 4)
    if action_tensor != -2 * expected_standard:
        raise AssertionError("normal-frame Bach table failed product scaling")
    return {
        "family": "g(x,y)=x g_dS2 + y g_S2",
        "variation": "d/dx-d/dy at x=y=1",
        "standard_Bach_variation": [str(entry) for entry in standard_variation],
        "action_normalized_variation": [str(entry) for entry in action_tensor],
        "normalization": "B_action=-2 B_standard",
        "exact_match": True,
    }


def build() -> dict[str, object]:
    old = json.loads(OLD_OBSTRUCTION.read_text())
    cylinder = json.loads(CYLINDER_BACH.read_text())
    if old["flags"]["UNIQUE_ALGEBRAIC_GAUGE_REPAIR_EXISTS"] is not True:
        raise ValueError("prior endpoint correction unavailable")
    if cylinder.get("normalization", "").split()[0] != "-2":
        raise ValueError("repository Bach action normalization drifted")

    value = endpoint_operator()
    product = _product_scaling_fixture(value)
    action = value["action_bach"]
    parent = value["parent_corrected"]
    if value["symmetry_defects"] or value["trace_defect"]:
        raise AssertionError("tensor Bach algebraic identities failed")
    if any(value["divergence_defects"]):
        raise AssertionError("linearized Bach divergence identity failed")
    if value["action_gauge_defect"]:
        raise AssertionError("linearized Bach gauge identity failed")
    if value["compression_defect"]:
        raise AssertionError("corrected parent compression missed Bach")
    expected_words = {()} | set(combinations_with_replacement(range(4), 2)) | set(
        combinations_with_replacement(range(4), 4)
    )
    if set(action) != expected_words:
        raise AssertionError("action Bach PBW coverage drifted")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            PBW_SOURCE,
            INCIDENCE_SOURCE,
            BGG_SOURCE,
            MIDDLE_SOURCE,
        )
    }
    return {
        "schema": "pure-weyl-nariai-action-derived-bach-endpoint-v1",
        "result_id": "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1",
        "result_state": "ACTION_DERIVED_BACH_AND_CORRECTED_PARENT_COMPRESSION_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "prior_algebraic_screen": {
                "artifact_id": old["result_id"],
                "path": str(OLD_OBSTRUCTION.relative_to(ROOT)),
                "sha256": _sha256(OLD_OBSTRUCTION),
            },
            "action_normalization": {
                "artifact_id": cylinder["schema"],
                "path": str(CYLINDER_BACH.relative_to(ROOT)),
                "sha256": _sha256(CYLINDER_BACH),
            },
        },
        "construction": {
            "background": "unit Nariai dS2 x S2, Ric=g, scalar=4, nabla C=0",
            "standard_operator": "delta[nabla^c nabla^d C_acbd+(1/2)Ric^cd C_acbd]",
            "background_Weyl_connection_terms": "all four -deltaGamma*C slot actions retained inside delta(nabla C)",
            "input_bundle": "H1=S^2_0 T* in the certified nine-coordinate Kostant basis",
            "normal_form": "symmetrized covariant PBW words with exact Nariai commutators",
            "action_normalization": "B_action=-2 B_standard",
        },
        "exact_operator": {
            "shape": [9, 9],
            "orders": sorted({len(word) for word in action}),
            "coefficient_words": len(action),
            "nonzero_coefficients": _entry_count(action),
            "sha256": _table_digest(action),
            "coefficients": _sparse_table(action),
        },
        "exact_checks": {
            "tensor_symmetry_defects": len(value["symmetry_defects"]),
            "tensor_trace_defect_entries": _entry_count(value["trace_defect"]),
            "tensor_divergence_defect_entries": sum(
                _entry_count(defect) for defect in value["divergence_defects"]
            ),
            "B_action_K_defect_entries": _entry_count(value["action_gauge_defect"]),
            "corrected_parent_plus_2_B_action_defect_entries": _entry_count(value["compression_defect"]),
            "raw_parent_plus_2_B_action_defect_orders": sorted(
                {len(word) for word in value["raw_compression_defect"]}
            ),
            "raw_parent_plus_2_B_action_defect_entries": _entry_count(value["raw_compression_defect"]),
            "raw_defect_equals_minus_unique_Q": value["raw_compression_defect"].get(()) == -value["middle"]["endpoint_correction"],
            "product_scaling_exact": product["exact_match"],
            "formal_self_adjointness": "follows from the second variation of the Weyl-squared action at the Bach-flat solution",
            "generic_post_normal_order_adjoint_used_as_authority": False,
        },
        "product_scaling_regression": product,
        "compression_identity": {
            "formula": "B_parent_compressed + Q_unique = -2 B_action",
            "orders_checked": [0, 2, 4],
            "coefficientwise_defect": 0,
            "interpretation": "the unique algebraic gauge repair is exactly the missing action-derived Nariai Bach coefficient in the current parent normalization",
        },
        "repair": {
            "supersedes_theorem_interpretation_of": old["result_id"],
            "superseded_sha256": _sha256(OLD_OBSTRUCTION),
            "old_result_retained_as": "a scoped diagnostic that Q_unique alone is noncyclic in the provisional endpoint adjoint convention",
            "new_result": "Q_unique completes the full compressed operator to -2 times the action Bach Hessian; cyclicity must be reconciled at the Hom-bundle adjoint/pairing layer, not rejected from Q_unique in isolation",
        },
        "flags": {
            "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1": True,
            "NARIAI_METRIC_BACH_ENDPOINT_EXACT": True,
            "CORRECTED_PARENT_COMPRESSION_EQUALS_MINUS_TWO_BACH": True,
            "PRIOR_ALGEBRAIC_ENDPOINT_NO_GO_INTERPRETATION_SUPERSEDED": True,
            "RELATIVE_CYCLIC_PAIRING_RECONCILED": False,
            "METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_RELATIVE_CYCLIC_PAIRING_AND_EQUATION_CONE",
        "claim_boundary": (
            "This certificate derives the complete trace-free linearized Bach endpoint on unit Nariai from the covariant Bach tensor, including every connection variation against the nonzero parallel Weyl curvature. It proves the gauge, trace and divergence identities and the exact coefficient equality B_parent_compressed+Q_unique=-2 B_action. The product-scaling family independently checks the algebraic normalization. It supersedes the earlier interpretation of Q_unique as an endpoint no-go, but retains that receipt as a diagnostic of the provisional coefficientwise adjoint convention. It does not yet reconcile the relative cyclic pairing/Hom-bundle adjoint, construct the full equation/identity-row cone or SDR, build Green homotopies, prove an open-background theorem, or make nonlinear or quantum claims."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_linearized_bach_endpoint.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_linearized_bach_endpoint.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_linearized_bach_endpoint",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-action-derived-bach-endpoint-v1.schema.json -d d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json",
            ],
        },
    }


def render(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Action-derived Nariai Bach endpoint

The complete trace-free Nariai linearized Bach operator has now been derived
directly from

\[
B_{{ab}}=\nabla^c\nabla^d C_{{acbd}}+\frac12R^{{cd}}C_{{acbd}}.
\]

The derivation retains the variation of all four connection actions on the
nonzero parallel background Weyl tensor.  After the repository action
normalization \(B_{{\rm action}}=-2B_{{\rm standard}}\), the result has
orders `{value['exact_operator']['orders']}`, `{value['exact_operator']['coefficient_words']}`
PBW words, and `{value['exact_operator']['nonzero_coefficients']}` nonzero
coefficients.

The exact tensor checks give zero symmetry, trace, divergence and gauge
defects.  Most importantly,

\[
B_{{\rm parent,comp}}+Q_{{\rm unique}}=-2B_{{\rm action}}
\]

coefficientwise through orders zero, two and four.  The defect contains
`{checks['corrected_parent_plus_2_B_action_defect_entries']}` entries.  Before
adding \(Q_{{\rm unique}}\), the only difference is algebraic with
`{checks['raw_parent_plus_2_B_action_defect_entries']}` entries, and it is
exactly \(-Q_{{\rm unique}}\).

An independent product-family calculation for
\(g(x,y)=xg_{{dS_2}}+yg_{{S^2}}\) gives the standard variation
\(\operatorname{{diag}}(2/3,-2/3,2/3,2/3)\) along
\(\partial_x-\partial_y\), and the normal-frame operator reproduces its
action-normalized value exactly.

## Corrected interpretation

The previous noncyclicity of \(Q_{{\rm unique}}\) in isolation is not an
obstruction to the actual Bach endpoint.  It diagnoses the provisional
Hom-bundle adjoint/pairing realization.  The next gate is to reconcile that
cyclic pairing and then build the complete relative equation/identity-row
cone.

## Boundary

{value['claim_boundary']}
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.diagnose:
        raw = endpoint_operator()
        print("tensor_gram_rank", raw["tensor_gram"].rank())
        print("symmetry_defects", len(raw["symmetry_defects"]))
        print("trace_defect_entries", _entry_count(raw["trace_defect"]))
        print("divergence_defect_entries", sum(_entry_count(item) for item in raw["divergence_defects"]))
        for name, diagnostic in raw["candidates"].items():
            table = diagnostic["table"]
            print(name)
            print(" orders", sorted({len(word) for word in table}))
            print(" entries", _entry_count(table))
            print(" gauge_defect_entries", _entry_count(diagnostic["gauge_defect"]))
            print(" adjoint_replay_defect_entries", _entry_count(diagnostic["adjoint_defect"]))
        return
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.guards:
        checks = value["exact_checks"]
        if checks["corrected_parent_plus_2_B_action_defect_entries"] != 0:
            raise AssertionError("parent/Bach compression guard failed")
        if checks["B_action_K_defect_entries"] != 0:
            raise AssertionError("Bach gauge guard failed")
        if value["flags"]["RELATIVE_CYCLIC_PAIRING_RECONCILED"] is not False:
            raise AssertionError("relative cyclicity was overpromoted")
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render(value)
    if args.write:
        OUTPUT.write_text(encoded)
        REPORT.write_text(report)
    if args.check and (
        not OUTPUT.exists()
        or not REPORT.exists()
        or OUTPUT.read_text() != encoded
        or REPORT.read_text() != report
    ):
        raise SystemExit("generated Nariai Bach artifacts drifted")
    print(f"{value['result_id']}: PASS")


if __name__ == "__main__":
    main()
