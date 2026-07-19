"""Tier-1 fast rail for the BH-4 Hawking-monodromy certificate.

Exhaustive rail: `verify_bh4_hawking_monodromy.py` (~10 min, independent
VbGeo engine), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH4_HAWKING_MONODROMY.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh4-hawking-monodromy-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH4_HAWKING_MONODROMY_TEMPERATURE_UNIVERSAL_ACROSS_BRANCHES",
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["monodromy_universality_certified"])
        self.assertTrue(flags["thermal_extra_branch_weighting_certified"])
        self.assertTrue(flags["first_law_temperature_consistency_certified"])
        self.assertFalse(flags["lorentzian_hadamard_state_certified"])
        self.assertFalse(flags["renormalized_stress_tensor_certified"])
        self.assertFalse(flags["lorentzian_causal_hawking_theorem"])

    def test_quantum_boundary_and_vocabulary(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertIn("REDUCED-MODE", CERT["declaration"]["quantum_status"])
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal", "lorentzian-causal hawking theorem exists"):
            self.assertNotIn(banned, blob)

    def test_monodromy_exact_spot_check(self):
        """Every recorded exponent has monodromy 1 or e^{8 pi m omega}, and
        each family has at least one thermal exponent (exact recomputation
        from the recorded spectra strings)."""
        import sympy as sp

        m = sp.Symbol("m", positive=True)
        w = sp.Symbol("omega", positive=True)
        loc = {"m": m, "omega": w, "I": sp.I}
        thermal = sp.exp(8 * sp.pi * m * w)
        for fam, exps in CERT["spectra"].items():
            n_th = 0
            for s_ in exps:
                s0 = sp.sympify(s_, locals=loc)
                fac = sp.simplify(sp.exp(2 * sp.pi * sp.I * s0))
                trivial = sp.simplify(fac - 1) == 0
                is_th = sp.simplify(fac - thermal) == 0
                self.assertTrue(trivial or is_th, (fam, s_))
                n_th += int(bool(is_th))
            self.assertGreaterEqual(n_th, 1, fam)
        # T_H consistency
        self.assertEqual(CERT["temperature"]["T_H"], "1/(8*pi*m)")


if __name__ == "__main__":
    unittest.main()
