from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_radiative_symplectic_matching import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_radiative_symplectic_matching import (
    verify_certificate,
)


class RadiativeSymplecticMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_surface(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_action_normalized_polar_form(self) -> None:
        matrices = self.payload["master_matching"][
            "action_normalized_matrices_without_N_over_2"
        ]
        self.assertEqual(matrices["polar"], [["1", "-2"], ["-2", "2*lambda"]])

    def test_axial_curl_pullback(self) -> None:
        matching = self.payload["master_matching"]
        self.assertEqual(
            matching["action_normalized_matrices_without_N_over_2"]["axial"],
            [["lambda**2", "2*lambda"], ["2*lambda", "2*lambda"]],
        )
        self.assertIn("curl", matching["axial_curl_pullback"])

    def test_covariant_matching(self) -> None:
        self.assertTrue(
            self.payload["classification"]["covariant_Lee_Wald_integrated_matching"]
        )
        self.assertIn(
            "no boundary",
            self.payload["covariant_and_bundle_statement"]["closed_cauchy_surface"],
        )

    def test_fixed_bundle(self) -> None:
        statement = self.payload["covariant_and_bundle_statement"][
            "fixed_bundle_argument"
        ]
        self.assertIn("global one-form", statement)
        self.assertIn("c1(P_N)", statement)

    def test_ell1_kernel_and_corrected_weight(self) -> None:
        ell1 = self.payload["ell1_quotient"]
        self.assertEqual(ell1["polar_quotient_weight_without_N_over_2"], "4")
        self.assertIn("exactly", ell1["polar_kernel"])
        self.assertIn("massless", ell1["axial_kernel"])
        self.assertIn("replaces", ell1["supersession"])

    def test_fail_closed_global_and_weyl_gates(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["homogeneous_ell0_global_pairing"])
        self.assertFalse(classification["axial_ell1_global_twist_pairing"])
        self.assertFalse(classification["Weyl_Maxwell_pullback_matching"])

    def test_committed_certificate(self) -> None:
        self.assertEqual(
            json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")),
            self.payload,
        )
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
