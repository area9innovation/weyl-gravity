#!/usr/bin/env python3
"""Restrict the parent-cell moving join to the four frozen omega subcells."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path

from .verify_join import verify_join


SUBCELLS = (
    ("q0", "1/2", "513/1024", "1025/2048", "1/2048", Fraction(-3, 4)),
    ("q1", "513/1024", "257/512", "1027/2048", "1/2048", Fraction(-1, 4)),
    ("q2", "257/512", "515/1024", "1029/2048", "1/2048", Fraction(1, 4)),
    ("q3", "515/1024", "129/256", "1031/2048", "1/2048", Fraction(3, 4)),
)
SCALE = Fraction(1, 4)


def _fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _float(bits: str) -> float:
    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


def _bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _directed(value: Fraction, direction: float) -> float:
    out = float(value)
    if (
        direction < 0 and Fraction.from_float(out) > value
    ) or (
        direction > 0 and Fraction.from_float(out) < value
    ):
        out = math.nextafter(out, direction)
    return out


def _restrict_matrix(matrix: dict, shift: Fraction) -> dict:
    center, linear, remainder, hull = [], [], [], []
    for i in range(12):
        crow, lrow, rrow, hrow = [], [], [], []
        for j in range(12):
            c = Fraction(matrix["center"][i][j])
            l = Fraction(matrix["linear"][i][j])
            cc, ll = c + shift * l, SCALE * l
            rem = list(matrix["remainder"][i][j])
            rlo, rhi = map(_float, rem)
            lo = math.nextafter(
                _directed(cc - abs(ll), -math.inf) + rlo, -math.inf
            )
            hi = math.nextafter(
                _directed(cc + abs(ll), math.inf) + rhi, math.inf
            )
            crow.append(_fraction(cc))
            lrow.append(_fraction(ll))
            rrow.append(rem)
            hrow.append([_bits(lo), _bits(hi)])
        center.append(crow)
        linear.append(lrow)
        remainder.append(rrow)
        hull.append(hrow)
    return {
        "center": center, "linear": linear,
        "remainder": remainder, "hull": hull,
    }


def build(parent: dict, parent_path: Path, repo_root: Path) -> dict:
    verify_join(parent, repo_root)
    cells = []
    for cell_id, lo, hi, center, radius, shift in SUBCELLS:
        cells.append({
            "cell_id": cell_id,
            "omega_interval": [lo, hi],
            "center": center,
            "radius": radius,
            "affine_generator": 7315,
            "parent_epsilon_shift": _fraction(shift),
            "parent_epsilon_scale": _fraction(SCALE),
            "matrix": _restrict_matrix(parent["matrix"], shift),
        })
    return {
        "schema": "phase3-axial-moving-frame-restricted-joins-v1",
        "status": "CERTIFIED",
        "parent_cell": {
            "omega_interval": ["1/2", "129/256"],
            "center": "257/512", "radius": "1/512",
            "affine_generator": 7315,
        },
        "restriction": "Cq=C+shift*L; Lq=scale*L; outward remainder retained",
        "cells": cells,
        "provenance": {
            "parent_join_path": parent_path.resolve().relative_to(
                repo_root.resolve()
            ).as_posix(),
            "parent_join_sha256": hashlib.sha256(parent_path.read_bytes()).hexdigest(),
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    payload = build(json.loads(args.parent.read_text()), args.parent, args.repo_root)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
