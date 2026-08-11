"""Falsification tests for the BT logarithmic-shell Moller-limit theorem."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_log_shell_moller_limit.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_log_shell_moller_limit.py")


class LogShellMollerLimitTests(unittest.TestCase):
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

    def test_shell_overlap_mutation(self):
        result = self.mutate(
            lambda value: value["continuum_model"]["shell_fixtures"][1][
                "y_interval_in_units_of_ell"
            ][0].update(numerator=0)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_distance_mutation(self):
        result = self.mutate(
            lambda value: value["strong_limit_obstruction"][
                "distinct_shell_column_distance_square"
            ].update(denominator=16)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_false_strong_limit_mutation(self):
        result = self.mutate(
            lambda value: value["strong_limit_obstruction"].update(
                disposition="STRONG_LIMIT_EXISTS"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_weak_unitarity_mutation(self):
        result = self.mutate(
            lambda value: value["weak_limit"].update(disposition="UNITARY")
        )
        self.assertNotEqual(result.returncode, 0)

    def test_bundle_response_mutation(self):
        result = self.mutate(
            lambda value: value["dressed_boundary_bundle"][
                "hard_survival_response"
            ].update(numerator=0)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_local_affiliation_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                local_LSZ_or_AQFT_affiliation="ESTABLISHED"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_full_S_promotion_mutation(self):
        result = self.mutate(
            lambda value: value["disposition"].update(
                full_dynamical_dressed_S_matrix="CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
