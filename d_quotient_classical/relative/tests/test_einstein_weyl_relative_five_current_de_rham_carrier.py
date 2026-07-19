from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_five_current_de_rham_carrier as carrier


class FiveCurrentDeRhamCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = carrier.build()
        cls.schema = json.loads(carrier.SCHEMA.read_text())

    def test_exact_unary_carrier(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["support_local_de_rham_carrier_selected"])
        self.assertTrue(flags["unary_square_zero_exact"])
        self.assertTrue(flags["unary_cyclicity_exact"])
        self.assertEqual(self.value["carrier"]["row_count"], 160)

    def test_old_current_cone_row_layout_embeds_but_not_its_unary_complex(self) -> None:
        embedding = self.value["carrier"]["existing_current_cone_row_embedding"]
        self.assertEqual(embedding["embedded_rows"], 50)
        self.assertEqual(embedding["added_rows"], 110)
        self.assertFalse(embedding["unary_subcomplex"])

    def test_portable_layout_contains_unary_and_pairing(self) -> None:
        layout = carrier._generated(carrier.exact_data())
        self.assertEqual(len(layout["unary_terms"]), 320)
        self.assertEqual(len(layout["odd_pairing"]), 160)

    def test_claims_remain_fail_closed(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["full_augmented_q2_identity_certified"])
        self.assertFalse(flags["causal_green_homotopy_certified"])
        self.assertFalse(flags["candidate13_causal_crosswalk_certified"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_q2_promotion(self) -> None:
        bad = json.loads(json.dumps(self.value))
        bad["classification"]["full_augmented_q2_identity_certified"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(bad)


if __name__ == "__main__":
    unittest.main()
