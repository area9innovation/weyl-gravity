from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import SCHEMA, build


class NariaiParentDetourMappingConeRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_economical_carrier(self) -> None:
        self.assertEqual(self.value["carrier"]["total_rank"], 310)
        self.assertEqual(self.value["carrier"]["metric_total_rank"], 26)
        self.assertEqual(
            sum((4, 9, 9, 4)),
            self.value["carrier"]["metric_total_rank"],
        )
        self.assertEqual(self.value["carrier"]["added_rank_over_obstructed_carrier"], 22)
        self.assertEqual(self.value["exact_checks"]["ker_p0_dimension"], 11)

    def test_coefficient_repair(self) -> None:
        for name in (
            "p0_J0_rank", "r0_J0_minus_identity_rank",
            "p0_L0_minus_identity_entries", "J0_g_minus_R0_entries",
            "g_J0_minus_identity_entries", "g_L0_entries",
            "d_J0_g_plus_L1_k_minus_d_entries", "M_L1_minus_Phi_entries",
            "effective_Hessian_minus_B_action_entries",
        ):
            self.assertEqual(self.value["exact_checks"][name], 0, name)

    def test_cyclic_sdr(self) -> None:
        for name in (
            "split_Q_squared", "split_odd_cyclic", "projection_inclusion_identity",
            "inclusion_chain_map", "projection_chain_map", "retract_identity",
            "homotopy_odd_cyclic", "metric_pairing_pullback", "canonical_transform",
            "transform_left_inverse", "transform_right_inverse", "original_Q_squared",
            "original_odd_cyclic", "original_retract_identity",
        ):
            self.assertTrue(self.value["exact_checks"][name], name)

    def test_fail_closed_boundary(self) -> None:
        self.assertTrue(self.value["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"])
        self.assertFalse(self.value["flags"]["NARIAI_GREEN_HOMOTOPY"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_green_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NARIAI_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
