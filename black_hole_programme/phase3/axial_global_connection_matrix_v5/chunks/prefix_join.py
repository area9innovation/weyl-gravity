#!/usr/bin/env python3
"""Verify and join the exact mixed-depth prefix through t=191/8."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import build_microfactor_render_context
from .emit_join import parse_join_trace
from .emit_prefix_split_cover import PLAN
from .factor_cover import (
    factor_bounds,
    factor_id,
    factor_parent,
    factor_table_hash,
)
from .join_microfactors import render_join_source
from .split_microfactor import SCHEMA as SPLIT_SCHEMA, verify_split_microfactor
from .verify_handoff import (
    HandoffError,
    _file_sha256,
    _require,
    _verify_affine_hull,
    canonical_sha256,
)
from .verify_microfactor import (
    BLOCK_ORDER,
    SCHEMA as FULL_SCHEMA,
    verify_microfactor,
)


SCHEMA = "phase3-axial-moving-frame-prefix-join-v1"
PREFIX_END_PARENT = 191


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def load_prefix_cover(
    directory: Path, repo_root: Path, *, context: dict
) -> tuple[list[Path], list[dict]]:
    records = []
    for parent in range(PREFIX_END_PARENT):
        if parent < 182:
            paths = [directory / f"microfactor_{parent:03d}.json"]
        else:
            depth = PLAN[parent]
            paths = [
                directory / f"splitfactor_{parent:03d}_d{depth}_c{child}.json"
                for child in range(1 << depth)
            ]
        for path in paths:
            if not path.is_file():
                raise HandoffError(f"prefix cover: missing {path.name}")
            payload = json.loads(path.read_text())
            if payload.get("schema") == FULL_SCHEMA:
                verify_microfactor(payload, repo_root)
            elif payload.get("schema") == SPLIT_SCHEMA:
                verify_split_microfactor(payload, repo_root, context=context)
            else:
                raise HandoffError("prefix cover: unsupported factor schema")
            records.append((path, payload))
    records.sort(key=lambda item: factor_bounds(item[1])[0])
    paths = [path for path, _ in records]
    payloads = [payload for _, payload in records]
    _require(len(payloads) == 212, "prefix cover: wrong factor count")
    _require(
        factor_bounds(payloads[0])[0] == Fraction(0)
        and factor_bounds(payloads[-1])[1] == Fraction(PREFIX_END_PARENT, 8),
        "prefix cover: wrong endpoints",
    )
    table = factor_table_hash(payloads[0])
    cursor = Fraction(0)
    parents = set()
    for index, payload in enumerate(payloads):
        start, end = factor_bounds(payload)
        _require(start == cursor and end > start, "prefix cover: gap or overlap")
        cursor = end
        parents.add(factor_parent(payload))
        _require(factor_table_hash(payload) == table, "prefix cover: table drift")
        for value in payload["proof"]["block_max_width"].values():
            _require(
                math.isfinite(float(value)) and float(value) <= 1000.0,
                "prefix cover: factor width exceeds budget",
            )
        if index:
            _require(
                payloads[index - 1]["frames"]["right_boundary_sha256"]
                == payload["frames"]["left_boundary_sha256"],
                "prefix cover: adjacent frame hash mismatch",
            )
    _require(
        parents == set(range(PREFIX_END_PARENT)),
        "prefix cover: parent set incomplete",
    )
    return paths, payloads


def build_artifact(
    trace: str,
    directory: Path,
    source: Path,
    repo_root: Path,
    *,
    context: dict,
) -> dict[str, Any]:
    paths, factors = load_prefix_cover(directory, repo_root, context=context)
    expected_source = render_join_source(factors, certify_join_rank=False)
    _require(source.read_text() == expected_source, "prefix join: source drift")
    matrix, widths = parse_join_trace(trace)
    factor_set = [
        {
            "factor_id": factor_id(payload),
            "path": _relative(path, repo_root),
            "sha256": _file_sha256(path),
        }
        for path, payload in zip(paths, factors)
    ]
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-moving-frame-exact-prefix-join",
        "status": "CERTIFIED",
        "cell": {
            "parameter": "Momega",
            "lower": "1/2",
            "upper": "129/256",
            "center": "257/512",
            "radius": "1/512",
            "generator": 7315,
        },
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": "0/1",
            "end": f"{PREFIX_END_PARENT}/8",
        },
        "state": {
            "rows": 12, "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "composition": {
            "factor_count": len(factors),
            "radial_order": "left-multiply-increasing-exact-radial-leaf",
            "dyadic_rebase_bits_after_each_join": 128,
            "standard_frame_materialized": False,
        },
        "frames": {
            "table_sha256": factor_table_hash(factors[0]),
            "left_boundary_sha256": factors[0]["frames"]["left_boundary_sha256"],
            "right_boundary_sha256": factors[-1]["frames"]["right_boundary_sha256"],
            "adjacent_hashes_verified": True,
        },
        "matrix": matrix,
        "integrity": {
            "producer": {
                "path": _relative(Path(__file__), repo_root),
                "sha256": _file_sha256(Path(__file__)),
            },
            "join_source_sha256": hashlib.sha256(
                expected_source.encode()
            ).hexdigest(),
            "factor_artifacts": factor_set,
            "factor_set_sha256": canonical_sha256(factor_set),
            "output_sha256": canonical_sha256(matrix),
        },
        "proof": {
            "ok": True,
            "exact_prefix_cover_verified": True,
            "factor_rank_certified": True,
            "factor_rank": 12,
            "rank_argument": (
                "product-of-certified-invertible-block-triangular-factors"
            ),
            "joined_interval_rank_not_required": True,
            "upper_right_exact_zero": True,
            "shared_generator_preserved": True,
            "block_max_width": widths,
        },
    }
    verify_artifact(payload, directory, repo_root, context=context)
    return payload


def verify_artifact(
    data: Any, directory: Path, repo_root: Path, *, context: dict
) -> bool:
    _require(data.get("schema") == SCHEMA, "prefix join: wrong schema")
    _require(data.get("status") == "CERTIFIED", "prefix join: not certified")
    paths, factors = load_prefix_cover(directory, repo_root, context=context)
    _require(
        data["domain"]["start"] == "0/1"
        and data["domain"]["end"] == f"{PREFIX_END_PARENT}/8",
        "prefix join: domain drift",
    )
    _require(
        data["state"]["chart"] == "global-moving-block-lower-12"
        and data["state"]["order"] == list(BLOCK_ORDER),
        "prefix join: chart drift",
    )
    _verify_affine_hull(data["matrix"])
    factor_set = [
        {
            "factor_id": factor_id(payload),
            "path": _relative(path, repo_root),
            "sha256": _file_sha256(path),
        }
        for path, payload in zip(paths, factors)
    ]
    integrity = data["integrity"]
    _require(
        integrity["factor_artifacts"] == factor_set
        and integrity["factor_set_sha256"] == canonical_sha256(factor_set)
        and integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "prefix join: integrity drift",
    )
    _require(
        integrity["join_source_sha256"]
        == hashlib.sha256(
            render_join_source(factors, certify_join_rank=False).encode()
        ).hexdigest(),
        "prefix join: source rerender drift",
    )
    _require(
        data["proof"]["ok"] is True
        and data["proof"]["exact_prefix_cover_verified"] is True
        and data["proof"]["factor_rank"] == 12,
        "prefix join: proof incomplete",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--run-timeout", type=float, default=1200.0)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=True)
    context = build_microfactor_render_context()
    _, factors = load_prefix_cover(
        args.artifact_dir, args.repo_root, context=context
    )
    source = args.scratch / "prefix_join.forge"
    binary = args.scratch / "prefix_join"
    log = args.scratch / "prefix_join.log"
    source.write_text(render_join_source(factors, certify_join_rank=False))
    compiled = subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        text=True, capture_output=True, timeout=600, check=False,
    )
    if compiled.returncode:
        print("REFUSED compile: " + compiled.stderr[-4000:])
        return 3
    ran = subprocess.run(
        [str(binary)], text=True, capture_output=True,
        timeout=args.run_timeout, check=False,
    )
    log.write_text(ran.stdout)
    if ran.returncode != 42:
        print("REFUSED run: " + ran.stderr[-4000:])
        return 3
    payload = build_artifact(
        ran.stdout, args.artifact_dir, source, args.repo_root,
        context=context,
    )
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
