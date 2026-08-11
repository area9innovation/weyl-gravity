"""Falsification tests for the BT quantum-stochastic Moller dilation."""
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
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_quantum_stochastic_moller_dilation.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_quantum_stochastic_moller_dilation.py"
)


class QuantumStochasticMollerDilationTests(unittest.TestCase):
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
        self.assertEqual(self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_noise_multiplicity_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["system_and_noise_carrier"].update(noise_multiplicity=74)).returncode,
            0,
        )

    def test_channel_hash_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["system_and_noise_carrier"].update(noise_channel_sha256="0" * 64)).returncode,
            0,
        )

    def test_kraus_rank_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["minimal_kraus_theorem"].update(rank=74)).returncode,
            0,
        )

    def test_drift_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["hudson_parthasarathy_cocycle"]["drift_eigenvalues_by_level"].__setitem__(1, "5/31")).returncode,
            0,
        )

    def test_isometry_identity_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["hudson_parthasarathy_cocycle"].update(isometry_identity="NOT_CHECKED")).returncode,
            0,
        )

    def test_coisometry_identity_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["hudson_parthasarathy_cocycle"].update(coisometry_identity="NOT_CHECKED")).returncode,
            0,
        )

    def test_generator_hash_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["vacuum_reduction"].update(pinned_classical_generator_sha256="0" * 64)).returncode,
            0,
        )

    def test_third_amplitude_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["finite_jet_intertwiner"]["normalized_simplex_compressed_amplitudes"].__setitem__(2, "sqrt(30)/1279")).returncode,
            0,
        )

    def test_barrier_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(ordinary_additive_strong_generator="CONSTRUCTED")).returncode,
            0,
        )

    def test_physical_absorption_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(physical_level_three_absorption="PROVED")).returncode,
            0,
        )

    def test_fourth_jump_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(fourth_jump="COMPUTED")).returncode,
            0,
        )

    def test_complete_probability_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(complete_BT_probability="CONSTRUCTED")).returncode,
            0,
        )

    def test_spacetime_operator_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(spacetime_Moller_LSZ_S_operator="CONSTRUCTED")).returncode,
            0,
        )

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(Eq19_all_orders="PROVED")).returncode,
            0,
        )

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["provenance"]["inputs"][0].update(sha256="0" * 64)).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
