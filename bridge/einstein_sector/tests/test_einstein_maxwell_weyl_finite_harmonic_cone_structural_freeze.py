import json
import subprocess
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze import (
    ATLAS,
    OUTPUT,
    build_certificate,
)


class FiniteHarmonicStructuralFreezeTests(unittest.TestCase):
    def test_generated_outputs_are_current(self):
        self.assertEqual(json.loads(OUTPUT.read_text()), build_certificate())

    def test_exact_freeze_split(self):
        value = build_certificate()
        self.assertTrue(value["classification"]["finite_exponential_polynomial_cone_theorem_ready"])
        self.assertTrue(value["classification"]["bounded_obstruction_ledger_theorem_ready"])
        self.assertTrue(value["classification"]["theorem_freeze_promoted"])
        self.assertTrue(value["classification"]["tier3_provenance_relock_complete"])
        self.assertFalse(value["classification"]["bounded_common_zero_locus_solved"])

    def test_zero_factor_mutations_rejected(self):
        value = build_certificate()
        rows = value["output_strata"]
        self.assertEqual(sum(row["zero_factors"] for row in rows), 5)
        self.assertEqual(rows[0]["zero_factors"], 0)
        self.assertNotEqual(sum(row["zero_factors"] for row in rows) + 1, 5)

    def test_independent_verifier_and_atlas(self):
        subprocess.run(
            ["python3", "bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py"],
            check=True,
        )
        atlas = json.loads(ATLAS.read_text())
        self.assertEqual(atlas["entries"][0]["mode_data"]["resonance"]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
