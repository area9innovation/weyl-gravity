from __future__ import annotations

from copy import deepcopy
import json
import unittest

from d_quotient_classical.backreacted_clock import (
    berger_filtered_cyclic_branch_extension_obstruction as producer,
)


class BergerFilteredCyclicBranchExtensionObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_committed_certificate_matches_build(self) -> None:
        self.assertEqual(
            json.loads(producer.OUTPUT.read_text()),
            self.value,
        )

    def test_first_obstruction_is_normalized_and_nonzero(self) -> None:
        obstruction = self.value["first_obstruction_class"]
        self.assertEqual(obstruction["normalized_evaluation"], [["1", "0"]])
        self.assertEqual(
            obstruction["certified_rank_ledger"],
            {
                "allowed_boundary": 4,
                "plus_augmented": 5,
                "cross_augmented": 4,
                "both_augmented": 5,
            },
        )

    def test_minimal_page_repair_is_one_hyperbolic_pair(self) -> None:
        fixture = self.value["minimal_page_enlargement_classification"][
            "standard_fibre"
        ]
        self.assertEqual(fixture["obstruction_image_rank"], 1)
        self.assertEqual(fixture["minimum_new_field_directions"], 1)
        self.assertEqual(fixture["minimum_cyclic_BV_rows"], 2)
        self.assertFalse(fixture["zero_new_boundary_directions_sufficient"])
        self.assertTrue(fixture["one_new_boundary_direction_sufficient_at_page"])
        self.assertEqual(
            fixture["extended_boundary_rank"],
            fixture["extended_augmented_rank"],
        )

    def test_contractible_rank46_does_not_repair(self) -> None:
        self.assertFalse(
            self.value["claim_flags"][
                "RANK46_CONTRACTIBLE_GRAPH_REPAIRS_OBSTRUCTION"
            ]
        )

    def test_ell3_is_not_projected(self) -> None:
        relation = self.value["relation_to_retained_ell3"]
        self.assertEqual(relation["branch_label_status"], "NO_CERTIFIED_MAP")
        self.assertEqual(
            relation["mode_pair_source_table_status"],
            "NO_CERTIFIED_MAP",
        )
        self.assertFalse(
            self.value["claim_flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"]
        )

    def test_forbidden_promotions_are_rejected(self) -> None:
        for flag in (
            "ARITY_ONE_BRANCH_SPLIT_EXISTS",
            "CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS",
            "RANK46_CONTRACTIBLE_GRAPH_REPAIRS_OBSTRUCTION",
            "GLOBAL_EQUIVARIANT_ENLARGEMENT_CONSTRUCTED",
            "ELL3_BRANCH_PROJECTION_AUTHORIZED",
            "MODE_PAIR_SOURCE_TABLE_AUTHORIZED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.assertRaises(Exception):
                producer.validate(mutant, verify_sources=False)


if __name__ == "__main__":
    unittest.main()
