from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_physical_ring import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_physical_ring import (
    verify_certificate as verify_independently,
)


class AxialPhysicalRingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_no_momentum_inverse_and_bezout_unit(self) -> None:
        audit = self.payload["audit"]
        self.assertIn("k", audit["not_inverted"])
        self.assertTrue(audit["Bezout_unit_ideal_witness"]["right_hand_side_is_a_unit_in_R_phys"])
        self.assertTrue(audit["determinantal_ideals_over_R_phys_omega"]["no_k_torsion"])

    def test_all_physical_fibers(self) -> None:
        specialization = self.payload["audit"]["specialization"]
        self.assertEqual(specialization["fiberwise_Smith_invariants"], ["1", "1", "p", "p*q"])
        self.assertTrue(self.payload["audit"]["zero_momentum_audit"]["zero_momentum_retained"])

    def test_stronger_global_smith_claim_fails_closed(self) -> None:
        self.assertFalse(
            self.payload["classification"]["global_unimodular_Smith_transformations_over_multivariate_ring_claimed"]
        )

    def test_Einstein_image_is_full_q_primary_summand(self) -> None:
        primary = self.payload["audit"]["Einstein_image_primary_identification"]
        self.assertTrue(primary["source_image_lies_in_q_primary_summand"])
        self.assertTrue(primary["Einstein_image_equals_complete_q_primary_summand"])
        self.assertEqual(primary["source_K_dimension"], primary["target_q_primary_K_dimension"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
