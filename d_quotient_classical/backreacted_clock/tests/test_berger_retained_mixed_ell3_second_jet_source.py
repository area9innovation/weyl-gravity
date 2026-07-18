from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)


class SecondJetSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(second.OUTPUT.read_text())
        second.validate(cls.value)

    def test_lower_pages_reproduce(self) -> None:
        self.assertEqual(self.value["reproduction"], {
            "zero_page_euler_terms": 0,
            "first_page_euler_terms": 0,
        })

    def test_total_derivative_and_ansatz_controls(self) -> None:
        quotient = self.value["quotient"]
        self.assertEqual(quotient["first_total_derivative_mutations_killed"], 4)
        self.assertEqual(quotient["second_total_derivative_mutations_killed"], 16)
        self.assertEqual(self.value["second_jet_ansatz"]["symmetric_PBW_label_count"], 155640)

    def test_source_is_not_promoted_to_a_verdict(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["ORDER_TWO_SOURCE_COMPUTED"])
        self.assertFalse(flags["ORDER_TWO_PRIMITIVE_COMPUTED"])
        self.assertFalse(flags["ORDER_TWO_OBSTRUCTION_PROVED"])

    def test_digest_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["order_two_source"]["Euler_records_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "certificate replay drifted"):
            second.validate(mutant)

    def test_overclaim_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["ORDER_TWO_OBSTRUCTION_PROVED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            second.validate(mutant, replay=False)


if __name__ == "__main__":
    unittest.main()
