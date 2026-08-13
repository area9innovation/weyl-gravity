import copy
import json
import os
import unittest

from reverse_physics.verify_bt_reeh_schlieder_local_detector_obstruction import (
    CERT_REL,
    ROOT,
    verify,
)


class ReehSchliederLocalDetectorObstructionTests(unittest.TestCase):
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

    def test_rejects_input_hash(self):
        self.alter(["provenance", "inputs", 1, "sha256"], "0" * 64)

    def test_rejects_missing_predecessor(self):
        self.alter(["provenance", "inputs", 1, "path"], "missing.json")

    def test_rejects_source_commit(self):
        self.alter(["provenance", "source_commit"], "0" * 40)

    def test_rejects_commuting_hypothesis_loss(self):
        self.alter(["abstract_commuting_algebra_theorem", "hypotheses"], "M,N are algebras")

    def test_rejects_cyclicity_hypothesis_loss(self):
        self.alter(["abstract_commuting_algebra_theorem", "hypotheses"], "M,N commute")

    def test_rejects_separating_conclusion(self):
        self.alter(["abstract_commuting_algebra_theorem", "separating_conclusion"], "A may survive")

    def test_rejects_commuting_proof_step(self):
        self.alter(["abstract_commuting_algebra_theorem", "proof", 0], "unsupported")

    def test_rejects_density_proof_step(self):
        self.alter(["abstract_commuting_algebra_theorem", "proof", 1], "orbit is small")

    def test_rejects_boundedness_proof_step(self):
        self.alter(["abstract_commuting_algebra_theorem", "proof", 2], "unbounded extension")

    def test_rejects_square_root_identity(self):
        self.alter(["positive_effect_corollary", "square_root_identity"], "approximate")

    def test_rejects_functional_calculus(self):
        self.alter(["positive_effect_corollary", "functional_calculus"], "external")

    def test_rejects_effect_conclusion(self):
        self.alter(["positive_effect_corollary", "conclusion"], "E may be nonzero")

    def test_rejects_pointer_slice_formula(self):
        self.alter(["normal_pointer_dilation_corollary", "induced_effect"], "nonlocal slice")

    def test_rejects_pointer_slice_locality(self):
        self.alter(["normal_pointer_dilation_corollary", "slice_map_result"], "E is global")

    def test_rejects_pointer_no_go(self):
        self.alter(["normal_pointer_dilation_corollary", "exact_Julia_realization"], "CONSTRUCTED")

    def test_rejects_Julia_effect(self):
        self.alter(["exact_Julia_application", "effect"], "E_click=0")

    def test_rejects_Julia_vacuum_probability(self):
        self.alter(["exact_Julia_application", "vacuum_probability"], "positive")

    def test_rejects_Julia_nonzero_witness(self):
        self.alter(["exact_Julia_application", "nonzero_witness"], "0")

    def test_rejects_click_locality_promotion(self):
        self.alter(["exact_Julia_application", "click_Kraus_locality"], "K_click IN_M")

    def test_rejects_no_click_locality_promotion(self):
        self.alter(["exact_Julia_application", "no_click_Kraus_locality"], "K_no IN_M")

    def test_rejects_countermodel_orbit_rank(self):
        self.alter(["finite_exact_fixtures", "cyclicity_necessity_countermodel", "commutant_orbit_dimension"], 2)

    def test_rejects_countermodel_conclusion(self):
        self.alter(["finite_exact_fixtures", "cyclicity_necessity_countermodel", "conclusion"], "hypothesis unnecessary")

    def test_rejects_balanced_fixture_probability(self):
        self.alter(["finite_exact_fixtures", "balanced_diagonal_fixture", "vacuum_probabilities", 0], "0")

    def test_rejects_balanced_BT_promotion(self):
        self.alter(["balanced_contrast_boundary", "BT_status"], "CONSTRUCTED")

    def test_rejects_affiliation_hypothesis_loss(self):
        self.alter(["bounded_spectral_truncation_lift", "additional_hypotheses", 0], "D is formal")

    def test_rejects_domain_hypothesis_loss(self):
        self.alter(["bounded_spectral_truncation_lift", "additional_hypotheses", 1], "domains omitted")

    def test_rejects_bounded_truncations(self):
        self.alter(["bounded_spectral_truncation_lift", "truncations"], "D_n is unbounded")

    def test_rejects_response_limit(self):
        self.alter(["bounded_spectral_truncation_lift", "limit"], "limit is zero")

    def test_rejects_closed_span_step(self):
        self.alter(["bounded_spectral_truncation_lift", "closed_span_step"], "closure assumed")

    def test_rejects_finite_combination_bound(self):
        self.alter(["bounded_spectral_truncation_lift", "finite_combination"], "infinite series")

    def test_rejects_bounded_response(self):
        self.alter(["bounded_spectral_truncation_lift", "exact_responses"], "X4 response zero")

    def test_rejects_phase_reversal_formula(self):
        self.alter(["bounded_spectral_truncation_lift", "phase_reversal_contrast"], "one-shot probability")

    def test_rejects_operational_response(self):
        self.alter(["bounded_spectral_truncation_lift", "operational_response"], "X2 leaks")

    def test_rejects_span_fixture(self):
        self.alter(["finite_exact_fixtures", "spectral_truncation_span_fixture", "coefficients", 0], "1")

    def test_rejects_unconditional_affiliation_promotion(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "self-adjoint affiliation" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_BT_net_promotion(self):
        self.alter(["disposition", "positive_BT_Haag_Kastler_net"], "CONSTRUCTED")

    def test_rejects_BT_Reeh_Schlieder_promotion(self):
        self.alter(["disposition", "BT_Reeh_Schlieder_property"], "PROVED")

    def test_rejects_Eq19_promotion(self):
        self.alter(["disposition", "general_Eq19"], "PROVED")

    def test_rejects_gravity_promotion(self):
        self.alter(["disposition", "gravity_or_metric_BV_BRST_transfer"], "CONSTRUCTED")

    def test_rejects_Lorentzian_promotion(self):
        self.alter(["disposition", "Lorentzian_causal_BT_claim"], "ESTABLISHED")

    def test_rejects_BT_net_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "Haag--Kastler net" not in item
            ]
        self.assert_rejected(mutate)

    def test_rejects_Reeh_Schlieder_boundary_removal(self):
        def mutate(row):
            row["does_not_establish"] = [
                item for item in row["does_not_establish"]
                if "Reeh--Schlieder" not in item
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

    def test_rejects_priority_claim(self):
        self.alter(["literature_context", "priority_status"], "NEW")


if __name__ == "__main__":
    unittest.main()
