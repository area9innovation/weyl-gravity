"""Falsification tests for the BT full-map Eq. (19) charge dichotomy."""
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
    "REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eq19_spurion_squeeze_dichotomy_no_go.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eq19_spurion_squeeze_dichotomy_no_go.py"
)


class Eq19SpurionSqueezeDichotomyNoGoTests(unittest.TestCase):
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
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_charge_lock_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["full_map_factorization"].update(
                    locking_identity="q_S=+2q_K"
                )
            ).returncode,
            0,
        )

    def test_s_less_charge_sequence_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["homogeneous_charge_exhaustion"]["cases"][0].update(
                    order_lambda_full_charges=["-q_K", "-3q_K"]
                )
            ).returncode,
            0,
        )

    def test_s_less_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["homogeneous_charge_exhaustion"]["cases"][0].update(
                    rank_by_component=[0, 8, 4]
                )
            ).returncode,
            0,
        )

    def test_s_equal_conclusion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["homogeneous_charge_exhaustion"]["cases"][1].update(
                    conclusion="EQ19_SATISFIED"
                )
            ).returncode,
            0,
        )

    def test_s_greater_positive_support_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["homogeneous_charge_exhaustion"]["cases"][2].update(
                    free_full_charges=["0", "-q_S"]
                )
            ).returncode,
            0,
        )

    def test_pair_odd_norm_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_squeezed_n1_witness"].update(
                    pair_ghost_odd_relative_norm="0"
                )
            ).returncode,
            0,
        )

    def test_n1_odd_norm_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_squeezed_n1_witness"].update(
                    n1_tensor_ghost_odd_relative_norm="-z^2"
                )
            ).returncode,
            0,
        )

    def test_fixture_norm_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_squeezed_n1_witness"].update(
                    physical_fixture_n1_odd_norm="0"
                )
            ).returncode,
            0,
        )

    def test_ghost_support_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["exact_squeezed_n1_witness"][
                    "ghost_odd_rank_by_support"
                ].update({"2": 0})
            ).returncode,
            0,
        )

    def test_fixed_vacuum_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    fixed_vacuum_s_zero="EQ19_PROVED"
                )
            ).returncode,
            0,
        )

    def test_covariant_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    covariant_orbit_s_one="EQ19_PROVED"
                )
            ).returncode,
            0,
        )

    def test_enlarged_no_go_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    nonhomogeneous_or_enlarged_charge_architecture="REFUTED"
                )
            ).returncode,
            0,
        )

    def test_non_fock_no_go_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    continuum_or_non_Fock_Eq19="REFUTED"
                )
            ).returncode,
            0,
        )

    def test_predecessor_scope_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["predecessor_scope"].update(
                    disposition="UNCHANGED_FULL_MAP_PROOF"
                )
            ).returncode,
            0,
        )

    def test_physical_probability_promotion_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    selected_q6_physical_probability="PROVES_GENERAL_EQ19"
                )
            ).returncode,
            0,
        )

    def test_scope_boundary_removal_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64

        self.assertNotEqual(self.mutate(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
