from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest

from reverse_physics import bt_euclidean_tropical_flow_transport as producer


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_euclidean_tropical_flow_transport.py"
)


class TropicalFlowTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = producer.build()

    def verify(self, certificate: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(certificate, handle)
            path = handle.name
        try:
            return subprocess.run(
                ["python3", VERIFIER, "--certificate", path],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            os.unlink(path)

    def test_certificate_self_check(self) -> None:
        self.assertTrue(self.certificate["checks"]["ok"])
        self.assertEqual(self.certificate["checks"]["passed"], 6)

    def test_every_fixture_satisfies_transport_bound(self) -> None:
        for row in self.certificate["exact_fixtures"]:
            self.assertGreaterEqual(
                row["divergence_l2_squared"] * row["diameter"],
                2 * row["flow_mass"],
            )
            self.assertEqual(row["path_edge_mass"], row["flow_mass"])

    def test_unmodified_certificate_passes_independent_verifier(self) -> None:
        result = self.verify(self.certificate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_weakened_declared_coefficient_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["theorem"]["coefficient_bound"] = (
            "(sum d_x^2)/(sum c_x^2)>=1/diam(G)"
        )
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_divergence_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][0]["flow_divergence"][0] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_path_mass_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_fixtures"][1]["path_decomposition"][0]["mass"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_h_minus_one_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["actual_interacting_h_minus_one"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_joint_uniformity_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["joint_L_dependent_uniform_remainder"] = (
            "PROVED"
        )
        self.assertNotEqual(self.verify(mutated).returncode, 0)


if __name__ == "__main__":
    unittest.main()
