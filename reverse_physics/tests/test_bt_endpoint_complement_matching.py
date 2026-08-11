"""Falsification tests for the BT endpoint-complement matching theorem."""
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
    "REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_endpoint_complement_matching.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_endpoint_complement_matching.py"
)


class EndpointComplementMatchingTests(unittest.TestCase):
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

    def test_producer_check(self):
        result = self.command([sys.executable, PRODUCER, "--check"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_independent_verifier(self):
        result = self.command([sys.executable, VERIFIER])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_affine_reference_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["endpoint_extension"]
                ["reference_actions_on_product_probes"][2].update(
                    numerator=0, denominator=1
                )
            ).returncode,
            0,
        )

    def test_jet_matrix_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["endpoint_extension"]["jet_action_matrix"]
                [1][1].update(numerator=2)
            ).returncode,
            0,
        )

    def test_matching_intercept_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["matching_theorem"]["unique_coefficients"]
                .__setitem__(1, "c1=1+rho/2")
            ).returncode,
            0,
        )

    def test_matching_slope_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["matching_theorem"]
                ["coefficient_derivative_with_respect_to_rho"]
                .__setitem__(1, "1")
            ).returncode,
            0,
        )

    def test_fixture_rho_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_fixtures"][0]["rho"].update(
                    numerator=820
                )
            ).returncode,
            0,
        )

    def test_fixture_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_fixtures"][1]["coefficients"]
                [1].update(numerator=1, denominator=1)
            ).returncode,
            0,
        )

    def test_universal_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["matching_theorem"].update(
                    universal_status="ONE_FIXED_EXTENSION_MATCHES_ALL_PHYSICAL_RHOS"
                )
            ).returncode,
            0,
        )

    def test_pointwise_fit_promoted_to_dynamics_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    pointwise_endpoint_match="DERIVED_FROM_BT_DYNAMICS"
                )
            ).returncode,
            0,
        )

    def test_missing_complement_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    BT_derived_missing_complement="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    Eq19_all_orders="PROVED"
                )
            ).returncode,
            0,
        )

    def test_physical_s_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_two_sided_S_operator="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["provenance"]["inputs"][0].update(
                    sha256="0" * 64
                )
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
