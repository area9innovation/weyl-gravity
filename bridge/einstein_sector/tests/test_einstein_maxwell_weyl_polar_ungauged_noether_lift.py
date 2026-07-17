from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _complex_data,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_noether_lift import (
    verify_certificate as verify_independently,
)


class PolarUngaugedNoetherLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_contractions_and_complexes(self) -> None:
        data = _complex_data()
        self.assertEqual(data["matrices"]["source_gauge"].shape, (8, 3))
        self.assertEqual(data["matrices"]["target_gauge"].shape, (8, 4))
        self.assertTrue(self.payload["classification"]["polynomial_ghost_field_equation_identity_chain_map_certified"])
        self.assertFalse(self.payload["contractions"]["k_omega_p_q_inverted"])

    def test_green_current_and_claim_boundary(self) -> None:
        audit = self.payload["local_Green_current"]
        self.assertEqual(audit["off_shell_jet_identity_remainder"], [])
        self.assertTrue(audit["restriction_to_reduced_section_exact"])
        self.assertFalse(self.payload["classification"]["cyclic_BV_chain_map_certified"])
        self.assertFalse(self.payload["classification"]["final_residual_descent_certified"])
        self.assertEqual(self.payload["verification_receipt"]["tier_1"]["status"], "PASS")

    def test_schema_committed_certificate_and_independent_verifier(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
