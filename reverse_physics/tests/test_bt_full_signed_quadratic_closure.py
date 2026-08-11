import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_full_signed_quadratic_closure.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_full_signed_quadratic_closure.py")


class FullSignedQuadraticClosureTests(unittest.TestCase):
    def command(self, arguments):
        return subprocess.run(arguments, cwd=ROOT, text=True, capture_output=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutation(payload)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_phase_mutation(self):
        result = self.mutate(lambda value: value["inverse_preimage_rule"]["all_contributions"][7]["total_phase"].__setitem__(0, 1))
        self.assertNotEqual(result.returncode, 0)

    def test_kernel_mutation(self):
        result = self.mutate(lambda value: value["completed_signed_kernel"]["exact_rows"][0]["terms"][0]["coefficient"]["real"].update(numerator=2))
        self.assertNotEqual(result.returncode, 0)

    def test_gram_mutation(self):
        result = self.mutate(lambda value: value["endpoint_cancellation"]["complete_parent_gram"].update(G_OmegaUpsilon="-1/(2r^3)"))
        self.assertNotEqual(result.returncode, 0)

    def test_ward_mutation(self):
        result = self.mutate(lambda value: value["canonicality"]["exact_fixture_rows"][3]["CCR_defect"].update(numerator=1))
        self.assertNotEqual(result.returncode, 0)

    def test_eq19_promotion_mutation(self):
        result = self.mutate(lambda value: value["disposition"].update(continuum_all_order_Eq19="PROVED"))
        self.assertNotEqual(result.returncode, 0)

    def test_physical_one_over_48_mutation(self):
        result = self.mutate(lambda value: value["disposition"].update(physical_one_over_48="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)

    def test_physical_zero_mutation(self):
        result = self.mutate(lambda value: value["coefficient_disposition"].update(physical_zero="ESTABLISHED"))
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
