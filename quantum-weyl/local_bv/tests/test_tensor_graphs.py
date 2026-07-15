import unittest

from local_bv.basis_exhaustiveness import coarse_top_form_signatures
from local_bv.tensor_graphs import contraction_graph_artifact, contraction_graph_manifest


class TensorGraphTests(unittest.TestCase):
    def test_raw_even_and_odd_pairing_counts(self) -> None:
        even_c2 = coarse_top_form_signatures(0, "even")[-1]
        odd_c2 = coarse_top_form_signatures(0, "odd")[-1]
        self.assertEqual(
            contraction_graph_manifest(even_c2)["raw_contraction_graph_count"],
            105,
        )
        self.assertEqual(
            contraction_graph_manifest(odd_c2)["raw_contraction_graph_count"],
            210,
        )
        even_artifact = contraction_graph_artifact(even_c2)
        self.assertEqual(
            even_artifact["raw_generation"]["independent_combinatorial_count"],
            105,
        )
        self.assertEqual(
            even_artifact["symmetry_quotient"]["symmetry_canonical_orbit_count"],
            4,
        )

    def test_seedless_tensor_derivatives_are_rejected(self) -> None:
        seedless = coarse_top_form_signatures(0, "even")[0]
        result = contraction_graph_manifest(seedless)
        self.assertEqual(
            result["tensor_realizability"],
            "NOT_REALIZABLE_AFTER_REFINED_GRADING",
        )
        self.assertEqual(result["raw_contraction_graph_count"], 0)

    def test_slot_variance_and_graphwise_currents_are_explicit(self) -> None:
        odd_single_curvature = coarse_top_form_signatures(0, "odd")[1]
        artifact = contraction_graph_artifact(odd_single_curvature)
        derivative_slots = [
            slot for slot in artifact["slot_metadata"]
            if slot["slot_kind"] == "DERIVATIVE"
        ]
        self.assertEqual(
            [slot["derivative_order_position"] for slot in derivative_slots],
            [0, 1],
        )
        divergence = artifact["divergence_witness"]
        self.assertEqual(divergence["status"], "VERIFIED_EVERY_RAW_GRAPH")
        self.assertEqual(
            divergence["graphwise_current_count"],
            artifact["raw_generation"]["raw_contraction_graph_count"],
        )
        self.assertEqual(len(divergence["current_witnesses"]), 15)


if __name__ == "__main__":
    unittest.main()
