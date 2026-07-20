"""Tier-1 fast rail for the symbolic-frequency indicial certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-symbolic-indicial-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2C_SYMBOLIC_INDICIAL_EXCEPTIONAL_SET_IS_OMEGA_ZERO")
        f = CERT["claim_flags"]
        for k in ("polar_symbolic_exponents_certified",
                  "polar_mu2w_symbolic_certified",
                  "axial_symbolic_exponents_certified",
                  "semisimplicity_certified", "exceptional_set_certified",
                  "resonance_omega_independence_certified"):
            self.assertTrue(f[k], k)
        for k in ("metric_reconstruction_all_orders_certified",
                  "symbolic_flux_table_certified",
                  "endpoint_nonselection_theorem_certified",
                  "general_l_certified"):
            self.assertFalse(f[k], k)

    def test_symbolic_exponents_are_exact(self):
        pol = CERT["polar"]["sectors"]
        self.assertEqual(sorted(pol["0"]), ["-1", "-2", "-3"])
        self.assertEqual(sorted(pol["-2*I*omega"]),
                         ["-4*I*omega - 1", "-4*I*omega - 2",
                          "-4*I*omega - 3"])
        # every recorded exponent is exact -- never a float
        for sigs in pol.values():
            for s in sigs:
                self.assertNotIn(".", s, s)

    def test_exceptional_set_is_exactly_omega_zero(self):
        exc = CERT["exceptional_set"]
        self.assertEqual(exc["real_frequencies"], ["0"])
        self.assertGreaterEqual(len(exc["mechanisms"]), 2)
        # the omega = 0 mutation must show a genuine Jordan degeneration
        mut = CERT["polar"]["omega_zero_mutation"]
        self.assertEqual(mut["charpoly"], "lam**6")
        self.assertLess(mut["geometric_multiplicity"],
                        mut["algebraic_multiplicity"])

    def test_resonance_is_frequency_independent(self):
        res = CERT["resonance"]
        self.assertFalse(res["within_sector_omega_dependent"])
        self.assertTrue(res["cross_sector_integral_only_for_imaginary_omega"])
        self.assertTrue(res["real_parts_omega_independent"])
        self.assertEqual(sorted(res["within_sector_differences"]),
                         [-2, -1, 1, 2])
        for rp in res["real_parts_by_sector"].values():
            self.assertEqual(sorted(rp), [-3, -2, -1])
        # every cross-sector difference must carry omega
        for d in res["cross_sector_differences"]:
            self.assertIn("omega", d)

    def test_axial_rank_one_and_extends_not_supersedes(self):
        self.assertEqual(CERT["axial"]["level2_determinant"],
                         "identically zero (rank 1)")
        self.assertEqual(CERT["axial"]["rw_charpoly"], "lam*(lam + 2*I*omega)")
        self.assertIn("extends", CERT)
        self.assertNotIn("supersedes", CERT)

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal", "stability", "ghost",
                       "unitarity"):
            self.assertNotIn(banned, blob, banned)


if __name__ == "__main__":
    unittest.main()
