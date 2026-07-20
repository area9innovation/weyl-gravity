"""Tier-1 fast rail for the polar metric-side indicial/obstruction certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2C_POLAR_METRIC_INDICIAL.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-polar-metric-indicial-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2C_POLAR_METRIC_INDICIAL_MU0_REQUIRES_SHEARING")
        f = CERT["claim_flags"]
        self.assertTrue(f["leading_charpoly_symbolic_certified"])
        self.assertTrue(f["semisimple_sector_exponent_certified"])
        self.assertTrue(f["jordan_structure_certified"])
        for k in ("mu0_exponents_certified", "shearing_analysis_performed",
                  "log_tail_mechanism_certified", "general_l_certified"):
            self.assertFalse(f[k], k)

    def test_fixture_cross_check(self):
        est = CERT["established"]
        self.assertEqual(est["charpoly"], "lam**3*(lam + 2*I*omega)")
        self.assertEqual(est["fixture_charpoly_omega_3_5"],
                         "lam**3*(5*lam + 6*I)/5")

    def test_both_controls(self):
        # positive control: method reproduces certified sigma0 where valid
        pos = CERT["established"]["semisimple_sector"]
        self.assertTrue(pos["match"])
        self.assertEqual(pos["extracted"], pos["certified_sigma0"])
        # negative control: method fails where the Jordan block invalidates it
        neg = CERT["obstruction"]["evidence"]
        self.assertFalse(neg["match"])
        self.assertNotIn(neg["certified_sigma0"], neg["extracted"])
        self.assertIn("REFUTED", neg["reading"])

    def test_obstruction_is_recorded_as_obstruction(self):
        obs = CERT["obstruction"]
        self.assertEqual(obs["kernel_staircase"], [1, 2, 3])
        self.assertEqual(obs["jordan_chain_lengths"], [3])
        self.assertEqual(obs["algebraic_multiplicity"], 3)
        self.assertEqual(obs["geometric_multiplicity"], 1)
        self.assertIn("Moser", obs["required_technique"])

    def test_log_tail_link_is_explicitly_disclaimed(self):
        nc = CERT["not_claimed"]
        self.assertFalse(nc["jordan_chain_explains_log_tails"])
        self.assertFalse(nc["mu0_metric_exponents_established"])
        for sec in CERT["sectors"].values():
            for v in sec["exponent_log_factors"].values():
                self.assertEqual(v, 0)

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal", "stability", "ghost",
                       "unitarity"):
            self.assertNotIn(banned, blob, banned)


if __name__ == "__main__":
    unittest.main()
