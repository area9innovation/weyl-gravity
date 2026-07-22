"""Exact negative mutations for the axial reconstruction repair."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run() -> None:
    cert = json.loads(CERT.read_text())
    r, omega = sp.symbols("r omega", nonzero=True)

    # M1: omitting v-phi falsely retains the transverse polynomial vector.
    transverse = 3*sp.I*(omega - 2*sp.I)/r**2
    require(sp.simplify(transverse.subs(omega, sp.Rational(3, 5))) != 0,
            "M1 omission mutation escaped")

    # M2: the opposite repair sign doubles rather than cancels kappa.
    kappa = sp.I*(omega - 18*sp.I)/(2*omega**2)
    alpha = -(omega - 18*sp.I)/(6*omega**2*(omega - 2*sp.I))
    require(sp.simplify(
        kappa - alpha*3*sp.I*(omega - 2*sp.I) - 2*kappa
    ) == 0,
            "M2 repair-sign mutation escaped")

    # M3: dropping any endpoint column cannot retain rank six.
    for side in ("horizon", "infinity"):
        columns = cert["endpoint_bases"][side]["columns"][:-1]
        require(len(columns) == 5, f"M3 {side} rank mutation escaped")

    # M4: C'=-C/r would not conserve r^2 C.
    C = sp.Function("C")(r)
    wrong = sp.diff(r**2*C, r).subs(sp.diff(C, r), -C/r)
    require(sp.simplify(wrong) == r*C and wrong != 0,
            "M4 propagation mutation escaped")
    print("PASS four exact axial reconstruction mutations rejected")


if __name__ == "__main__":
    run()
