"""Falsification tests for the BT neutral graph projector extension."""
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
    "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_neutral_graph_projector_extension.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_neutral_graph_projector_extension.py"
)


class NeutralGraphProjectorExtensionTests(unittest.TestCase):
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

    def test_odd_metric_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_odd_source_extension"][
                    "odd_partner_metric"
                ][0].__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_target_metric_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_odd_source_extension"][
                    "composite_negative_metric"
                ][0].__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_slope_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_odd_source_extension"]["slope_T"][0]
                .__setitem__(0, "sqrt(6699)/8")
            ).returncode,
            0,
        )

    def test_pullback_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_odd_source_extension"][
                    "slope_covariant_pullback"
                ][0].__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_partner_dimension_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["minimal_odd_source_extension"].update(
                    partner_dimension=1
                )
            ).returncode,
            0,
        )

    def test_graph_embedding_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"][
                    "graph_embedding_L"
                ][0].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_M_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"]["positive_M"][0]
                .__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_range_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"]["range_gram"][0]
                .__setitem__(0, "6827/128")
            ).returncode,
            0,
        )

    def test_projector_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"]["projector"][0]
                .__setitem__(0, "1")
            ).returncode,
            0,
        )

    def test_projector_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"].update(rank=3)
            ).returncode,
            0,
        )

    def test_Born_trace_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"].update(
                    finite_algebraic_generalized_Born_trace=1
                )
            ).returncode,
            0,
        )

    def test_kernel_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["neutral_graph_projector"]["kernel_embedding"][0]
                .__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_affiliation_rank_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_source_affiliation"].update(
                    coefficient_rank=3
                )
            ).returncode,
            0,
        )

    def test_affiliation_solution_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_source_affiliation"].update(
                    only_solution="F=I2"
                )
            ).returncode,
            0,
        )

    def test_affiliation_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["positive_source_affiliation"].update(
                    norm_preserving_positive_source_map="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_Rt_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    BT_Rt_derivation="CONSTRUCTED"
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
