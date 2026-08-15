#!/usr/bin/env python3
"""Typed Bach-flat unary BV complex and exact local fixture receiver.

The module deliberately sits downstream of the portable Bach natural-operator
certificate.  It does not alter that hash-pinned AST.  Instead it names the
five nonzero background-linear Taylor components of the strict minimal BV
differential and evaluates the three nontrivial square-zero identities over
the exact normalized coordinate-jet algebra.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from typing import Mapping, Sequence

try:
    from . import cylinder_polarized_bach_evaluator as point
except ImportError:  # direct path execution
    import cylinder_polarized_bach_evaluator as point


DIMENSION = 4
EXPRESSION_SCHEMA_VERSION = "strict-pure-weyl-local-q1-bach-flat-v1"
SYMBOLS = ("h", "c", "omega", "h_star", "c_star", "omega_star")
DEGREES = {"h": 0, "c": -1, "omega": -1, "h_star": 1, "c_star": 2, "omega_star": 2}
PARITIES = {symbol: degree % 2 for symbol, degree in DEGREES.items()}


class LocalQ1Error(ValueError):
    """Raised when the typed unary payload or exact fixture is invalid."""


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def canonical_nodes() -> list[dict[str, object]]:
    """Return the canonical portable unary DAG in topological order."""

    return [
        {
            "node_id": "gbar",
            "operation": "bach_flat_background_metric",
            "inputs": [],
            "parameters": {"condition": "E_g(gbar)=0"},
            "declared_output_type": "symmetric_covariant_2",
            "maximum_input_jet_orders": [],
        },
        {
            "node_id": "R_diff",
            "operation": "background_lie_derivative_metric",
            "inputs": ["gbar"],
            "parameters": {
                "formula": "(L_c gbar)_ab=c^rho partial_rho gbar_ab+gbar_rho_b partial_a c^rho+gbar_a_rho partial_b c^rho"
            },
            "declared_output_type": "c_to_symmetric_covariant_2",
            "maximum_input_jet_orders": [1],
        },
        {
            "node_id": "R_weyl",
            "operation": "background_weyl_metric_action",
            "inputs": ["gbar"],
            "parameters": {"formula": "2 omega gbar_ab"},
            "declared_output_type": "omega_to_symmetric_covariant_2",
            "maximum_input_jet_orders": [0],
        },
        {
            "node_id": "B_linear",
            "operation": "frechet_derivative_of_portable_E_g",
            "inputs": ["gbar"],
            "parameters": {
                "formula": "[a]E_g(gbar+a h)",
                "portable_parent_result_id": "STRICT_BACH_NATURAL_OPERATOR_AST_V1",
                "parent_node": "E_g",
            },
            "declared_output_type": "h_to_symmetric_contravariant_density_weight_plus_1",
            "maximum_input_jet_orders": [4],
        },
        {
            "node_id": "N_diff_linear",
            "operation": "formal_adjoint_diff_gauge_map",
            "inputs": ["gbar"],
            "parameters": {
                "formula": "H^ab partial_lambda gbar_ab-2 partial_a(H^ab gbar_lambda_b)"
            },
            "declared_output_type": "h_star_to_covector_density",
            "maximum_input_jet_orders": [1],
        },
        {
            "node_id": "N_weyl_linear",
            "operation": "formal_adjoint_weyl_gauge_map",
            "inputs": ["gbar"],
            "parameters": {"formula": "2 gbar_ab H^ab"},
            "declared_output_type": "h_star_to_scalar_density",
            "maximum_input_jet_orders": [0],
        },
    ]


def canonical_ast() -> dict[str, object]:
    nodes = canonical_nodes()
    components = [
        {"component_id": "q1_h_c", "output": "h", "input": "c", "operator_node": "R_diff", "coefficient": 1},
        {"component_id": "q1_h_omega", "output": "h", "input": "omega", "operator_node": "R_weyl", "coefficient": 1},
        {"component_id": "q1_hstar_h", "output": "h_star", "input": "h", "operator_node": "B_linear", "coefficient": 1},
        {"component_id": "q1_cstar_hstar", "output": "c_star", "input": "h_star", "operator_node": "N_diff_linear", "coefficient": 1},
        {"component_id": "q1_omegastar_hstar", "output": "omega_star", "input": "h_star", "operator_node": "N_weyl_linear", "coefficient": 1},
    ]
    return {
        "schema": "strict-pure-weyl-local-q1-ast-v1",
        "expression_schema_version": EXPRESSION_SCHEMA_VERSION,
        "coefficient_field": "Q",
        "background_condition": "E_g(gbar)=0",
        "nodes": nodes,
        "components": components,
        "zero_output_rows": ["c", "omega"],
        "canonical_nodes_sha256": digest(nodes),
        "canonical_components_sha256": digest(components),
    }


def validate_ast(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or value != canonical_ast():
        raise LocalQ1Error("local q1 AST is not the canonical v1 payload")
    for component in value["components"]:
        output, input_ = component["output"], component["input"]
        if DEGREES[output] - DEGREES[input_] != 1:
            raise LocalQ1Error(f"non-degree-one component: {component['component_id']}")
        if (PARITIES[output] - PARITIES[input_] - 1) % 2:
            raise LocalQ1Error(f"parity failure: {component['component_id']}")
    return value


def vector_fixture(seed: int, order: int = 5) -> dict[int, point.Jet]:
    words = (
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
        (2, 1, 0, 0),
        (0, 1, 2, 0),
        (1, 0, 0, 3),
        (2, 1, 1, 1),
    )
    return {
        mu: point.Jet.coordinate_series(
            order,
            {
                word: Fraction((seed + 3 * mu + 5 * index) % 13 - 6, (mu + index) % 4 + 1)
                for index, word in enumerate(words)
            },
        )
        for mu in range(DIMENSION)
    }


def scalar_fixture(seed: int) -> dict[tuple[int, int, int, int], Fraction]:
    words = (
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 0, 2),
        (1, 1, 1, 1),
        (0, 0, 0, 4),
    )
    return {
        word: Fraction((seed + 7 * index) % 17 - 8, index % 4 + 1)
        for index, word in enumerate(words)
    }


def _plain_metric_jets(values: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {
            alpha: coefficient
            for a_degree, b_degree, alpha, coefficient in values[pair].terms
            if a_degree == b_degree == 0
        }
        for pair in point.PAIRS
    }


def diff_gauge_direction(
    background: Mapping[tuple[int, int], point.Jet], seed: int
) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Return the exact normalized jets of ``L_c gbar``."""

    order = min(value.order for value in background.values())
    if order < 5:
        raise LocalQ1Error("Diff gauge fixture requires background five-jets")
    vector = vector_fixture(seed, order)
    values = {}
    for a, b in point.PAIRS:
        values[(a, b)] = point.sum_jets(
            (
                vector[rho] * background[(a, b)].derivative(rho)
                + background[(rho, b)] * vector[rho].derivative(a)
                + background[(a, rho)] * vector[rho].derivative(b)
                for rho in range(DIMENSION)
            ),
            order=4,
        )
    return _plain_metric_jets(values)


