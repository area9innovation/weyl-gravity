"""Regression tests for the asymptotic raw-flux obstruction."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.asymptotic_bach_raw_flux_corner_obstruction import (
    DEFAULT_OUTPUT,
    build_certificate,
)


class AsymptoticRawFluxObstructionTest(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), build_certificate())

    def test_raw_flux_dichotomy(self) -> None:
        algebra = build_certificate()["raw_flux_algebra"]
        self.assertEqual(algebra["p0_p0"]["verdict"], "GENERIC_LINEAR_CUT_DIVERGENCE")
        self.assertEqual(algebra["p1_p1"]["verdict"], "ZERO_RAW_NULL_INFINITY_FLUX")

    def test_charge_names_remain_distinct(self) -> None:
        charges = build_certificate()["generator_charge_disposition"]
        self.assertEqual(charges["P0"]["final_status"], "OPEN")
        self.assertEqual(charges["D_M"]["final_status"], "OPEN")
        self.assertEqual(charges["H_ESU"]["final_status"], "OBSTRUCTED")
        self.assertEqual(charges["D_rad"]["final_status"], "NO_CERTIFIED_MAP")

    def test_full_phase_space_is_not_promoted(self) -> None:
        flags = build_certificate()["classification"]
        self.assertFalse(flags["full_tensor_BV_BFV_phase_space_constructed"])
        self.assertFalse(flags["boundary_counterterm_constructed"])


if __name__ == "__main__":
    unittest.main()
