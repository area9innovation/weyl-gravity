import unittest

from d_quotient_classical.atlas import generate_two_phase_counterflow_background_component_round_atlas_fragment as atlas
from d_quotient_classical.atlas import verify_two_phase_counterflow_background_component_round_atlas_fragment as verifier


class ComponentAtlasTests(unittest.TestCase):
    def test_generated_fragment_is_current(self):
        atlas.check()

    def test_independent_verifier(self):
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
