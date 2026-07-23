#!/usr/bin/env python3
"""Typed dyadic replacement factors for an over-wide radial microfactor.

The split changes only the radial factorization.  It retains the v6 frequency
cell and affine generator, uses boundary frames from the same global table,
and refuses any leaf whose declared block-width budget is exceeded.
"""
from __future__ import annotations

import hashlib
import json
import math
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import (
    MICROFACTOR_COUNT,
    MICROFACTOR_PANELS,
    build_microfactor_render_context,
    render_microfactor_adapter,
)
from .emit_microfactor import DEFAULT_INPUTS, parse_trace
from .verify_handoff import (
    CELL,
    HandoffError,
    _exact_keys,
    _file_sha256,
    _rational,
    _require,
    _sha,
    _verify_affine_hull,
    canonical_sha256,
)
from .verify_microfactor import BLOCK_ORDER


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SCHEMA = "phase3-axial-global-affine-split-microfactor-handoff-v1"
WIDTH_LIMIT = 1000.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def trace_id(parent: int, depth: int, child: int) -> int:
    if not (0 <= parent < MICROFACTOR_COUNT):
        raise ValueError("parent microfactor out of range")
    if depth not in (1, 2, 3):
        raise ValueError("split depth must lie in [1,3]")
    if not (0 <= child < 1 << depth):
        raise ValueError("split child out of range")
    return 100_000 + 100 * parent + 10 * (depth - 1) + child


def split_geometry(parent: int, depth: int, child: int) -> tuple[int, int]:
    trace_id(parent, depth, child)
    count = MICROFACTOR_PANELS // (1 << depth)
    return MICROFACTOR_PANELS * parent + child * count, count


def build_split_handoff(
    parent: int,
    depth: int,
    child: int,
    trace: str,
    root: Path,
    *,
    runner: Path,
    context: dict,
) -> dict:
    start, count = split_geometry(parent, depth, child)
    tid = trace_id(parent, depth, child)
    source, metadata = render_microfactor_adapter(
        parent,
        context=context,
        panel_start=start,
        panel_count=count,
        trace_id=tid,
    )
    if not runner.is_file() or runner.read_text() != source:
        raise HandoffError("split runner is not the deterministic rendered source")
    matrix, rank, widths = parse_trace(trace, tid)
    numeric_widths = [float(value) for value in widths.values()]
    if any(not math.isfinite(value) or value > WIDTH_LIMIT for value in numeric_widths):
        raise HandoffError("split leaf exceeds the declared width budget")

    inputs = [
        {"path": relative(path, root), "sha256": sha256(path)}
        for path in DEFAULT_INPUTS
    ]
    end = start + count
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-moving-frame-split-microfactor",
        "factor_id": f"micro-{parent:03d}-d{depth}-c{child}",
        "status": "CERTIFIED",
        "cell": dict(CELL),
        "split": {
            "parent_micro": parent,
            "depth": depth,
            "child": child,
            "trace_id": tid,
            "replacement": True,
            "width_limit": repr(WIDTH_LIMIT),
        },
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": rational_text(Fraction(start, 64)),
            "end": rational_text(Fraction(end, 64)),
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "solver": {
            "panels": count,
            "resets": 1,
            "local_steps": count,
            "order": 12,
            "rank_cells": 16,
            "global_panel_start": start,
            "global_panel_end": end,
            "structured_panels": count,
            "structured_order": 12,
            "structured_rebase_bits": 128,
            "rank_argument": "block-lower-determinant",
        },
        "frames": {
            "base_table_sha256": metadata["frame_table_sha256"],
            "left_boundary_sha256": metadata["frame_sha256"][start],
            "right_boundary_sha256": metadata["frame_sha256"][end],
            "generation": "same-global-frame-table-dyadic-slice",
        },
        "matrix": matrix,
        "integrity": {
            "producer": {
                "path": relative(Path(__file__), root),
                "sha256": sha256(Path(__file__)),
            },
            "inputs": inputs,
            "input_sha256": canonical_sha256(inputs),
            "output_sha256": canonical_sha256(matrix),
            "generated_source": {
                "renderer_path": relative(PACKAGE / "affine_rail.py", root),
                "renderer_sha256": sha256(PACKAGE / "affine_rail.py"),
                "base_manifest_path": relative(HERE / "manifest.json", root),
                "base_manifest_sha256": sha256(HERE / "manifest.json"),
                "base_frame_table_sha256": metadata["frame_table_sha256"],
                "parent_micro": parent,
                "depth": depth,
                "child": child,
                "global_panel_start": start,
                "panel_count": count,
                "trace_id": tid,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "retained_in_git": False,
            },
        },
        "proof": {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "factor_rank": rank,
            "outward_remainders": True,
            "lower_lift_included": True,
            "upper_right_exact_zero": True,
            "structured_lower_recurrence": True,
            "dyadic_rebase_bits": 128,
            "rank_argument": "block-lower-determinant",
            "block_max_width": widths,
            "width_limit_enforced": True,
            "storage_layout": "contiguous-block-lower-v1",
            "coefficient_layout": "standard-interleaved-v1",
            "transition_extractor": "contiguous-8-plus-4-v1",
        },
    }
    verify_split_microfactor(payload, root, context=context)
    return payload


