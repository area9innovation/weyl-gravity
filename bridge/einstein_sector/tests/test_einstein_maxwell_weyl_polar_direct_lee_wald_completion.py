from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_polar_direct_lee_wald_completion import (
    DEFAULT_OUTPUT,
    _direct_interpolation,
    _shell_pullback,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_direct_lee_wald_completion import (
    verify_payload,
)


class PolarDirectLeeWaldCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))

    def test_direct_producer_and_shell_pullback(self) -> None:
        current, audit, symbols = _direct_interpolation()
        self.assertEqual(audit["spectral_promotion"]["nodes"], [6, 12, 20])
        self.assertLessEqual(audit["spectral_promotion"]["maximum_degree"], 2)
        shell = _shell_pullback(current, symbols)
        self.assertEqual(shell["Einstein_extra_cross_block_remainder"], ["0", "0"])
        self.assertEqual(shell["extra_inertia"], [2, 0])
        self.assertEqual(shell["radical_dimension_extra"], 0)

    def test_generator_and_independent_verifier(self) -> None:
        verify_certificate()
        verify_payload(self.payload)

    def test_sign_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["direct_current"]["generic_direct_current_per_scalar_harmonic_norm"][0][1] = "0"
        with self.assertRaises(AssertionError):
            verify_payload(mutated, verify_files=False)

    def test_normalization_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["shell_pullback"]["normalization"] = "Omega_WM/(-2*i*omega_e*L*N_(ell,m))"
        with self.assertRaises(AssertionError):
            verify_payload(mutated, verify_files=False)

    def test_omitted_delta_nabla_C_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["delta_nabla_C"]["complete_delta_nabla_C_contribution"] = "0"
        with self.assertRaises(AssertionError):
            verify_payload(mutated, verify_files=False)


if __name__ == "__main__":
    unittest.main()
