"""Falsification tests for the finite physical BT Moller column."""
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
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_finite_physical_moller_column.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_finite_physical_moller_column.py"
)


class FinitePhysicalMollerColumnTests(unittest.TestCase):
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
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_probability_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_vacuum_moller_column"]
                ["sector_probabilities"].__setitem__(1, "exp(-a)")
            ).returncode,
            0,
        )

    def test_drift_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_vacuum_moller_column"]
                ["amplitude_drifts"].__setitem__(1, "1/32")
            ).returncode,
            0,
        )

    def test_edge_mark_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_vacuum_moller_column"]
                ["physical_edge_marks"].__setitem__(74, 73)
            ).returncode,
            0,
        )

    def test_hard_response_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_model_inclusive_response"]
                ["hard_absolute_response"].update(numerator=-2)
            ).returncode,
            0,
        )

    def test_public_leg_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_public_Rt_compression"]
                ["public_leg_D"][0].__setitem__(1, "2")
            ).returncode,
            0,
        )

    def test_missing_leg_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_public_Rt_compression"]
                ["missing_leg_C"][0].__setitem__(1, "-2")
            ).returncode,
            0,
        )

    def test_bridge_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_public_Rt_compression"]
                ["bridge_W"][0].__setitem__(1, "1/L")
            ).returncode,
            0,
        )

    def test_positive_auxiliary_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_public_Rt_compression"].update(
                    positive_auxiliary_obstruction=(
                        "A positive Hilbert auxiliary realizes the exact required "
                        "complement without changing any physical input or trace."
                    )
                )
            ).returncode,
            0,
        )

    def test_dynamic_complement_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    missing_public_Rt_complement="DERIVED_FROM_BT_DYNAMICS"
                )
            ).returncode,
            0,
        )

    def test_two_sided_s_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    full_two_sided_physical_S_operator="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_complete_probability_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    complete_BT_probability="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["typed_Eq19_boundary"].update(
                    Eq19_all_orders="PROVED"
                )
            ).returncode,
            0,
        )

    def test_lorentzian_boundary_mutation(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation(self):
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
