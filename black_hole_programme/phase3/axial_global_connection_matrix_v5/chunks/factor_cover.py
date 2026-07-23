"""Verify and order a mixed full/split exact radial factor cover."""
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from .split_microfactor import SCHEMA as SPLIT_SCHEMA, WIDTH_LIMIT, verify_split_microfactor
from .verify_handoff import HandoffError, _rational, _require
from .verify_microfactor import SCHEMA as FULL_SCHEMA, verify_microfactor


def factor_id(data: dict[str, Any]) -> str:
    return data["chunk_id"] if data["schema"] == FULL_SCHEMA else data["factor_id"]


def factor_parent(data: dict[str, Any]) -> int:
    if data["schema"] == FULL_SCHEMA:
        return int(data["chunk_id"].split("-", 1)[1])
    return int(data["split"]["parent_micro"])


def factor_table_hash(data: dict[str, Any]) -> str:
    if data["schema"] == FULL_SCHEMA:
        return data["frames"]["table_sha256"]
    return data["frames"]["base_table_sha256"]


def factor_bounds(data: dict[str, Any]) -> tuple[Fraction, Fraction]:
    return (
        _rational(data["domain"]["start"], "domain.start"),
        _rational(data["domain"]["end"], "domain.end"),
    )


def verify_factor_cover(
    factors: list[dict[str, Any]],
    repo_root: Path | None = None,
    *,
    split_context: dict | None = None,
) -> list[dict[str, Any]]:
    _require(bool(factors), "cover: empty")
    ordered = sorted(factors, key=lambda item: factor_bounds(item)[0])
    ids = [factor_id(item) for item in ordered]
    _require(len(ids) == len(set(ids)), "cover: duplicate factor id")
    for item in ordered:
        if item.get("schema") == FULL_SCHEMA:
            verify_microfactor(item, repo_root)
        elif item.get("schema") == SPLIT_SCHEMA:
            verify_split_microfactor(item, repo_root, context=split_context)
        else:
            raise HandoffError("cover: unsupported factor schema")
        for value in item["proof"]["block_max_width"].values():
            width = float(value)
            _require(
                math.isfinite(width) and width <= WIDTH_LIMIT,
                f"cover: factor {factor_id(item)} exceeds width budget",
            )

    _require(factor_bounds(ordered[0])[0] == Fraction(0), "cover: wrong start")
    _require(factor_bounds(ordered[-1])[1] == Fraction(28), "cover: wrong end")
    table = factor_table_hash(ordered[0])
    for index, item in enumerate(ordered):
        start, end = factor_bounds(item)
        parent = factor_parent(item)
        _require(
            Fraction(parent, 8) <= start < end <= Fraction(parent + 1, 8),
            f"cover: factor {factor_id(item)} leaves its parent",
        )
        _require(factor_table_hash(item) == table, "cover: base frame table differs")
        if index:
            left = ordered[index - 1]
            _require(factor_bounds(left)[1] == start, "cover: gap or overlap")
            _require(
                left["frames"]["right_boundary_sha256"]
                == item["frames"]["left_boundary_sha256"],
                "cover: adjacent frame hashes differ",
            )

    # A parent is represented either by its one full factor or by a complete
    # dyadic leaf partition, never both.
    by_parent: dict[int, list[dict[str, Any]]] = {}
    for item in ordered:
        by_parent.setdefault(factor_parent(item), []).append(item)
    _require(set(by_parent) == set(range(224)), "cover: parent set incomplete")
    for parent, leaves in by_parent.items():
        schemas = {leaf["schema"] for leaf in leaves}
        _require(len(schemas) == 1, f"cover: mixed full/split parent {parent}")
        if FULL_SCHEMA in schemas:
            _require(len(leaves) == 1, f"cover: duplicate full parent {parent}")
        else:
            _require(
                factor_bounds(leaves[0])[0] == Fraction(parent, 8)
                and factor_bounds(leaves[-1])[1] == Fraction(parent + 1, 8),
                f"cover: split parent {parent} incomplete",
            )
    return ordered


def load_factor_cover(
    directory: Path,
    repo_root: Path | None = None,
    *,
    split_context: dict | None = None,
) -> tuple[list[Path], list[dict[str, Any]]]:
    paths = sorted(directory.glob("*.json"))
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        data = json.loads(path.read_text())
        if data.get("schema") in (FULL_SCHEMA, SPLIT_SCHEMA):
            records.append((path, data))
    ordered = verify_factor_cover(
        [data for _, data in records], repo_root, split_context=split_context
    )
    by_id = {factor_id(data): path for path, data in records}
    return [by_id[factor_id(data)] for data in ordered], ordered
