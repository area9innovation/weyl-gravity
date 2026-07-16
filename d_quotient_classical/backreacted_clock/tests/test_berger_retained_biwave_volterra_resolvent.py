import unittest

from d_quotient_classical.backreacted_clock.berger_retained_biwave_volterra_resolvent import build, verify


class BergerRetainedBiwaveVolterraResolventTest(unittest.TestCase):
    def test_metric_causal_resolvent_and_boundary(self):
        payload = build()
        verify(payload)
        self.assertTrue(payload["flags"]["BERGER_RETAINED_METRIC_GREEN_OPERATORS"])
        self.assertFalse(payload["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])
        self.assertFalse(payload["zero_mode_policy"]["spatial_mode_projector"])


if __name__ == "__main__":
    unittest.main()
