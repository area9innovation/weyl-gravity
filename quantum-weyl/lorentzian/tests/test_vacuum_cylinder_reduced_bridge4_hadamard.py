from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from lorentzian.vacuum_cylinder_reduced_bridge4_hadamard import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from lorentzian.verify_vacuum_cylinder_reduced_bridge4_hadamard import (
    mutation_guards,
    verify,
)


class VacuumCylinderReducedBridge4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_generated_certificate_is_current_and_strict(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.value)
        self.assertEqual(self.value["dependency_tags"], ["REDUCED-MODE", "LORENTZIAN-CAUSAL"])

    def test_same_background_activation_gate_is_closed(self) -> None:
        scope = self.value["scope"]
        self.assertEqual(scope["background"], "vacuum conformal cylinder R x S3 of unit radius")
        self.assertEqual(
            self.value["activation_gate"]["gate_status"],
            "CLOSED_FOR_REDUCED_PHYSICAL_BRIDGE4",
        )

    def test_all_branch_identities_and_signs_are_exact(self) -> None:
        expected = {"E": (2, 1), "A": (3, -1), "L": (4, -1)}
        for family, (minimum, sign) in expected.items():
            row = self.value["branch_data"][family]
            self.assertEqual((row["minimum_energy"], row["krein_sign"]), (minimum, sign))
            self.assertTrue(all(row["exact_checks"].values()))

    def test_reduced_hadamard_does_not_promote_full_bv(self) -> None:
        decision = self.value["decision"]
        self.assertEqual(decision["Bridge_4_reduced_vacuum_cylinder"], "CERTIFIED")
        self.assertEqual(decision["Bridge_4_full_BV"], "NO_CERTIFIED_MAP")
        self.assertEqual(decision["Bridge_4_Berger"], "NO_CERTIFIED_MAP")
        self.assertEqual(decision["global_BRST_Hadamard_state"], "NO_CERTIFIED_MAP")

    def test_state_space_is_krein_not_positive_hilbert(self) -> None:
        state = self.value["state_space"]
        self.assertEqual(state["E"], "POSITIVE_QUASIFREE_HADAMARD_STATE_SECTOR")
        self.assertIn("NEGATIVE_KREIN", state["A"])
        self.assertIn("NEGATIVE_KREIN", state["L"])
        self.assertFalse(state["positive_graviton_Hilbert_space"])

    def test_forbidden_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_independent_replay_and_mutation_guards(self) -> None:
        self.assertEqual(verify(), self.value)
        mutation_guards(self.value)


if __name__ == "__main__":
    unittest.main()
