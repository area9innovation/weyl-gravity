from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import two_phase_counterflow_einstein_source_condition as source


class CounterflowEinsteinSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = source.build_certificate()

    def test_canonical_outputs_are_current(self) -> None:
        self.assertEqual(json.loads(source.OUTPUT.read_text()), self.certificate)
        self.assertEqual(json.loads(source.ATLAS.read_text()), source.build_atlas(self.certificate))

    def test_first_failed_map_is_background_incidence(self) -> None:
        test = self.certificate["exact_background_test"]
        self.assertEqual(test["stress_proportionality_minor_00_11"], "-279/2560")
        self.assertNotEqual(test["kappa_from_00"], test["kappa_from_11"])
        self.assertEqual(test["first_failed_map"], "background incidence Sol_Einstein-matter -> Sol_Weyl-matter")

    def test_charge_sectors_are_not_merged(self) -> None:
        split = self.certificate["charge_sector_split"]
        self.assertIn("Darboux pair survives", split["unrestricted_Q_rel"]["clock"])
        self.assertIn("zero Jordan block", split["unrestricted_Q_rel"]["linear_health"])
        self.assertIn("remove the complete relative-clock", split["fixed_Q_rel"]["clock"])

    def test_neutrality_does_not_promote_source_closure(self) -> None:
        disposition = self.certificate["source_condition_disposition"]
        self.assertEqual(disposition["Q_T_status"], "NOT_APPLICABLE")
        self.assertFalse(self.certificate["claim_flags"]["diagonal_neutrality_used_as_stress_vanishing"])
        self.assertFalse(self.certificate["claim_flags"]["flat_Q_operator_transplanted_to_Berger"])

    def test_cross_background_map_is_rejected(self) -> None:
        comparison = self.certificate["relative_triangle"]["comparison_map_disposition"]
        self.assertEqual(comparison["status"], "NOT_APPLICABLE")
        self.assertIn("Plebanski--Hacyan", comparison["reason"])

    def test_residual_K_ledger_is_not_promoted_to_full_receiver(self) -> None:
        residual = self.certificate["pairing_and_residual_action"]
        self.assertIn("CERTIFIED", residual["K_Berger_target_action"])
        self.assertTrue(residual["full_five_generator_residual_receiver"].startswith("OBSTRUCTED"))
        self.assertEqual(residual["descended_residual_pairing"], "NO_CERTIFIED_MAP")

    def test_decisive_mutation_is_detected(self) -> None:
        forged = copy.deepcopy(self.certificate)
        forged["claim_flags"]["same_background_linear_inclusion"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaises(source.CounterflowEinsteinSourceError):
                source.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
