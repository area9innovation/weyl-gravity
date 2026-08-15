#!/usr/bin/env python3
"""Exact typed local receiver for the strict arity-two identity ``[q1,q2]=0``.

The receiver composes the portable Bach-flat unary maps with the ordered
six-row bilinear ledger on deterministic rational coordinate jets.  It is
independent of the legacy finite-dimensional Cartan helper: local operators
must propagate coordinate jets and apply the Leibniz rule, not merely multiply
matrices.
"""

from __future__ import annotations

from collections import defaultdict
import copy
from fractions import Fraction
from itertools import product
from typing import Any, Mapping, Sequence

try:
    from . import cylinder_polarized_bach_evaluator as point
    from .local_q1_bach_flat import scalar_fixture, vector_fixture
except ImportError:  # direct path execution
    import cylinder_polarized_bach_evaluator as point
    from local_q1_bach_flat import scalar_fixture, vector_fixture


DIMENSION = 4
Field = Any


def _extract(value: point.Jet, a_degree: int, b_degree: int, order: int) -> point.Jet:
    return point.Jet.from_terms(
        order,
        (
            (0, 0, alpha, coefficient)
            for a, b, alpha, coefficient in value.terms
            if a == a_degree and b == b_degree
        ),
    )


def _sym(values: Mapping[tuple[int, int], point.Jet], a: int, b: int) -> point.Jet:
    return values[tuple(sorted((a, b)))]


def _series(seed: int, order: int) -> point.Jet:
    base = scalar_fixture(seed)
    extra = {
        (2, 1, 1, 1): Fraction(seed % 9 - 4, 3),
        (1, 2, 2, 0): Fraction((2 * seed) % 11 - 5, 4),
    }
    return point.Jet.coordinate_series(order, {**base, **extra})


def field_fixture(symbol: str, seed: int, order: int = 5) -> Field:
    if symbol == "h":
        return {
            pair: _series(seed + 3 * index, order)
            for index, pair in enumerate(point.PAIRS)
        }
    if symbol == "c":
        return vector_fixture(seed, order)
    if symbol == "omega":
        return _series(seed, order)
    if symbol == "h_star":
        return {
            pair: _series(seed + 5 * index, order)
            for index, pair in enumerate(point.PAIRS)
        }
    if symbol == "c_star":
        return {index: _series(seed + 7 * index, order) for index in range(DIMENSION)}
    if symbol == "omega_star":
        return _series(seed, order)
    raise ValueError(f"unknown field symbol: {symbol}")


def _metric_payload(values: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {
            alpha: coefficient
            for a, b, alpha, coefficient in _sym(values, *pair).terms
            if a == b == 0
        }
        for pair in point.PAIRS
    }


def _background_metric(background: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], point.Jet]:
    return {pair: background[pair] for pair in point.PAIRS}


def _zero_like(symbol: str, order: int) -> Field:
    zero = point.Jet.zero(order)
    if symbol in {"h", "h_star"}:
        return {pair: zero for pair in point.PAIRS}
    if symbol == "c":
        return {index: zero for index in range(DIMENSION)}
    if symbol == "c_star":
        return {index: zero for index in range(DIMENSION)}
    return zero


def _add_fields(symbol: str, values: Sequence[Field], order: int) -> Field:
    if not values:
        return _zero_like(symbol, order)
    if symbol in {"h", "h_star"}:
        return {pair: point.sum_jets((value[pair] for value in values), order=order) for pair in point.PAIRS}
    if symbol in {"c", "c_star"}:
        return {index: point.sum_jets((value[index] for value in values), order=order) for index in range(DIMENSION)}
    return point.sum_jets(values, order=order)


def _scale_field(symbol: str, value: Field, coefficient: int, order: int) -> Field:
    if symbol in {"h", "h_star"}:
        return {pair: value[pair].scale(coefficient).truncate(order) for pair in point.PAIRS}
    if symbol in {"c", "c_star"}:
        return {index: value[index].scale(coefficient).truncate(order) for index in range(DIMENSION)}
    return value.scale(coefficient).truncate(order)


