from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator_module_preflight import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_operator_module_preflight import verify_certificate as verify_independently


class AxialOperatorModulePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_exact_gauge_contraction(self) -> None:
        row = self.payload["gauge_module_contraction"]
        self.assertEqual(row["identities"], {"K_G": "0", "K_J": "I_4", "I_6_minus_J_K": "G_H", "H_G": "I_2"})
        self.assertEqual(row["denominators_introduced"], ["2"])
        self.assertTrue(row["no_inverse_D"])
        self.assertTrue(row["no_inverse_k"])

    def test_fail_closed_operator_rails(self) -> None:
        rail = self.payload["hessian_noether_green_rail"]
        self.assertFalse(rail["target_operator_inserted"])
        self.assertFalse(rail["Noether_identities_verified"])
        self.assertFalse(self.payload["pivot_and_fixture_contract"]["ell2_independent_replay"]["completed"])

    def test_exceptional_strata_and_solution_functor(self) -> None:
        strata = [row["locus"] for row in self.payload["pivot_and_fixture_contract"]["mandatory_strata"]]
        self.assertIn("lambda=2", strata)
        self.assertIn("k=0", strata)
        self.assertIn("solution_cohomology", self.payload["operator_module_contract"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
