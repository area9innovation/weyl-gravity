"""Typed natural-operator AST and exact receiver for the pure-Weyl Bach row.

The large cylinder coefficient table is useful as a regression oracle, but a
table in one frame is not a coordinate-independent definition.  This module
provides the missing semantic layer.  Its small DAG is built only from the
metric, its Levi-Civita geometry, tensor contractions, the four-dimensional
Schouten/Weyl/Cotton/Bach construction, the metric volume density, and exact
mixed Frechet coefficient extraction.

The receiver evaluates the DAG over the exact square-free bivariate jet
algebra used by :mod:`cylinder_polarized_bach_evaluator`.  It intentionally
contains no inverse differential operator and accepts no floating-point data.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from typing import Any, Mapping, Sequence

try:
    from . import cylinder_polarized_bach_evaluator as point
except ImportError:  # direct path execution
    import cylinder_polarized_bach_evaluator as point


EXPRESSION_SCHEMA_VERSION = "strict-pure-weyl-bach-natural-operator-v1"
DIMENSION = 4

METRIC = "symmetric_covariant_2"
INVERSE = "symmetric_contravariant_2"
GEOMETRY = "levi_civita_geometry_bundle"
SCHOUTEN_WEYL = "schouten_cov2_and_weyl_cov4_bundle"
COTTON = "cotton_covariant_3"
BACH = "symmetric_covariant_2"
VOLUME = "absolute_metric_density_weight_plus_1"
RAISED = "symmetric_contravariant_2"
EULER = "symmetric_contravariant_density_weight_plus_1"
POLARIZED_EULER = "symmetric_bilinear_metric_jet_operator_to_" + EULER


class NaturalOperatorAstError(ValueError):
    """Raised when the typed natural-operator payload is not canonical."""


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _reject_floats(value: object, path: str = "$") -> None:
    if isinstance(value, float):
        raise NaturalOperatorAstError(f"floating-point value forbidden at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise NaturalOperatorAstError(f"non-string key at {path}")
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def canonical_nodes() -> list[dict[str, object]]:
    """Return the unique v1 natural Bach DAG in topological order."""

    return [
        {
            "node_id": "g_ab",
            "operation": "metric_two_parameter_family",
            "inputs": [],
            "parameters": {"base": "gbar", "left_direction": "h_left", "right_direction": "h_right", "formal_parameters": ["a", "b"]},
            "declared_output_type": METRIC,
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "g_inverse",
            "operation": "inverse_metric",
            "inputs": ["g_ab"],
            "parameters": {},
            "declared_output_type": INVERSE,
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "geometry",
            "operation": "levi_civita_geometry",
            "inputs": ["g_ab", "g_inverse"],
            "parameters": {"curvature_sign": "R^a_bcd=partial_c Gamma^a_db-partial_d Gamma^a_cb+Gamma^e_db Gamma^a_ce-Gamma^e_cb Gamma^a_de"},
            "declared_output_type": GEOMETRY,
            "declared_metric_jet_order": 2,
        },
        {
            "node_id": "P_and_C",
            "operation": "schouten_and_weyl_4d",
            "inputs": ["geometry"],
            "parameters": {"schouten": "P_ab=(Ric_ab-(R/6)g_ab)/2", "weyl": "C_abcd=R_abcd-(g_ac P_db-g_ad P_cb-g_bc P_da+g_bd P_ca)"},
            "declared_output_type": SCHOUTEN_WEYL,
            "declared_metric_jet_order": 2,
        },
        {
            "node_id": "Cotton",
            "operation": "cotton_4d",
            "inputs": ["geometry", "P_and_C"],
            "parameters": {"formula": "A_cab=nabla_c P_ab-nabla_a P_bc"},
            "declared_output_type": COTTON,
            "declared_metric_jet_order": 3,
        },
        {
            "node_id": "B_lower",
            "operation": "bach_4d",
            "inputs": ["geometry", "P_and_C", "Cotton"],
            "parameters": {"formula": "B_ab=nabla^c A_cab+P^cd C_acbd"},
            "declared_output_type": BACH,
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "B_upper",
            "operation": "raise_symmetric_two_tensor",
            "inputs": ["g_inverse", "B_lower"],
            "parameters": {"formula": "B^ab=g^ac g^bd B_cd"},
            "declared_output_type": RAISED,
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "volume",
            "operation": "absolute_metric_volume_density",
            "inputs": ["g_ab"],
            "parameters": {"formula": "sqrt(abs(det(g)))"},
            "declared_output_type": VOLUME,
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "E_g",
            "operation": "densitize_and_scale",
            "inputs": ["volume", "B_upper"],
            "parameters": {"coefficient": -2, "formula": "E^ab=-2 sqrt(abs(g)) B^ab"},
            "declared_output_type": EULER,
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "K_hh",
            "operation": "mixed_frechet_coefficient",
            "inputs": ["E_g"],
            "parameters": {"coefficient": "[a*b]", "left_direction": "h_left", "right_direction": "h_right", "hidden_factorial": False},
            "declared_output_type": POLARIZED_EULER,
            "declared_metric_jet_order": 4,
        },
    ]


def canonical_ast() -> dict[str, object]:
    nodes = canonical_nodes()
    value: dict[str, object] = {
        "schema": "strict-pure-weyl-bach-natural-operator-ast-v1",
        "expression_schema_version": EXPRESSION_SCHEMA_VERSION,
        "spacetime_dimension": DIMENSION,
        "coefficient_field": "Q",
        "nodes": nodes,
        "root_node": "K_hh",
        "canonical_node_sha256": _digest(nodes),
    }
    return value


def validate_ast(payload: object) -> dict[str, object]:
    """Validate exact fields, topological typing, jet order, and canonical DAG."""

    _reject_floats(payload)
    fields = {"schema", "expression_schema_version", "spacetime_dimension", "coefficient_field", "nodes", "root_node", "canonical_node_sha256"}
    if not isinstance(payload, dict) or set(payload) != fields:
        raise NaturalOperatorAstError("natural-operator AST has the wrong field set")
    if payload["schema"] != "strict-pure-weyl-bach-natural-operator-ast-v1" or payload["expression_schema_version"] != EXPRESSION_SCHEMA_VERSION:
        raise NaturalOperatorAstError("unsupported natural-operator AST version")
    if payload["spacetime_dimension"] != DIMENSION or payload["coefficient_field"] != "Q":
        raise NaturalOperatorAstError("the v1 Bach AST is exact and four-dimensional")
    nodes = payload["nodes"]
    if nodes != canonical_nodes():
        raise NaturalOperatorAstError("natural-operator nodes are not the canonical v1 DAG")
    if payload["root_node"] != "K_hh" or payload["canonical_node_sha256"] != _digest(nodes):
        raise NaturalOperatorAstError("natural-operator root or canonical hash drift")
    seen: set[str] = set()
    for node in nodes:
        if set(node) != {"node_id", "operation", "inputs", "parameters", "declared_output_type", "declared_metric_jet_order"}:
            raise NaturalOperatorAstError("natural-operator node has the wrong field set")
        if node["node_id"] in seen or any(parent not in seen for parent in node["inputs"]):
            raise NaturalOperatorAstError("natural-operator DAG is duplicated or not topological")
        seen.add(node["node_id"])
    return payload


def _cotton(
    geometry: Mapping[str, object],
    schouten: Mapping[tuple[int, int], point.Jet],
) -> dict[tuple[int, int, int], point.Jet]:
    gamma = geometry["connection"]
    assert isinstance(gamma, Mapping)
    curvature_order = next(iter(schouten.values())).order
    cotton_order = curvature_order - 1
    first = {}
    for axis, a, b in product(range(DIMENSION), repeat=3):
        first[(axis, a, b)] = (
            schouten[(a, b)].derivative(axis)
            - point.sum_jets(
                (
                    gamma[(replacement, axis, a)] * schouten[(replacement, b)]
                    + gamma[(replacement, axis, b)] * schouten[(a, replacement)]
                    for replacement in range(DIMENSION)
                ),
                order=cotton_order,
            )
        ).truncate(cotton_order)
    return {
        (c, a, b): first[(c, a, b)] - first[(a, b, c)]
        for c, a, b in product(range(DIMENSION), repeat=3)
    }


def _bach(
    geometry: Mapping[str, object],
    schouten: Mapping[tuple[int, int], point.Jet],
    weyl: Mapping[tuple[int, int, int, int], point.Jet],
    cotton: Mapping[tuple[int, int, int], point.Jet],
) -> dict[tuple[int, int], point.Jet]:
    inverse, gamma = geometry["inverse"], geometry["connection"]
    assert isinstance(inverse, Mapping) and isinstance(gamma, Mapping)
    bach_order = next(iter(cotton.values())).order - 1
    divergence = {}
    for a, b in product(range(DIMENSION), repeat=2):
        rows = []
        for outer, inner in product(range(DIMENSION), repeat=2):
            derivative = cotton[(inner, a, b)].derivative(outer) - point.sum_jets(
                (
                    gamma[(replacement, outer, inner)] * cotton[(replacement, a, b)]
                    + gamma[(replacement, outer, a)] * cotton[(inner, replacement, b)]
                    + gamma[(replacement, outer, b)] * cotton[(inner, a, replacement)]
                    for replacement in range(DIMENSION)
                ),
                order=bach_order,
            )
            rows.append(inverse[(outer, inner)] * derivative)
        divergence[(a, b)] = point.sum_jets(rows, order=bach_order)
    schouten_up = {
        (c, d): point.sum_jets(
            (
                inverse[(c, left)] * inverse[(d, right)] * schouten[(left, right)]
                for left, right in product(range(DIMENSION), repeat=2)
            ),
            order=bach_order,
        )
        for c, d in product(range(DIMENSION), repeat=2)
    }
    return {
        (a, b): (
            divergence[(a, b)]
            + point.sum_jets(
                (schouten_up[(c, d)] * weyl[(a, c, b, d)] for c, d in product(range(DIMENSION), repeat=2)),
                order=bach_order,
            )
        ).truncate(bach_order)
        for a, b in product(range(DIMENSION), repeat=2)
    }


def evaluate_ast(
    payload: Mapping[str, object],
    left: point.MetricJets,
    right: point.MetricJets,
    *,
    background: Mapping[tuple[int, int], point.Jet] | None = None,
) -> dict[tuple[int, int], Fraction]:
    """Execute the canonical DAG and return its exact mixed coefficient."""

    validate_ast(payload)
    background = point.cylinder_background(4) if background is None else background
    if min(value.order for value in background.values()) < 4:
        raise NaturalOperatorAstError("Bach evaluation requires background metric four-jets")
    values: dict[str, object] = {}
    for node in payload["nodes"]:
        operation = node["operation"]
        inputs = [values[parent] for parent in node["inputs"]]
        if operation == "metric_two_parameter_family":
            result = point.perturbed_metric(background, left, right)
        elif operation == "inverse_metric":
            result = point.inverse_matrix(inputs[0])
        elif operation == "levi_civita_geometry":
            result = point._geometry(inputs[0])
            if result["inverse"] != inputs[1]:
                raise NaturalOperatorAstError("independent inverse-metric nodes disagree")
        elif operation == "schouten_and_weyl_4d":
            result = point._schouten_and_weyl(inputs[0])
        elif operation == "cotton_4d":
            result = _cotton(inputs[0], inputs[1][0])
        elif operation == "bach_4d":
            result = _bach(inputs[0], inputs[1][0], inputs[1][1], inputs[2])
        elif operation == "raise_symmetric_two_tensor":
            inverse, lower = inputs
            order = min(value.order for value in lower.values())
            result = {
                (a, b): point.sum_jets(
                    (inverse[(a, c)] * inverse[(b, d)] * lower[(c, d)] for c, d in product(range(DIMENSION), repeat=2)),
                    order=order,
                )
                for a, b in product(range(DIMENSION), repeat=2)
            }
        elif operation == "absolute_metric_volume_density":
            result = point.determinant(inputs[0]).scale(-1).sqrt().truncate(0)
        elif operation == "densitize_and_scale":
            volume, raised = inputs
            result = {pair: volume * value.scale(-2) for pair, value in raised.items()}
        elif operation == "mixed_frechet_coefficient":
            result = {pair: inputs[0][pair].coefficient(1, 1) for pair in point.PAIRS}
        else:  # protected by canonical validation
            raise NaturalOperatorAstError(f"unknown natural operation: {operation}")
        values[node["node_id"]] = result
    root = values[payload["root_node"]]
    assert isinstance(root, dict)
    return root


def transform_metric_jets(
    values: point.MetricJets,
    permutation: Sequence[int],
    signs: Sequence[int],
) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Pull covariant metric jets through ``x[p[i]]=sign[i] y[i]``."""

    if sorted(permutation) != list(range(DIMENSION)) or len(signs) != DIMENSION or any(sign not in (-1, 1) for sign in signs):
        raise ValueError("expected a signed coordinate permutation")
    output: dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]] = {}
    for i, j in point.PAIRS:
        old_pair = tuple(sorted((permutation[i], permutation[j])))
        component_sign = signs[i] * signs[j]
        row = {}
        for old_word, coefficient in values.get(old_pair, {}).items():
            new_word = tuple(old_word[permutation[index]] for index in range(DIMENSION))
            derivative_sign = 1
            for axis in range(DIMENSION):
                derivative_sign *= product_sign(signs[axis], new_word[axis])
            row[new_word] = row.get(new_word, Fraction(0)) + Fraction(coefficient) * component_sign * derivative_sign
        output[(i, j)] = {word: value for word, value in row.items() if value}
    return output


