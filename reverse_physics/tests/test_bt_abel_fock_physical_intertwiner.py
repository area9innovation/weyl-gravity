"""Falsification tests for the BT physical Abel--Fock intertwiner."""
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
    "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_abel_fock_physical_intertwiner.py")
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_abel_fock_physical_intertwiner.py"
)


class AbelFockPhysicalIntertwinerTests(unittest.TestCase):
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

    def test_raw_gram_difference_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["raw_column_covariance_obstruction"]["fixtures"].update(difference="0")).returncode,
            0,
        )

    def test_raw_covariance_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(raw_fixed_regulator_column_translation="CONSTRUCTED")).returncode,
            0,
        )

    def test_polar_gram_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["physical_polar_ranges"].update(normalized_gram="E_R^sharp E_R=2*I2")).returncode,
            0,
        )

    def test_abel_isometry_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["abel_physical_range_intertwiner"].update(isometry="NOT_CONSTRUCTED")).returncode,
            0,
        )

    def test_translation_intertwiner_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["translation_intertwiner"].update(intertwining="NOT_CHECKED")).returncode,
            0,
        )

    def test_first_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["first_emission_hp_affiliation"]["physical_rate_per_pair"].update(denominator=47)).returncode,
            0,
        )

    def test_first_mark_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["first_emission_hp_affiliation"]["first_edge_noise_indices"].__setitem__(2, 3)).returncode,
            0,
        )

    def test_noise_only_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(noise_only_channel_faithful_intertwiner="CONSTRUCTED")).returncode,
            0,
        )

    def test_full_75_mark_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(full_seventy_five_mark_physical_intertwiner="CONSTRUCTED")).returncode,
            0,
        )

    def test_remaining_marks_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value["disposition"].update(remaining_seventy_two_edge_continuum_affiliation="CONSTRUCTED")).returncode,
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
