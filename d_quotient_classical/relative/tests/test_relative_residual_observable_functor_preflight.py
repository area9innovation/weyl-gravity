from copy import deepcopy
import unittest

from d_quotient_classical.relative.relative_residual_observable_functor_preflight import build, verify


class RelativeFunctorPreflightTest(unittest.TestCase):
    def test_exact_preflight(self):
        payload = build()
        self.assertTrue(payload["flags"]["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"])
        self.assertFalse(payload["flags"]["RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"])

    def test_rejects_premature_promotion(self):
        payload = build()
        payload = deepcopy(payload)
        payload["flags"]["OBSERVABLE_PULLBACK_CONSTRUCTED"] = True
        with self.assertRaises(AssertionError):
            verify(payload)


if __name__ == "__main__":
    unittest.main()
