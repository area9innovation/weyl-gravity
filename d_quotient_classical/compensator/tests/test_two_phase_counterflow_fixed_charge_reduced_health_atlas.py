import unittest

from d_quotient_classical.atlas import generate_two_phase_counterflow_fixed_charge_reduced_health_atlas_fragment as generator
from d_quotient_classical.atlas import verify_two_phase_counterflow_fixed_charge_reduced_health_atlas_fragment as verifier


class FixedChargeAtlasTests(unittest.TestCase):
    def test_fragment_is_current(self):
        generator.check()

    def test_independent_boundary(self):
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
