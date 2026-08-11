import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics", "bt_extended_squeeze_carrier.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics", "verify_bt_extended_squeeze_carrier.py"
)


class ExtendedSqueezeCarrierTests(unittest.TestCase):
    def run_command(self, command):
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            payload = json.load(handle)
        mutation(payload)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(payload, handle)
            handle.flush()
            return self.run_command(
                [sys.executable, VERIFIER, "--verify", handle.name]
            )

    def test_producer(self):
        self.assertEqual(
            self.run_command([sys.executable, PRODUCER, "--check"]).returncode,
            0,
        )

    def test_verifier(self):
        self.assertEqual(
            self.run_command([sys.executable, VERIFIER]).returncode,
            0,
        )

    def test_pair_amplitude_mutation(self):
        result = self.mutate(
            lambda payload: payload["full_pair_exponential"]
            ["unordered_creation_coefficient"].update(denominator=8)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_contraction_threshold_mutation(self):
        result = self.mutate(
            lambda payload: payload["ordinary_topology_obstruction"].update(
                contraction_failure_threshold="never"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_weighted_density_mutation(self):
        result = self.mutate(
            lambda payload: payload["explicit_weighted_candidate"]
            ["density_coefficient_times_pi_inverse"].update(denominator=8)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_positive_Bogoliubov_mutation(self):
        result = self.mutate(
            lambda payload: payload["positive_adjoint_audit"]
            ["raw_positive_Bogoliubov_fixture"]
            ["u_squared_minus_v_squared"].update(numerator=1, denominator=1)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_import_boundary_mutation(self):
        result = self.mutate(
            lambda payload: payload["extended_implementation_import_gate"].update(
                import_disposition="THEOREM_APPLIES_VERBATIM"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_trace_claim_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                positive_cyclic_generalized_Born_trace="CONSTRUCTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
