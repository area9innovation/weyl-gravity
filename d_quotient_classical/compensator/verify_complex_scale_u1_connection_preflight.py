#!/usr/bin/env python3
"""Independent exact replay of the separated scale/U(1) preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1.json"
)

EXPECTED_IMPORTS = {
    "level3b": "78258a1a76c81183699e8fe6923c8eccb79c030ec8174c7fe8716a97a923713c",
    "minimal_ladder": "a942ff6a15af0c8a79978dc22ff2cc128a238c3abd6feb2685197d48deaeaf37",
    "level4_real_connection": "d1037ef2fa9222d02513d093c27a02e6fc5da71ec0b731d3b9b2cd2f51e52652",
    "positive_Berger_clock": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
    "Berger_charge": "0ae894432b065f9f4ba116e6e2d42e69d1d60cd37dbf6ef21a14d7073c75b786",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(RESULT.read_text())
    for key, expected in EXPECTED_IMPORTS.items():
        record = payload["imports"][key]
        if record["sha256"] != expected or _sha(ROOT / record["path"]) != expected:
            raise AssertionError(f"{key} import drifted")

    a, b, s = sp.symbols("a b s", real=True)
    gauge = sp.Matrix(
        [
            [1, a, 0],
            [-1, -b, 0],
            [-1, -a, 0],
            [0, s, 1],
            [0, -s, -1],
        ]
    )
    if sp.factor(gauge.extract([0, 1, 3], [0, 1, 2]).det()) != a - b:
        raise AssertionError("independence minor failed")
    if gauge.subs(b, a) * sp.Matrix([-a, 1, -s]) != sp.zeros(5, 1):
        raise AssertionError("reducibility replay failed")
    reducible = payload["bv_and_dressed_trace"][
        "Delta_zero_reducible_completion"
    ]
    if (
        reducible["reducibility_vector_(omega,eta,gamma)"]
        != ["-a", "1", "-s"]
        or reducible["additional_rows"]["Q eta"] != "L_xi eta+z"
        or payload["bv_and_dressed_trace"]["dressed_trace_constraint"][
            "Q_eta_u_hat"
        ]
        != "Delta eta"
    ):
        raise AssertionError("BV reducibility/dressed-trace replay failed")

    Delta, kr, kR, kt, lam = sp.symbols("Delta kr kR kt lam")
    ward = [Delta * kr, Delta * kR, Delta * kt, Delta * lam]
    if [sp.cancel(x / Delta) for x in ward] != [kr, kR, kt, lam]:
        raise AssertionError("Ward branch replay failed")

    cylinder = sp.Matrix(
        [
            [0, 36, -sp.Rational(1, 2), 0, -sp.Rational(1, 4)],
            [0, 12, sp.Rational(1, 6), 0, sp.Rational(1, 4)],
            [0, 0, 1, 0, 1],
        ]
    )
    if cylinder.rank() != 2:
        raise AssertionError("cylinder rank failed")
    expected_cylinder = {
        (1, 0, 0, 0, 0),
        (0, 0, 0, 1, 0),
        (0, -sp.Rational(1, 144), -1, 0, 1),
    }
    if {tuple(x) for x in cylinder.nullspace()} != expected_cylinder:
        raise AssertionError("cylinder kernel failed")

    beta2 = sp.Rational(9, 16)
    berger = sp.Matrix(
        [
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                -sp.Rational(151, 960),
                -beta2 / 2,
                -sp.Rational(1, 4),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                sp.Rational(3, 320),
                -beta2 / 2,
                sp.Rational(1, 4),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                sp.Rational(133, 960),
                -beta2 / 2,
                sp.Rational(1, 4),
            ],
            [0, 0, sp.Rational(151, 480), -beta2, 1],
            [0, 0, 0, 1, 0],
        ]
    )
    expected = sp.Matrix(
        [0, -sp.Rational(1600, 22801), -sp.Rational(480, 151), 0, 1]
    )
    positive_fixture = sp.Matrix(
        [5, 0, 1, 1, sp.Rational(119, 480)]
    )
    if (
        berger.rank() != 4
        or berger.nullspace() != [expected]
        or berger * expected != sp.zeros(5, 1)
        or berger[:4, :] * positive_fixture != sp.zeros(4, 1)
        or berger * positive_fixture != sp.Matrix([0, 0, 0, 0, 1])
    ):
        raise AssertionError("Berger stationary/Gauss replay failed")
    minor = sp.factor(berger.extract([0, 1, 2, 4], [0, 1, 2, 3]).det())
    if minor != sp.Rational(2120493, 40960000):
        raise AssertionError("Berger rank witness failed")

    zW, zA, chi = sp.symbols("zW zA chi")
    if sp.factor(sp.Matrix([[zW, chi], [chi, zA]]).det()) != zW * zA - chi**2:
        raise AssertionError("kinetic determinant failed")

    verdict = payload["terminal_verdict"]
    if (
        verdict["healthy_locus"] != "EMPTY"
        or verdict["selected_action"]
        or verdict["causal_completion_activated"]
        or payload["stationary_systems"]["frozen_Berger_clock_lift"][
            "decisive_relation"
        ]
        != "Z_theta=0"
    ):
        raise AssertionError("terminal scope drifted")
    print(
        "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1 "
        "independent exact replay: PASS"
    )


if __name__ == "__main__":
    verify()
