"""Tier-1 fast rail for the BH-1B dynamical extension certificate.

The exhaustive rail is `verify_bh1b_dynamical.py` (a few minutes of exact
computation); it is run separately and recorded in the report receipts.
This suite keeps the commit loop fast: schema/flags, the Noether identity,
the identity-route diffeo annihilation, and the theta audit on
Schwarzschild via the producer machinery (seconds each).
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

import dynamical_charges as dc  # noqa: E402
from weyl_geometry import Geometry, static_spherical_metric  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json").read_text())


class TestFastRail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t, cls.ph = sp.symbols("t phi")
        cls.r, cls.th = sp.symbols("r theta", positive=True)
        cls.alpha = sp.Symbol("alpha")
        cls.m = sp.Symbol("m", positive=True)
        cls.coords = [cls.t, cls.r, cls.th, cls.ph]
        B = 1 - 2 * cls.m / cls.r
        cls.g0 = static_spherical_metric(B, 1 / B, cls.r, cls.th)
        cls.geo0 = Geometry(cls.coords, cls.g0)
        cls.E0 = dc.E_weyl(cls.geo0, cls.alpha)
        cls.L0 = cls.alpha * cls.geo0.invariants()["WeylSq"]
        cls.chi = [2 * cls.m, 0, 0, 0]

    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh1b-dynamical-extension-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"], "BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED")
        flags = CERT["claim_flags"]
        self.assertFalse(flags["radiative_bilinear_flux_matrix_certified"])
        self.assertFalse(flags["second_order_physical_process_certified"])
        self.assertFalse(flags["harmonic_orthogonality_machine_checked"])
        self.assertFalse(flags["stability_certified"])

    def test_noether_identity_schwarzschild(self):
        a = sp.Function("a")(self.t, self.r)
        b = sp.Function("b")(self.t, self.r)
        defects = dc.noether_identity_defect(
            self.coords, self.geo0, self.E0, [a, b, 0, 0], self.L0, self.alpha
        )
        self.assertTrue(all(v == 0 for v in defects.values()))

    def test_diffeo_charge_annihilation_schwarzschild(self):
        a = sp.Function("a")(self.t, self.r)
        b = sp.Function("b")(self.t, self.r)
        kform = dc.diffeo_charge_form_identity_route(
            self.coords, self.geo0, self.E0, self.chi, [a, b, 0, 0], self.L0
        )
        self.assertTrue(all(v == 0 for v in kform.values()))

    def test_theta_conformal_divergence_free(self):
        om = sp.Function("omega")(self.t, self.r)
        thv = dc.theta_up(self.geo0, self.E0, 2 * om * self.g0)
        sqrtg = sp.sqrt(-self.g0.det())
        div = sp.simplify(
            sum(sp.diff(sqrtg * thv[a], self.coords[a]) for a in range(4)) / sqrtg
        )
        self.assertEqual(div, 0)


if __name__ == "__main__":
    unittest.main()
