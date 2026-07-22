"""Independent verifier for the Phase-3 axial endpoint-basis obstruction."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
BH = HERE.parents[1]
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def direct_linearized_bach_row():
    """Recompute the omitted row with the independent LinearizedBach rail."""
    import sys
    sys.path.insert(0, str(BH))
    from linearized_bach import LinearizedBach
    from weyl_geometry import Geometry

    v, r, x, ph = sp.symbols("v r x phi")
    omega = sp.Symbol("omega")
    B = 1 - 2 / r
    g = sp.zeros(4, 4)
    g[0, 0] = -B
    g[0, 1] = g[1, 0] = 1
    g[2, 2] = r**2 / (1 - x**2)
    g[3, 3] = r**2 * (1 - x**2)
    h0, h1 = sp.Function("h0")(v, r), sp.Function("h1")(v, r)
    S = -3*x*(1-x**2)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0*S
    h[1, 3] = h[3, 1] = h1*S
    lb = LinearizedBach(Geometry([v, r, x, ph], g))
    lb.build(h)
    H0, H1 = sp.Function("H0")(r), sp.Function("H1")(r)
    phase = sp.exp(sp.I*omega*v)
    row = lb.dRic[0, 3].subs(x, sp.Rational(1, 2)) / S.subs(x, sp.Rational(1, 2))
    row = sp.factor(sp.cancel(row.subs({h0: H0*phase, h1: H1*phase}).doit()/phase))
    return row, r, omega, H0, H1


def verify() -> None:
    cert = json.loads(CERT.read_text())
    jsonschema.validate(cert, json.loads(SCHEMA.read_text()))
    row, r, omega, H0, H1 = direct_linearized_bach_row()
    recorded = sp.sympify(
        cert["metric_reconstruction_gate"]["omitted_row_formula_ell2"],
        locals={"r": r, "omega": omega, "H0": sp.Function("H0"),
                "H1": sp.Function("H1"), "I": sp.I})
    if sp.simplify(row-recorded) != 0:
        raise AssertionError("independent LinearizedBach row disagrees")
    residual = sp.factor(sp.cancel(row.subs({H0: -sp.I*omega*r+2+2/r,
                                             H1: 1}).doit()))
    expected = 3*sp.I*(omega-2*sp.I)/r**2
    if sp.simplify(residual-expected) != 0:
        raise AssertionError(f"independent polynomial residual changed: {residual}")
    if sp.solve(sp.Eq(sp.factor(residual*r**2), 0), omega) != [2*sp.I]:
        raise AssertionError("residual zero set changed")
    horizon = cert["carrier_endpoint_basis"]["horizon"]
    if horizon["integer_spaced_resonance"]["cokernel_obstruction"] != "0":
        raise AssertionError("carrier resonance is no longer compatible")
    flags = cert["claim_flags"]
    if flags["complete_metric_endpoint_basis_certified"]:
        raise AssertionError("obstructed metric basis was promoted")
    for forbidden in ("connection", "finite_flux_or_scattering"):
        if any(value for key, value in flags.items() if forbidden in key):
            raise AssertionError(f"forbidden promotion through {forbidden}")
    print("PASS independent axial endpoint-basis obstruction verifier")


if __name__ == "__main__":
    verify()
