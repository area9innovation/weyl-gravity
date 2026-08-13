import copy
import json
import os
import unittest

from reverse_physics.verify_bt_positive_local_real_structure_dichotomy import (
    CERT_REL,
    ROOT,
    verify,
)


class PositiveLocalRealStructureDichotomyTests(unittest.TestCase):
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

    def assert_rejected(self, mutation):
        row = copy.deepcopy(self.certificate)
        mutation(row)
        checks = verify(row)
        self.assertFalse(all(checks.values()), checks)

    def alter(self, path, value):
        self.assert_rejected(lambda row: self.set_path(row, path, value))

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [key for key, value in checks.items() if not value])

    def test_rejects_identity(self):
        self.alter(["certificate"], "PROMOTED")

    def test_rejects_lifecycle_promotion(self):
        self.alter(["lifecycle_state"], "LORENTZIAN_CERTIFIED")

    def test_rejects_dependency_promotion(self):
        self.alter(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_source_commit(self):
        self.alter(["provenance", "source_commit"], "0" * 40)

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_rejects_missing_public_digest(self):
        self.alter(["provenance", "inputs", 2, "path"], "missing.md")

    def test_rejects_missing_predecessor(self):
        self.alter(["provenance", "inputs", 3, "path"], "missing.json")

    def test_rejects_cross_Gram_diagonal(self):
        self.alter(["positive_Wightman_obstruction", "factored_public_Gram", 0, 0], "1")

    def test_rejects_cross_Gram_offdiagonal(self):
        self.alter(["positive_Wightman_obstruction", "factored_public_Gram", 0, 1], "0")

    def test_rejects_positive_direction_norm(self):
        self.alter(["positive_Wightman_obstruction", "positive_direction_scaled_norm"], "1")

    def test_rejects_negative_direction_norm(self):
        self.alter(["positive_Wightman_obstruction", "negative_direction_scaled_norm"], "2")

    def test_rejects_determinant(self):
        self.alter(["positive_Wightman_obstruction", "determinant"], "1")

    def test_rejects_positive_representation_promotion(self):
        self.alter(["positive_Wightman_obstruction", "conclusion"], "POSITIVE_REPRESENTATION_EXISTS")

    def test_rejects_kappa(self):
        self.alter(["kappa_Hilbertization_dictionary", "fundamental_symmetry_kappa", 0, 1], "0")

    def test_rejects_positive_Hilbert_Gram(self):
        self.alter(["kappa_Hilbertization_dictionary", "positive_Hilbert_Gram_G_kappa", 1, 1], "-1")

    def test_rejects_adjoint_relation(self):
        self.alter(["kappa_Hilbertization_dictionary", "adjoint_relation"], "A*=A^sharp")

    def test_rejects_field_adjoint_map(self):
        self.alter(["kappa_Hilbertization_dictionary", "field_adjoint_map", 0], "Omega*=Omega")

    def test_rejects_Hilbertization_removal(self):
        self.alter(["kappa_Hilbertization_dictionary", "status"], "IMPOSSIBLE")

    def test_rejects_parity_hypothesis(self):
        self.alter(["observable_parity_theorem", "hypothesis"], "A arbitrary")

    def test_rejects_even_formula(self):
        self.alter(["observable_parity_theorem", "even_part"], "A_even=A")

    def test_rejects_odd_formula(self):
        self.alter(["observable_parity_theorem", "odd_part"], "A_odd=0")

    def test_rejects_i_odd_selfadjointness(self):
        self.alter(["observable_parity_theorem", "adjoints", 2], "(i A_odd)*=-i A_odd")

    def test_rejects_observable_iff(self):
        self.alter(["observable_parity_theorem", "iff_statement"], "all A are observables")

    def test_rejects_domain_boundary(self):
        self.alter(["observable_parity_theorem", "local_escape_condition"], "all unbounded operators work")

    def test_rejects_Q_matrix_unit(self):
        self.alter(["weak_ghost_Born_separation", "Q_negative", 1, 0], "0")

    def test_rejects_Q_sharp(self):
        self.alter(["weak_ghost_Born_separation", "Q_sharp", 0, 1], "1")

    def test_rejects_Q_star(self):
        self.alter(["weak_ghost_Born_separation", "Q_star", 0, 1], "0")

    def test_rejects_Q_nilpotence(self):
        self.alter(["weak_ghost_Born_separation", "Q_squared", 0, 0], "1")

    def test_rejects_Krein_null_weight(self):
        self.alter(["weak_ghost_Born_separation", "Krein_null_weight"], "1")

    def test_rejects_Krein_cross_weight(self):
        self.alter(["weak_ghost_Born_separation", "Krein_cross_weight"], "1")

    def test_rejects_Hilbert_remainder_weight(self):
        self.alter(["weak_ghost_Born_separation", "positive_Hilbert_remainder_weight"], "0")

    def test_rejects_generalized_Born_weight(self):
        self.alter(["weak_ghost_Born_separation", "generalized_Krein_Born_weight"], "3")

    def test_rejects_Hilbert_Born_weight(self):
        self.alter(["weak_ghost_Born_separation", "ordinary_Hilbert_Born_weight"], "2")

    def test_rejects_Born_separation_status(self):
        self.alter(["weak_ghost_Born_separation", "status"], "EQUIVALENT")

    def test_rejects_Eq19_positive_norm_gate(self):
        self.alter(["Eq19_and_detector_consequence", "Eq19_role"], "Q vanishes in every norm")

    def test_rejects_physical_quotient_gate(self):
        self.alter(["Eq19_and_detector_consequence", "physical_quotient_gate"], "discard Q formally")

    def test_rejects_quadrupole_parity_promotion(self):
        self.alter(["Eq19_and_detector_consequence", "current_quadrupole_status"], "KAPPA_EVEN")

    def test_rejects_positive_net_promotion(self):
        self.alter(["disposition", "positive_BT_Haag_Kastler_net"], "CONSTRUCTED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_quadrupole_disposition_promotion(self):
        self.alter(["disposition", "compact_quadrupole_kappa_parity"], "PROVED_EVEN")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_promotion(self):
        self.alter(["disposition", "Lorentzian_causal_BT_claim"], "ESTABLISHED")

    def test_rejects_Hilbertization_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "kappa-Hilbertization is mathematically impossible" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_generalized_Born_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "generalized Krein Born rule is inconsistent" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_net_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "Haag--Kastler" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_Eq19_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "Eq. (19)" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_Lorentzian_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "LORENTZIAN-CAUSAL" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_public_version_promotion(self):
        self.alter(["literature_context", "current_public_version_checked"], "companion proof published")

    def test_rejects_priority_claim(self):
        self.alter(["literature_context", "priority_status"], "NEW")


if __name__ == "__main__":
    unittest.main()
