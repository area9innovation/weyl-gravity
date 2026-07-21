from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_candidate18_spectator_moment_ball_reduction import (
    ATLAS,
    OUTPUT,
    build_certificate,
    verify_output,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_candidate18_spectator_moment_ball_reduction import (
    verify_certificate,
    verify_payload,
)


class Candidate18SpectatorMomentBallReductionTests(unittest.TestCase):
    def test_generated_outputs_current(self) -> None:
        verify_output()

    def test_independent_verifier(self) -> None:
        verify_certificate()

    def test_dimension_reduction_retains_spectators(self) -> None:
        value = build_certificate()
        self.assertEqual(value["spectator_representation"]["real_dimension"], 20)
        self.assertEqual(value["active_coordinate_gate"]["ambient_real_dimension"], 40)
        self.assertTrue(
            value["classification"]["ten_spectators_retained_by_exact_fibre_reconstruction"]
        )

    def test_exact_ball_inequality(self) -> None:
        value = build_certificate()
        self.assertEqual(
            value["active_coordinate_gate"]["exact_spectator_existence_conditions"],
            ["H_s>=0", "|M_f|^2<=4*H_s^2"],
        )

    def test_atlas_is_fail_closed(self) -> None:
        entry = json.loads(ATLAS.read_text(encoding="utf-8"))["entries"][0]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")

    def test_false_promotions_and_spectator_drop_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text(encoding="utf-8"))
        promotion = copy.deepcopy(value)
        promotion["classification"]["active_real_radical_classified"] = True
        with self.assertRaises(AssertionError):
            verify_payload(promotion)
        drop = copy.deepcopy(value)
        drop["classification"]["ten_spectators_retained_by_exact_fibre_reconstruction"] = False
        with self.assertRaises(AssertionError):
            verify_payload(drop)


if __name__ == "__main__":
    unittest.main()
