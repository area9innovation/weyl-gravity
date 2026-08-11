"""Falsification tests for the BT fourth-profile positivity obstruction."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eight_point_profile_positivity_obstruction.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_profile_positivity_obstruction.py"
)


class EightPointProfilePositivityObstructionTests(unittest.TestCase):
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

    def test_producer_fast_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_profile_coefficient_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["orientation_audit"]["profile_coefficients"][0]
                .update(numerator=-6698)
            ).returncode,
            0,
        )

    def test_external_sign_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["orientation_audit"].update(
                    eight_external_delta_prime_sign=-1
                )
            ).returncode,
            0,
        )

    def test_lower_chain_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["orientation_audit"][
                    "lower_selected_history_chain"
                ].update(numerator=10)
            ).returncode,
            0,
        )

    def test_normalization_orientation_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["orientation_audit"][
                    "remaining_normalization_signs"
                ].update(squared_amplitude_phase_sign=-1)
            ).returncode,
            0,
        )

    def test_effect_matrix_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_profile_test"]["effect_matrix"][0]
                .__setitem__(0, "-6698/128")
            ).returncode,
            0,
        )

    def test_effect_inertia_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_profile_test"]["effect_inertia"]
                .update(positive=1, negative=1)
            ).returncode,
            0,
        )

    def test_convex_interval_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_profile_test"][
                    "closed_weight_interval"
                ][1].update(numerator=-6698)
            ).returncode,
            0,
        )

    def test_cp_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_profile_test"].update(
                    ordinary_CP_or_HP_jump="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_rho_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"]["rho"].update(
                    numerator=820
                )
            ).returncode,
            0,
        )

    def test_single_fibre_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"]["single_fibre_gram"][1]
                .__setitem__(1, "-3")
            ).returncode,
            0,
        )

    def test_forward_block_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"]["forward_block_B"][1]
                .__setitem__(0, "sqrt(6698)/16")
            ).returncode,
            0,
        )

    def test_pullback_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"]["pullback"][1]
                .__setitem__(1, "-7148/128")
            ).returncode,
            0,
        )

    def test_module_inertia_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"][
                    "two_point_module_inertia"
                ].update(positive=3, negative=1)
            ).returncode,
            0,
        )

    def test_dynamic_lift_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["fibrewise_krein_lift"].update(
                    status="BT_DERIVED"
                )
            ).returncode,
            0,
        )

    def test_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_fourth_probability="ESTABLISHED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
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
