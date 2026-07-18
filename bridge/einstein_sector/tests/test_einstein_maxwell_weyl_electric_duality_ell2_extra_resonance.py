"""Tests for electric-duality mixed removability."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_electric_duality_ell2_extra_resonance import DEFAULT_OUTPUT


class ElectricDualityResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_duality_covariance(self) -> None:
        self.assertTrue(self.payload["classification"]["Maxwell_equations_duality_covariant"])
        self.assertTrue(self.payload["classification"]["Maxwell_stress_duality_invariant"])

    def test_mixed_source_removable(self) -> None:
        self.assertTrue(self.payload["classification"]["electric_Qe_times_ell2_extra_source_in_linear_image"])

    def test_fixed_bundle_boundary(self) -> None:
        self.assertTrue(self.payload["classification"]["mixed_correction_fixed_bundle_admissible"])
        self.assertFalse(self.payload["classification"]["all_orders_fixed_bundle_duality_orbit"])


if __name__ == "__main__":
    unittest.main()
