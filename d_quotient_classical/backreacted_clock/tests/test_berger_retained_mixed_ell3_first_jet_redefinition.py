from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)


class FirstJetRedefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(first.OUTPUT.read_text())
        first.validate(cls.value)

    def test_exact_first_jet_primitive(self) -> None:
        self.assertEqual(self.value["coupled_schur_problem"]["C_rank"], 1327)
        self.assertEqual(self.value["coupled_schur_problem"]["Schur_rank"], 557)
        self.assertEqual(self.value["exact_primitive"]["positive_jet_nonzero_by_axis"], [43, 94, 95, 108])

    def test_scope_is_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_COMPUTED"])
        for name, flag in flags.items():
            if name != "FIRST_JET_PHYSICAL_ACTION_TRIVIALIZATION_COMPUTED":
                self.assertFalse(flag)

    def test_primitive_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_primitive"]["positive_jet_by_axis"][0][0]["coefficient"] = "0"
        with self.assertRaisesRegex(ValueError, "first-jet primitive reconstruction"):
            first.validate(mutant, ranks=False)

    def test_overclaim_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["CYCLIC_DEFORMATION_CLASS_DECIDED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            first.validate(mutant, replay=False)


if __name__ == "__main__":
    unittest.main()
