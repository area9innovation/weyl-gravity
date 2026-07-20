from __future__ import annotations

from copy import deepcopy
import json
import unittest

from lorentzian.berger_c26_bikernel_support_profile_nondefinition import (
    UNDEFINED,
    evaluate,
    validate,
)
from lorentzian.berger_c26_bikernel_support_profile_nondefinition_certificate import (
    OUTPUT,
    build,
)
from lorentzian.verify_berger_c26_bikernel_support_profile_nondefinition import (
    verify,
)


class BergerC26SupportProfileNondefinitionTests(unittest.TestCase):
    def test_exact_audit_passes(self) -> None:
        value = evaluate()
        self.assertTrue(all(value["exact_checks"].values()))

    def test_smoothness_is_retained_without_support_promotion(self) -> None:
        value = evaluate()
        self.assertTrue(value["claim_flags"]["C26_SMOOTH"])
        self.assertFalse(value["claim_flags"]["C26_SERIALIZED"])
        self.assertEqual(value["support_profile"]["x_past_compact"], UNDEFINED)

    def test_all_endpoint_blocks_are_symbolic_or_existential(self) -> None:
        blocks = evaluate()["representation_audit"]["blocks"]
        self.assertEqual(len(blocks), 3)
        self.assertTrue(all(not row["serialized_bikernel"] for row in blocks))
        self.assertTrue(all(not row["stationary_mode_table"] for row in blocks))

    def test_first_obstruction_names_minimal_carrier(self) -> None:
        obstruction = evaluate()["first_obstruction"]
        self.assertEqual(
            obstruction["obstruction_id"],
            "MISSING_NORMALIZED_SERIALIZED_H26_REPRESENTATIVE",
        )
        self.assertIn(
            "the resulting serialized commutator C26=[H26_plus,q26]",
            obstruction["minimal_next_payload"],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_support_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["support_profile"]["x_past_compact"] = "TRUE"
        with self.assertRaisesRegex(ValueError, "support or pairing"):
            validate(mutant)

    def test_hadamard_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["RETAINED_26_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "claim flags"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
