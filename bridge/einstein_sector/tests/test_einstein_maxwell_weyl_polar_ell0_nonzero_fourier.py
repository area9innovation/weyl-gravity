"""Tests for the exceptional polar ell=0 nonzero Fourier complex."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_polar_ell0_nonzero_fourier import DEFAULT_OUTPUT, build_certificate


class PolarEll0NonzeroFourierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_static_complex_exact_modulo_gauge(self) -> None:
        block = self.payload["static_nonzero_momentum"]
        self.assertEqual(block["operator_rank"] + block["gauge_rank"], 6)
        self.assertTrue(block["kernel_equals_Diff_Weyl_U1_image"])

    def test_all_nonzero_fourier_pairs_exact(self) -> None:
        block = self.payload["all_nonzero_fourier_pairs"]
        self.assertEqual(block["operator_rank"] + block["gauge_rank"], 6)
        self.assertTrue(block["cokernel_equals_adjoint_gauge_Noether_space"])

    def test_phase_source_removable(self) -> None:
        self.assertTrue(self.payload["phase_channel_consequence"]["therefore_source_is_in_operator_image"])
        self.assertTrue(self.payload["classification"]["static_phase_sensitive_source_removable_if_Noether_compatible"])

    def test_bounded_gate_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["bounded_resonant_projection_classified"])


if __name__ == "__main__":
    unittest.main()