def verify_split_microfactor(
    data: Any,
    repo_root: Path | None = None,
    *,
    context: dict | None = None,
) -> bool:
    _exact_keys(
        data,
        {
            "schema", "artifact_kind", "factor_id", "status", "cell", "split",
            "domain", "state", "solver", "frames", "matrix", "integrity", "proof",
        },
        "root",
    )
    _require(data["schema"] == SCHEMA, "root: wrong split schema")
    _require(
        data["artifact_kind"] == "infinity-moving-frame-split-microfactor"
        and data["status"] == "CERTIFIED",
        "root: split factor is not certified",
    )
    _require(data["cell"] == CELL, "cell: wrong shared parameter cell")
    split = data["split"]
    _exact_keys(
        split,
        {
            "parent_micro", "depth", "child", "trace_id", "replacement",
            "width_limit",
        },
        "split",
    )
    parent, depth, child = (
        split["parent_micro"], split["depth"], split["child"]
    )
    start, count = split_geometry(parent, depth, child)
    end = start + count
    _require(split["trace_id"] == trace_id(parent, depth, child), "split: bad trace id")
    _require(split["replacement"] is True, "split: not marked as a replacement")
    _require(float(split["width_limit"]) == WIDTH_LIMIT, "split: width budget drift")
    _require(
        data["factor_id"] == f"micro-{parent:03d}-d{depth}-c{child}",
        "factor_id: malformed",
    )
    _require(
        _rational(data["domain"]["start"], "domain.start") == Fraction(start, 64)
        and _rational(data["domain"]["end"], "domain.end") == Fraction(end, 64),
        "domain: wrong split interval",
    )
    _require(
        data["solver"]["panels"] == count
        and data["solver"]["local_steps"] == count
        and data["solver"]["global_panel_start"] == start
        and data["solver"]["global_panel_end"] == end,
        "solver: wrong split geometry",
    )
    _require(
        data["state"] == {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "state: wrong chart/order",
    )
    _verify_affine_hull(data["matrix"])
    zero_bits = ["0000000000000000", "0000000000000000"]
    for row in range(8):
        for col in range(8, 12):
            _require(
                data["matrix"]["center"][row][col] == "0/1"
                and data["matrix"]["linear"][row][col] == "0/1"
                and data["matrix"]["remainder"][row][col] == zero_bits,
                "matrix: upper-right block is not exactly zero",
            )
    widths = data["proof"]["block_max_width"]
    for key in ("carrier", "lower", "kernel"):
        value = float(widths[key])
        _require(
            math.isfinite(value) and 0.0 <= value <= WIDTH_LIMIT,
            f"proof.block_max_width.{key}: width budget exceeded",
        )
    _require(
        data["proof"]["ok"] is True
        and data["proof"]["factor_rank_certified"] is True
        and data["proof"]["factor_rank"] == 12
        and data["proof"]["width_limit_enforced"] is True,
        "proof: incomplete split factor",
    )
    integrity = data["integrity"]
    _require(
        integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "integrity: output hash mismatch",
    )
    for item in (integrity["producer"], *integrity["inputs"]):
        _sha(item["sha256"], "integrity path hash")
        if repo_root is not None:
            path = repo_root / item["path"]
            _require(path.is_file() and _file_sha256(path) == item["sha256"],
                     f"integrity: path drift {item['path']}")
    _require(
        integrity["input_sha256"] == canonical_sha256(integrity["inputs"]),
        "integrity: input manifest mismatch",
    )
    generated = integrity["generated_source"]
    if repo_root is not None:
        for key, hash_key in (
            ("renderer_path", "renderer_sha256"),
            ("base_manifest_path", "base_manifest_sha256"),
        ):
            path = repo_root / generated[key]
            _require(path.is_file() and _file_sha256(path) == generated[hash_key],
                     f"generated source: {key} drift")
        context = context or build_microfactor_render_context()
        source, metadata = render_microfactor_adapter(
            parent,
            context=context,
            panel_start=start,
            panel_count=count,
            trace_id=split["trace_id"],
        )
        _require(
            hashlib.sha256(source.encode()).hexdigest() == generated["source_sha256"],
            "generated source: deterministic rerender differs",
        )
        _require(
            metadata["frame_table_sha256"] == data["frames"]["base_table_sha256"]
            == generated["base_frame_table_sha256"],
            "frames: base table drift",
        )
        _require(
            metadata["frame_sha256"][start] == data["frames"]["left_boundary_sha256"]
            and metadata["frame_sha256"][end] == data["frames"]["right_boundary_sha256"],
            "frames: boundary hash drift",
        )
    return True


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=int, required=True)
    parser.add_argument("--depth", type=int, required=True)
    parser.add_argument("--child", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    context = build_microfactor_render_context()
    start, count = split_geometry(args.parent, args.depth, args.child)
    tid = trace_id(args.parent, args.depth, args.child)
    source, _ = render_microfactor_adapter(
        args.parent, context=context, panel_start=start,
        panel_count=count, trace_id=tid
    )
    with tempfile.TemporaryDirectory(prefix="axial-split-source-") as temp:
        runner = Path(temp) / "runner.forge"
        runner.write_text(source)
        payload = build_split_handoff(
            args.parent, args.depth, args.child, args.log.read_text(),
            args.repo_root, runner=runner, context=context
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {payload['factor_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
