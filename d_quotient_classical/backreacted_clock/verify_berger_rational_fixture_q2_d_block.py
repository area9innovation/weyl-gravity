#!/usr/bin/env python3
"""Independent action rederivation of the rational Berger q2/D block."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value) for value in row] for row in rows])


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    c, lapse, rho, omega = sp.symbols("c N rho omega", positive=True, real=True)
    lagrangian = sp.factor(lapse * c * (
        sp.Rational(5, 8) * 4 * (1 - c**2) ** 2 / 3
        + rho**2 * omega**2 / (2 * lapse**2)
        - (4 - c**2) * rho**2 / 24
        - sp.Rational(119, 1920) * rho**4
    ))
    fields = (c, lapse, rho)
    fixture = {c: 3 * sp.sqrt(10) / 20, lapse: 1, rho: 1, omega: sp.Rational(3, 4)}
    assert all(sp.factor(sp.diff(lagrangian, field).subs(fixture)) == 0 for field in fields)
    hessian = sp.Matrix(3, 3, lambda row, column: sp.factor(sp.diff(lagrangian, fields[row], fields[column]).subs(fixture)))
    q1 = _matrix(payload["classical_unary_q1"]["matrix"])
    assert q1[3:6, 0:3] == hessian
    assert q1[:3, :] == sp.zeros(3, 6) and q1[:, 3:6] == sp.zeros(6, 3)
    expected = {}
    for output in range(3):
        for left in range(3):
            for right in range(left, 3):
                value = sp.factor(sp.diff(lagrangian, fields[output], fields[left], fields[right]).subs(fixture))
                if value:
                    expected[(3 + output, left, right)] = value
    observed = {(entry["output"], entry["left"], entry["right"]): sp.sympify(entry["coefficient"]) for entry in payload["classical_binary_q2"]["entries"]}
    assert observed == expected
    pairing = _matrix(payload["cyclic_pairing"]["matrix"])
    assert pairing.rank() == 6
    assert q1.T * pairing + pairing * q1 == sp.zeros(6)
    assert _matrix(payload["D_action_cl"]["matrix"]) == sp.zeros(6)
    assert payload["scope"]["not_support_local_q2"] is True
    assert payload["exact_checks"]["declared_mode_block_closed"] is True
    assert payload["flags"]["CLASSICAL_REDUCED_MODE_Q2_D"] is True
    assert payload["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is False
    assert payload["flags"]["ND2_PHYSICAL_EXECUTION_AUTHORIZED"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK_INDEPENDENT: PASS")
    print("action-derived six-row REDUCED-MODE q2/D block: PASS")
    print("full support-local q2 and nonzero-weight D test: OPEN")


if __name__ == "__main__":
    main()
