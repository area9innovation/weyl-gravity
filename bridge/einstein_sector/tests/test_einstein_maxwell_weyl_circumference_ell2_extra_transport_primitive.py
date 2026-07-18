from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive as result


class CircumferenceEll2ExtraTransportPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(result.OUTPUT.read_text(encoding="utf-8"))

    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(self.value, result.build())

    def test_actual_resonant_source_has_ordinary_primitive(self) -> None:
        disposition = self.value["transport_primitive"]["disposition"]
        self.assertTrue(disposition["potential_p_primary_resonance"])
        self.assertFalse(disposition["actual_source_requires_secular_prefactor"])
        self.assertTrue(disposition["all_four_extra_columns_in_linear_image"])
        self.assertEqual(self.value["transport_primitive"]["specialization"]["p"], "0")

    def test_unique_nonzero_source_and_full_remainders(self) -> None:
        axial = self.value["transport_primitive"]["axial"]
        polar = self.value["transport_primitive"]["polar"]
        self.assertTrue(all(value == "0" for row in axial["source_columns"] for value in row))
        self.assertTrue(all(row[0] == "0" for row in polar["source_columns"]))
        self.assertTrue(any(row[1] != "0" for row in polar["source_columns"]))
        self.assertTrue(all(value == "0" for row in axial["remainder_columns"] for value in row))
        self.assertTrue(all(value == "0" for row in polar["remainder_columns"] for value in row))

    def test_covariant_index_weight_mutation_is_nonzero(self) -> None:
        mutation = self.value["transport_primitive"]["negative_control"]
        self.assertTrue(mutation["detected"])
        self.assertTrue(any(value != "0" for row in mutation["remainder_columns"] for value in row))

    def test_later_claims_remain_false(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["causal_retarded_map_certified"])
        self.assertFalse(flags["residual_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
