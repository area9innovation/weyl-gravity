import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720DeformableKernelCompleteContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_time_reversal_homotopy_is_explicit_and_monotone(self) -> None:
        reversal = self.payload["spin_two_time_reversal"]
        self.assertIn("anti_diag", reversal["time_reversal"])
        self.assertIn("q(theta)", reversal["moment_formula"])
        self.assertIn("decreases from 1 to 0", reversal["monotonicity"])
        self.assertIn("phase-real", reversal["endpoint"])
        self.assertIn("unsigned anti-diagonal fails", reversal["mutation_control"])

    def test_negative_delta_deletes_positive_node(self) -> None:
        row = self.payload["convex_one_node_deletion"]["delta_negative"]
        self.assertIn("G_t=sqrt(t)G", row["path"])
        self.assertIn("alpha+b=delta+a", row["endpoint_bound"])
        self.assertIn("norm of the affine moment", row["convexity"])
        self.assertIn("-delta/a", row["survivor"])

    def test_positive_delta_deletes_negative_node(self) -> None:
        row = self.payload["convex_one_node_deletion"]["delta_positive"]
        self.assertIn("F_t=sqrt(t)F", row["path"])
        self.assertIn("-alpha+a=b-delta", row["endpoint_bound"])
        self.assertIn("norm of the affine moment", row["convexity"])
        self.assertIn("delta/b", row["survivor"])

    def test_every_component_reaches_incidence(self) -> None:
        strict = self.payload["strict_opposite_sign_contraction"]
        self.assertIn(
            "every path component meets I", strict["component_consequence"]
        )
        self.assertTrue(
            self.payload["classification"]["every_admissible_component_meets_incidence"]
        )

    def test_wrong_node_deletions_hit_the_wall_too_early(self) -> None:
        controls = self.payload["convex_one_node_deletion"]["wrong_node_controls"]
        self.assertIn("c=delta-b<0", controls["delta_negative"])
        self.assertIn("c(1)=alpha>0", controls["delta_negative"])
        self.assertIn("c=delta+a>0", controls["delta_positive"])
        self.assertIn("c(1)=alpha<0", controls["delta_positive"])

    def test_complete_candidate_assembly_covers_balance_and_off_balance(self) -> None:
        assembly = self.payload["complete_candidate_assembly"]
        self.assertIn("alpha<=0", assembly["candidate17"])
        self.assertIn("delta=0", assembly["candidate20_balance"])
        self.assertIn("alpha*delta<0", assembly["candidate20_off_balance"])
        flags = self.payload["classification"]
        self.assertTrue(flags["candidate17_complete_singular_rotation_zero_fibre_connected"])
        self.assertTrue(flags["candidate20_complete_singular_rotation_zero_fibre_connected"])

    def test_schema_rejects_candidate_identification(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate17_candidate20_identified"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)

    def test_schema_rejects_occupation_gluing_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["occupation_strata_glued"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)

    def test_schema_rejects_all_orders_promotion(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["all_orders_integration"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
