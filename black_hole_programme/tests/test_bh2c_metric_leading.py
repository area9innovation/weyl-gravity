"""Tier-1 fast rail for the BH-2C metric-leading certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads((PKG / "certificates" / "BH2C_METRIC_LEADING.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-metric-leading-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2C_METRIC_RECONSTRUCTION_LEADING_ORDER_CLASSIFIED")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["rank_one_resonance_certified"])
        self.assertTrue(flags["on_characteristic_vanishing_certified"])
        self.assertFalse(flags["all_orders_reconstruction_certified"])
        self.assertFalse(flags["finite_flux_boundary_class_certified"])

    def test_tables_and_symbol(self):
        for par in ("axial", "polar"):
            for sec in CERT[par]["sectors"].values():
                self.assertTrue(sec["resonant"])
                self.assertEqual(sec["kernel_dim"], 1)
        import sympy as sp
        alpha = sp.Symbol("alpha", positive=True)
        lam = sp.Symbol("lambda_", real=True)
        w1 = sp.Symbol("omega1")
        lead = sp.sympify(CERT["flux_symbol"]["leading"],
                          locals={"alpha": alpha, "lambda_": lam, "omega1": w1,
                                  "I": sp.I, "pi": sp.pi})
        self.assertEqual(sp.simplify(lead.subs(lam, w1)), 0)

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
