#!/usr/bin/env python3
"""Independent fail-closed checks for the four restricted moving joins."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .restrict_join import SCALE, SUBCELLS, _restrict_matrix
from .verify_handoff import HandoffError, _exact_keys, _require, _verify_affine_hull
from .verify_join import verify_join


def verify(data: dict, repo_root: Path) -> bool:
    _exact_keys(
        data,
        {"schema", "status", "parent_cell", "restriction", "cells", "provenance"},
        "root",
    )
    _require(
        data["schema"] == "phase3-axial-moving-frame-restricted-joins-v1"
        and data["status"] == "CERTIFIED",
        "root: wrong schema/status",
    )
    _require(data["parent_cell"] == {
        "omega_interval": ["1/2", "129/256"],
        "center": "257/512", "radius": "1/512",
        "affine_generator": 7315,
    }, "parent cell mismatch")
    _require(
        data["restriction"]
        == "Cq=C+shift*L; Lq=scale*L; outward remainder retained",
        "restriction rule mismatch",
    )
    provenance = data["provenance"]
    parent_path = repo_root / provenance["parent_join_path"]
    _require(parent_path.is_file(), "parent join missing")
    _require(
        hashlib.sha256(parent_path.read_bytes()).hexdigest()
        == provenance["parent_join_sha256"],
        "parent join hash mismatch",
    )
    producer_path = Path(__file__).with_name("restrict_join.py")
    _require(
        hashlib.sha256(producer_path.read_bytes()).hexdigest()
        == provenance["producer_sha256"],
        "restriction producer hash mismatch",
    )
    parent = json.loads(parent_path.read_text())
    verify_join(parent, repo_root)
    _require(len(data["cells"]) == 4, "wrong restricted cover size")
    for actual, expected in zip(data["cells"], SUBCELLS):
        cell_id, lo, hi, center, radius, shift = expected
        _require(actual["cell_id"] == cell_id, "cell order/id mismatch")
        _require(actual["omega_interval"] == [lo, hi], "cell bounds mismatch")
        _require(
            actual["center"] == center and actual["radius"] == radius,
            "cell center/radius mismatch",
        )
        _require(
            actual["affine_generator"] == 7315
            and Fraction(actual["parent_epsilon_shift"]) == shift
            and Fraction(actual["parent_epsilon_scale"]) == SCALE,
            "cell normalized affine restriction mismatch",
        )
        _verify_affine_hull(actual["matrix"])
        _require(
            actual["matrix"] == _restrict_matrix(parent["matrix"], shift),
            "restricted matrix is not the exact parent restriction",
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify(json.loads(args.artifact.read_text()), args.repo_root)
    except (OSError, json.JSONDecodeError, HandoffError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
