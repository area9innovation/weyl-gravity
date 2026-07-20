import json
import subprocess
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock import (
    OUTPUT,
    RECEIPT,
    build_certificate,
)


class FiniteHarmonicTier3ProvenanceRelockTests(unittest.TestCase):
    def test_generated_outputs_are_current(self):
        self.assertEqual(json.loads(OUTPUT.read_text()), build_certificate())
        receipt = json.loads(RECEIPT.read_text())
        self.assertEqual(receipt["tier_3"]["status"], "PASS")
        self.assertEqual(receipt["post_promotion_tier_3"]["tests"], 1258)

    def test_fail_closed_boundaries(self):
        value = build_certificate()
        self.assertEqual(value["provenance_graph"]["stale_reference_count"], 0)
        self.assertTrue(all(item["status"] == "TIMEOUT_NONPASS" for item in value["excluded_opt_in_replays"]))
        self.assertIn("does not certify", value["claim_boundary"])

    def test_independent_verifier(self):
        subprocess.run(
            ["python3", "bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock.py"],
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