def apply_q1(
    component_id: str,
    value: Field,
    background: Mapping[tuple[int, int], point.Jet],
    output_order: int,
) -> Field:
    if component_id == "q1_h_c":
        return {
            (a, b): point.sum_jets(
                (
                    value[rho] * background[(a, b)].derivative(rho)
                    + background[(rho, b)] * value[rho].derivative(a)
                    + background[(a, rho)] * value[rho].derivative(b)
                    for rho in range(DIMENSION)
                ),
                order=output_order,
            )
            for a, b in point.PAIRS
        }
    if component_id == "q1_h_omega":
        return {
            pair: (background[pair] * value).scale(2).truncate(output_order)
            for pair in point.PAIRS
        }
    if component_id == "q1_hstar_h":
        _, density = point._bach_euler_density_jets(
            _metric_payload(value),
            {},
            background=background,
            output_coordinate_order=output_order,
        )
        return {pair: _extract(density[pair], 1, 0, output_order) for pair in point.PAIRS}
    if component_id == "q1_cstar_hstar":
        return {
            covector: (
                point.sum_jets(
                    (
                        _sym(value, a, b) * background[(a, b)].derivative(covector)
                        for a, b in product(range(DIMENSION), repeat=2)
                    ),
                    order=output_order,
                )
                - point.sum_jets(
                    (
                        (_sym(value, a, b) * background[(covector, b)]).derivative(a)
                        for a, b in product(range(DIMENSION), repeat=2)
                    ),
                    order=output_order,
                ).scale(2)
            )
            for covector in range(DIMENSION)
        }
    if component_id == "q1_omegastar_hstar":
        return point.sum_jets(
            (
                background[(a, b)] * _sym(value, a, b).scale(2)
                for a, b in product(range(DIMENSION), repeat=2)
            ),
            order=output_order,
        )
    raise ValueError(f"unknown q1 component: {component_id}")


def apply_primary_q2(
    primary_id: str,
    left: Field,
    right: Field,
    output_order: int,
    *,
    background: Mapping[tuple[int, int], point.Jet] | None = None,
) -> Field:
    if primary_id == "q2_c_cc":
        return {
            mu: point.sum_jets(
                (
                    left[rho] * right[mu].derivative(rho)
                    - right[rho] * left[mu].derivative(rho)
                    for rho in range(DIMENSION)
                ),
                order=output_order,
            )
            for mu in range(DIMENSION)
        }
    if primary_id == "q2_omega_comega":
        return point.sum_jets(
            (left[rho] * right.derivative(rho) for rho in range(DIMENSION)),
            order=output_order,
        )
    if primary_id == "q2_h_ch":
        return {
            (a, b): point.sum_jets(
                (
                    left[rho] * _sym(right, a, b).derivative(rho)
                    + _sym(right, rho, b) * left[rho].derivative(a)
                    + _sym(right, a, rho) * left[rho].derivative(b)
                    for rho in range(DIMENSION)
                ),
                order=output_order,
            )
            for a, b in point.PAIRS
        }
    if primary_id == "q2_h_omegah":
        return {pair: (left * right[pair]).scale(2).truncate(output_order) for pair in point.PAIRS}
    if primary_id == "q2_hstar_hh":
        if background is None:
            raise ValueError("the Bach Hessian requires an explicit background")
        _, density = point._bach_euler_density_jets(
            _metric_payload(left),
            _metric_payload(right),
            background=background,
            output_coordinate_order=output_order,
        )
        return {pair: _extract(density[pair], 1, 1, output_order) for pair in point.PAIRS}
    if primary_id == "q2_hstar_chstar":
        return {
            (mu, nu): point.sum_jets(
                (
                    left[rho] * _sym(right, mu, nu).derivative(rho)
                    - _sym(right, rho, nu) * left[mu].derivative(rho)
                    - _sym(right, mu, rho) * left[nu].derivative(rho)
                    + left[rho].derivative(rho) * _sym(right, mu, nu)
                    for rho in range(DIMENSION)
                ),
                order=output_order,
            )
            for mu, nu in point.PAIRS
        }
    if primary_id == "q2_hstar_omegahstar":
        return {pair: (left * right[pair]).scale(-2).truncate(output_order) for pair in point.PAIRS}
    if primary_id == "q2_cstar_hhstar":
        return {
            covector: (
                point.sum_jets(
                    (
                        _sym(right, mu, nu) * _sym(left, mu, nu).derivative(covector)
                        for mu, nu in product(range(DIMENSION), repeat=2)
                    ),
                    order=output_order,
                )
                - point.sum_jets(
                    (
                        (_sym(right, mu, nu) * _sym(left, covector, nu)).derivative(mu)
                        for mu, nu in product(range(DIMENSION), repeat=2)
                    ),
                    order=output_order,
                ).scale(2)
            )
            for covector in range(DIMENSION)
        }
    if primary_id == "q2_cstar_ccstar":
        return {
            covector: point.sum_jets(
                (
                    left[rho] * right[covector].derivative(rho)
                    + right[rho] * left[rho].derivative(covector)
                    + left[rho].derivative(rho) * right[covector]
                    for rho in range(DIMENSION)
                ),
                order=output_order,
            )
            for covector in range(DIMENSION)
        }
    if primary_id == "q2_cstar_omegaomegastar":
        return {
            covector: right * left.derivative(covector)
            for covector in range(DIMENSION)
        }
    if primary_id == "q2_omegastar_hhstar":
        return point.sum_jets(
            (
                _sym(left, mu, nu) * _sym(right, mu, nu).scale(2)
                for mu, nu in product(range(DIMENSION), repeat=2)
            ),
            order=output_order,
        )
    if primary_id == "q2_omegastar_comegastar":
        return point.sum_jets(
            ((left[rho] * right).derivative(rho) for rho in range(DIMENSION)),
            order=output_order,
        )
    raise ValueError(f"unknown q2 primary component: {primary_id}")


