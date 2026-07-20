from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_apparatus_z2_integrability_receiver_disposition import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_apparatus_z2_integrability_receiver_disposition import (
    verify,
)


class BergerApparatusZ2ReceiverDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_first_missing_operator_precedes_source_and_cokernel(self) -> None:
        gates = self.value["ordered_gate_disposition"]
        self.assertEqual([row["gate"] for row in gates], [1, 2, 3, 4])
        self.assertEqual(
            gates[0]["object"], "combined_q1_pairing_real_K_carrier"
        )
        self.assertEqual(
            self.value["first_missing_operator"]["status"],
            "OBSTRUCTED_IN_DECLARED_LINEAR_K_IDENTIFICATION_CLASS",
        )
        self.assertEqual(gates[0]["status"], "OBSTRUCTED")

    def test_combined_q1_obstruction_is_scoped_and_has_minimal_repair(self) -> None:
        row = self.value["combined_q1_crosswalk_obstruction"]
        self.assertEqual(row["current_global_rod_span_rank"], 6)
        self.assertEqual(row["time_translation_closure_rank"], 8)
        self.assertEqual(row["material_to_global_constant_mixing_nullity"], 0)
        self.assertEqual(row["prospective_repaired_base_rows"], 112)
        self.assertEqual(row["prospective_identified_union_rows"], 160)
        self.assertFalse(row["global_no_go"])

    def test_all_symmetric_pairs_are_required(self) -> None:
        self.assertEqual(
            self.value["strict_receiver_contract"]["quadratic_pairs"],
            ["(u_0,u_0)", "(u_0,u_1)", "(u_1,u_1)"],
        )

    def test_all_receiver_outputs_fail_closed(self) -> None:
        self.assertEqual(
            set(self.value["strict_receiver_contract"]["required_outputs"].values()),
            {"NO_CERTIFIED_MAP"},
        )
        self.assertEqual(
            set(self.value["downstream_disposition"].values()),
            {"NO_CERTIFIED_MAP"},
        )

    def test_charge_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["strict_receiver_contract"]["required_outputs"][
            "moment_map_Taub_polynomials"
        ] = "CERTIFIED"
        with self.assertRaises(Exception):
            validate(mutant)

    def test_resonance_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["strict_receiver_contract"]["required_outputs"][
            "nonzero_shell_resonant_pairings"
        ] = "CERTIFIED"
        with self.assertRaises(Exception):
            validate(mutant)

    def test_background_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["strict_receiver_contract"]["background"] = (
            "compact product relabelled as Berger"
        )
        with self.assertRaises(Exception):
            validate(mutant)

    def test_mixed_pair_deletion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["strict_receiver_contract"]["quadratic_pairs"].remove("(u_0,u_1)")
        with self.assertRaises(Exception):
            validate(mutant)

    def test_q2_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["flags"]["QUADRATIC_SOURCE_CERTIFIED"] = True
        with self.assertRaises(Exception):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
