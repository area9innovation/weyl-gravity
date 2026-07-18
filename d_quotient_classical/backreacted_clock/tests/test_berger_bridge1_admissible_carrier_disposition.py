from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_bridge1_admissible_carrier_disposition import build, validate
from d_quotient_classical.backreacted_clock.verify_berger_bridge1_admissible_carrier_disposition import verify


class BergerBridge1DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_unsplit_carrier_is_selected(self) -> None:
        self.assertTrue(self.value["flags"]["BERGER_UNSPLIT_RETAINED_CARRIER_SELECTED"])
        self.assertEqual(self.value["bridge_disposition"]["atlas_status"], "NO_CERTIFIED_MAP")
        self.assertFalse(self.value["bridge_disposition"]["ell3_branch_mixing_authorized"])

    def test_four_alternatives_remain_scoped(self) -> None:
        statuses = {name: row["status"] for name, row in self.value["four_alternative_disposition"].items()}
        self.assertEqual(statuses, {
            "relative_cofiber": "OPEN",
            "noncontractible_mixed_bundle": "OPEN",
            "declared_nonlocal_reduced_mode": "NO_CERTIFIED_MAP",
            "port_to_certified_split_background": "OPEN",
        })

    def test_overclaim_is_rejected(self) -> None:
        for flag in (
            "BERGER_BRIDGE1_ACTIVATED",
            "BERGER_RETAINED_BRANCH_CROSSWALK",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