def product_sign(sign: int, exponent: int) -> int:
    return -1 if sign == -1 and exponent % 2 else 1


def transform_background(
    background: Mapping[tuple[int, int], point.Jet],
    permutation: Sequence[int],
    signs: Sequence[int],
) -> dict[tuple[int, int], point.Jet]:
    """Pull an exact background metric jet through a signed permutation."""

    output = {}
    for i, j in product(range(DIMENSION), repeat=2):
        old = background[(permutation[i], permutation[j])]
        terms = []
        for a_degree, b_degree, old_word, coefficient in old.terms:
            new_word = tuple(old_word[permutation[index]] for index in range(DIMENSION))
            sign = signs[i] * signs[j]
            for axis in range(DIMENSION):
                sign *= product_sign(signs[axis], new_word[axis])
            terms.append((a_degree, b_degree, new_word, coefficient * sign))
        output[(i, j)] = point.Jet.from_terms(old.order, terms)
    return output


def transform_output_density(
    values: Mapping[tuple[int, int], Fraction],
    permutation: Sequence[int],
    signs: Sequence[int],
) -> dict[tuple[int, int], Fraction]:
    """Transform a symmetric contravariant weight-one density at a point."""

    return {
        (i, j): Fraction(signs[i] * signs[j]) * values[tuple(sorted((permutation[i], permutation[j])))]
        for i, j in point.PAIRS
    }
