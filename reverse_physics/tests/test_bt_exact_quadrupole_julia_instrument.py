import copy
import json
import os
import unittest

from reverse_physics.verify_bt_exact_quadrupole_julia_instrument import (
    CERT_REL,
    ROOT,
    verify,
)


class ExactQuadrupoleJuliaInstrumentTests(unittest.TestCase):
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
        self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_rejects_identity(self):
        self.alter(["certificate"], "PROMOTED")

    def test_rejects_lifecycle_promotion(self):
        self.alter(["lifecycle_state"], "LORENTZIAN_CERTIFIED")

    def test_rejects_dependency_promotion(self):
        self.alter(["dependency_tags"], ["LORENTZIAN-CAUSAL"])

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 1, "sha256"], "0" * 64)

    def test_rejects_missing_input(self):
        self.alter(["provenance", "inputs", 2, "path"], "missing.json")

    def test_rejects_click_Kraus(self):
        self.alter(["bounded_click_instrument", "click_Kraus"], "K=I")

    def test_rejects_click_norm(self):
        self.alter(["bounded_click_instrument", "click_norm"], "2")

    def test_rejects_source_effect(self):
        self.alter(["bounded_click_instrument", "source_effect"], "E=I")

    def test_rejects_no_click_Kraus(self):
        self.alter(["bounded_click_instrument", "no_click_Kraus"], "I")

    def test_rejects_no_click_effect(self):
        self.alter(["bounded_click_instrument", "no_click_effect"], "0")

    def test_rejects_normalization(self):
        self.alter(["bounded_click_instrument", "normalization"], "incomplete")

    def test_rejects_probability(self):
        self.alter(["bounded_click_instrument", "probability"], "negative")

    def test_rejects_click_matrix(self):
        self.alter(["exact_Julia_dilation", "click_matrix", 0, 0], "1")

    def test_rejects_source_defect(self):
        self.alter(["exact_Julia_dilation", "source_defect", 0, 0], "1/2")

    def test_rejects_output_defect(self):
        self.alter(["exact_Julia_dilation", "output_defect", 0, 0], "1")

    def test_rejects_Julia_matrix(self):
        self.alter(["exact_Julia_dilation", "Julia_matrix", 2, 0], "0")

    def test_rejects_intertwining(self):
        self.alter(["exact_Julia_dilation", "intertwining"], "fails")

    def test_rejects_unitarity(self):
        self.alter(["exact_Julia_dilation", "unitarity"], "approximate")

    def test_rejects_leading_subspace(self):
        self.alter(["darkness_and_response", "leading_subspace"], "one fixture")

    def test_rejects_orthogonality(self):
        self.alter(["darkness_and_response", "orthogonality"], "small")

    def test_rejects_strict_response(self):
        self.alter(["darkness_and_response", "strict_response"], "zero")

    def test_rejects_exact_probability(self):
        self.alter(["darkness_and_response", "exact_instrument_probability"], "series")

    def test_rejects_coefficient(self):
        self.alter(["darkness_and_response", "coefficient_statement"], "zero")

    def test_rejects_detector_order_boundary(self):
        self.alter(["darkness_and_response", "detector_coupling_status"], "PERTURBATIVE")

    def test_rejects_BT_order_promotion(self):
        self.alter(["darkness_and_response", "BT_coupling_status"], "ALL_ORDER")

    def test_rejects_cubic_moment(self):
        self.alter(["full_local_exponential_obstruction", "cubic_moment"], "0")

    def test_rejects_scalar_projection(self):
        self.alter(["full_local_exponential_obstruction", "scalar_projection_coefficient"], "0")

    def test_rejects_exponential_promotion(self):
        self.alter(["full_local_exponential_obstruction", "consequence"], "full exponential is dark")

    def test_rejects_local_density_loss(self):
        self.alter(["locality_ledger", "underlying_density"], "nonlocal")

    def test_rejects_compression_loss(self):
        self.alter(["locality_ledger", "click_compression"], "D_h")

    def test_rejects_global_click_objects_loss(self):
        self.alter(["locality_ledger", "global_objects_in_click"], [])

    def test_rejects_global_no_click_loss(self):
        self.alter(["locality_ledger", "global_object_in_no_click"], "local")

    def test_rejects_local_Kraus_promotion(self):
        self.alter(["disposition", "compact_local_Kraus_realization"], "CONSTRUCTED")

    def test_rejects_public_BT_promotion(self):
        self.alter(["disposition", "public_BT_selection"], "CONSTRUCTED")

    def test_rejects_all_lambda_promotion(self):
        self.alter(["disposition", "all_order_BT_lambda_probability"], "CONSTRUCTED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "PROVED")

    def test_rejects_Lorentzian_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "LORENTZIAN-CAUSAL" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_priority_claim(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if item != "literature priority"
            ]
        self.assert_rejected(mutate)


if __name__ == "__main__":
    unittest.main()
