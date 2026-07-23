#!/usr/bin/env python3
"""Typed exact join of one final-frequency child's local-reset tail."""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import (
    SCHEMA as FACTOR_SCHEMA,
    TAIL_END_PARENT,
    TAIL_START_PARENT,
    cell_payload,
    frequency_cell,
    verify_factor,
)
from .emit_join import parse_join_trace
from .join_microfactors import render_join_source
from .verify_handoff import (
    HandoffError,
    _file_sha256,
    _require,
    _verify_affine_hull,
    canonical_sha256,
)
from .verify_microfactor import BLOCK_ORDER


SCHEMA = "phase3-axial-final-frequency-child-tail-join-v1"


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def expected_path(directory: Path, child: int, parent: int, leaf: int) -> Path:
    return directory / f"child_q{child:02d}_p{parent:03d}_l{leaf}.json"


def load_cover(
    directory: Path,
    child: int,
    repo_root: Path,
    *,
    context: dict | None = None,
    prefix_context: dict | None = None,
) -> tuple[list[Path], list[dict]]:
    context = context or build_microfactor_render_context(frequency_cell(child))
    prefix_context = prefix_context or build_microfactor_render_context()
    paths, payloads = [], []
    cursor = Fraction(TAIL_START_PARENT, 8)
    crosswalk_hash = None
    for parent in range(TAIL_START_PARENT, TAIL_END_PARENT):
        for leaf in (0, 1):
            path = expected_path(directory, child, parent, leaf)
            if not path.is_file():
                raise HandoffError(f"child tail cover: missing {path.name}")
            payload = json.loads(path.read_text())
            _require(
                payload.get("schema") == FACTOR_SCHEMA,
                "child tail cover: wrong factor schema",
            )
            verify_factor(
                payload, repo_root, context=context,
                prefix_context=prefix_context,
            )
            start = Fraction(payload["radial"]["start"])
            end = Fraction(payload["radial"]["end"])
            _require(
                start == cursor and end > start,
                "child tail cover: gap, overlap, or reversed leaf",
            )
            cursor = end
            digest = payload["inherited_prefix_boundary_crosswalk"][
                "crosswalk_sha256"
            ]
            if crosswalk_hash is None:
                crosswalk_hash = digest
            _require(
                digest == crosswalk_hash,
                "child tail cover: prefix crosswalk differs between leaves",
            )
            paths.append(path)
            payloads.append(payload)
    _require(
        cursor == Fraction(28) and len(payloads) == 66,
        "child tail cover: incomplete exact radial cover",
    )
    return paths, payloads


def build_join(
    *,
    child: int,
    trace: str,
    artifact_dir: Path,
    source: Path,
    repo_root: Path,
    context: dict,
    prefix_context: dict,
) -> dict[str, Any]:
    paths, payloads = load_cover(
        artifact_dir, child, repo_root,
        context=context, prefix_context=prefix_context,
    )
    expected_source = render_join_source(payloads, certify_join_rank=False)
    if source.read_text() != expected_source:
        raise HandoffError("child tail join: generated source drift")
    matrix, widths = parse_join_trace(trace)
    factor_set = [
        {
            "factor_id": payload["factor_id"],
            "path": _relative(path, repo_root),
            "sha256": _file_sha256(path),
        }
        for path, payload in zip(paths, payloads)
    ]
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-final-frequency-child-tail-join",
        "status": "CERTIFIED",
        "cell": cell_payload(child),
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": f"{TAIL_START_PARENT}/8",
            "end": "28/1",
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "fixed-standard-frame-block-order-12",
            "order": list(BLOCK_ORDER),
        },
        "composition": {
            "factor_count": len(payloads),
            "radial_order": "left-multiply-increasing-exact-radial-leaf",
            "dyadic_rebase_bits_after_each_join": 128,
            "standard_frame_materialized": True,
            "physical_restart": False,
        },
        "inherited_prefix_boundary_crosswalk": payloads[0][
            "inherited_prefix_boundary_crosswalk"
        ],
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
            "exact_cover_verified": True,
            "identity_transitions_verified": True,
            "prefix_crosswalk_verified": True,
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
    verify_join(
        payload, artifact_dir, repo_root,
        context=context, prefix_context=prefix_context,
    )
    return payload


def verify_join(
    data: Any,
    artifact_dir: Path,
    repo_root: Path,
    *,
    context: dict | None = None,
    prefix_context: dict | None = None,
) -> bool:
    _require(data.get("schema") == SCHEMA, "child tail join: wrong schema")
    _require(data.get("status") == "CERTIFIED", "child tail join: not certified")
    child = data["cell"]["parent_child_index"]
    _require(data["cell"] == cell_payload(child), "child tail join: cell drift")
    paths, payloads = load_cover(
        artifact_dir, child, repo_root,
        context=context, prefix_context=prefix_context,
    )
    _require(
        data["domain"]["start"] == f"{TAIL_START_PARENT}/8"
        and data["domain"]["end"] == "28/1",
        "child tail join: domain drift",
    )
    _require(
        data["state"] == {
            "rows": 12,
            "cols": 12,
            "chart": "fixed-standard-frame-block-order-12",
            "order": list(BLOCK_ORDER),
        },
        "child tail join: state chart drift",
    )
    _require(
        data["composition"]["factor_count"] == 66
        and data["composition"]["standard_frame_materialized"] is True
        and data["composition"]["physical_restart"] is False,
        "child tail join: composition drift",
    )
    expected_crosswalk = payloads[0]["inherited_prefix_boundary_crosswalk"]
    _require(
        data["inherited_prefix_boundary_crosswalk"] == expected_crosswalk,
        "child tail join: inherited prefix crosswalk drift",
    )
    _verify_affine_hull(data["matrix"])
    for width in data["proof"]["block_max_width"].values():
        _require(
            math.isfinite(float(width)) and float(width) >= 0.0,
            "child tail join: invalid width",
        )
    expected_set = [
        {
            "factor_id": payload["factor_id"],
            "path": _relative(path, repo_root),
            "sha256": _file_sha256(path),
        }
        for path, payload in zip(paths, payloads)
    ]
    integrity = data["integrity"]
    _require(
        integrity["factor_artifacts"] == expected_set
        and integrity["factor_set_sha256"] == canonical_sha256(expected_set)
        and integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "child tail join: integrity drift",
    )
    expected_source = render_join_source(payloads, certify_join_rank=False)
    _require(
        integrity["join_source_sha256"]
        == hashlib.sha256(expected_source.encode()).hexdigest(),
        "child tail join: source rerender drift",
    )
    _require(
        data["proof"]["ok"] is True
        and data["proof"]["exact_cover_verified"] is True
        and data["proof"]["identity_transitions_verified"] is True
        and data["proof"]["prefix_crosswalk_verified"] is True
        and data["proof"]["factor_rank"] == 12,
        "child tail join: proof incomplete",
    )
    return True
