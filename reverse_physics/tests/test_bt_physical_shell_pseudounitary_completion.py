"""Falsification tests for the BT physical-shell pseudo-unitarity theorem."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_physical_shell_pseudounitary_completion.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_physical_shell_pseudounitary_completion.py"
)


class PhysicalShellPseudounitaryCompletionTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT) as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_real_column_mutation(self):
        result = self.mutate(
            lambda value: value["exact_witness"]["per_pair_amplitude"]["sqrt3"].update(
                denominator=11
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_hard_amplitude_mutation(self):
        result = self.mutate(
            lambda value: value["response_ledger"][
                "forced_hard_amplitude_real_part"
            ].update(numerator=-2)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_pseudounitary_witness_mutation(self):
        result = self.mutate(
            lambda value: value["exact_witness"]["B_equals_A2_over_2"][0][
                "value"
            ]["rational"].update(numerator=0)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_object_conflation_mutation(self):
        result = self.mutate(
            lambda value: value["assumptions"].update(
                physical_operator="R_t P R_t^dagger"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_continuum_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                continuum_dressed_physical_S_matrix="CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_positivity_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                beyond_tree_positivity="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
