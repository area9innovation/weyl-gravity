#!/usr/bin/env python3
"""Fail-closed verifier for eight-panel affine radial microfactors."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from .verify_handoff import (
    CELL,
    HandoffError,
    STANDARD_ORDER,
    _exact_keys,
    _file_sha256,
    _rational,
    _require,
    _sha,
    _verify_affine_hull,
    _verify_path_hash,
    canonical_sha256,
)


SCHEMA = "phase3-axial-global-affine-microfactor-handoff-v3"
COUNT = 224
BLOCK_ORDER = (
    "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)",
    "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)",
    "Re(H1)", "Re(F)", "Im(H1)", "Im(F)",
)
TOP_KEYS = {
    "schema", "artifact_kind", "chunk_id", "status", "cell", "domain",
    "state", "solver", "frames", "matrix", "integrity", "proof",
}


def verify_microfactor(data: Any, repo_root: Path | None = None) -> bool:
    _exact_keys(data, TOP_KEYS, "root")
    _require(data["schema"] == SCHEMA, "root: wrong schema")
    _require(
        data["artifact_kind"] == "infinity-moving-frame-microfactor",
        "root: wrong artifact kind",
    )
    _require(data["status"] == "CERTIFIED", "root: noncertified handoff")
    _exact_keys(data["cell"], set(CELL), "cell")
    _require(data["cell"] == CELL, "cell: wrong shared parameter cell/generator")

    _require(
        isinstance(data["chunk_id"], str)
        and data["chunk_id"].startswith("micro-"),
        "chunk_id: malformed",
    )
    try:
        j = int(data["chunk_id"].split("-", 1)[1])
    except ValueError as exc:
        raise HandoffError("chunk_id: malformed") from exc
    _require(0 <= j < COUNT, "chunk_id: out of range")

    _exact_keys(
        data["domain"], {"coordinate", "orientation", "start", "end"}, "domain"
    )
    _require(
        data["domain"]["coordinate"] == "t=32-r"
        and data["domain"]["orientation"] == "increasing-t/inward-r",
        "domain: wrong coordinate/orientation",
    )
    _require(
        _rational(data["domain"]["start"], "domain.start") == Fraction(j, 8)
        and _rational(data["domain"]["end"], "domain.end") == Fraction(j + 1, 8),
        "domain: wrong exact microinterval",
    )

    _exact_keys(
        data["solver"],
        {
            "panels", "resets", "local_steps", "order", "rank_cells",
            "global_panel_start", "global_panel_end",
            "structured_panels", "structured_order", "structured_rebase_bits",
            "structured_global_panel_start", "structured_global_panel_end",
            "rank_argument",
        },
        "solver",
    )
    _require(
        data["solver"] == {
            "panels": 8,
            "resets": 1,
            "local_steps": 8,
            "order": 12,
            "rank_cells": 16,
            "global_panel_start": 8 * j,
            "global_panel_end": 8 * (j + 1),
            "structured_panels": 8,
            "structured_order": 12,
            "structured_rebase_bits": 128,
            "structured_global_panel_start": 8 * j,
            "structured_global_panel_end": 8 * (j + 1),
            "rank_argument": "block-lower-determinant",
        },
        "solver: wrong microfactor contract",
    )

    _exact_keys(data["state"], {"rows", "cols", "chart", "order"}, "state")
    _require(
        data["state"] == {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "state: wrong chart/order",
    )

    _exact_keys(
        data["frames"],
        {"table_sha256", "left_boundary_sha256", "right_boundary_sha256", "generation"},
        "frames",
    )
    for key in ("table_sha256", "left_boundary_sha256", "right_boundary_sha256"):
        _sha(data["frames"][key], f"frames.{key}")
    _require(
        data["frames"]["generation"]
        == "single-global-exact-table-sliced-with-byte-identical-overlap",
        "frames: independently generated/rounded boundary frames forbidden",
    )

    _exact_keys(data["matrix"], {"center", "linear", "remainder", "hull"}, "matrix")
    _verify_affine_hull(data["matrix"])
    zero_bits = ["0000000000000000", "0000000000000000"]
    for i in range(8):
        for col in range(8, 12):
            _require(
                data["matrix"]["center"][i][col] == "0/1"
                and data["matrix"]["linear"][i][col] == "0/1"
                and data["matrix"]["remainder"][i][col] == zero_bits,
                "matrix: upper-right block is not exactly zero",
            )

    _exact_keys(
        data["proof"],
        {
            "ok", "refusal_code", "existence_certified", "uniqueness_certified",
            "factor_rank_certified", "factor_rank", "outward_remainders",
            "lower_lift_included", "upper_right_exact_zero",
            "structured_lower_recurrence", "dyadic_rebase_bits",
            "rank_argument", "block_max_width", "storage_layout",
            "coefficient_layout", "transition_extractor",
        },
        "proof",
    )
    _require(
        data["proof"] == {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "factor_rank": 12,
            "outward_remainders": True,
            "lower_lift_included": True,
            "upper_right_exact_zero": True,
            "structured_lower_recurrence": True,
            "dyadic_rebase_bits": 128,
            "rank_argument": "block-lower-determinant",
            "block_max_width": data["proof"]["block_max_width"],
            "storage_layout": "contiguous-block-lower-v1",
            "coefficient_layout": "standard-interleaved-v1",
            "transition_extractor": "contiguous-8-plus-4-v1",
        },
        "proof: incomplete or refused",
    )
    _exact_keys(
        data["proof"]["block_max_width"], {"carrier", "lower", "kernel"},
        "proof.block_max_width",
    )
    for name, value in data["proof"]["block_max_width"].items():
        _require(isinstance(value, str), f"proof.block_max_width.{name}: expected string")
        try:
            width = float(value)
        except ValueError as exc:
            raise HandoffError(
                f"proof.block_max_width.{name}: malformed"
            ) from exc
        _require(
            math.isfinite(width) and width >= 0.0,
            f"proof.block_max_width.{name}: nonfinite/negative",
        )

    integrity = data["integrity"]
    _exact_keys(
        integrity,
        {
            "producer", "inputs", "input_sha256", "output_sha256",
            "generated_source",
        },
        "integrity",
    )
    _verify_path_hash(integrity["producer"], repo_root, "integrity.producer")
    _require(
        isinstance(integrity["inputs"], list) and integrity["inputs"],
        "integrity.inputs: expected nonempty list",
    )
    inputs = [
        _verify_path_hash(item, repo_root, f"integrity.inputs[{i}]")
        for i, item in enumerate(integrity["inputs"])
    ]
    _require(
        len({item["path"] for item in inputs}) == len(inputs),
        "integrity.inputs: duplicate paths",
    )
    _require(
        integrity["input_sha256"] == canonical_sha256(inputs),
        "integrity.input_sha256: manifest hash mismatch",
    )
    _require(
        integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "integrity.output_sha256: matrix payload hash mismatch",
    )
    generated = integrity["generated_source"]
    _exact_keys(
        generated,
        {
            "manifest_path", "manifest_file_sha256", "renderer_path",
            "renderer_sha256", "frame_table_sha256", "micro",
            "source_sha256", "retained_in_git",
        },
        "integrity.generated_source",
    )
    for key in (
        "manifest_file_sha256", "renderer_sha256", "frame_table_sha256",
        "source_sha256",
    ):
        _sha(generated[key], f"integrity.generated_source.{key}")
    _require(generated["micro"] == j, "generated source: wrong micro id")
    _require(
        isinstance(generated["retained_in_git"], bool),
        "generated source: retained flag must be boolean",
    )
    if repo_root is not None:
        manifest_path = repo_root / generated["manifest_path"]
        renderer_path = repo_root / generated["renderer_path"]
        _require(manifest_path.is_file(), "generated source: manifest missing")
        _require(renderer_path.is_file(), "generated source: renderer missing")
        _require(
            _file_sha256(manifest_path) == generated["manifest_file_sha256"],
            "generated source: manifest file hash mismatch",
        )
        _require(
            _file_sha256(renderer_path) == generated["renderer_sha256"],
            "generated source: renderer hash mismatch",
        )
        manifest = json.loads(manifest_path.read_text())
        _require(
            manifest.get("schema")
            == "axial-affine-microfactor-runner-manifest-v3",
            "generated source: wrong manifest schema",
        )
        _require(
            manifest.get("frame_table_sha256")
            == generated["frame_table_sha256"],
            "generated source: frame-table hash mismatch",
        )
        chunks = manifest.get("chunks", [])
        _require(len(chunks) == COUNT, "generated source: incomplete manifest")
        _require(
            chunks[j].get("start") == j
            and chunks[j].get("sha256") == generated["source_sha256"],
            "generated source: specialized source pin mismatch",
        )
    return True


def verify_microfactor_chain(
    handoffs: Iterable[dict[str, Any]], repo_root: Path | None = None
) -> bool:
    items = list(handoffs)
    _require(len(items) == COUNT, f"chain: expected {COUNT} factors")
    for j, item in enumerate(items):
        verify_microfactor(item, repo_root)
        _require(item["chunk_id"] == f"micro-{j:03d}", "chain: wrong radial order")
        if j:
            left = items[j - 1]
            _require(
                left["domain"]["end"] == item["domain"]["start"],
                "chain: exact boundary gap/overlap",
            )
            _require(
                left["frames"]["table_sha256"] == item["frames"]["table_sha256"],
                "chain: global frame table differs",
            )
            _require(
                left["frames"]["right_boundary_sha256"]
                == item["frames"]["left_boundary_sha256"],
                "chain: adjacent boundary frames differ",
            )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args(argv)
    try:
        payloads = [json.loads(path.read_text()) for path in args.artifacts]
        if args.chain:
            verify_microfactor_chain(payloads, args.repo_root)
        else:
            for payload in payloads:
                verify_microfactor(payload, args.repo_root)
    except (OSError, json.JSONDecodeError, HandoffError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
