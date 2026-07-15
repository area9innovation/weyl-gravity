import unittest

from local_bv.basis_exhaustiveness import grading_signature_manifest


class BasisExhaustivenessTests(unittest.TestCase):
    def test_integer_signatures_are_exhaustive_for_declared_scalar_grading(self) -> None:
        h04 = grading_signature_manifest(0)
        h14 = grading_signature_manifest(1)
        self.assertEqual(h04["integer_solution_count"], 3)
        self.assertEqual(h14["integer_solution_count"], 9)
        self.assertEqual(h04["currently_generated_signature_count"], 2)
        self.assertEqual(h14["currently_generated_signature_count"], 2)
        self.assertEqual(h04["exhaustiveness_status"], "IN_PROGRESS")
        self.assertRegex(h14["grading_manifest_hash"], r"^[0-9a-f]{64}$")

    def test_unsupported_ghost_number_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "ghost number"):
            grading_signature_manifest(2)


if __name__ == "__main__":
    unittest.main()
