from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_exact_primitive as primitive,
)


class SecondJetExactPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(primitive.OUTPUT.read_text())
        primitive.validate(cls.value)

    def test_exact_replay_counts(self) -> None:
        replay = self.value["full_replay"]
        self.assertEqual(replay["correction_total_nonzero"], 4276)
        self.assertEqual(replay["Euler_target_coordinates"], 10043)
        self.assertEqual((replay["missing"], replay["extra"], replay["changed"]), (0, 0, 0))

    def test_exact_quotient_dimension(self) -> None:
        self.assertEqual(len(primitive.second.independent_mixed_euler_coordinates()), 39170)

    def test_coefficient_field_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "escaped QQ"):
            primitive._scalar("sqrt(2)")

    def test_scope_is_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED"])
        for name, flag in flags.items():
            if name != "PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED":
                self.assertFalse(flag)

    def test_coefficient_mutation_fails_exact_replay(self) -> None:
        mutant = deepcopy(primitive._load_records(self.value))
        mutant[0]["coefficient"] = "0"
        with self.assertRaisesRegex(ValueError, "zero coefficient"):
            primitive._correction(mutant)

    def test_record_file_digest_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_correction"]["records_file_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "file digest"):
            primitive.validate(mutant, replay=False)

    def test_overclaim_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["FULL_BV_POSITIVE_JET_REDEFINITION_MATCHED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            primitive.validate(mutant, replay=False)


if __name__ == "__main__":
    unittest.main()
