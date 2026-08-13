import copy
import json
import os
import unittest

from reverse_physics.verify_bt_fully_rearranged_v4_cubed_triangle_block import CERT_REL, ROOT, verify


class FullyRearrangedV4CubedTriangleBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutate(self, path, value):
        candidate = copy.deepcopy(self.certificate)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        self.assertFalse(all(verify(candidate).values()))

    def test_00_certificate_passes(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_identity_mutation(self):
        self.mutate(["certificate"], "X")

    def test_lifecycle_mutation(self):
        self.mutate(["lifecycle_state"], "CLASSIFIED")

    def test_tag_mutation(self):
        self.mutate(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_hash_mutation(self):
        self.mutate(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_pairing_mutation(self):
        self.mutate(["species_tensor", "pairing_count"], 14)

    def test_tensor_mutation(self):
        self.mutate(["species_tensor", "tensors", 0, 0, 7], 9)

    def test_source_weight_mutation(self):
        self.mutate(["species_tensor", "rows", 0, "source_weight"], 7)

    def test_cross_Gram_mutation(self):
        self.mutate(["tree_triangle_interference", "cross_Gram", 0, 0], "0")

    def test_common_Born_mutation(self):
        self.mutate(["tree_triangle_interference", "status"], "SIGN_POSITIVE")

    def test_invariant_mutation(self):
        self.mutate(["hard_packet_regularization", "rows", 0, "pair_invariants", 0], "0")

    def test_margin_mutation(self):
        self.mutate(["hard_packet_regularization", "minimum_absolute_Kallen"], "0")

    def test_symmetry_mutation(self):
        self.mutate(["graph_and_master", "symmetry_factor"], "1/2")

    def test_degree_mutation(self):
        self.mutate(["graph_and_master", "superficial_UV_degree"], 0)

    def test_master_mutation(self):
        self.mutate(["graph_and_master", "triangle_master"], "bubble")

    def test_counterterm_mutation(self):
        self.mutate(["graph_and_master", "renormalization"], "MSBAR_REQUIRED")

    def test_complete_q10_mutation(self):
        self.mutate(["disposition", "complete_q10"], "COEFFICIENT_COMPUTED")

    def test_Dyson_mutation(self):
        self.mutate(["disposition", "finite_duration_three_Dyson_affiliation"], "PROVED")

    def test_Eq19_mutation(self):
        self.mutate(["disposition", "general_Eq19"], "PROVED")

    def test_causal_mutation(self):
        self.mutate(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")

    def test_boundaries_mutation(self):
        self.mutate(["does_not_establish"], [])

    def test_next_gate_mutation(self):
        self.mutate(["next_gate"], "done")

    def test_report_mutation(self):
        self.mutate(["report"], "none")


if __name__ == "__main__":
    unittest.main()
