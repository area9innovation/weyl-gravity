import json
import unittest

from jsonschema import ValidationError

from d_quotient_classical.causal_transfer import (
    green_hyperbolic_cyclic_transfer_theorem as theorem,
)


class GreenHyperbolicCyclicTransferTheoremTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_positive_toy_covers_difference_and_pairing(self) -> None:
        toy = self.value["toy_fixture"]
        self.assertEqual(toy["causal_difference_rank"], 2)
        self.assertTrue(all(value == 0 for value in toy["identity_defects"].values()))
        self.assertTrue(self.value["exact_checks"]["induced_pairing_identity_exact"])

    def test_causal_quasi_isomorphism_is_a_composite(self) -> None:
        statement = self.value["conclusions"]["causal_quasi_isomorphism"]
        self.assertIn("[i_sc][Delta_E][p_c]", statement)
        self.assertIn("whenever the endpoint map is", statement)

    def test_seven_sharp_counterexamples(self) -> None:
        rows = self.value["necessity_counterexamples"]
        self.assertEqual(len(rows), 7)
        support = next(
            row
            for row in rows
            if row["counterexample_id"] == "SUPPORT_LOCALITY_IS_ESSENTIAL"
        )
        self.assertEqual(support["defect"]["rank"], 0)
        self.assertEqual(
            support["defect"]["nonzero_entries"],
            [{"row": 2, "column": 1, "coefficient": 1}],
        )
        for row in rows:
            if row is not support:
                self.assertGreater(row["defect"]["rank"], 0)

    def test_normalizations_are_not_overclaimed(self) -> None:
        normalizations = self.value["sharp_hypotheses"][
            "normalizations_not_needed_for_one_step_chain_identity"
        ]
        self.assertEqual(normalizations, ["h^2=0", "h i=0", "p h=0"])
        replacements = " ".join(
            self.value["sharp_hypotheses"][
                "replaceable_sufficient_conditions"
            ]
        )
        self.assertIn("timelike boundary", replacements)
        self.assertIn("finite rank", replacements)

    def test_consumers_are_same_background_and_read_only(self) -> None:
        consumers = self.value["consumer_replays"]
        self.assertFalse(
            self.value["background_scope"]["cross_background_identification"]
        )
        self.assertFalse(consumers["conformal_cylinder"]["producer_rerun"])
        self.assertFalse(consumers["unit_nariai"]["producer_rerun"])
        self.assertIn("386=356+30", consumers["conformal_cylinder"]["carrier"])
        self.assertIn("310=15+140+140+15", consumers["unit_nariai"]["carrier"])

    def test_hadamard_is_outside_the_claim(self) -> None:
        self.assertIn(
            "does not transport wavefront sets",
            self.value["claim_boundary"],
        )
        self.assertIn(
            "Hadamard two-point function",
            self.value["claim_boundary"],
        )

    def test_guard_rejects_cross_background_promotion(self) -> None:
        mutant = json.loads(json.dumps(self.value))
        mutant["background_scope"]["cross_background_identification"] = True
        with self.assertRaises((AssertionError, ValidationError)):
            theorem.validate(mutant)

    def test_guard_rejects_missing_counterexample_carrier(self) -> None:
        mutant = json.loads(json.dumps(self.value))
        mutant["necessity_counterexamples"][3]["defect"][
            "nonzero_entries"
        ] = []
        with self.assertRaises((AssertionError, ValidationError)):
            theorem.validate(mutant)


if __name__ == "__main__":
    unittest.main()
