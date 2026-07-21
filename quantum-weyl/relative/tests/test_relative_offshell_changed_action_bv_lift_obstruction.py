from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from relative.relative_offshell_changed_action_bv_lift_obstruction import (
    ACTION_RESPONSE,
    HERE,
    OUTPUT,
    build_certificate,
    exact_replay,
    validate,
)
from relative.verify_relative_offshell_changed_action_bv_lift_obstruction import verify


class RelativeOffshellChangedActionBVLiftObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_checked_in_certificate(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        validate(self.certificate)

    def test_strict_schema(self) -> None:
        schema = json.loads(
            (HERE / "schema/relative-offshell-changed-action-bv-lift-obstruction-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_action_quotient_and_dual_witnesses(self) -> None:
        replay = self.certificate["exact_replay"]
        self.assertEqual(replay["relation_matrix_shape"], [7, 10])
        self.assertEqual(replay["relation_rank"], 7)
        self.assertEqual(replay["four_derivative_quotient_dimension"], 3)
        self.assertEqual(replay["axial_witness"]["on_requested_shift"], "-9")
        self.assertEqual(replay["polar_witness"]["on_requested_shift"], "-9/4")

    def test_one_action_covers_both_parities_without_orbit_mixing(self) -> None:
        selected = self.certificate["selected_repair_orbit"]
        self.assertTrue(selected["axial_and_polar_treated_together"])
        self.assertFalse(selected["pairing_deformation_mixed_in"])
        self.assertFalse(selected["physical_auxiliary_extension_mixed_in"])

    def test_p_shell_control_is_full_column_rank(self) -> None:
        control = self.certificate["p_shell_control"]
        self.assertEqual(control["constraint_matrix_shape"], [17, 6])
        self.assertEqual(control["rank"], 6)
        self.assertEqual(control["kernel_dimension"], 0)

    def test_rank_one_wall_mutation_is_rejected(self) -> None:
        action = json.loads(ACTION_RESPONSE.read_text())
        mutant = deepcopy(action)
        mutant["exact_cokernel"]["requested_source_action_shift"]["axial"][1][1] = "0"
        with self.assertRaisesRegex(ValueError, "cokernel witness drifted"):
            exact_replay(mutant)

    def test_bv_and_qme_lifecycle_remain_fail_closed(self) -> None:
        disposition = self.certificate["noether_and_bv_disposition"]
        self.assertEqual(disposition["requested_changed_local_action"], "OBSTRUCTED")
        self.assertEqual(disposition["requested_changed_master_action"], "NOT_ACTIVATED")
        self.assertEqual(
            disposition["requested_full_40_to_38_cyclic_chain_lift"],
            "NOT_ACTIVATED",
        )
        quantum = self.certificate["relative_quantum_disposition"]
        self.assertEqual(quantum["relative_anomaly_coefficients"], "NOT_COMPUTED")
        self.assertEqual(quantum["relative_one_loop_QME"], "UNDEFINED")

    def test_upstream_action_variation_rail_is_independent(self) -> None:
        rail = self.certificate["independent_rails"]["upstream_action_variation"]
        self.assertEqual(rail["status"], "PASS")
        self.assertFalse(rail["imports_producer_matrices"])

    def test_independent_quantum_integration_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
