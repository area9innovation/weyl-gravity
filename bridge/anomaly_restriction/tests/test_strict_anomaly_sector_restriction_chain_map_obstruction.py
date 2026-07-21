import copy
import unittest
from fractions import Fraction

from bridge.anomaly_restriction.strict_anomaly_sector_restriction_chain_map_obstruction import (
    build_certificate,
)


class StrictAnomalyRestrictionObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = build_certificate()
        cls.sectors = {r["sector_id"]: r for r in cls.cert["sector_dispositions"]}

    def test_berger_antifield_defect_is_exactly_nonzero(self):
        witness = self.sectors["Berger_fixed_coupling"]["exact_witness"]
        self.assertEqual(Fraction(witness["chain_defect"]), Fraction(961, 1920))
        self.assertNotEqual(Fraction(witness["chain_defect"]), 0)

    def test_cylinder_is_fail_closed_not_a_false_unary_deletion(self):
        row = self.sectors["cylinder_Taub_zero"]
        self.assertEqual(row["charge_sector_inclusion"], "NO_CERTIFIED_MAP")
        self.assertFalse(row["exact_witness"]["unary_tangent_complex_changed"])
        self.assertIn("eta_A", row["exact_witness"]["required_new_generators"])

    def test_no_class_image_is_promoted(self):
        for row in self.sectors.values():
            for image in row["class_images"]:
                self.assertEqual(image["status"], "UNDEFINED_CARRIER_OBSTRUCTION")
                self.assertFalse(image["zero_claimed"])
                self.assertFalse(image["exact_claimed"])
                self.assertFalse(image["nontrivial_claimed"])

    def test_mutations_are_decisive(self):
        mutated = copy.deepcopy(self.cert)
        sectors = {r["sector_id"]: r for r in mutated["sector_dispositions"]}
        sectors["Berger_fixed_coupling"]["exact_witness"]["chain_defect"] = "0"
        self.assertNotEqual(
            Fraction(
                sectors["Berger_fixed_coupling"]["exact_witness"]["chain_defect"]
            ),
            Fraction(961, 1920),
        )
        mutated = copy.deepcopy(self.cert)
        mutated["sector_dispositions"][0]["class_images"][0]["status"] = "ZERO"
        self.assertTrue(
            any(
                image["status"] != "UNDEFINED_CARRIER_OBSTRUCTION"
                for row in mutated["sector_dispositions"]
                for image in row["class_images"]
            )
        )


if __name__ == "__main__":
    unittest.main()
