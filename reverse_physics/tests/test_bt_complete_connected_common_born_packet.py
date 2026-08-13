import copy
import json
import os
import unittest

from reverse_physics.verify_bt_complete_connected_common_born_packet import CERT_REL, ROOT, verify


class CompleteConnectedCommonBornPacketTests(unittest.TestCase):
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
        self.assertTrue(all(checks.values()), [key for key, value in checks.items() if not value])

    def test_identity(self): self.assert_rejected(["certificate"], "PROMOTED")
    def test_schema(self): self.assert_rejected(["schema"], "wrong.json")
    def test_version(self): self.assert_rejected(["schema_version"], 2)
    def test_lifecycle(self): self.assert_rejected(["lifecycle_state"], "LORENTZIAN_CERTIFIED")
    def test_tags(self): self.assert_rejected(["dependency_tags"], ["LORENTZIAN-CAUSAL"])
    def test_source_hash(self): self.assert_rejected(["provenance", "source_commit"], "0" * 40)
    def test_input_hash(self): self.assert_rejected(["provenance", "inputs", 3, "sha256"], "0" * 64)
    def test_producer(self): self.assert_rejected(["provenance", "generated_by"], "producer.py")
    def test_verifier(self): self.assert_rejected(["provenance", "independent_verifier"], "same.py")
    def test_masks(self): self.assert_rejected(["exact_generic_Choi_witness", "channel_masks", 0], 0)
    def test_coefficients(self): self.assert_rejected(["exact_generic_Choi_witness", "coefficient_fixture", 9], "11")
    def test_kappa(self): self.assert_rejected(["exact_generic_Choi_witness", "kappa_3", 0, 7], "0")
    def test_A(self): self.assert_rejected(["exact_generic_Choi_witness", "A_6", 0, 0], "99")
    def test_even(self): self.assert_rejected(["exact_generic_Choi_witness", "A_even", 0, 0], "99")
    def test_odd(self): self.assert_rejected(["exact_generic_Choi_witness", "A_odd", 0, 0], "1")
    def test_public_square(self): self.assert_rejected(["exact_generic_Choi_witness", "public_Krein_square"], "769")
    def test_hilbert_square(self): self.assert_rejected(["exact_generic_Choi_witness", "positive_Hilbert_square"], "771")
    def test_defect(self): self.assert_rejected(["exact_generic_Choi_witness", "Born_defect"], "1")
    def test_witness_status(self): self.assert_rejected(["exact_generic_Choi_witness", "status"], "ASSUMED")
    def test_operator(self): self.assert_rejected(["complete_packet_descent", "operator"], "A=0")
    def test_weights(self): self.assert_rejected(["complete_packet_descent", "channel_rule"], "selected channel")
    def test_fixed(self): self.assert_rejected(["complete_packet_descent", "fixed_point_identity"], "alpha(A)!=A")
    def test_adjoint(self): self.assert_rejected(["complete_packet_descent", "adjoint_identity"], "sharp!=star")
    def test_effect(self): self.assert_rejected(["complete_packet_descent", "effect_identity"], "different")
    def test_operator_defect(self): self.assert_rejected(["complete_packet_descent", "Born_defect"], "nonzero")
    def test_bound(self): self.assert_rejected(["complete_packet_descent", "operator_bound"], "unbounded")
    def test_domain(self): self.assert_rejected(["complete_packet_descent", "positive_domain"], "always")
    def test_effects(self): self.assert_rejected(["complete_packet_descent", "effects"], [])
    def test_packet_status(self): self.assert_rejected(["complete_packet_descent", "status"], "FULL_EVOLUTION")
    def test_source(self): self.assert_rejected(["dressed_source_probability", "source"], "odd")
    def test_hard_channel(self): self.assert_rejected(["dressed_source_probability", "hard_channel"], "R_0 u0=u0")
    def test_exchange(self): self.assert_rejected(["dressed_source_probability", "exchange_channels"], "zero")
    def test_probability(self): self.assert_rejected(["dressed_source_probability", "common_probability"], "different")
    def test_no_click(self): self.assert_rejected(["dressed_source_probability", "no_click"], "q_no=0")
    def test_interference(self): self.assert_rejected(["dressed_source_probability", "interference"], "decohered")
    def test_source_status(self): self.assert_rejected(["dressed_source_probability", "status"], "GENERAL")
    def test_connected_type(self): self.assert_rejected(["disposition", "complete_connected_order_lambda4_graph_type"], "ALL_GRAPHS")
    def test_physical(self): self.assert_rejected(["disposition", "complete_connected_public_vs_Hilbert_Born_equivalence"], "NOT_PROVED")
    def test_disconnected_promotion(self): self.assert_rejected(["disposition", "disconnected_order_lambda4_spectator_completion"], "CONSTRUCTED")
    def test_eq19_promotion(self): self.assert_rejected(["disposition", "general_Eq19"], "PROVED")
    def test_lorentzian_promotion(self): self.assert_rejected(["disposition", "Lorentzian_causal_claim"], "ESTABLISHED")
    def test_boundaries(self): self.assert_rejected(["does_not_establish"], [])
    def test_missing(self): self.assert_rejected(["missing_object_ledger"], [])
    def test_next_gate(self): self.assert_rejected(["next_gate"], "done")
    def test_commands(self): self.assert_rejected(["verification_commands"], [])
    def test_report(self): self.assert_rejected(["report"], "none")


if __name__ == "__main__":
    unittest.main()
