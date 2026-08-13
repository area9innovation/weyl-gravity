import copy
import json
import os
import unittest

from reverse_physics.verify_bt_kappa_fixed_born_descent import CERT_REL, ROOT, verify


class KappaFixedBornDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    @staticmethod
    def set_path(row, path, value):
        cursor = row
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    def assert_rejected(self, path, value):
        row = copy.deepcopy(self.certificate)
        self.set_path(row, path, value)
        self.assertFalse(all(verify(row).values()))

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_identity(self): self.assert_rejected(["certificate"], "PROMOTED")
    def test_lifecycle(self): self.assert_rejected(["lifecycle_state"], "LORENTZIAN_CERTIFIED")
    def test_tags(self): self.assert_rejected(["dependency_tags"], ["LORENTZIAN-CAUSAL"])
    def test_hash(self): self.assert_rejected(["provenance", "inputs", 5, "sha256"], "0" * 64)
    def test_automorphism(self): self.assert_rejected(["canonical_expectation_theorem", "automorphism"], "alpha=0")
    def test_decomposition(self): self.assert_rejected(["canonical_expectation_theorem", "decomposition"], "A=A")
    def test_adjoint(self): self.assert_rejected(["canonical_expectation_theorem", "positive_adjoint"], "sharp=star")
    def test_orthogonality(self): self.assert_rejected(["canonical_expectation_theorem", "orthogonality"], "assumed")
    def test_difference_formula(self): self.assert_rejected(["canonical_expectation_theorem", "public_Born_identity"], "sum")
    def test_expectation(self): self.assert_rejected(["canonical_expectation_theorem", "expectation"], "projection")
    def test_defect_sign(self): self.assert_rejected(["canonical_expectation_theorem", "weight_defect"], "minus")
    def test_iff(self): self.assert_rejected(["canonical_expectation_theorem", "iff"], "always")
    def test_theorem_status(self): self.assert_rejected(["canonical_expectation_theorem", "status"], "GENERAL_EQ19")
    def test_kappa(self): self.assert_rejected(["exact_rational_witness", "kappa", 0, 0], "1")
    def test_A(self): self.assert_rejected(["exact_rational_witness", "A", 0, 0], "2")
    def test_even(self): self.assert_rejected(["exact_rational_witness", "A_even", 0, 0], "0")
    def test_odd(self): self.assert_rejected(["exact_rational_witness", "A_odd", 0, 0], "0")
    def test_q(self): self.assert_rejected(["exact_rational_witness", "q_K_A"], "21")
    def test_even_square(self): self.assert_rejected(["exact_rational_witness", "Hilbert_square_even"], "20")
    def test_odd_square(self): self.assert_rejected(["exact_rational_witness", "Hilbert_square_odd"], "0")
    def test_expected_q(self): self.assert_rejected(["exact_rational_witness", "q_K_E_kappa_A"], "20")
    def test_witness_defect(self): self.assert_rejected(["exact_rational_witness", "weight_defect"], "0")
    def test_remainder_fixture(self): self.assert_rejected(["weak_ghost_remainder_disposition", "imported_fixture"], "Q=0")
    def test_remainder_consequence(self): self.assert_rejected(["weak_ghost_remainder_disposition", "expectation_consequence"], "preserved")
    def test_remainder_eq19(self): self.assert_rejected(["weak_ghost_remainder_disposition", "Eq19_consequence"], "proved")
    def test_remainder_status(self): self.assert_rejected(["weak_ghost_remainder_disposition", "status"], "REMOVED")
    def test_V_symmetry(self): self.assert_rejected(["selected_pointer_descent", "symmetries", 0], "broken")
    def test_U_symmetry(self): self.assert_rejected(["selected_pointer_descent", "symmetries", 1], "broken")
    def test_ground_symmetry(self): self.assert_rejected(["selected_pointer_descent", "symmetries", 2], "broken")
    def test_click_symmetry(self): self.assert_rejected(["selected_pointer_descent", "symmetries", 3], "broken")
    def test_transition(self): self.assert_rejected(["selected_pointer_descent", "transition"], "odd")
    def test_adjoints_agree(self): self.assert_rejected(["selected_pointer_descent", "adjoints"], "not equal")
    def test_public_effect(self): self.assert_rejected(["selected_pointer_descent", "public_effect"], "negative")
    def test_hilbert_effect(self): self.assert_rejected(["selected_pointer_descent", "positive_Hilbert_effect"], "different")
    def test_probability(self): self.assert_rejected(["selected_pointer_descent", "probability_identity"], "one state")
    def test_pair_intertwining(self): self.assert_rejected(["selected_pointer_descent", "selected_pair_map_kappa_intertwining"], "false")
    def test_bound(self): self.assert_rejected(["selected_pointer_descent", "strict_bound"], "0")
    def test_selected_status(self): self.assert_rejected(["selected_pointer_descent", "status"], "GENERAL")
    def test_selected_physical(self): self.assert_rejected(["disposition", "selected_pointer_public_vs_Hilbert_Born_equivalence"], "NOT PROVED")
    def test_general_promotion(self): self.assert_rejected(["disposition", "arbitrary_weak_ghost_process_equivalence"], "PROVED")
    def test_eq19_promotion(self): self.assert_rejected(["disposition", "general_Eq19"], "PROVED")
    def test_lorentzian_promotion(self): self.assert_rejected(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")
    def test_boundaries(self): self.assert_rejected(["does_not_establish"], [])
    def test_missing(self): self.assert_rejected(["missing_object_ledger"], [])
    def test_next_gate(self): self.assert_rejected(["next_gate"], "done")


if __name__ == "__main__":
    unittest.main()
