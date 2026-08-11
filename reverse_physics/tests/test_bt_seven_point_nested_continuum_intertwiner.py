"""Falsification tests for the seven-point nested continuum intertwiner."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_seven_point_nested_continuum_intertwiner.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_seven_point_nested_continuum_intertwiner.py"
)


class SevenPointNestedContinuumIntertwinerTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command(
                [sys.executable, VERIFIER, "--verify", handle.name]
            )

    def test_producer_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_primitive_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_cumulative_resolution"].update(
                    primitive_F=value["physical_cumulative_resolution"]
                    ["primitive_F"].replace("log(w)", "2*log(w)")
                )
            ).returncode,
            0,
        )

    def test_density_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_cumulative_resolution"].update(
                    density="2*(w-1)/w"
                )
            ).returncode,
            0,
        )

    def test_quotient_H_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["seven_point_positive_quotient_range"].update(
                    H="2+alpha/w"
                )
            ).returncode,
            0,
        )

    def test_isometry_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["conditional_direct_integral_isometry"].update(
                    identity="NOT_CHECKED"
                )
            ).returncode,
            0,
        )

    def test_edge_mark_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["ordered_three_noise_intertwiner"]
                ["edge_marks"].__setitem__(0, 14)
            ).returncode,
            0,
        )

    def test_third_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_and_channel_affiliation"]
                ["conditional_third_rate_q2"].update(denominator=401)
            ).returncode,
            0,
        )

    def test_aggregate_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_and_channel_affiliation"]
                ["aggregate_three_count_coefficient"].update(numerator=8)
            ).returncode,
            0,
        )

    def test_hierarchy_domain_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_hierarchy_dense_domain"].update(
                    endpoint_limits="bounded"
                )
            ).returncode,
            0,
        )

    def test_mark_completion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["seventy_five_mark_completion"]
                ["physically_intertwined_edge_marks"].pop()
            ).returncode,
            0,
        )

    def test_all_order_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    all_order_inductive_intertwiner="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_fourth_jump_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    fourth_jump="COMPUTED"
                )
            ).returncode,
            0,
        )

    def test_probability_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    complete_BT_probability="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_spacetime_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    spacetime_Moller_LSZ_S_operator="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_public_rt_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    public_Rt_identification="ESTABLISHED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
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