def q1_required_input_order(component_id: str, output_order: int) -> int:
    return output_order + {
        "q1_h_c": 1,
        "q1_h_omega": 0,
        "q1_hstar_h": 4,
        "q1_cstar_hstar": 1,
        "q1_omegastar_hstar": 0,
    }[component_id]


def q2_required_input_orders(primary: Mapping[str, Any], output_order: int) -> tuple[int, int]:
    left, right = primary["maximum_input_jet_orders"]
    return output_order + left, output_order + right


def enumerate_channels(
    q1_components: Sequence[Mapping[str, Any]],
    ordered_q2: Sequence[Mapping[str, Any]],
    parities: Mapping[str, int],
) -> list[dict[str, Any]]:
    paths: dict[tuple[str, tuple[str, str]], list[dict[str, Any]]] = defaultdict(list)
    for q2 in ordered_q2:
        left, right = q2["inputs"]
        coefficient = q2["coefficient_relative_to_primary"]
        for q1 in q1_components:
            if q1["input"] == q2["output"]:
                paths[(q1["output"], (left, right))].append(
                    {"kind": "post", "q1_component_id": q1["component_id"], "q2_component_id": q2["component_id"], "multiplier": coefficient}
                )
            if q1["output"] == left:
                paths[(q2["output"], (q1["input"], right))].append(
                    {"kind": "pre_left", "q1_component_id": q1["component_id"], "q2_component_id": q2["component_id"], "multiplier": coefficient}
                )
            if q1["output"] == right:
                second_sign = -1 if parities[left] else 1
                paths[(q2["output"], (left, q1["input"]))].append(
                    {"kind": "pre_right", "q1_component_id": q1["component_id"], "q2_component_id": q2["component_id"], "multiplier": second_sign * coefficient}
                )
    return [
        {"output": output, "inputs": list(inputs), "paths": rows}
        for (output, inputs), rows in sorted(paths.items())
    ]


def _q2_application(
    q2_record: Mapping[str, Any],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    left: Field,
    right: Field,
    output_order: int,
    background: Mapping[tuple[int, int], point.Jet],
) -> Field:
    primary = primary_by_id[q2_record["primary_id"]]
    if q2_record["orientation"] == "KOSZUL_SWAP":
        left, right = right, left
    return apply_primary_q2(
        primary["primary_id"], left, right, output_order, background=background
    )


