"""Tier-1 fast rail for the symplectic-extension normal-form certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2_SYMPLECTIC_NORMAL_FORM.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2-symplectic-normal-form-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(schema and CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2_SYMPLECTIC_EXTENSION_HYPERBOLIC_NORMAL_FORM")
        f = CERT["claim_flags"]
        for k in ("normal_form_certified", "cross_invariance_certified",
                  "self_pairing_removability_certified", "inertia_certified",
                  "lagrangian_status_certified", "a_zero_branch_certified",
                  "invariant_sign_question_resolved"):
            self.assertTrue(f[k], k)
        for k in ("symbolic_frequency_certified", "general_l_certified"):
            self.assertFalse(f[k], k)

    def test_shear_law_has_the_conjugate_on_beta(self):
        # the transformation law is d -> d + 2 Re(conj(beta) a), NOT 2 Re(beta a)
        self.assertEqual(CERT["shear_action"]["self"],
                         "d + 2*Re(conj(beta)*a)")
        self.assertEqual(CERT["shear_action"]["cross"], "a (invariant)")

    def test_hyperbolic_block(self):
        blk = CERT["theorem_a_nonzero"]["block"]
        self.assertEqual(blk["determinant"], "-|a|^2")
        self.assertEqual(blk["rank_when_a_nonzero"], 2)
        self.assertEqual(blk["inertia"], [1, 1])
        self.assertIn("hyperbolic", blk["normal_form"])
        lag = CERT["theorem_a_nonzero"]["lagrangian"]
        self.assertTrue(lag["E_is_lagrangian_in_block"])

    def test_a_zero_branch_is_qualitatively_different(self):
        dz = CERT["degeneration_a_zero"]
        self.assertTrue(dz["self_pairing_invariant"])
        self.assertTrue(dz["sign_of_d_is_invariant"])
        self.assertTrue(dz["E_joins_radical"])
        self.assertEqual(dz["rank_when_d_nonzero"], 1)

    def test_both_mutations_and_controls(self):
        m = CERT["mutations"]
        self.assertTrue(m["M1_shear_moves_self_pairing_fixes_invariants"])
        self.assertTrue(m["M2_at_a_zero_shears_cannot_move_self_pairing"])
        self.assertGreaterEqual(m["trials"], 3)
        # every fixture control must show E isotropic and cross nonzero
        for key, ctl in CERT["fixture_controls"].items():
            self.assertTrue(ctl["cross_nonzero"], key)

    def test_sign_question_resolved_negatively_not_claimed_positively(self):
        res = CERT["resolves"]
        self.assertIn("NEGATIVELY", res["answer"])
        self.assertTrue(res["supersedes_nothing"])
        nc = CERT["not_claimed"]
        self.assertFalse(nc["sign_from_a_canonical_lift"])
        self.assertFalse(nc["canonical_direct_sum_splitting"])

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal", "scattering",
                       "ghost-free", "unitarity"):
            self.assertNotIn(banned, blob, banned)


if __name__ == "__main__":
    unittest.main()
