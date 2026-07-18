#!/usr/bin/env python3
"""Independent replay of the one-loop Slavnov-Q1 underdetermination theorem."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

try:
    from .one_loop_slavnov_q1_disposition import OUTPUT, ROOT, build, validate
except ImportError:
    from one_loop_slavnov_q1_disposition import OUTPUT, ROOT, build, validate


def _rank(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [entry - factor * pivot for entry, pivot in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def _response(h: list[list[Fraction]]) -> tuple[Fraction, Fraction]:
    p = [Fraction(1), Fraction(), Fraction(), Fraction()]
    riemann = [[[[Fraction() for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    riemann[a][b][c][d] = Fraction(1, 2) * (
                        p[c] * p[b] * h[a][d]
                        + p[d] * p[a] * h[b][c]
                        - p[d] * p[b] * h[a][c]
                        - p[c] * p[a] * h[b][d]
                    )
    ricci = [[sum((riemann[a][b][a][d] for a in range(4)), Fraction()) for d in range(4)] for b in range(4)]
    scalar = sum((ricci[index][index] for index in range(4)), Fraction())
    riemann_squared = sum((riemann[a][b][c][d] ** 2 for a in range(4) for b in range(4) for c in range(4) for d in range(4)), Fraction())
    ricci_squared = sum((entry * entry for row in ricci for entry in row), Fraction())
    return riemann_squared - 2 * ricci_squared + Fraction(1, 3) * scalar * scalar, scalar * scalar


def verify() -> None:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("stored one-loop Slavnov Q1 disposition does not reproduce")
    validate(stored)

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    tt = [[Fraction() for _ in range(4)] for _ in range(4)]
    tt[1][1], tt[2][2] = Fraction(1), Fraction(-1)
    conformal = [[Fraction(int(row == column)) for column in range(4)] for row in range(4)]
    tt_response = _response(tt)
    conformal_response = _response(conformal)
    response = [
        [tt_response[0], Fraction(), tt_response[1], Fraction()],
        [conformal_response[0], Fraction(), conformal_response[1], Fraction()],
    ]
    if response != [[Fraction(1), Fraction(), Fraction(), Fraction()], [Fraction(), Fraction(), Fraction(9), Fraction()]]:
        raise ValueError("independent curvature response replay failed")
    if _rank(response) != 2:
        raise ValueError("independent finite-counterterm ambiguity rank failed")

    mutated = deepcopy(stored)
    mutated["finite_counterterm_ambiguity"]["bulk_response_rank"] = 1
    try:
        validate(mutated)
    except Exception:
        pass
    else:
        raise ValueError("rank mutation was accepted")

    mutated = deepcopy(stored)
    mutated["claim_flags"]["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] = True
    try:
        validate(mutated)
    except Exception:
        pass
    else:
        raise ValueError("Q1 over-promotion mutation was accepted")

    print("One-loop Slavnov Q1 disposition independent replay: PASS")


if __name__ == "__main__":
    verify()