def evaluate_channel(
    channel: Mapping[str, Any],
    q1_by_id: Mapping[str, Mapping[str, Any]],
    q2_by_id: Mapping[str, Mapping[str, Any]],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    background: Mapping[tuple[int, int], point.Jet],
    *,
    left_seed: int,
    right_seed: int,
) -> Field:
    left_symbol, right_symbol = channel["inputs"]
    left = field_fixture(left_symbol, left_seed)
    right = field_fixture(right_symbol, right_seed)
    terms = []
    for path in channel["paths"]:
        q1 = q1_by_id[path["q1_component_id"]]
        q2 = q2_by_id[path["q2_component_id"]]
        primary = primary_by_id[q2["primary_id"]]
        if path["kind"] == "post":
            middle_order = q1_required_input_order(q1["component_id"], 0)
            middle = _q2_application(
                q2, primary_by_id, left, right, middle_order, background
            )
            value = apply_q1(q1["component_id"], middle, background, 0)
        else:
            required = q2_required_input_orders(primary, 0)
            if q2["orientation"] == "KOSZUL_SWAP":
                required = (required[1], required[0])
            if path["kind"] == "pre_left":
                changed = apply_q1(q1["component_id"], left, background, required[0])
                value = _q2_application(
                    q2, primary_by_id, changed, right, 0, background
                )
            else:
                changed = apply_q1(q1["component_id"], right, background, required[1])
                value = _q2_application(
                    q2, primary_by_id, left, changed, 0, background
                )
        terms.append(_scale_field(channel["output"], value, path["multiplier"], 0))
    return _add_fields(channel["output"], terms, 0)


def serialize_field(symbol: str, value: Field) -> list[str]:
    if symbol in {"h", "h_star"}:
        return [str(value[pair].constant_term) for pair in point.PAIRS]
    if symbol in {"c", "c_star"}:
        return [str(value[index].constant_term) for index in range(DIMENSION)]
    return [str(value.constant_term)]


def is_zero_field(symbol: str, value: Field) -> bool:
    return all(item == "0" for item in serialize_field(symbol, value))


def channel_id(channel: Mapping[str, Any]) -> str:
    return "q1q2__" + channel["output"] + "__" + "__".join(channel["inputs"])


def fixture_record(
    channels: Sequence[Mapping[str, Any]],
    q1_by_id: Mapping[str, Mapping[str, Any]],
    q2_by_id: Mapping[str, Mapping[str, Any]],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    background_name: str,
    background: Mapping[tuple[int, int], point.Jet],
    *,
    left_seed: int,
    right_seed: int,
) -> dict[str, Any]:
    rows = []
    for channel in channels:
        value = evaluate_channel(
            channel,
            q1_by_id,
            q2_by_id,
            primary_by_id,
            background,
            left_seed=left_seed,
            right_seed=right_seed,
        )
        output = serialize_field(channel["output"], value)
        rows.append(
            {
                "channel_id": channel_id(channel),
                "output": channel["output"],
                "inputs": channel["inputs"],
                "path_count": len(channel["paths"]),
                "defect": output,
                "defect_zero": all(item == "0" for item in output),
            }
        )
    if not all(row["defect_zero"] for row in rows):
        raise ValueError(f"{background_name}: nonzero q1q2 fixture channel")
    return {
        "background": background_name,
        "left_seed": left_seed,
        "right_seed": right_seed,
        "channel_count": len(rows),
        "path_count": sum(row["path_count"] for row in rows),
        "all_channels_zero": True,
        "rows": rows,
    }


def mutation_record(
    channel: Mapping[str, Any],
    q1_by_id: Mapping[str, Mapping[str, Any]],
    q2_by_id: Mapping[str, Mapping[str, Any]],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    background: Mapping[tuple[int, int], point.Jet],
    *,
    path_index: int,
    left_seed: int,
    right_seed: int,
) -> dict[str, Any]:
    mutated = copy.deepcopy(channel)
    path = mutated["paths"][path_index]
    old = path["multiplier"]
    path["multiplier"] = -old
    value = evaluate_channel(
        mutated,
        q1_by_id,
        q2_by_id,
        primary_by_id,
        background,
        left_seed=left_seed,
        right_seed=right_seed,
    )
    output = serialize_field(mutated["output"], value)
    if all(item == "0" for item in output):
        raise ValueError(f"mutation did not expose channel {channel_id(channel)}")
    return {
        "channel_id": channel_id(channel),
        "mutated_path_index": path_index,
        "old_multiplier": old,
        "new_multiplier": -old,
        "defect": output,
        "nonzero_component_count": sum(item != "0" for item in output),
    }
