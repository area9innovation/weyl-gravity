from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

from ...affine_rail import build_microfactor_render_context
from ..child_cell_factor import (
    FREQUENCY_CHILDREN,
    frequency_cell,
    verify_factor,
)
from ..verify_handoff import HandoffError


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "child_q00_p223_l0.json"
)


class ChildCellFactorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text())
        cls.context = build_microfactor_render_context(frequency_cell(0))
        cls.prefix_context = build_microfactor_render_context()

    def test_final_frequency_children_are_an_exact_cover(self) -> None:
        cells = [frequency_cell(child) for child in range(FREQUENCY_CHILDREN)]
        self.assertEqual(cells[0][0], Fraction(1, 2))
        self.assertEqual(cells[-1][1], Fraction(129, 256))
        for left, right in zip(cells, cells[1:]):
            self.assertEqual(left[1], right[0])

    def test_sentinel_factor_and_prefix_crosswalk_verify(self) -> None:
        self.assertTrue(verify_factor(
            self.payload,
            ROOT,
            context=self.context,
            prefix_context=self.prefix_context,
        ))

    def test_false_local_restart_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["frame_reset"]["physical_restart"] = True
        with self.assertRaisesRegex(HandoffError, "exact coordinate identity"):
            verify_factor(
                payload, context=self.context,
                prefix_context=self.prefix_context,
            )

    def test_mutated_identity_transition_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["frame_reset"]["right_change_of_coordinates"][0][0] = "0/1"
        with self.assertRaisesRegex(HandoffError, "exact coordinate identity"):
            verify_factor(
                payload, context=self.context,
                prefix_context=self.prefix_context,
            )

    def test_mutated_prefix_crosswalk_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["inherited_prefix_boundary_crosswalk"]["center"][0][0] = "0/1"
        with self.assertRaisesRegex(HandoffError, "prefix boundary crosswalk"):
            verify_factor(
                payload, context=self.context,
                prefix_context=self.prefix_context,
            )


if __name__ == "__main__":
    unittest.main()
