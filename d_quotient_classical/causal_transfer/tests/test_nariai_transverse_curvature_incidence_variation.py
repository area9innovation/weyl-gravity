from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer import nariai_transverse_curvature_incidence_variation as producer
from d_quotient_classical.causal_transfer import verify_nariai_transverse_curvature_incidence_variation as independent


class NariaiTransverseCurvatureIncidenceVariationTest(unittest.TestCase):
    def test_exact_variation(self) -> None:
        value = producer.exact_variation()
        self.assertEqual(value["delta_ricci"]["rank"], 0)
        self.assertEqual(value["algebraic_bianchi_defect_count"], 0)
        self.assertEqual(value["delta_curvature_incidence"]["rank"], 4)
        self.assertEqual(len(value["delta_curvature_incidence"]["entries"]), 12)
        self.assertEqual(value["normalized_anchor"]["value"], "1")

    def test_schema_and_scope(self) -> None:
        payload = producer.build()
        producer.verify(payload)
        schema = json.loads(producer.SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        self.assertTrue(payload["flags"]["TRANSVERSE_FIRST_AND_DUAL_INCIDENCE_VARIATION"])
        self.assertFalse(payload["flags"]["TRANSVERSE_BGG_SPLITTING_VARIATION"])
        self.assertFalse(payload["flags"]["TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION"])

    def test_independent_replay(self) -> None:
        incidence, correction = independent._independent_incidence()
        self.assertEqual(incidence.rank(), 4)
        self.assertEqual(correction.rank(), 4)
        self.assertEqual(len(incidence.todok()), 12)


if __name__ == "__main__":
    unittest.main()