def weyl_gauge_direction(
    background: Mapping[tuple[int, int], point.Jet], seed: int
) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Return the exact normalized jets of ``2 omega gbar``."""

    omega = point.Jet.coordinate_series(min(value.order for value in background.values()), scalar_fixture(seed))
    return _plain_metric_jets(
        {pair: background[pair].scale(2) * omega for pair in point.PAIRS}
    )


def linearized_euler(
    direction: point.MetricJets,
    background: Mapping[tuple[int, int], point.Jet],
) -> dict[tuple[int, int], Fraction]:
    return point.bach_euler_density_coefficient(direction, {}, 1, 0, background=background)


def unary_noether_defects(
    direction: point.MetricJets,
    background: Mapping[tuple[int, int], point.Jet],
) -> tuple[dict[int, Fraction], Fraction]:
    """Evaluate the linearized Diff and Weyl Noether compositions."""

    metric, density = point._bach_euler_density_jets(
        direction, {}, background=background, output_coordinate_order=1
    )
    diff = {}
    for covector in range(DIMENSION):
        first = point.sum_jets(
            (
                density[(a, b)] * metric[(a, b)].derivative(covector)
                for a, b in product(range(DIMENSION), repeat=2)
            ),
            order=0,
        )
        divergence = point.sum_jets(
            (
                (density[(a, b)] * metric[(covector, b)]).derivative(a)
                for a, b in product(range(DIMENSION), repeat=2)
            ),
            order=0,
        )
        diff[covector] = (first - divergence.scale(2)).coefficient(1, 0)
    trace = point.sum_jets(
        (
            metric[(a, b)] * density[(a, b)]
            for a, b in product(range(DIMENSION), repeat=2)
        ),
        order=0,
    ).coefficient(1, 0)
    return diff, trace


def background_euler(
    background: Mapping[tuple[int, int], point.Jet]
) -> dict[tuple[int, int], Fraction]:
    return point.bach_euler_density_coefficient({}, {}, 0, 0, background=background)


def serialize_symmetric(values: Mapping[tuple[int, int], Fraction]) -> list[str]:
    return [str(values[pair]) for pair in point.PAIRS]


def exact_fixture_record(
    name: str,
    background: Mapping[tuple[int, int], point.Jet],
    *,
    vector_seed: int,
    scalar_seed: int,
    metric_seed: int,
) -> dict[str, object]:
    """Replay every nontrivial ``q1^2`` composition on one background."""

    background_zero = background_euler(background)
    diff_gauge = linearized_euler(diff_gauge_direction(background, vector_seed), background)
    weyl_gauge = linearized_euler(weyl_gauge_direction(background, scalar_seed), background)
    diff_noether, weyl_noether = unary_noether_defects(point.sparse_fixture(metric_seed), background)
    checks = {
        "background_Bach_flat": not any(background_zero.values()),
        "B_linear_after_R_diff_zero": not any(diff_gauge.values()),
        "B_linear_after_R_weyl_zero": not any(weyl_gauge.values()),
        "N_diff_linear_after_B_linear_zero": not any(diff_noether.values()),
        "N_weyl_linear_after_B_linear_zero": weyl_noether == 0,
    }
    if not all(checks.values()):
        raise LocalQ1Error(f"{name}: q1 square fixture failed: {checks}")
    payload = {
        "background": serialize_symmetric(background_zero),
        "diff_gauge": serialize_symmetric(diff_gauge),
        "weyl_gauge": serialize_symmetric(weyl_gauge),
        "diff_noether": [str(diff_noether[index]) for index in range(DIMENSION)],
        "weyl_noether": str(weyl_noether),
    }
    return {
        "background": name,
        "vector_seed": vector_seed,
        "scalar_seed": scalar_seed,
        "metric_seed": metric_seed,
        "checks": checks,
        "zero_payload_sha256": digest(payload),
    }


def standard_backgrounds(order: int = 5) -> Sequence[tuple[str, Mapping[tuple[int, int], point.Jet], int, int, int]]:
    return (
        ("conformal_cylinder", point.cylinder_background(order), 2, 3, 4),
        ("minkowski", point.flat_background(order), 3, 4, 5),
        ("flat_brinkmann", point.brinkmann_background(order), 4, 5, 6),
    )
