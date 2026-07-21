"""Tier-1 fast rail for the BH-2C symbolic-frequency finite-flux certificate.

Structural checks only (no heavy symbolic recompute -- that is the verifier's
independent VbGeo rail).  Confirms the certificate's schema, verdict token,
the omega-independent finite/divergent split, the pure-imaginary carrier
exponents, and the fail-closed claim boundary.
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
CERT = json.loads(
    (PKG / "certificates" / "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_verdict(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh2c-symbolic-flux-radiation-class-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2C_SYMBOLIC_FREQUENCY_FINITE_FLUX_RADIATION_CLASS_EINSTEIN_SELECTED")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])

    def test_einstein_finite_side(self):
        tbl = CERT["einstein_literal_flux_axial"]
        for pair in ("E0|E0", "E2|E2"):
            self.assertEqual(tbl[pair]["leading_power"], [-2, 0])
            self.assertTrue(tbl[pair]["finite"])
            # leading coefficient is recorded and non-empty
            self.assertTrue(str(tbl[pair]["leading_coeff"]).strip())

    def test_carrier_exponents_pure_imaginary(self):
        ce = CERT["carrier_exponents_axial"]
        self.assertEqual(ce["rates"], ["-I*omega", "I*omega"])
        self.assertEqual(ce["powers"],
                         {"-I*omega": "-2*I*omega", "I*omega": "2*I*omega"})
        w = sp.Symbol("omega", positive=True)
        for e_str in ("-I*omega", "I*omega", "-2*I*omega", "2*I*omega"):
            e = sp.sympify(e_str, locals={"omega": w, "I": sp.I})
            self.assertEqual(sp.re(e), 0)   # amplitude real part 0
            self.assertNotEqual(sp.im(e), 0)  # genuinely oscillatory

    def test_frequency_independence(self):
        fd = CERT["frequency_dependence"]
        self.assertEqual(fd["extra_carrier_amplitude_real_part"], 0)
        self.assertTrue(fd["finite_divergent_split_omega_independent"])
        self.assertTrue(fd["omega_enters_only_imaginary_tortoise_phase"])
        self.assertIn("omega = 0", fd["excluded_frequency"])

    def test_claim_boundary(self):
        cf = CERT["claim_flags"]
        for t in ("axial_einstein_literal_flux_symbolic_certified",
                  "axial_carrier_exponents_symbolic_certified",
                  "finite_divergent_split_omega_independent_certified",
                  "no_real_exceptional_frequency_certified"):
            self.assertTrue(cf[t])
        for f in ("axial_divergent_table_symbolic_certified",
                  "symbolic_log_tails_certified",
                  "polar_literal_flux_symbolic_recomputed",
                  "asymptotic_phase_space_constructed",
                  "summability_certified", "general_l_certified"):
            self.assertFalse(cf[f])
        self.assertGreaterEqual(len(CERT["does_not_establish"]), 1)

    def test_no_overclaim_vocabulary(self):
        # promotional terms must not appear in POSITIVE fields; they are
        # allowed inside the honest-boundary ledgers (does_not_establish,
        # missing_objects), which legitimately name what is NOT claimed.
        positive = {k: v for k, v in CERT.items()
                    if k not in ("does_not_establish", "missing_objects")}
        blob = json.dumps(positive).lower()
        for banned in ("ringdown", "quasinormal", "scattering",
                       "lorentzian_certified"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
