from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_global_symplectic_restriction import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_homogeneous_global_symplectic_restriction import verify_certificate as verify_independently


class HomogeneousRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_exact_shear_and_rank(self) -> None:
        theorem = self.payload["theorem"]
        self.assertEqual(theorem["relative_endomorphism"]["rank_N"], 2)
        self.assertEqual(theorem["relative_endomorphism"]["N_squared"], "0")
        self.assertEqual(theorem["cauchy_forms_after_common_factor_2piL"]["both_rank"], 6)
        self.assertTrue(self.payload["classification"]["linear_symplectomorphism_exhibited"])
        self.assertFalse(self.payload["classification"]["identity_inclusion_symplectic"])

    def test_scope(self) -> None:
        scope = self.payload["theorem"]["topology_and_function_space"]
        self.assertTrue(scope["flat_holonomy_W_x_retained"])
        self.assertFalse(scope["bounded_in_time_restriction_imposed"])
        self.assertFalse(self.payload["classification"]["one_particle_or_quantum_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
