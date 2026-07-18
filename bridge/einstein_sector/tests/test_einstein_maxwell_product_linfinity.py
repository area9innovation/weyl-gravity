import unittest

from bridge.einstein_sector.verify_einstein_maxwell_product_linfinity import verify


class EinsteinMaxwellProductLinfinityTests(unittest.TestCase):
    def test_independent_payload_replay(self):
        value = verify()
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["row_count"], 38)
        self.assertTrue(all(not any(counts) for counts in value["defect_counts"].values()))
        self.assertEqual(value["cyclicity"]["unary_pairing_adjoint"], "PASS")
        self.assertEqual(value["cyclicity"]["higher_input_koszul_symmetry"], "PASS")
        self.assertEqual(value["cyclicity"]["higher_output_input_cyclicity"], "PASS")
        self.assertEqual(
            value["cyclicity"]["ordered_first_slot_transpose_counts"],
            {"q1": 192, "q2": 4654, "q3": 61306},
        )


if __name__ == "__main__":
    unittest.main()
