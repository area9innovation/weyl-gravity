from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from anomalies.wess_zumino_extended_local_bv_cohomology import OUTPUT, SCHEMA, build, validate
from anomalies.verify_wess_zumino_extended_local_bv_cohomology import verify


class WessZuminoExtendedLocalBVCohomologyTests(unittest.TestCase):
    def test_extended_quotients_and_qme_repair(self) -> None:
        value = build()
        self.assertEqual(value["H04"]["even_quotient_dimension"], 3)
        self.assertEqual(value["H04"]["odd_quotient_dimension"], 1)
        self.assertIn("R(g_hat)^2", value["H04"]["even_classes"])
        self.assertEqual(len(value["H04"]["even_dual_witnesses"]), 3)
        self.assertEqual(
            value["local_algebra"]["all_orders_inverse_status"],
            "VERIFIED_BY_BINOMIAL_THEOREM",
        )
        self.assertEqual(value["H14"]["even_quotient_dimension"], 0)
        self.assertEqual(value["H14"]["odd_quotient_dimension"], 0)
        self.assertEqual(
            value["one_loop_QME"]["strict_breaking_coordinates"],
            value["one_loop_QME"]["boundary_image_coordinates"],
        )

    def test_lorentzian_transfer_and_all_loop_claims_remain_open(self) -> None:
        value = build()
        self.assertEqual(value["lifecycle"]["all_loop_extended_QME"], "OPEN")
        self.assertEqual(value["lifecycle"]["Lorentzian_QME"], "OPEN")
        self.assertTrue(value["lifecycle"]["residual_transfer"].startswith("FORBIDDEN"))
        mutant = deepcopy(value)
        mutant["lifecycle"]["Bridge_4"] = "CERTIFIED"
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_schema_reproduction_and_independent_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        self.assertEqual(verify(), value)


if __name__ == "__main__":
    unittest.main()
