from copy import deepcopy
import unittest

from d_quotient_classical.relative.relative_residual_observable_functor_preflight import build, verify


class RelativeFunctorPreflightTest(unittest.TestCase):
    def test_exact_preflight(self):
        payload = build()
        self.assertTrue(payload["flags"]["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"])
        self.assertFalse(payload["flags"]["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"])
        self.assertTrue(payload["flags"]["EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED"])
        self.assertTrue(payload["flags"]["RESIDUAL_EQUIVARIANCE_CERTIFIED"])
        self.assertTrue(payload["flags"]["COFIBER_COMPATIBILITY_CERTIFIED"])
        self.assertFalse(payload["flags"]["OBSERVABLE_PULLBACK_CONSTRUCTED"])
        self.assertEqual(payload["shared_relative_row"]["relative_pairing"], "NONCYCLIC_THREE_ACTION_FORMS_IMPORTED")

    def test_rejects_premature_promotion(self):
        payload = build()
        payload = deepcopy(payload)
        payload["flags"]["OBSERVABLE_PULLBACK_CONSTRUCTED"] = True
        with self.assertRaises(AssertionError):
            verify(payload)


if __name__ == "__main__":
    unittest.main()
