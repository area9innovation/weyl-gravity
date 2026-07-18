"""Tests for the exceptional ell=1 static nonzero-momentum target."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell1_nonzero_static import DEFAULT_OUTPUT, build_certificate


class Ell1NonzeroStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_direct_not_lambda_continuation(self) -> None:
        self.assertFalse(self.payload["direct_replay"]["generic_lambda_continuation_used_as_proof"])

    def test_both_parities_exact_modulo_gauge(self) -> None:
        consequence = self.payload["static_consequence"]
        self.assertTrue(consequence["axial_kernel_equals_residual_gauge"])
        self.assertTrue(consequence["polar_kernel_equals_residual_gauge"])
        self.assertTrue(consequence["every_Noether_compatible_static_L1_source_is_removable"])

    def test_nonzero_fourier_shells_exposed(self) -> None:
        self.assertEqual(
            self.payload["nonzero_Fourier_consequence"]["reduced_shells"],
            ["omega^2-kappa^2=4", "omega^2-kappa^2=4/3"],
        )


if __name__ == "__main__":
    unittest.main()
