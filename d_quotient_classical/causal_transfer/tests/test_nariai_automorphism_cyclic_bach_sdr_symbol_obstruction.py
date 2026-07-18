from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_automorphism_cyclic_bach_sdr_symbol_obstruction import SCHEMA, build


class NariaiAutomorphismCyclicBachSDRObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_metric_symbol_exact(self) -> None:
        self.assertEqual(self.value["metric_exactness"]["symbol_cohomology_dimension"], 0)
        self.assertTrue(self.value["metric_exactness"]["kernel_B4_equals_image_K1"])
        self.assertTrue(self.value["metric_exactness"]["kernel_Ksharp1_equals_image_B4"])

    def test_multiplier_obstruction(self) -> None:
        self.assertEqual(self.value["kernel_witness"]["dimension"], 15)
        self.assertEqual(self.value["kernel_witness"]["incoming_lambda_arrows"], 0)
        self.assertFalse(self.value["obstruction"]["finite_order_filtration_compatible_SDR_exists"])

    def test_repair_not_overruled(self) -> None:
        self.assertFalse(self.value["flags"]["LARGER_MAPPING_CONE_REPAIR_OBSTRUCTED"])
        self.assertFalse(self.value["repair_boundary"]["sufficiency_claimed"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_sdr_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
