from __future__ import annotations

from copy import deepcopy
import json
import unittest

from relative.contribution import OUTPUT, build_contribution, validate_contribution


class RelativeQuantumContributionTests(unittest.TestCase):
    def test_reproduces_registered_contribution(self) -> None:
        contribution = build_contribution()
        self.assertEqual(json.loads(OUTPUT.read_text()), contribution)
        validate_contribution(contribution)

    def test_scope_and_verdict_remain_fail_closed(self) -> None:
        contribution = build_contribution()
        self.assertEqual(contribution["team_id"], "quantum")
        self.assertEqual(contribution["claim_status"], "BLOCKED")
        self.assertEqual(contribution["verdict"], "ANALYTIC_FRAMEWORK_MISSING")
        self.assertIn("off-shell", " ".join(contribution["not_established"]))

    def test_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build_contribution())
        mutant["claim_status"] = "CERTIFIED"
        mutant["verdict"] = "CARTAN_QUANTUM_EXACT"
        with self.assertRaisesRegex(ValueError, "scope drifted"):
            validate_contribution(mutant)


if __name__ == "__main__":
    unittest.main()
