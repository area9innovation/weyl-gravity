from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_parity_complete_residual_exact_sequence import DEFAULT_OUTPUT, _table, verify_certificate
from bridge.einstein_sector.verify_einstein_weyl_parity_complete_residual_exact_sequence import verify_payload


class ParityCompleteResidualExactSequenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_all_rows_are_dimension_and_rank_exact(self) -> None:
        for row in _table():
            self.assertEqual(row["Einstein_dimension"]+row["extra_dimension"], row["Weyl_dimension"])
            self.assertEqual(row["Einstein_pairing_rank"]+row["extra_pairing_rank"], row["Weyl_pairing_rank"])

    def test_generator_and_independent_verifier(self) -> None:
        verify_certificate()
        verify_payload(self.payload)

    def test_false_degreewise_short_exact_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["degreewise_short_exact_complex_certified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)

    def test_false_split_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["maximal_preresidual_statement"]["splitting_claim"] = True
        with self.assertRaises(AssertionError):
            verify_payload(mutated, verify_files=False)

    def test_false_after_residual_sequence_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["after_residual_exact_sequence_certified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)


if __name__ == "__main__":
    unittest.main()
