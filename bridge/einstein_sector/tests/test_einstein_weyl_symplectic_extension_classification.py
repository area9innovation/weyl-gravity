from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_symplectic_extension_classification import DEFAULT_OUTPUT, verify_certificate
from bridge.einstein_sector.verify_einstein_weyl_symplectic_extension_classification import verify_payload


class SymplecticExtensionClassificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_producer_and_independent_verifier(self) -> None:
        verify_certificate()
        verify_payload(self.payload)

    def test_false_raw_lift_sign_invariant_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["raw_lift_XX_sign_invariant"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)

    def test_false_cyclic_split_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["admissible_corrected_parity_complete_cyclic_split"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)

    def test_shear_mutation_is_decisive(self) -> None:
        for parity in ("axial", "polar"):
            raw = self.payload["generic_parity_blocks"][parity]["sheared_raw_extra_Gram"]
            self.assertTrue(raw[0][0].startswith("-"))

    def test_after_residual_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["after_residual_split"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)


if __name__ == "__main__":
    unittest.main()
