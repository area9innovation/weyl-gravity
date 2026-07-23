#!/usr/bin/env python3
"""Construct non-certifying dyadic frames for rigorous horizon transport.

The numerical solve in this module is used only to choose invertible rational
coordinate frames.  Every scientific enclosure is subsequently recomputed
with those exact frames by the Forge interval rail; no numerical value emitted
here is itself evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

from ...axial_horizon_grassmann_mobius_to_r4 import produce as horizon
from ...axial_horizon_grassmann_mobius_to_r4_taylor2.exact_point import (
    OMEGA0,
    OUTPUT as EXACT_SOURCE,
)
from .verify_handoff import canonical_sha256


SCHEMA = "phase3-axial-exact-point-horizon-dyadic-frame-schedule-v1"
EPSILON = Fraction(1, 1 << 22)
FRAMES_PER_SHELL = 8
SHELLS = tuple(
    (EPSILON * (1 << index), EPSILON * (1 << (index + 1)))
    for index in range(22)
) + ((Fraction(1), Fraction(2)),)
BOUNDARIES = tuple(
    lo + (hi - lo) * Fraction(segment, FRAMES_PER_SHELL)
    for lo, hi in SHELLS
    for segment in range(FRAMES_PER_SHELL)
) + (Fraction(2),)
PAIRS = tuple(combinations(range(4), 2))


def _complex_initial() -> np.ndarray:
    source = EXACT_SOURCE.read_text()
    match = re.search(
        r"fn hc_initial_model_center\(\) -> QMat \{(.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("exact-point initializer centre is absent")
    center = [[Fraction(0) for _ in range(6)] for _ in range(12)]
    for row, col, value in re.findall(
        r'a=qm_set\(a,(\d+),(\d+),big\("([^"]+)"\)\);',
        match.group(1),
    ):
        center[int(row)][int(col)] = Fraction(value)
    return np.asarray([
        [
            float(center[row][col])
            + 1j * float(center[row + 6][col])
            for col in range(2)
        ]
        for row in range(6)
    ], dtype=np.complex128)


def _dyadic(value: float, bits: int) -> Fraction:
    scale = 1 << bits
    return Fraction(int(round(value * scale)), scale)


def _zero_complex() -> list[Fraction]:
    return [Fraction(0), Fraction(0)]


def _serialize_complex(matrix: list[list[list[Fraction]]]) -> list:
    return [
        [
            [f"{z[0].numerator}/{z[0].denominator}",
             f"{z[1].numerator}/{z[1].denominator}"]
            for z in row
        ]
        for row in matrix
    ]


def _frame_for_plane(
    plane: np.ndarray, *, bits: int,
) -> tuple[tuple[int, int], list, list, float]:
    determinants = [
        (abs(np.linalg.det(plane[list(pair), :])), pair)
        for pair in PAIRS
    ]
    pivot_score, pivot = max(determinants)
    complement = tuple(index for index in range(4) if index not in pivot)
    pivot_matrix = plane[list(pivot), :]
    normalized = plane @ np.linalg.inv(pivot_matrix)
    z_float = normalized[list(complement), :]
    z = [
        [
            [_dyadic(float(value.real), bits),
             _dyadic(float(value.imag), bits)]
            for value in row
        ]
        for row in z_float
    ]

    # In pivot/complement row order the aligned frame and its inverse are
    # [[I,0],[-Z,I]] and [[I,0],[Z,I]].  Convert both back to global order.
    order = pivot + complement
    s_ordered = [[_zero_complex() for _ in range(4)] for _ in range(4)]
    b_ordered = [[_zero_complex() for _ in range(4)] for _ in range(4)]
    for index in range(4):
        s_ordered[index][index] = [Fraction(1), Fraction(0)]
        b_ordered[index][index] = [Fraction(1), Fraction(0)]
    for row in range(2):
        for col in range(2):
            zr, zi = z[row][col]
            s_ordered[row + 2][col] = [-zr, -zi]
            b_ordered[row + 2][col] = [zr, zi]

    # S = S_ordered P; Sinv = P^T B_ordered.
    s = [[_zero_complex() for _ in range(4)] for _ in range(4)]
    sinv = [[_zero_complex() for _ in range(4)] for _ in range(4)]
    for row in range(4):
        for ordered_col, global_col in enumerate(order):
            s[row][global_col] = s_ordered[row][ordered_col]
    for ordered_row, global_row in enumerate(order):
        for col in range(4):
            sinv[global_row][col] = b_ordered[ordered_row][col]
    return pivot, s, sinv, float(pivot_score)


def build_schedule(bits: int = 42) -> dict[str, Any]:
    rho, omega, flow = horizon.base_producer.exact_horizon_flow()
    point_flow = flow.subs(
        omega, sp.Rational(OMEGA0.numerator, OMEGA0.denominator)
    )
    numeric_flow = sp.lambdify(rho, point_flow, modules="numpy")
    initial = _complex_initial()

    def rhs(value: float, flat: np.ndarray) -> np.ndarray:
        state = flat.reshape((6, 2))
        return (
            np.asarray(numeric_flow(value), dtype=np.complex128) @ state
        ).reshape(-1)

    targets = np.asarray([float(value) for value in BOUNDARIES])
    solved = solve_ivp(
        rhs,
        (targets[0], targets[-1]),
        initial.reshape(-1),
        method="DOP853",
        t_eval=targets,
        rtol=2.0e-13,
        atol=2.0e-14,
    )
    if not solved.success or solved.y.shape[1] != len(BOUNDARIES):
        raise RuntimeError(f"numerical frame pilot failed: {solved.message}")

    frames = []
    for index, boundary in enumerate(BOUNDARIES):
        plane = solved.y[:, index].reshape((6, 2))[:4, :]
        pivot, s, sinv, score = _frame_for_plane(plane, bits=bits)
        frames.append({
            "index": index,
            "rho": f"{boundary.numerator}/{boundary.denominator}",
            "pivot_complex_rows": list(pivot),
            "pilot_pivot_abs_det": score,
            "S": _serialize_complex(s),
            "Sinv": _serialize_complex(sinv),
        })
    payload = {
        "schema": SCHEMA,
        "status": "NONCERTIFYING_FRAME_CHOICE",
        "frequency": "4097/8192",
        "dyadic_bits": bits,
        "frame_count": len(frames),
        "frames": frames,
        "role": (
            "choose exact invertible coordinates for a later independent "
            "interval Grassmann enclosure"
        ),
        "does_not_establish": [
            "horizon transport",
            "a radial connection",
            "a finite-flux channel",
            "flux, stability, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bits", type=int, default=42)
    args = parser.parse_args()
    payload = build_schedule(args.bits)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.write_text(rendered)
    print(hashlib.sha256(rendered.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
