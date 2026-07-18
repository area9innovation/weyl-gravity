from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.conformal_nariai_310_causal_transfer import SCHEMA, build


class ConformalNariai310CausalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_open_conformal_class(self) -> None:
        self.assertEqual(self.value["background_class"]["conformal_radius"], "1/9")
        self.assertTrue(self.value["background_class"]["inside_parent_ADM_radius_1_over_4"])
        self.assertTrue(self.value["nonconstant_consumer"]["inside_conformal_radius"])

    def test_metric_and_all_row_transport(self) -> None:
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertTrue(self.value["flags"]["METRIC_BACH_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS"])
        self.assertTrue(self.value["flags"]["RANK_310_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS"])
        self.assertTrue(self.value["flags"]["METRIC_DESCENT_ON_CONFORMAL_CLASS"])

    def test_transverse_scope_remains_open(self) -> None:
        self.assertFalse(self.value["flags"]["ALL_BACH_FLAT_ADM_BALL_METRIC_THEOREM"])
        self.assertFalse(self.value["flags"]["TRANSVERSE_BACH_FLAT_DEFORMATIONS"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_transverse_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["TRANSVERSE_BACH_FLAT_DEFORMATIONS"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
