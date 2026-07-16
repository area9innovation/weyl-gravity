from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_symplectic_preflight import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_symplectic_preflight import (
    verify_certificate as verify_independently,
)


class EinsteinMaxwellWeylSymplecticPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_quotient_map_is_injective(self) -> None:
        theorem = self.payload["quotient_injectivity_theorem"]
        self.assertEqual(theorem["elimination"], "-3*Delta_S2_sigma + 2*sigma")
        self.assertEqual(theorem["harmonic_coefficient"], "3*ell**2 + 3*ell + 2")
        self.assertEqual(theorem["status"], "CERTIFIED")
        self.assertTrue(self.payload["classification"]["induced_linear_tangent_quotient_map_injective"])

    def test_linear_restriction_not_nonlinear_pullback(self) -> None:
        contract = self.payload["terminology_contract"]
        self.assertEqual(contract["preferred_name"], "linear tangent symplectic restriction")
        self.assertIn("nonlinear", contract["forbidden_promotion"])
        self.assertFalse(self.payload["classification"]["nonlinear_solution_space_embedding_certified"])

    def test_complete_block_inventory(self) -> None:
        self.assertEqual(
            [entry["block"] for entry in self.payload["block_inventory"]],
            [
                "axial radiative",
                "polar radiative",
                "physical ell=1 quotient",
                "homogeneous ell=0",
                "axial ell=1 twist",
            ],
        )

    def test_flat_control_and_full_mixing_are_mandatory(self) -> None:
        self.assertEqual(
            self.payload["flat_control_contract"]["imported_verdict"],
            "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED",
        )
        terms = self.payload["action_and_current_contract"]["mandatory_terms"]
        self.assertTrue(any("background-flux" in term for term in terms))
        self.assertTrue(any("symbolic time" in term for term in terms))

    def test_target_gauge_loss_is_not_an_admissible_outcome(self) -> None:
        comparison = self.payload["comparison_contract"]
        self.assertNotIn("TARGET_GAUGE_LOSS", comparison["admissible_verdicts"])
        self.assertIn("excluded", comparison["target_gauge_loss"])

    def test_claims_remain_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["weyl_maxwell_symplectic_restriction_computed"])
        self.assertFalse(classification["universal_nonzero_proportionality_certified"])
        self.assertFalse(classification["final_residual_SO42_quotient_computed"])
        self.assertFalse(classification["lorentzian_causal_or_scattering_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
