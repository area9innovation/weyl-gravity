from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction

import pytest

from ..factor_cover import verify_factor_cover
from ..split_microfactor import (
    SCHEMA,
    split_geometry,
    trace_id,
    verify_split_microfactor,
)
from ..verify_handoff import HandoffError, canonical_sha256
from .test_microfactor import HASH_A, HASH_B, _artifact


def split_artifact(parent: int, child: int) -> dict:
    base = _artifact(parent)
    start, count = split_geometry(parent, 1, child)
    end = start + count
    data = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-moving-frame-split-microfactor",
        "factor_id": f"micro-{parent:03d}-d1-c{child}",
        "status": "CERTIFIED",
        "cell": base["cell"],
        "split": {
            "parent_micro": parent,
            "depth": 1,
            "child": child,
            "trace_id": trace_id(parent, 1, child),
            "replacement": True,
            "width_limit": "1000.0",
        },
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": str(Fraction(start, 64)),
            "end": str(Fraction(end, 64)),
        },
        "state": base["state"],
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
            "base_table_sha256": HASH_A,
            "left_boundary_sha256": f"{start:064x}",
            "right_boundary_sha256": f"{end:064x}",
            "generation": "same-global-frame-table-dyadic-slice",
        },
        "matrix": base["matrix"],
        "integrity": {
            "producer": {"path": "producer", "sha256": HASH_A},
            "inputs": [{"path": "input", "sha256": HASH_B}],
            "input_sha256": canonical_sha256(
                [{"path": "input", "sha256": HASH_B}]
            ),
            "output_sha256": canonical_sha256(base["matrix"]),
            "generated_source": {
                "renderer_path": "renderer",
                "renderer_sha256": HASH_A,
                "base_manifest_path": "manifest",
                "base_manifest_sha256": HASH_B,
                "base_frame_table_sha256": HASH_A,
                "parent_micro": parent,
                "depth": 1,
                "child": child,
                "global_panel_start": start,
                "panel_count": count,
                "trace_id": trace_id(parent, 1, child),
                "source_sha256": HASH_A,
                "retained_in_git": False,
            },
        },
        "proof": {
            **base["proof"],
            "block_max_width": {
                "carrier": "0.1", "lower": "999.0", "kernel": "0.1",
            },
            "width_limit_enforced": True,
        },
    }
    return data


def test_split_leaf_and_width_mutation() -> None:
    data = split_artifact(182, 0)
    assert verify_split_microfactor(data)
    bad = copy.deepcopy(data)
    bad["proof"]["block_max_width"]["lower"] = "1000.0001"
    with pytest.raises(HandoffError):
        verify_split_microfactor(bad)


def test_complete_mixed_cover_and_missing_child() -> None:
    factors = [_artifact(j) for j in range(224) if j != 182]
    factors += [split_artifact(182, 0), split_artifact(182, 1)]
    ordered = verify_factor_cover(factors)
    assert len(ordered) == 225
    with pytest.raises(HandoffError):
        verify_factor_cover(factors[:-1])
