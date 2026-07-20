#!/usr/bin/env python3
"""Independent exact replay of the two-field charge/health preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(RESULT.read_text())
    for record in payload["imports"].values():
        if _sha(ROOT / record["path"]) != record["sha256"]:
            raise AssertionError("import hash replay failed")

    cases = [
        (sp.Matrix([[1], [0]]), [1]),
        (sp.Matrix([[2], [0]]), [2]),
        (sp.eye(2), [1, 1]),
        (sp.diag(2, 4), [2, 4]),
    ]
    for matrix, expected in cases:
        diagonal = smith_normal_form(matrix, domain=ZZ)
        actual = [
            abs(int(diagonal[i, i]))
            for i in range(min(diagonal.rows, diagonal.cols))
            if diagonal[i, i] != 0
        ]
        if actual != expected:
            raise AssertionError("independent SNF replay failed")

    a, b1, b2, s1, s2 = sp.symbols("a b1 b2 s1 s2")
    gauge = sp.Matrix(
        [
            [1, a, 0],
            [-1, -b1, 0],
            [-1, -b2, 0],
            [0, s1, 1],
            [0, s2, 0],
            [-1, -a, 0],
            [0, -s1, -1],
        ]
    )
    if (
        sp.factor(gauge.extract([0, 1], [0, 1]).det()) != a - b1
        or sp.factor(gauge.extract([0, 2], [0, 1]).det()) != a - b2
        or sp.factor(gauge.extract([0, 3, 4], [0, 1, 2]).det()) != -s2
    ):
        raise AssertionError("gauge minors replay failed")
    dependent = gauge.subs({b1: a, b2: a, s2: 0})
    if dependent * sp.Matrix([-a, 1, -s1]) != sp.zeros(7, 1):
        raise AssertionError("reducibility replay failed")

    k11, k12, k22 = sp.symbols("k11 k12 k22")
    if sp.factor(sp.Matrix([[k11, k12], [k12, k22]]).det()) != (
        k11 * k22 - k12**2
    ):
        raise AssertionError("positivity determinant replay failed")

    berger = sp.Matrix(
        [
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                -sp.Rational(151, 960),
                -sp.Rational(1, 2),
                -sp.Rational(1, 4),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                sp.Rational(3, 320),
                -sp.Rational(1, 2),
                sp.Rational(1, 4),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                sp.Rational(133, 960),
                -sp.Rational(1, 2),
                sp.Rational(1, 4),
            ],
        ]
    )
    fixture = sp.Matrix(
        [5, 0, 1, sp.Rational(9, 16), sp.Rational(119, 480)]
    )
    if berger * fixture != sp.zeros(3, 1):
        raise AssertionError("relative-clock stationary replay failed")

    verdict = payload["terminal_verdict"]
    if (
        verdict["healthy_locus"] != "EMPTY"
        or verdict["selected_action"]
        or verdict["full_BV_or_causal_completion_activated"]
    ):
        raise AssertionError("terminal promotion detected")
    print(
        "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1 "
        "independent exact replay: PASS"
    )


if __name__ == "__main__":
    verify()
