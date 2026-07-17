"""Regression tests for the paired opposite-momentum cone."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_cone import (
    DEFAULT_OUTPUT,
    build_certificate,
)


class OppositeMomentumConeTest(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), build_certificate())

    def test_nonzero_standing_face(self) -> None:
        payload = build_certificate()
        self.assertTrue(payload["classification"]["nonzero_standing_wave_subcone_constructed"])
        self.assertEqual(payload["standing_wave_subcone"]["P_x"], "0 identically")

    def test_source_gate_remains_open(self) -> None:
        self.assertFalse(build_certificate()["classification"]["relative_phase_quadratic_source_classified"])


if __name__ == "__main__":
    unittest.main()
