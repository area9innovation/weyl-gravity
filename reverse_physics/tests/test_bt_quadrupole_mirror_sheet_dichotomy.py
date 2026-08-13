import copy
import json
import os
import unittest

from reverse_physics.verify_bt_quadrupole_mirror_sheet_dichotomy import (
    CERT_REL,
    ROOT,
    verify,
)


class QuadrupoleMirrorSheetDichotomyTests(unittest.TestCase):
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
        checks = verify(row)
        self.assertFalse(all(checks.values()), checks)

    def test_baseline(self):
        checks = verify(copy.deepcopy(self.certificate))
        self.assertTrue(all(checks.values()), [name for name, value in checks.items() if not value])

    def test_rejects_identity(self):
        self.assert_rejected(["certificate"], "PROMOTED")

    def test_rejects_lifecycle(self):
        self.assert_rejected(["lifecycle_state"], "LORENTZIAN_CERTIFIED")

    def test_rejects_dependency(self):
        self.assert_rejected(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.assert_rejected(["provenance", "inputs", 2, "sha256"], "0" * 64)

    def test_rejects_hidden_field(self):
        self.assert_rejected(["same_chart_hidden_image", "hidden_field"], "g=phi")

    def test_rejects_bilinear_formula(self):
        self.assert_rejected(["same_chart_hidden_image", "bilinear_formula"], "D[h]=D")

    def test_rejects_even_projection(self):
        self.assert_rejected(["same_chart_hidden_image", "even_projection"], "D_even=D")

    def test_rejects_odd_projection(self):
        self.assert_rejected(["same_chart_hidden_image", "odd_projection"], "D_odd=0")

    def test_rejects_same_chart_promotion(self):
        self.assert_rejected(["same_chart_hidden_image", "status"], "CONSTRUCTED")

    def test_rejects_pair_coefficient(self):
        self.assert_rejected(["scaled_mirror_jet_witness", "quadrupole_pair_coefficient"], "0")

    def test_rejects_path(self):
        self.assert_rejected(["scaled_mirror_jet_witness", "sample_t", 2], "1/4")

    def test_rejects_path_coefficient(self):
        self.assert_rejected(["scaled_mirror_jet_witness", "sample_pair_coefficients", 1], "0")

    def test_rejects_nonextension(self):
        self.assert_rejected(["scaled_mirror_jet_witness", "status"], "EXTENDS")

    def test_rejects_sheet_Gram(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "Krein_Gram_G", 0, 1], "0")

    def test_rejects_kappa(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "fundamental_symmetry_kappa", 1, 0], "0")

    def test_rejects_positive_Gram(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "positive_Hilbert_Gram", 1, 1], "-1")

    def test_rejects_even_projector(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "even_sheet_projector", 0, 0], "1")

    def test_rejects_density_parity(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "mirrored_density_fixture", 1, 1], "1/2")

    def test_rejects_changed_theory_boundary(self):
        self.assert_rejected(["minimal_mirror_sheet_completion", "status"], "PUBLIC_BT")

    def test_rejects_amplitude_doubling(self):
        self.assert_rejected(["response_transfer", "normalized_symmetric_amplitude"], "6/5")

    def test_rejects_probability(self):
        self.assert_rejected(["response_transfer", "symmetric_fixture_probability"], "18/25")

    def test_rejects_q8_bound(self):
        self.assert_rejected(["response_transfer", "inherited_compact_q8_lower"], "zero")

    def test_rejects_public_action_promotion(self):
        self.assert_rejected(["disposition", "public_scalar_action_selects_doubling"], "YES")

    def test_rejects_public_Rt_promotion(self):
        self.assert_rejected(["disposition", "public_Rt_selects_doubling"], "YES")

    def test_rejects_Eq19_promotion(self):
        self.assert_rejected(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_positive_net_promotion(self):
        self.assert_rejected(["disposition", "positive_BT_Haag_Kastler_net"], "CONSTRUCTED")

    def test_rejects_gravity_promotion(self):
        self.assert_rejected(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_promotion(self):
        self.assert_rejected(["disposition", "Lorentzian_causal_BT_claim"], "ESTABLISHED")

    def test_rejects_next_gate_erasure(self):
        self.assert_rejected(["next_gate"], "done")


if __name__ == "__main__":
    unittest.main()
