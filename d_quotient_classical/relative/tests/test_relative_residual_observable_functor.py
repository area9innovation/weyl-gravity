"""Tests for the relative residual and observable functor."""

import unittest

from d_quotient_classical.relative import relative_residual_observable_functor as producer
from d_quotient_classical.relative.verify_relative_residual_observable_functor import verify


class RelativeResidualObservableFunctorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()

    def test_observable_pullback(self) -> None:
        producer.validate(self.value)
        self.assertTrue(self.value["classification"]["relative_observable_pullback_constructed"])
        self.assertTrue(self.value["classification"]["observable_pullback_is_chain_map"])
        self.assertTrue(self.value["classification"]["H_product_equivariance_exact"])

    def test_detectors_are_reduced_mode_only(self) -> None:
        self.assertTrue(self.value["classification"]["detectors_annihilate_einstein_image"])
        self.assertTrue(self.value["classification"]["detectors_separate_certified_extra_cofibers"])
        self.assertTrue(self.value["classification"]["reduced_mode_pullback_kernel_nonzero"])
        self.assertFalse(self.value["classification"]["full_SO42_equivariance_claimed"])
        self.assertFalse(self.value["classification"]["causal_green_relative_functor"])
        self.assertFalse(self.value["classification"]["Berger_cross_background_map"])

    def test_independent_replay(self) -> None:
        if producer.OUTPUT.exists():
            self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
