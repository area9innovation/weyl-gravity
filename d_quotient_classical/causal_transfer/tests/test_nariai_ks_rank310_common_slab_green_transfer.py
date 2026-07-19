from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_ks_rank310_common_slab_green_transfer import (
    SCHEMA,
    build,
)


class NariaiKSRank310CommonSlabGreenTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_six_block_natural_binding(self) -> None:
        binding = self.value["natural_geometric_binding"]
        self.assertEqual(binding["difference_block_count"], 6)
        self.assertTrue(binding["all_entries_finite_order_differential"])
        self.assertTrue(binding["all_coordinate_coefficients_determined_by_metric"])
        self.assertFalse(binding["component_expanded_PBW_table_emitted"])
        self.assertEqual(len(self.value["operator_registry"]), 6)
        self.assertEqual(
            {entry["name"] for entry in self.value["operator_registry"]},
            {"Delta g", "Delta k", "Delta M", "Delta B", "Delta gsharp", "Delta ksharp"},
        )

    def test_original_coordinate_conjugation_is_declared(self) -> None:
        conjugation = self.value["coordinate_conjugation"]
        self.assertIn("T_epsilon^{-1}", conjugation["original_differential"])
        self.assertIn("BV canonical", conjugation["properties"])

    def test_all_row_causal_scope(self) -> None:
        flags = self.value["flags"]
        self.assertTrue(flags["KS_COMMON_SLAB_RANK310_CYCLIC_SDR"])
        self.assertTrue(flags["KS_COMMON_SLAB_RANK310_GREEN_HOMOTOPY"])
        self.assertTrue(flags["KS_COMMON_SLAB_METRIC_DESCENT"])
        self.assertFalse(flags["KS_NONZERO_WHOLE_CYLINDER_GREEN_THEOREM"])
        self.assertFalse(flags["NON_EINSTEIN_BACH_FLAT_METRIC_TRANSFER"])

    def test_all_exact_checks(self) -> None:
        self.assertTrue(all(self.value["exact_checks"].values()))

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_whole_cylinder_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["KS_NONZERO_WHOLE_CYLINDER_GREEN_THEOREM"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)

    def test_schema_rejects_pretend_PBW_export(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["COMPONENT_EXPANDED_PBW_TABLE"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
