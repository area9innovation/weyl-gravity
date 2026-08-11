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
    "REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics", "bt_squeezed_vacuum_implementability.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics", "verify_bt_squeezed_vacuum_implementability.py"
)


class SqueezedVacuumImplementabilityTests(unittest.TestCase):
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

    def test_pair_power_mutation(self):
        result = self.mutate(
            lambda payload: payload["direct_vacuum_norm"].update(
                radial_integrand_power=0
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_wick_coefficient_mutation(self):
        result = self.mutate(
            lambda payload: payload["direct_vacuum_norm"]
            ["ordered_sum_coefficient"].update(denominator=16)
        )
        self.assertNotEqual(result.returncode, 0)

    def test_lowest_shell_mutation(self):
        result = self.mutate(
            lambda payload: payload["direct_vacuum_norm"]["lowest_shell"].update(
                ordered_momentum_count=8
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_inequivalent_topology_mutation(self):
        result = self.mutate(
            lambda payload: payload["topology_boundary"].update(
                why_not_a_repair_here="rho(p) removes the divergence in the same topology"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_nullity_mutation(self):
        result = self.mutate(
            lambda payload: payload["Krein_nullity_audit"].update(
                conclusion="KREIN_NULL_IMPLIES_NORMALIZABLE"
            )
        )
        self.assertNotEqual(result.returncode, 0)

    def test_claim_promotion_mutation(self):
        result = self.mutate(
            lambda payload: payload["disposition"].update(
                Eq19_in_extended_representation="REFUTED"
            )
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
