"""Falsification tests for the crossed six-point pre-trace no-go."""
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
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_crossed_six_point_nonfactorizing_pretrace_no_go.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_crossed_six_point_nonfactorizing_pretrace_no_go.py"
)
TEMP_ROOT = os.path.join(ROOT, "reverse_physics/.tmp_crossed_pretrace_tests")
os.makedirs(TEMP_ROOT, exist_ok=True)


class CrossedSixPointNonfactorizingPretraceNoGoTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", dir=TEMP_ROOT
        ) as handle:
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

    def test_mask_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_pretrace_rows"].update(spectator_masks=[0, 1])
        )

    def test_singleton_row_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_pretrace_rows"].update(singleton_row="0")
        )

    def test_pair_row_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_pretrace_rows"].update(pair_row="0")
        )

    def test_cubic_row_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_pretrace_rows"].update(cubic_row="1")
        )

    def test_fixture_component_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_pretrace_rows"]["three_hard_fixture_rows"][1]
            ["leading_components"].__setitem__("1", "0")
        )

    def test_profile_matrix_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_factorization"]["outer_profile_matrix"][0].__setitem__(0, "0")
        )

    def test_u_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_factorization"].update(u_e="0")
        )

    def test_v_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_factorization"].update(v_e="0")
        )

    def test_residual_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["exact_factorization"].update(nonfactorizing_residual=["1", "0"])
        )

    def test_u_cross_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_hierarchy_crossing"].update(u_cross="1")
        )

    def test_v_cross_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_hierarchy_crossing"].update(v_cross="-1")
        )

    def test_crossed_D_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_hierarchy_crossing"]["crossed_D"][0].__setitem__(0, "0")
        )

    def test_raised_pullback_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_hierarchy_crossing"]["raised_pullback"][0].__setitem__(0, "0")
        )

    def test_characteristic_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["finite_hierarchy_crossing"].update(characteristic_polynomial="z**4")
        )

    def test_full_phase_space_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["physical_disposition"].update(
                complete_noncorrelated_crossed_three_to_three_phase_space="COMPUTED"
            )
        )

    def test_history_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["physical_disposition"].update(
                first_twelve_reversed_histories_on_available_cylinder="AFFILIATED"
            )
        )

    def test_eq19_promotion_rejected(self):
        self.assert_rejected(
            lambda v: v["physical_disposition"].update(Eq19_all_orders="PROVED")
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assert_rejected(lambda v: v.update(does_not_establish=[]))

    def test_input_hash_mutation_rejected(self):
        self.assert_rejected(
            lambda v: v["provenance"]["inputs"][0].update(sha256="0" * 64)
        )


if __name__ == "__main__":
    unittest.main()
