from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.curvature_image_presymplectic_ccr import validate
from lorentzian.curvature_image_presymplectic_ccr_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_curvature_image_presymplectic_ccr import verify


class CurvatureImagePresymplecticCCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/curvature-image-presymplectic-ccr-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_curvature_graph_and_causal_pairing_are_bound(self) -> None:
        self.assertTrue(self.certificate["carrier"]["support_local"])
        self.assertEqual(
            self.certificate["causal_presymplectic_form"]["status"],
            "CERTIFIED_ON_CURVATURE_GRAPH_IMAGE",
        )
        self.assertTrue(
            all(self.certificate["well_definedness_replay"]["checks"].values())
        )

    def test_universal_graded_star_algebra_is_defined(self) -> None:
        algebra = self.certificate["universal_star_algebra"]
        self.assertEqual(algebra["status"], "DEFINED_AND_WELL_DEFINED")
        self.assertIn("graded CCR", algebra["definition"])
        self.assertIn("anticommutator", algebra["odd_specialization"])

    def test_direct_kernel_and_state_remain_open(self) -> None:
        boundary = self.certificate["analytic_boundary"]
        self.assertEqual(
            boundary["direct_curvature_causal_propagator_kernel"],
            "NOT_CONSTRUCTED",
        )
        self.assertEqual(boundary["Hadamard_two_point_function"], "NOT_CONSTRUCTED")
        self.assertEqual(boundary["Lorentzian_QME"], "NOT_COMPUTED")

    def test_residual_H4_is_not_promoted_to_particle_space(self) -> None:
        guard = self.certificate["observable_comparison"]["H4_scope_guard"]
        self.assertIn("deformation/vertex", guard)
        self.assertIn("not one-particle", guard)

    def test_overclaims_fail_closed(self) -> None:
        for flag in (
            "DIRECT_CURVATURE_CAUSAL_PROPAGATOR_CONSTRUCTED",
            "CURVATURE_HADAMARD_STATE_CONSTRUCTED",
            "PHYSICAL_POSITIVITY_CERTIFIED",
            "LORENTZIAN_QME_RESTORED",
        ):
            mutant = deepcopy(self.certificate)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "over-promoted"):
                validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
