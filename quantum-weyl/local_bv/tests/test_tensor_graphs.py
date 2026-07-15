import unittest

from local_bv.basis_exhaustiveness import coarse_top_form_signatures
from local_bv.tensor_graphs import contraction_graph_manifest


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

    def test_seedless_tensor_derivatives_are_rejected(self) -> None:
        seedless = coarse_top_form_signatures(0, "even")[0]
        result = contraction_graph_manifest(seedless)
        self.assertEqual(
            result["tensor_realizability"],
            "NOT_REALIZABLE_AFTER_REFINED_GRADING",
        )
        self.assertEqual(result["raw_contraction_graph_count"], 0)


if __name__ == "__main__":
    unittest.main()
