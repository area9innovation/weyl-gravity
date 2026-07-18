from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from spectral.euclidean.generic_background_ghost_n1_n2_vector_cpt_projection import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n1_n2_vector_cpt_projection import unseen_residual_count


class GenericGhostVectorN1N2CPTProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_minimal_cpt_rows_and_exact_replay(self) -> None:
        sign_flip = self.value["minimal_operator_sign_flip"]
        self.assertEqual(sign_flip["surviving_rows"], [1, 3, 14])
        self.assertEqual(sign_flip["n1_plus_n2_formula"], "6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14")
        replay = self.value["ordered_structure_projection"]["direct_fixture_replay"]
        self.assertEqual(replay["direct_identity_rows"], 2500)
        self.assertEqual(replay["convention_identity_rows"], 750)
        self.assertEqual(replay["nonzero_residual_count"], 0)

    def test_three_longitudinal_carriers_remain_open(self) -> None:
        theorem = self.value["minimal_missing_carrier_theorem"]
        self.assertEqual(
            theorem["missing_carriers"],
            [
                "N1_LONGITUDINAL_SCALAR",
                "N2_VECTOR_LONGITUDINAL",
                "N2_LONGITUDINAL_LONGITUDINAL",
            ],
        )
        self.assertEqual(theorem["irreducible_insertion"], "D_W=delta W d")
        self.assertFalse(self.value["claim_flags"]["ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"])

    def test_schema_and_claim_boundary_are_fail_closed(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        mutant = deepcopy(self.value)
        mutant["extra"] = True
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(mutant)))
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED"] = True
        with self.assertRaises((ValueError, ValidationError)):
            validate(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.value)

    def test_independent_unseen_replay_and_mutation(self) -> None:
        self.assertEqual(unseen_residual_count(self.value), 0)
        self.assertGreater(
            unseen_residual_count(self.value, mutate=True, stop_on_first=True), 0
        )


if __name__ == "__main__":
    unittest.main()
