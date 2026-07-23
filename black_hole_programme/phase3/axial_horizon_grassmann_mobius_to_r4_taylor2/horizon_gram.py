#!/usr/bin/env python3
"""Direct interval Lee--Wald Gram on the future-horizon Frobenius basis."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures import (
    produce as endpoint,
)
from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4 import (
    produce as horizon,
)

HERE = Path(__file__).resolve().parent
CURRENT = (
    HERE.parent / "axial_null_infinity_trace_preflight" / "certificate.json"
)
OUTPUT = HERE / "future_horizon_outward_gram.json"
EPSILON = Fraction(1, 1 << 22)


def conjugate(z: endpoint.CI) -> endpoint.CI:
    return endpoint.CI(z.re, -z.im)


def model_hull(cell: tuple[Fraction, Fraction]) -> list[list[endpoint.CI]]:
    model = horizon.child_initializer_model(cell)
    radius = (cell[1] - cell[0]) / 2
    real = [[endpoint.RI(0) for _ in range(3)] for _ in range(6)]
    imag = [[endpoint.RI(0) for _ in range(3)] for _ in range(6)]
    for i in range(6):
        for j in range(3):
            def hull(row: int) -> endpoint.RI:
                center = model.center[row][j]
                delta = abs(model.derivative[row][j] * radius)
                rem = model.remainder[row][j]
                return endpoint.RI(
                    center - delta + rem.lo,
                    center + delta + rem.hi,
                )
            real[i][j] = hull(i)
            imag[i][j] = hull(i + 6)
    answer = [[endpoint.CI(real[i][j], imag[i][j])
               for j in range(3)] for i in range(6)]
    for j in range(3):
        answer[5][j] = answer[5][j] / EPSILON
    return answer


def load_current() -> tuple[sp.Symbol, sp.Symbol, list[list[sp.Expr]]]:
    payload = json.loads(CURRENT.read_text())["exact_radial_current"]
    r, omega = sp.symbols("r omega", real=True)
    local = {"r": r, "omega": omega, "I": sp.I}
    rows = [[sp.sympify(value, locals=local) for value in row]
            for row in payload["matrix_without_pi_alpha"]]
    return r, omega, rows


def current_box(
    parsed: tuple[sp.Symbol, sp.Symbol, list[list[sp.Expr]]],
    cell: tuple[Fraction, Fraction],
) -> list[list[endpoint.CI]]:
    r, omega, rows = parsed
    environment = {
        r: endpoint.CI(2 + EPSILON),
        omega: endpoint.CI(endpoint.RI(*cell)),
    }
    return [[endpoint.eval_rational_rect(value, environment)
             for value in row] for row in rows]


def outward_gram(
    y: list[list[endpoint.CI]],
    current: list[list[endpoint.CI]],
) -> list[list[endpoint.CI]]:
    answer = [[endpoint.CI() for _ in range(3)] for _ in range(3)]
    minus_i = endpoint.CI(0, -1)
    for a in range(3):
        for b in range(3):
            value = endpoint.CI()
            for i in range(6):
                for j in range(6):
                    value += conjugate(y[i][a]) * current[i][j] * y[j][b]
            answer[a][b] = minus_i * value
    return answer


def interval_inertia(
    matrix: list[list[endpoint.CI]],
) -> tuple[int, int, int] | None:
    current = [[value for value in row] for row in matrix]
    positive = negative = 0
    while current:
        n = len(current)
        pivot = None
        for i in range(n):
            diagonal = current[i][i]
            if not diagonal.im.lo <= 0 <= diagonal.im.hi:
                return None
            if diagonal.re.lo > 0 or diagonal.re.hi < 0:
                pivot = i
                break
        if pivot is None:
            return None
        order = [pivot] + [i for i in range(n) if i != pivot]
        current = [[current[i][j] for j in order] for i in order]
        p = current[0][0].re
        if p.lo > 0:
            positive += 1
        else:
            negative += 1
        if n == 1:
            current = []
            continue
        tail = [[endpoint.CI() for _ in range(n - 1)]
                for _ in range(n - 1)]
        for i in range(1, n):
            for j in range(1, n):
                tail[i - 1][j - 1] = (
                    current[i][j]
                    - current[i][0] * conjugate(current[j][0]) / p
                )
        current = tail
    return positive, negative, 0


def encode(z: endpoint.CI) -> dict[str, list[str]]:
    return {
        "re": [str(z.re.lo), str(z.re.hi)],
        "im": [str(z.im.lo), str(z.im.hi)],
    }


def produce(cells: int = 64) -> dict:
    parsed = load_current()
    records = []
    for index in range(cells):
        lo = Fraction(1, 2) + Fraction(index, 4 * cells)
        hi = Fraction(1, 2) + Fraction(index + 1, 4 * cells)
        cell = (lo, hi)
        gram = outward_gram(model_hull(cell), current_box(parsed, cell))
        inertia = interval_inertia(gram)
        records.append({
            "index": index,
            "frequency": [str(lo), str(hi)],
            "inertia": list(inertia) if inertia is not None else None,
            "gram": [[encode(value) for value in row] for row in gram],
        })
        print(index, inertia, flush=True)
    passed = all(record["inertia"] == [1, 2, 0] for record in records)
    document = {
        "schema": "phase3-axial-future-horizon-outward-gram-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": "PASS" if passed else "METHOD_SHORTFALL",
        "basis": ["XH0a", "XH0b", "EH0"],
        "frequency_interval": ["1/2", "3/4"],
        "cells": cells,
        "epsilon": str(EPSILON),
        "orientation": "minus the increasing-r radial current",
        "normalization": "canonical repaired future-regular Frobenius heads",
        "inertia_for_alpha_W_positive": [1, 2, 0] if passed else None,
        "records": records,
        "provenance": {
            "current_path": str(CURRENT.relative_to(HERE.parents[3])),
            "current_sha256": hashlib.sha256(CURRENT.read_bytes()).hexdigest(),
            "horizon_recurrence": (
                "black_hole_programme/phase3/"
                "axial_endpoint_remainder_enclosures/produce.py"
            ),
        },
        "does_not_establish": [
            "a global horizon-to-infinity connection",
            "a boundary projection rank or scattering map",
            "stability, ghost, positivity, CPT or unitarity",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["status"])
    raise SystemExit(0 if result["status"] == "PASS" else 3)
