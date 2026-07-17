from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from active_frontier import build, validate
from active_frontier_certificate import HERE, OUTPUT, build_certificate
from verify_active_frontier import verify


class ActiveFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_frontier_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads((HERE / "schema/active-frontier-v1.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)

    def test_g1_is_the_only_completed_quantum_promotion_level(self) -> None:
        ladder = self.payload["promotion_ladder"]
        self.assertEqual(ladder["G1"], "PASSED_AFN0_LOCAL_QUOTIENT")
        self.assertTrue(ladder["G2"].startswith("BLOCKED"))
        self.assertTrue(ladder["G5"].startswith("BLOCKED"))

    def test_supersession_does_not_delete_history(self) -> None:
        for row in self.payload["supersession_ledger"]:
            self.assertIn("HISTORY_RETAINED", row["disposition"])

    def test_mixed_q3_is_independently_accepted_and_transfer_is_next(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["MAXWELL_TRANSFER_FORMULA_INDEPENDENTLY_REPLAYED_BY_QUANTUM"])
        self.assertTrue(flags["MAXWELL_TRANSFER_INDEPENDENTLY_REPLAYED_BY_QUANTUM"])
        self.assertTrue(flags["COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED"])
        self.assertTrue(flags["MIXED_Q3_INPUT_UNBLOCKED"])
        self.assertTrue(flags["MIXED_Q3_INDEPENDENTLY_ACCEPTED"])
        row = self.payload["active_rows"]["classical_interacting_input"]
        self.assertIn("MIXED_Q3_INDEPENDENTLY_ACCEPTED", row["status"])
        self.assertEqual(
            row["next_gate"], "BERGER_RETAINED_MIXED_ELL3_TRANSFER_AND_EXCHANGE"
        )

    def test_hadamard_existence_boundary_is_authoritative(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["COMPANION_DECOMPOSABILITY_CERTIFIED"])
        self.assertTrue(flags["STATIONARY_GENERATOR_IMPORT_CONSUMER_READY"])
        self.assertFalse(flags["HADAMARD_EXISTENCE_THEOREM_APPLIES"])
        row = self.payload["active_rows"]["free_Lorentzian_state"]
        self.assertIn(
            "STATIONARY_IMPORT_CONSUMER_READY_INPUT_ABSENT",
            row["status"],
        )
        self.assertEqual(
            row["next_gate"],
            "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
        )

    def test_relative_frontier_imports_polar_but_not_global_triangle(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED"])
        self.assertTrue(flags["PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED"])
        row = self.payload["active_rows"]["relative_Einstein_Weyl"]
        self.assertEqual(
            row["status"],
            "PRINCIPAL_GENERIC_AXIAL_AND_GENERIC_POLAR_UNGAUGED_PREFLIGHTS_GLOBAL_V1_OPEN",
        )
        self.assertEqual(
            row["next_gate"], "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        )

    def test_quantum_overclaim_is_rejected(self) -> None:
        mutant = json.loads(json.dumps(self.payload))
        mutant["claim_flags"]["QME_RESTORED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate())


if __name__ == "__main__":
    unittest.main()
