"""Tier-1 tests for the BH-1A normalized generator certificate."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

import verify_bh1a_normalized_generator as vf  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH1A_NORMALIZED_GENERATOR.json").read_text())


class TestFastRail(unittest.TestCase):
    def setUp(self):
        self.beta, self.gam, self.k, self.alpha = sp.symbols("beta gamma k alpha")
        self.rh = sp.Symbol("r_h")
        self.SYM = {
            "beta": self.beta,
            "gamma": self.gam,
            "k": self.k,
            "alpha": self.alpha,
            "pi": sp.pi,
            "r_h": self.rh,
        }

    def _sym(self, s):
        return sp.sympify(s, locals=dict(self.SYM))

    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh1a-normalized-generator-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"], "BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR"
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["static_first_law_certified"])
        self.assertFalse(flags["full_bh1_phase_space_certified"])
        self.assertFalse(flags["dynamical_perturbation_flux_certified"])
        self.assertFalse(flags["stability_certified"])
        self.assertFalse(flags["quantum_or_hawking_certified"])

    def test_hamiltonian_closes_normalized_charge_form(self):
        beta, gam, k, alpha = self.beta, self.gam, self.k, self.alpha
        u = beta * (2 - 3 * beta * gam)
        F = [
            16 * sp.pi * alpha * (12 * beta * gam * k - gam**2 - 4 * k),
            16 * sp.pi * alpha * beta * (6 * beta * k - gam),
            16 * sp.pi * alpha * beta * (3 * beta * gam - 2),
        ]
        H = self._sym(CERT["hamiltonian"]["H"])
        for p, f in zip([beta, gam, k], F):
            self.assertEqual(sp.simplify(sp.diff(H, p) - u * f), 0)

    def test_first_law_at_fixture_event_horizon(self):
        beta, gam, k = self.beta, self.gam, self.k
        rh = self.rh
        u = beta * (2 - 3 * beta * gam)
        w = 1 - 3 * beta * gam
        B = w - u / rh + gam * rh - k * rh**2
        r = sp.Symbol("r", positive=True)
        Bp = sp.diff(w - u / r + gam * r - k * r**2, r).subs(r, rh)
        S = self._sym(CERT["wald_entropy"]["S"])
        H = self._sym(CERT["hamiltonian"]["H"])
        T = u * Bp / (4 * sp.pi)
        fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
        for p in (beta, gam, k):
            dS_p = sp.diff(S, p) - sp.diff(S, rh) * sp.diff(B, p) / Bp
            self.assertEqual(
                sp.simplify((sp.diff(H, p) - T * dS_p).subs(fx).subs(rh, 3)), 0
            )

    def test_schwarzschild_ensemble(self):
        beta = self.beta
        H = self._sym(CERT["hamiltonian"]["H"])
        S = self._sym(CERT["wald_entropy"]["S"])
        self.assertEqual(sp.simplify(H.subs({self.gam: 0, self.k: 0})), 0)
        self.assertEqual(
            sp.simplify(S.subs({self.gam: 0, self.rh: 2 * beta}) - 64 * sp.pi**2 * self.alpha),
            0,
        )


class TestExhaustiveRail(unittest.TestCase):
    def test_full_independent_verifier(self):
        vf.verify_certificate()


if __name__ == "__main__":
    unittest.main()
