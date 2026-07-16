from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_exceptional_global_symplectic import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_exceptional_global_symplectic import (
    verify_certificate,
)


class ExceptionalGlobalSymplecticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_surface(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_ell0_form_is_nondegenerate(self) -> None:
        ell0 = self.payload["ell0_global_theorem"]
        self.assertEqual(ell0["matrix_rank"], 6)
        self.assertEqual(ell0["matrix_determinant"], 4)

    def test_metric_labels_mix(self) -> None:
        self.assertIn(
            "mix symplectically",
            self.payload["ell0_global_theorem"]["Darboux_reorganization"],
        )

    def test_charge_holonomy_pair(self) -> None:
        ell0 = self.payload["ell0_global_theorem"]
        self.assertIn("mathcal W", ell0["Maxwell_Darboux_pair"])
        self.assertIn("not c1(P_N)", ell0["fixed_bundle_scope"])

    def test_twist_generalized_pair(self) -> None:
        twist = self.payload["axial_ell1_twist_theorem"]
        self.assertEqual(twist["rank_per_real_harmonic"], 2)
        self.assertIn("time-linear", twist["interpretation"])

    def test_direct_currents(self) -> None:
        self.assertEqual(
            self.payload["direct_lee_wald_fixture"]["remainders"],
            {"ell0": "0", "twist": "0"},
        )

    def test_machine_readable_completion(self) -> None:
        self.assertEqual(len(self.payload["completes"]), 2)
        self.assertIn("zero field strength", self.payload["completes"][0]["scope"])

    def test_fail_closed_scope(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["bounded_in_time_subspace_theorem"])
        self.assertFalse(classification["Weyl_Maxwell_pullback_matching"])
        self.assertFalse(classification["one_particle_complex_structure_constructed"])

    def test_committed_certificate(self) -> None:
        self.assertEqual(
            json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")),
            self.payload,
        )
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
