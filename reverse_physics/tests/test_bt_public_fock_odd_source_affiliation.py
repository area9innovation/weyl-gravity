"""Falsification tests for the BT public-Fock odd-source affiliation."""
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
    "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_public_fock_odd_source_affiliation.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_public_fock_odd_source_affiliation.py"
)


class PublicFockOddSourceAffiliationTests(unittest.TestCase):
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

    def test_public_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["public_neutral_degree_four_sector"]["gram"][0]
                .__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_public_parity_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["public_neutral_degree_four_sector"][
                    "ghost_parity"
                ][0].__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_inertia_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["public_neutral_degree_four_sector"].update(
                    inertia=[7, 2]
                )
            ).returncode,
            0,
        )

    def test_selected_column_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["public_neutral_degree_four_sector"][
                    "selected_normalized_columns"
                ][1].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_selected_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["public_neutral_degree_four_sector"][
                    "selected_gram"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_missing_leg_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["complement_to_public_symmetric_power"][
                    "missing_leg_C"
                ][0].__setitem__(1, "1")
            ).returncode,
            0,
        )

    def test_charge_basis_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["complement_to_public_symmetric_power"][
                    "complement_charge_basis_S"
                ][1].__setitem__(1, "819/4000")
            ).returncode,
            0,
        )

    def test_Sym4_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["complement_to_public_symmetric_power"][
                    "Sym4_C_in_charge_basis"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_forward_matrix_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["complement_to_public_symmetric_power"][
                    "selected_forward_matrix_U_to_W"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_inverse_matrix_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["complement_to_public_symmetric_power"][
                    "selected_inverse_matrix_W_to_U"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_graph_source_metric_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["graph_source_realization"][
                    "public_selected_metric"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_graph_slope_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["graph_source_realization"]["graph_slope_T"][0]
                .__setitem__(0, "sqrt(6699)/8")
            ).returncode,
            0,
        )

    def test_graph_slope_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["graph_source_realization"].update(
                    graph_slope_status="DERIVED_BY_SYM4_C"
                )
            ).returncode,
            0,
        )

    def test_scalar_source_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["graph_source_realization"].update(
                    original_scalar_positive_source_status="AFFILIATED"
                )
            ).returncode,
            0,
        )

    def test_Rt_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    graph_slope_from_public_Rt="DERIVED"
                )
            ).returncode,
            0,
        )

    def test_Eq19_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
            ).returncode,
            0,
        )

    def test_physical_probability_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    physical_fourth_probability="ESTABLISHED"
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
