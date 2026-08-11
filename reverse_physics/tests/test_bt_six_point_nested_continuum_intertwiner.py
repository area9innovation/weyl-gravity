"""Falsification tests for the six-point nested continuum intertwiner."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_six_point_nested_continuum_intertwiner.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_six_point_nested_continuum_intertwiner.py"
)


class SixPointNestedContinuumIntertwinerTests(unittest.TestCase):
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
                    primitive_F_m=value["physical_cumulative_resolution"]
                    ["primitive_F_m"].replace("- log(z)", "+ log(z)")
                )
            ).returncode,
            0,
        )

    def test_density_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["physical_cumulative_resolution"].update(
                    definition="d sigma_r=2*dmu_r"
                )
            ).returncode,
            0,
        )

    def test_quotient_range_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["six_point_positive_quotient_range"].update(
                    v="a2"
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
                lambda value: value["ordered_two_noise_intertwiner"]
                ["edge_marks"].__setitem__(0, 2)
            ).returncode,
            0,
        )

    def test_second_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_and_channel_affiliation"]
                ["conditional_second_rate_q1"].update(denominator=63)
            ).returncode,
            0,
        )

    def test_aggregate_rate_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["rate_and_channel_affiliation"]
                ["aggregate_two_count_coefficient"].update(numerator=4)
            ).returncode,
            0,
        )

    def test_hierarchy_domain_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["finite_hierarchy_dense_domain"].update(
                    upper_endpoint="bounded"
                )
            ).returncode,
            0,
        )

    def test_endpoint_derivative_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    strong_massless_endpoint_derivative="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_remaining_edges_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    remaining_sixty_edge_continuum_affiliation="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_full_75_promotion_mutation(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    full_seventy_five_mark_physical_intertwiner="CONSTRUCTED"
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
                    sha256="0"*64
                )
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
