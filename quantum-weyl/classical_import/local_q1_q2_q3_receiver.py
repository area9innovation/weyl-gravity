#!/usr/bin/env python3
"""Exact typed local receiver for the minimal-BV arity-three identity.

This module composes the already certified local q1 and ordered q2 ledgers
with the imported natural q3.  It enumerates every type-compatible path in
``q1 q3 + q2 q2 + q3 q1`` using the same suspended Koszul unshuffle signs as
the classical Berger engine, but evaluates local coordinate jets rather than
finite PBW matrices.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Any, Mapping, Sequence

try:
    from . import cylinder_polarized_bach_evaluator as point
    from . import pure_weyl_cubic_natural_operator as cubic
    from . import local_q1_q2_receiver as lower
except ImportError:  # direct path execution
    import cylinder_polarized_bach_evaluator as point
    import pure_weyl_cubic_natural_operator as cubic
    import local_q1_q2_receiver as lower


Field = Any


_SPARSE_WORDS = (
    (0, 0, 0, 0),
    (1, 0, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 0, 2),
    (1, 1, 0, 1),
    (0, 2, 1, 1),
    (2, 1, 1, 1),
)


def sparse_field_fixture(symbol: str, seed: int, order: int = 9) -> Field:
    """A derivative-sensitive but memory-bounded exact arity-three fixture."""

    def series(index: int) -> point.Jet:
        first = _SPARSE_WORDS[(seed + 2 * index) % len(_SPARSE_WORDS)]
        second = _SPARSE_WORDS[(seed + 3 * index + 3) % len(_SPARSE_WORDS)]
        terms = {
            first: Fraction((seed + index) % 7 - 3, index % 3 + 1),
            second: Fraction((2 * seed + index) % 11 - 5, index % 4 + 1),
        }
        return point.Jet.coordinate_series(order, terms)

    if symbol in {"h", "h_star"}:
        return {pair: series(index) for index, pair in enumerate(point.PAIRS)}
    if symbol in {"c", "c_star"}:
        return {index: series(index) for index in range(4)}
    if symbol in {"omega", "omega_star"}:
        return series(0)
    raise ValueError(f"unknown field symbol: {symbol}")


def enumerate_channels(
    q1_components: Sequence[Mapping[str, Any]],
    ordered_q2: Sequence[Mapping[str, Any]],
    parities: Mapping[str, int],
) -> list[dict[str, Any]]:
    """Return every typed arity-three output/input channel and path."""

    paths: dict[tuple[str, tuple[str, str, str]], list[dict[str, Any]]] = defaultdict(list)

    # q2(q2(-,-),-) with the (12|3), (13|2), (23|1) unshuffles.
    for outer in ordered_q2:
        middle_symbol, last_symbol = outer["inputs"]
        for inner in ordered_q2:
            if inner["output"] != middle_symbol:
                continue
            first_symbol, second_symbol = inner["inputs"]
            base = outer["coefficient_relative_to_primary"] * inner["coefficient_relative_to_primary"]
            unshuffles = (
                ((first_symbol, second_symbol, last_symbol), (0, 1), 2, 1),
                (
                    (first_symbol, last_symbol, second_symbol),
                    (0, 2),
                    1,
                    -1 if parities[second_symbol] * parities[last_symbol] else 1,
                ),
                (
                    (last_symbol, first_symbol, second_symbol),
                    (1, 2),
                    0,
                    -1 if parities[last_symbol] * (parities[first_symbol] + parities[second_symbol]) % 2 else 1,
                ),
            )
            for inputs, inner_positions, last_position, sign in unshuffles:
                paths[(outer["output"], inputs)].append(
                    {
                        "kind": "q2_q2",
                        "outer_q2_component_id": outer["component_id"],
                        "inner_q2_component_id": inner["component_id"],
                        "inner_positions": list(inner_positions),
                        "last_position": last_position,
                        "multiplier": base * sign,
                    }
                )

    # q1(q3(h,h,h)).
    for q1 in q1_components:
        if q1["input"] == "h_star":
            paths[(q1["output"], ("h", "h", "h"))].append(
                {
                    "kind": "q1_q3",
                    "q1_component_id": q1["component_id"],
                    "q3_component_id": "q3_hstar_hhh",
                    "multiplier": 1,
                }
            )

    # q3(q1(-),-,-) in all three slots.  The expected q3 inputs are even h,
    # so the preceding-slot Koszul sign is +1 for every insertion.
    for q1 in q1_components:
        if q1["output"] != "h":
            continue
        for slot in range(3):
            inputs = ["h", "h", "h"]
            inputs[slot] = q1["input"]
            paths[("h_star", tuple(inputs))].append(
                {
                    "kind": "q3_q1",
                    "q1_component_id": q1["component_id"],
                    "q3_component_id": "q3_hstar_hhh",
                    "slot": slot,
                    "multiplier": 1,
                }
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
    return lower.apply_primary_q2(
        primary["primary_id"], left, right, output_order, background=background
    )


def _ordered_required_orders(
    record: Mapping[str, Any],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    output_order: int,
) -> tuple[int, int]:
    orders = lower.q2_required_input_orders(primary_by_id[record["primary_id"]], output_order)
    return (orders[1], orders[0]) if record["orientation"] == "KOSZUL_SWAP" else orders


def _metric_payload(value: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {
            alpha: coefficient
            for a, b, alpha, coefficient in value[pair].terms
            if a == b == 0
        }
        for pair in point.PAIRS
    }


def _hstar_field(
    values: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]],
    order: int,
) -> dict[tuple[int, int], point.Jet]:
    return {
        pair: point.Jet.coordinate_series(order, values[pair])
        for pair in point.PAIRS
    }


def evaluate_channel(
    channel: Mapping[str, Any],
    q1_by_id: Mapping[str, Mapping[str, Any]],
    q2_by_id: Mapping[str, Mapping[str, Any]],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    q3_ast: Mapping[str, Any],
    background: Mapping[tuple[int, int], point.Jet],
    *,
    seeds: tuple[int, int, int],
) -> Field:
    symbols = channel["inputs"]
    # Eight coordinate derivatives suffice for the only possible nested pair
    # of fourth-order Bach operations.  Backgrounds carry the same margin.
    inputs = [sparse_field_fixture(symbol, seed, 9) for symbol, seed in zip(symbols, seeds)]
    terms: list[Field] = []
    for path in channel["paths"]:
        kind = path["kind"]
        if kind == "q2_q2":
            outer = q2_by_id[path["outer_q2_component_id"]]
            inner = q2_by_id[path["inner_q2_component_id"]]
            outer_orders = _ordered_required_orders(outer, primary_by_id, 0)
            inner_positions = path["inner_positions"]
            middle = _q2_application(
                inner,
                primary_by_id,
                inputs[inner_positions[0]],
                inputs[inner_positions[1]],
                outer_orders[0],
                background,
            )
            value = _q2_application(
                outer,
                primary_by_id,
                middle,
                inputs[path["last_position"]],
                0,
                background,
            )
        elif kind == "q1_q3":
            q1 = q1_by_id[path["q1_component_id"]]
            q3_order = lower.q1_required_input_order(q1["component_id"], 0)
            q3 = cubic.evaluate_ast(
                q3_ast,
                *(_metric_payload(item) for item in inputs),
                background=background,
                output_coordinate_order=q3_order,
            )
            value = lower.apply_q1(
                q1["component_id"], _hstar_field(q3, q3_order), background, 0
            )
        elif kind == "q3_q1":
            q1 = q1_by_id[path["q1_component_id"]]
            slot = path["slot"]
            changed = lower.apply_q1(
                q1["component_id"],
                inputs[slot],
                background,
                4,
            )
            metric_inputs = [
                _metric_payload(changed if index == slot else inputs[index])
                for index in range(3)
            ]
            q3 = cubic.evaluate_ast(q3_ast, *metric_inputs, background=background)
            value = _hstar_field(q3, 0)
        else:
            raise ValueError(f"unknown arity-three path kind: {kind}")
        terms.append(lower._scale_field(channel["output"], value, path["multiplier"], 0))
    return lower._add_fields(channel["output"], terms, 0)


def channel_id(channel: Mapping[str, Any]) -> str:
    return "q1q2q3__" + channel["output"] + "__" + "__".join(channel["inputs"])


def fixture_record(
    channels: Sequence[Mapping[str, Any]],
    q1_by_id: Mapping[str, Mapping[str, Any]],
    q2_by_id: Mapping[str, Mapping[str, Any]],
    primary_by_id: Mapping[str, Mapping[str, Any]],
    q3_ast: Mapping[str, Any],
    background_name: str,
    background: Mapping[tuple[int, int], point.Jet],
    *,
    seeds: tuple[int, int, int],
) -> dict[str, Any]:
    rows = []
    for channel in channels:
        value = evaluate_channel(
            channel, q1_by_id, q2_by_id, primary_by_id, q3_ast,
            background, seeds=seeds,
        )
        defect = lower.serialize_field(channel["output"], value)
        rows.append({
            "channel_id": channel_id(channel),
            "output": channel["output"],
            "inputs": channel["inputs"],
            "path_count": len(channel["paths"]),
            "path_kind_counts": {
                kind: sum(path["kind"] == kind for path in channel["paths"])
                for kind in ("q1_q3", "q2_q2", "q3_q1")
            },
            "defect": defect,
            "defect_zero": all(item == "0" for item in defect),
        })
    return {
        "background": background_name,
        "seeds": list(seeds),
        "channels": rows,
        "all_channel_defects_zero": all(row["defect_zero"] for row in rows),
    }
