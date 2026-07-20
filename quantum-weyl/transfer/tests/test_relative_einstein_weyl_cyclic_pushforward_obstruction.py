from __future__ import annotations

from copy import deepcopy
import json
import unittest

from transfer.relative_einstein_weyl_cyclic_pushforward_obstruction import (
    evaluate,
    validate,
)
from transfer.relative_einstein_weyl_cyclic_pushforward_obstruction_certificate import (
    OUTPUT,
    build,
)
from transfer.verify_relative_einstein_weyl_cyclic_pushforward_obstruction import (
    verify,
)


class RelativeEinsteinWeylCyclicPushforwardTests(unittest.TestCase):
    def test_exact_checks(self) -> None:
        self.assertTrue(all(evaluate()["exact_checks"].values()))

    def test_action_carriers_are_cotangent_complete(self) -> None:
        carriers = evaluate()["action_carriers"]
        self.assertEqual(carriers["Einstein_Maxwell"]["row_count"], 38)
        self.assertEqual(carriers["Weyl_Maxwell"]["row_count"], 40)
        self.assertTrue(
            carriers["Einstein_Maxwell"]["dual_involution_exact"]
        )
        self.assertTrue(carriers["Weyl_Maxwell"]["dual_involution_exact"])

    def test_316_minimality_is_scoped(self) -> None:
        carrier = evaluate()["relative_cotangent_carrier"]
        self.assertEqual(
            carrier["minimality_status"],
            "MINIMAL_WITHIN_DECLARED_FULL_CONE_COTANGENT_CLASS_ONLY",
        )
        self.assertEqual(carrier["absolute_mixed_bundle_minimality"], "NOT_PROVED")

    def test_action_pushforward_is_obstructed(self) -> None:
        verdict = evaluate()["verdict"]
        self.assertFalse(verdict["action_compatible_cyclic_pushforward_exists"])
        self.assertTrue(verdict["canonical_316_unary_cyclic_carrier_exists"])
        self.assertFalse(verdict["canonical_316_pairing_is_action_pairing"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_action_pairing_promotion_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"][
            "CANONICAL_316_PAIRING_PROMOTED_TO_ACTION_PAIRING"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_coefficient_promotion_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["MATCHED_ONE_LOOP_COEFFICIENTS_COMPUTED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
