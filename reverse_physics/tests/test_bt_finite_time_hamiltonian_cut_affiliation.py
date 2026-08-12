import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_finite_time_hamiltonian_cut_affiliation import CERT, verify


class FiniteTimeHamiltonianCutAffiliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_kernel_derived_but_survival_embedding_open(self):
        result = self.certificate["interpretation"]
        self.assertEqual(result["finite_time_shell_kernel_BT_affiliation"], "DERIVED_AT_CUT_PROBABILITY_LEVEL")
        self.assertEqual(result["BT_Hamiltonian_positive_survival_embedding"], "NOT_CONSTRUCTED")

    def test_rejects_kernel_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["hamiltonian_cut_kernel"]["exact_kernel"] = "|F_T(omega)|^2=sin^2(omega*T)/omega^2"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_detector_rate_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["coefficient_match"]["declared_detector_rate"] = "3*lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_positive_Krein_complement(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["pseudo_unitary_survival_boundary"]["complement"] = "tr(U_r^sharp (1-P) U_r P)=+sinh(r)^2"
        self.assertFalse(all(verify(mutation).values()))

    def test_rejects_survival_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["BT_Hamiltonian_positive_survival_embedding"] = "CONSTRUCTED"
        self.assertFalse(all(verify(mutation).values()))


if __name__ == "__main__":
    unittest.main()
