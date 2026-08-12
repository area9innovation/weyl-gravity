import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_scalar_dressed_source_free_normal_form import CERT, verify


class ScalarDressedSourceFreeNormalFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_explicit_leading_source_and_boundaries(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["leading_scalar_source"], "EXPLICIT_ON_FINITE_COVARIANT_CORE")
        self.assertEqual(result["ordinary_massless_Fock_thermodynamic_source"], "OBSTRUCTED")

    def test_rejects_bare_vacuum_substitution(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["explicit_leading_scalar_source"]["pulled_vacuum"] = "|0_phi>"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_lost_orbit_branch(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["explicit_leading_scalar_source"]["state_orbit_support"] = ["Z^3"]
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_premature_annihilator_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["explicit_leading_scalar_source"]["one_mode_Omega_creator_full"] = mutation["explicit_leading_scalar_source"]["one_mode_Omega_creator_on_vacuum"]
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_lambda_eight_source_correction(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["perturbative_order_protection"]["first_source_correction_order_in_probability"] = "lambda^8"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_ordinary_Fock_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["ordinary_massless_Fock_thermodynamic_source"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_general_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
