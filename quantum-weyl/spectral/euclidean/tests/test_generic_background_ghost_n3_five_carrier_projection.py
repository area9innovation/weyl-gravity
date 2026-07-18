from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_n3_five_carrier_projection import (
    OUTPUT,
    SCHEMA,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_five_carrier_projection import (
    _formula_digest,
    verify,
)


class GenericGhostN3FiveCarrierProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_strict_schema_and_exact_quotient(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(
            self.value["quotient_section"]["raw_effective_channel_count"], 11
        )
        self.assertEqual(self.value["quotient_section"]["quotient_dimension"], 10)
        self.assertEqual(len(self.value["projection_rows"]), 11)

    def test_row_gradings_and_i28_section(self) -> None:
        validate(self.value)
        rows = self.value["projection_rows"]
        self.assertEqual(
            [row["numerator_box_degree"] for row in rows],
            [3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0],
        )

    def test_independent_unseen_fixture_replay(self) -> None:
        self.assertEqual(verify(), self.value)

    def test_formula_mutation_is_rejected_even_with_rehashed_digest(self) -> None:
        mutant = deepcopy(self.value)
        coefficient = mutant["projection_rows"][0]["terms"][0]["coefficient"]
        coefficient["numerator"] += coefficient["denominator"]
        mutant["formula_digest"] = _formula_digest(mutant["projection_rows"])
        with self.assertRaisesRegex(ValueError, "unseen exact tensor holdout"):
            verify(mutant)

    def test_fail_closed_lifecycle_mutation(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"] = True
        with self.assertRaises(Exception):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
