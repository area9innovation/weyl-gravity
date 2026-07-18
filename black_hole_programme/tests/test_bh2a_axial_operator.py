"""Tier-1 fast rail for the BH-2A axial operator certificate.

Exhaustive rail: `verify_bh2a_axial_operator.py` (~25 s), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

from linearized_bach import LinearizedBach  # noqa: E402
from weyl_geometry import Geometry  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH2A_AXIAL_OPERATOR.json").read_text())


class TestFastRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t, cls.ph = sp.symbols("t phi")
        cls.r = sp.Symbol("r", positive=True)
        cls.x = sp.Symbol("x")
        cls.m = sp.Symbol("m", positive=True)
        cls.coords = [cls.t, cls.r, cls.x, cls.ph]
        B0 = 1 - 2 * cls.m / cls.r
        cls.g0 = sp.diag(-B0, 1 / B0, cls.r**2 / (1 - cls.x**2), cls.r**2 * (1 - cls.x**2))
        cls.B0 = B0
        cls.geo0 = Geometry(cls.coords, cls.g0)
        cls.lb = LinearizedBach(cls.geo0)
        cls.h0 = sp.Function("h0")(cls.t, cls.r)
        cls.h1 = sp.Function("h1")(cls.t, cls.r)
        S = -3 * cls.x * (1 - cls.x**2)
        h = sp.zeros(4, 4)
        h[0, 3] = h[3, 0] = cls.h0 * S
        h[1, 3] = h[3, 1] = cls.h1 * S
        cls.S = S
        cls.dB = cls.lb.build(h)

    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-axial-operator-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"], "BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED"
        )
        flags = CERT["claim_flags"]
        self.assertFalse(flags["flux_matrix_certified"])
        self.assertFalse(flags["extra_branch_horizon_reach_certified"])
        self.assertFalse(flags["causal_well_posedness_certified"])
        self.assertFalse(flags["stability_or_ringdown_certified"])

    def test_nonzero_rows_and_trace(self):
        nz = {(i, j) for i in range(4) for j in range(i, 4)
              if sp.cancel(sp.together(self.dB[i, j])) != 0}
        self.assertEqual(nz, {(0, 3), (1, 3), (2, 3)})
        gi = self.geo0.ginv
        trace = sp.simplify(
            sum(gi[a, b] * self.dB[a, b] for a in range(4) for b in range(4))
        )
        self.assertEqual(trace, 0)

    def test_regge_wheeler_master_equation(self):
        w = sp.Symbol("omega")
        r, B0 = self.r, self.B0
        dRic = self.lb.dRic
        R1 = sp.cancel(sp.cancel(sp.together(dRic[1, 3])) / self.S)
        R2 = sp.cancel(sp.cancel(sp.together(dRic[2, 3])) / (3 * (self.x - 1) * (self.x + 1)))
        H0 = sp.Function("H0")(r)
        H1 = sp.Function("H1")(r)
        four = {self.h0: H0 * sp.exp(sp.I * w * self.t), self.h1: H1 * sp.exp(sp.I * w * self.t)}
        E = sp.exp(sp.I * w * self.t)
        R1f = sp.cancel(sp.together(sp.expand(R1.subs(four).doit() / E)))
        R2f = sp.cancel(sp.together(sp.expand(R2.subs(four).doit() / E)))
        H0sol = sp.solve(sp.Eq(R2f, 0), H0)[0]
        resid = sp.cancel(sp.together(
            R1f.subs({sp.Derivative(H0, r): sp.diff(H0sol, r), H0: H0sol}).doit()))
        num, _ = sp.fraction(resid)
        psi = sp.Function("psi")(r)
        n2, _ = sp.fraction(sp.cancel(sp.together(sp.expand(num).subs(H1, r * psi / B0).doit())))
        V = B0 * (6 / r**2 - 6 * self.m / r**3)
        master = sp.expand(B0 * sp.diff(B0 * sp.diff(psi, r), r) + (w**2 - V) * psi)
        ratio = sp.cancel(sp.together(sp.expand(n2) / master))
        self.assertFalse(ratio.has(psi))
        self.assertEqual(sp.simplify(ratio + r**6), 0)


if __name__ == "__main__":
    unittest.main()
