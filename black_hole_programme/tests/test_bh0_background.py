"""Tier-1 tests for the BH-0 static spherical background certificate.

Fast rail: schema/hash validation plus direct exact spot checks of the
discrete claims (fixture algebra, defect, invariant J, mutation, EF chart).
Exhaustive rail: the full structurally independent verifier.
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

import verify_bh0_background as vf  # noqa: E402
import weyl_geometry as wg  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json").read_text())


class TestFastRail(unittest.TestCase):
    def setUp(self):
        self.r, self.th = sp.symbols("r theta", positive=True)
        self.beta, self.gam, self.k = sp.symbols("beta gamma k")

    def test_schema_and_token(self):
        schema = json.loads(
            (PKG / "schema" / "bh0-static-spherical-background-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"], "PURE_WEYL_STATIC_SPHERICAL_BACKGROUND_CLASSIFIED")
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")

    def test_claim_flags_fail_closed(self):
        flags = CERT["claim_flags"]
        for name in (
            "regular_causal_horizon_certified",
            "physical_frame_horizon_regularity_certified",
            "exterior_initial_boundary_problem_certified",
            "lee_wald_flux_or_charge_certified",
            "quasinormal_mode_certified",
            "quantum_state_or_hawking_certified",
            "general_completeness_certified",
        ):
            self.assertFalse(flags[name], name)

    def test_fixture_cubic_and_surface_gravities(self):
        r = self.r
        B = wg.mk_metric_function(
            sp.Rational(3, 2), sp.Rational(12, 19), sp.Rational(1, 19), r
        )
        self.assertEqual(
            sp.expand(B * r - sp.Rational(-1, 19) * (r - 1) * (r - 3) * (r - 8)), 0
        )
        dB = sp.diff(B, r)
        expected = {"1": sp.Rational(-7, 19), "3": sp.Rational(5, 57), "8": sp.Rational(-35, 304)}
        for root in CERT["horizon_fixture"]["roots"]:
            kappa = sp.simplify(dB.subs(r, sp.Integer(int(root["r"]))) / 2)
            self.assertEqual(kappa, expected[root["r"]])
            self.assertEqual(sp.sympify(root["chart_surface_gravity"]), kappa)

    def test_einstein_defect_and_invariant(self):
        beta, gam, k, r = self.beta, self.gam, self.k, self.r
        x = sp.Symbol("x")
        u = beta * (2 - 3 * beta * gam)
        w = 1 - 3 * beta * gam
        Q = -u * x**3 + w * x**2 + gam * x - k
        J = sp.expand(u**2 * sp.discriminant(Q, x))
        stored = sp.sympify(
            CERT["residual_gauge"]["continuous_invariant"]["J"],
            locals={"beta": beta, "gamma": gam, "k": k},
        )
        self.assertEqual(sp.simplify(J - sp.expand(stored)), 0)
        fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
        self.assertEqual(J.subs(fx), sp.sympify(CERT["horizon_fixture"]["invariant_J_value"]))
        defect = sp.sympify(
            CERT["einstein_split"]["defect_thth"], locals={"beta": beta, "gamma": gam, "r": r}
        )
        self.assertEqual(sp.simplify(defect - (-gam * (r - 3 * beta) / 2)), 0)
        self.assertEqual(sp.simplify(defect.subs(gam, 0)), 0)

    def test_fixture_bach_flat_and_mutation_not(self):
        t, ph = sp.symbols("t phi")
        r, th = self.r, self.th
        B = wg.mk_metric_function(
            sp.Rational(3, 2), sp.Rational(12, 19), sp.Rational(1, 19), r
        )
        geo = wg.Geometry([t, r, th, ph], wg.static_spherical_metric(B, 1 / B, r, th))
        bach = geo.bach()
        self.assertTrue(all(sp.simplify(bach[i, j]) == 0 for i in range(4) for j in range(4)))
        Bmut = B + sp.Rational(1, 7) / r**2
        geoM = wg.Geometry([t, r, th, ph], wg.static_spherical_metric(Bmut, 1 / Bmut, r, th))
        bachM = geoM.bach()
        self.assertTrue(any(sp.simplify(bachM[i, j]) != 0 for i in range(4) for j in range(4)))

    def test_ef_chart_fixture(self):
        v, ph = sp.symbols("v phi")
        r, th = self.r, self.th
        B = wg.mk_metric_function(
            sp.Rational(3, 2), sp.Rational(12, 19), sp.Rational(1, 19), r
        )
        geo = wg.Geometry([v, r, th, ph], wg.eddington_finkelstein_metric(B, r, th))
        bach = geo.bach()
        self.assertTrue(all(sp.simplify(bach[i, j]) == 0 for i in range(4) for j in range(4)))
        self.assertEqual(sp.simplify(geo.ginv[1, 1] - B), 0)


class TestExhaustiveRail(unittest.TestCase):
    def test_full_independent_verifier(self):
        vf.verify_certificate()


if __name__ == "__main__":
    unittest.main()
