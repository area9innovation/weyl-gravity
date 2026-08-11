"""Falsification tests for the BT six-point strongly ordered tree result."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json")
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_six_point_strongly_ordered_tree.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_six_point_strongly_ordered_tree.py")


class SixPointStronglyOrderedTreeTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_tree_count_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["topology"].update(total=219)).returncode, 0)

    def test_kernel_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["correlated_boundary"]["rows"][0].update(projected="0")).returncode, 0)

    def test_raw_cocycle_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_and_factorial_analysis"]["double_cocycle"]["raw_nested_coefficient"].update(numerator=9)).returncode, 0)

    def test_physical_cutoff_boundary_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_and_factorial_analysis"]["inner_physical_cutoff_finite_part"].update(physical_cutoff_boundary_finite_part_identity=False)).returncode, 0)

    def test_history_count_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_and_factorial_analysis"]["normalization"].update(labeled_nested_histories=9)).returncode, 0)

    def test_poisson_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(coherent_Poisson_dynamics="AGREES")).returncode, 0)

    def test_cumulant_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["threshold_and_factorial_analysis"]["factorial_cumulant"]["second_factorial_cumulant_coefficient"].update(numerator=0)).returncode, 0)

    def test_full_probability_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(full_six_body_probability="CONSTRUCTED")).returncode, 0)

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["disposition"].update(Eq19_all_orders="PROVED")).returncode, 0)

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v.update(does_not_establish=[])).returncode, 0)

    def test_hard_angle_boundary_mutation(self):
        self.assertNotEqual(self.mutate(lambda v: v["does_not_establish"].remove("universal hard-angle independence beyond the three exact hard fixtures")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
