"""Falsification tests for the crossed Wightman-dual no-go."""
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
    "REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_wightman_dual_no_go.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_wightman_dual_no_go.py"
)


class CrossedWightmanDualNoGoTests(unittest.TestCase):
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

    def assert_rejected(self, mutation):
        result = self.mutate(mutation)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_producer_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_reflection_matrix_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["spectral_reflection_crosswalk"]
            ["reflection_matrix"][1].__setitem__(1, "-1")
        )

    def test_jet_metric_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["spectral_reflection_crosswalk"]
            ["jet_metric"][0].__setitem__(1, "-1")
        )

    def test_jacobian_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["spectral_reflection_crosswalk"].update(
                jacobian_boundary="An oriented minus sign is used."
            )
        )

    def test_distributional_scope_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["spectral_reflection_crosswalk"].update(
                domain_boundary="Complete interacting LSZ state constructed."
            )
        )

    def test_qx_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"].update(q_x="1")
        )

    def test_ellx_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"].update(ell_x="1")
        )

    def test_crossed_T_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"]
            ["T_cross"][0].__setitem__(0, value["crossed_five_to_four_operator"]["q_x"])
        )

    def test_crossed_sharp_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"]
            ["T_cross_sharp"][0].__setitem__(0, "0")
        )

    def test_signed_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"]
            ["signed_physical_gram"][0].__setitem__(0, "0")
        )

    def test_external_derivative_sign_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["crossed_five_to_four_operator"].update(
                fifth_external_delta_prime_sign=1
            )
        )

    def test_internal_parity_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["universal_parity_incompatibility"]
            ["required_six_point_parity"][1].__setitem__(1, "1")
        )

    def test_parity_dressed_T_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["universal_parity_incompatibility"]
            ["parity_dressed_T"][1].__setitem__(1, "0")
        )

    def test_parity_signed_gram_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["universal_parity_incompatibility"]
            ["fifth_signed_parity_gram"][0].__setitem__(0, "0")
        )

    def test_history_count_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["history_disposition"].update(
                reversed_six_point_history_count=11
            )
        )

    def test_profile_selective_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                profile_selective_or_higher_composite_parity="DERIVED"
            )
        )

    def test_nonfactorizing_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(
                nonfactorizing_crossed_six_point_term="COMPUTED"
            )
        )

    def test_eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assert_rejected(lambda value: value.update(does_not_establish=[]))

    def test_input_hash_mutation_rejected(self):
        self.assert_rejected(
            lambda value: value["provenance"]["inputs"][0].update(
                sha256="0" * 64
            )
        )


if __name__ == "__main__":
    unittest.main()
