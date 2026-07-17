"""Tier-1 tests for the BH-1 Lee--Wald preflight certificate."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema
import sympy as sp

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

import verify_bh1_lee_wald_preflight as vf  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json").read_text())


class TestFastRail(unittest.TestCase):
    def setUp(self):
        self.beta, self.gam, self.k, self.alpha = sp.symbols("beta gamma k alpha")
        self.SYM = {
            "beta": self.beta,
            "gamma": self.gam,
            "k": self.k,
            "alpha": self.alpha,
            "pi": sp.pi,
        }

    def _sym(self, s):
        return sp.sympify(s, locals=dict(self.SYM))

    def test_schema_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh1-lee-wald-preflight-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"], "BH1_PREFLIGHT_COMPLETE_BARE_FORM_NONINTEGRABLE")
        flags = CERT["claim_flags"]
        self.assertFalse(flags["differentiable_hamiltonian_certified"])
        self.assertFalse(flags["entropy_or_first_law_certified"])
        self.assertFalse(flags["full_horizon_phase_space_certified"])
        self.assertFalse(flags["dynamical_perturbation_flux_certified"])
        self.assertFalse(flags["stability_certified"])

    def test_obstruction_algebra_from_stored_charges(self):
        beta, gam, k = self.beta, self.gam, self.k
        ps = [beta, gam, k]
        F = [
            self._sym(CERT["bare_charges"]["F_beta"]),
            self._sym(CERT["bare_charges"]["F_gamma"]),
            self._sym(CERT["bare_charges"]["F_k"]),
        ]
        dF = {
            (i, j): sp.simplify(sp.diff(F[j], ps[i]) - sp.diff(F[i], ps[j]))
            for i in range(3)
            for j in range(i + 1, 3)
        }
        self.assertTrue(any(v != 0 for v in dF.values()))
        gen_c = [-3 * beta**2, 6 * beta * gam - 2, gam]
        for j in range(3):
            s = sp.Integer(0)
            for i in range(3):
                if i < j:
                    s += gen_c[i] * dF[(i, j)]
                elif i > j:
                    s -= gen_c[i] * dF[(j, i)]
            self.assertEqual(sp.simplify(s), 0)
        self.assertEqual(sp.simplify(sum(f * v for f, v in zip(F, gen_c))), 0)
        gen_l = [-beta, gam, 2 * k]
        self.assertEqual(sp.simplify(sum(f * v for f, v in zip(F, gen_l))), 0)

    def test_fixture_values(self):
        fx = {
            self.beta: sp.Rational(3, 2),
            self.gam: sp.Rational(12, 19),
            self.k: sp.Rational(1, 19),
        }
        hf = CERT["horizon_fixture_charges"]
        F_beta = self._sym(CERT["bare_charges"]["F_beta"])
        self.assertEqual(sp.simplify(F_beta.subs(fx) - self._sym(hf["F_beta"])), 0)

    def test_schwarzschild_limits(self):
        F_beta = self._sym(CERT["bare_charges"]["F_beta"])
        F_gamma = self._sym(CERT["bare_charges"]["F_gamma"])
        F_k = self._sym(CERT["bare_charges"]["F_k"])
        schw = {self.gam: 0, self.k: 0}
        self.assertEqual(sp.simplify(F_beta.subs(schw)), 0)
        self.assertEqual(sp.simplify(F_gamma.subs(schw)), 0)
        self.assertEqual(sp.simplify(F_k.subs(schw) + 32 * sp.pi * self.alpha * self.beta), 0)


class TestExhaustiveRail(unittest.TestCase):
    def test_full_independent_verifier(self):
        vf.verify_certificate()


if __name__ == "__main__":
    unittest.main()
