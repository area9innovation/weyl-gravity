from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_minimal_ladder_synthesis_after_level3b import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json"
)


class MinimalLadderSynthesisAfterLevel3bTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_independent_exact_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_import_hash_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["imports"]["correct_level3b"]["sha256"] = "0" * 64
        with self.assertRaises(Exception):
            verify(mutated)

    def test_theory_row_omission_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["theory_space_table"].pop()
        with self.assertRaises(Exception):
            verify(mutated)

    def test_gate_column_omission_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["theory_space_columns"].pop()
        with self.assertRaises(Exception):
            verify(mutated)

    def test_superseded_parent_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        for row in mutated["theory_space_table"]:
            if row["family_id"] == "CANDIDATE_A_TUNED_R2_AUXILIARY":
                row["causal_parent_status"]["status"] = "CERTIFIED"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_literal_corrected_conflation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["convention_reconciliation"]["literal_level3"][
            "coefficient"
        ] = "-2F_X"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_hybrid_closure_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["tested_union"]["not_a_closure_under_hybrids"] = (
            "All hybrids are included."
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_escape_or_downstream_promotion_rejected(self) -> None:
        mutations = [
            ("escape", "ACTIVATED_HEALTHY_ACTION"),
            ("selected_action", True),
            ("quantum", True),
        ]
        for kind, value in mutations:
            with self.subTest(kind=kind):
                mutated = deepcopy(self.value)
                if kind == "escape":
                    mutated["smallest_representation_level_escape"][
                        "activation"
                    ] = value
                elif kind == "selected_action":
                    mutated["terminal_verdict"]["selected_action"] = value
                else:
                    mutated["claim_flags"][
                        "HADAMARD_ANOMALY_QME_OR_QUANTUM"
                    ] = value
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
