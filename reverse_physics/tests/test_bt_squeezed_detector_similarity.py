import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_squeezed_detector_similarity.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_squeezed_detector_similarity.py")


class SqueezedDetectorSimilarityTests(unittest.TestCase):
    def command(self, args):
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle: value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle); handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self): self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)
    def test_verifier(self): self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)
    def test_trace_mutation(self): self.assertNotEqual(self.mutate(lambda x: x["signed_kernel_similarity_fixtures"][0]["transformed_parent_trace"].update(numerator=1)).returncode, 0)
    def test_projector_mutation(self): self.assertNotEqual(self.mutate(lambda x: x["finite_projector_similarity_fixture"]["transported_projector"][0][0].update(numerator=7)).returncode, 0)
    def test_bare_detector_mutation(self): self.assertNotEqual(self.mutate(lambda x: x["bare_detector_mismatch"]["fixture_probability"].update(numerator=1)).returncode, 0)
    def test_physical_zero_mutation(self): self.assertNotEqual(self.mutate(lambda x: x["coefficient_disposition"].update(physical_zero="ESTABLISHED")).returncode, 0)
    def test_continuum_promotion_mutation(self): self.assertNotEqual(self.mutate(lambda x: x["disposition"].update(continuum_Eq19="PROVED")).returncode, 0)


if __name__ == "__main__": unittest.main()
