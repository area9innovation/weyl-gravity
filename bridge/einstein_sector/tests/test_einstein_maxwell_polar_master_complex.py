from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_polar_master_complex import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_polar_master_complex import (
    verify_certificate,
)


class EinsteinMaxwellPolarMasterComplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_all_arbitrary_harmonic_columns_vanish(self) -> None:
        tensor = self.payload["exact_tensor_identity"]
        self.assertEqual([row["column"] for row in tensor["column_checks"]], ["A", "B", "C", "K", "U"])
        self.assertTrue(all(row["Einstein_component_remainders"] == "0" for row in tensor["column_checks"]))
        self.assertTrue(all(row["Maxwell_density_remainders"] == "0" for row in tensor["column_checks"]))

    def test_maxwell_volume_density_is_retained(self) -> None:
        self.assertIn("perturbed sqrt(-g)", self.payload["exact_tensor_identity"]["volume_density"])

    def test_gauge_rank_and_flux_shift(self) -> None:
        gauge = self.payload["gauge_theorem"]
        self.assertEqual(gauge["tensor_harmonic_norm_factor"], "lambda*(lambda - 2)/2")
        self.assertIn("delta U=-xi", gauge["transformations"][-1])
        self.assertIn("none", gauge["residual_gauge"])

    def test_all_m_promotion_is_equivariant(self) -> None:
        argument = self.payload["gauge_theorem"]["all_m_argument"]
        self.assertIn("SO(3)-invariant", argument)
        self.assertIn("tensor identity on all m", argument)

    def test_s_zero_rank_audit(self) -> None:
        audit = self.payload["algebraic_and_singular_audit"]
        self.assertEqual(audit["s_zero_minor"], "lambda**3*(lambda - 2)/8")
        self.assertIn("full column rank", audit["s_zero_verdict"])

    def test_all_momentum_dispersion_and_isospectrality(self) -> None:
        audit = self.payload["algebraic_and_singular_audit"]
        self.assertEqual(audit["dispersion"], "omega^2=k_n^2+lambda+/-sqrt(2*lambda)")
        self.assertIn("every n, ell>=2, and m", self.payload["isospectral_theorem"])

    def test_reduced_current_scope(self) -> None:
        pairing = self.payload["reduced_pairing"]
        self.assertEqual(pairing["symmetrizer"], "diag(1,2lambda)")
        self.assertFalse(pairing["covariant_symplectic_matching"])

    def test_exceptional_and_adjoint_gates_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["arbitrary_lambda_full_tensor_identity"])
        self.assertFalse(classification["ell0_ell1_complete"])
        self.assertFalse(classification["complete_fourth_order_adjoint"])
        self.assertFalse(classification["full_polar_including_exceptions"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
