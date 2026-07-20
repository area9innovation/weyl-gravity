import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720DeformableKernelIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_moduli_retains_boundaries_and_stabilizers(self) -> None:
        moduli = self.payload["compactified_moduli"]
        self.assertIn("no direction is introduced at a zero node", moduli["occupation_coordinates"])
        self.assertIn("full stabilizer", moduli["one_node_boundaries"])
        self.assertIn("no freeness", moduli["orbit_type_statement"])
        self.assertIn("semialgebraically path connected", moduli["component_path_property"])
        self.assertIn("slice theorem", moduli["component_path_property"])

    def test_admissible_base_is_fail_closed(self) -> None:
        base = self.payload["moment_map_and_admissible_base"]
        self.assertIn("||M_K(F,G)||<=|c(F,G)|", base["admissible_prequotient"])
        self.assertEqual(
            base["zero_wall_incidence"],
            "I={[F,G] in A:c(F,G)=0 and M_K(F,G)=0}",
        )

    def test_component_criterion_is_necessary_and_sufficient(self) -> None:
        theorem = self.payload["component_incidence_theorem"]
        self.assertIn("if and only if", theorem["equivalence"])
        self.assertIn("c changes from alpha to delta", theorem["necessity"])
        self.assertIn("semialgebraically path connected", theorem["sufficiency_stage_1"])
        self.assertIn("phase-real", theorem["sufficiency_stage_2"])
        self.assertIn("c=(1-s)delta", theorem["sufficiency_stage_3"])

    def test_square_moment_path_lift_handles_singular_radius(self) -> None:
        lift = self.payload["exact_algebra"]["cartan_square_path_lift"]
        self.assertIn("connected rotation orbit", lift["connected_fibres"])
        self.assertIn("phase-real RP2", lift["connected_fibres"])
        self.assertIn("isolated zero", lift["path_lifting"])

    def test_both_boundary_incidence_witnesses_are_present(self) -> None:
        boundary = self.payload["boundary_incidence"]
        self.assertIn("-delta/a", boundary["delta_negative_alpha_positive"]["witness"])
        self.assertIn("delta/b", boundary["delta_positive_alpha_negative"]["witness"])
        self.assertIn("nonemptiness alone", boundary["consequence"])

    def test_candidates_remain_separate(self) -> None:
        disposition = self.payload["candidate_disposition"]
        self.assertIn("candidate-17", disposition["candidate17"])
        self.assertIn("candidate-20", disposition["candidate20_negative_delta"])
        self.assertIn("candidate-20", disposition["candidate20_positive_delta"])
        self.assertIn("distinct backgrounds", disposition["separation"])

    def test_schema_rejects_unproved_component_connectedness(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["every_admissible_component_meets_incidence"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)

    def test_schema_rejects_global_zero_fibre_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["global_zero_fibre_connected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
