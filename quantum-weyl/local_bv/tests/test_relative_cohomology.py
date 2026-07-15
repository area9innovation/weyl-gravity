import unittest

from local_bv.relative_cohomology import (
    Bidegree,
    FiniteBicomplex,
    SparseMatrix,
    certification_bicomplex,
)


class RelativeCohomologyTests(unittest.TestCase):
    def test_sparse_composition_and_totalization_sign(self) -> None:
        complex_ = certification_bicomplex()
        self.assertEqual(
            complex_.verify_bicomplex()["totalized_differential_squared_zero"],
            "VERIFIED",
        )
        differential = complex_.total_differential(1)
        self.assertEqual(differential.dense_rows(), ((1, 0, -1, 0),))
        self.assertFalse(complex_.total_differential(2).compose(differential).entries)

    def test_exact_quotient_detects_one_isolated_class(self) -> None:
        result = certification_bicomplex().cohomology(1)
        self.assertEqual(result["ansatz_dimension"], 4)
        self.assertEqual(result["cocycle_dimension"], 3)
        self.assertEqual(result["coboundary_matrix_rank"], 1)
        self.assertEqual(result["quotient_dimension"], 2)
        self.assertEqual(result["dual_witness_pairings"], [
            {"numerator": 1, "denominator": 1},
            {"numerator": 1, "denominator": 1},
        ])
        self.assertEqual(
            result["dual_witness_type"], "TRUNCATED_NONMEMBERSHIP_WITNESS"
        )
        self.assertEqual(len(result["proof_hash"]), 64)

    def test_anchored_relative_quotient_excludes_lower_only_class(self) -> None:
        result = certification_bicomplex().relative_cohomology(0, 1)
        self.assertEqual(result["top_ansatz_dimension"], 2)
        self.assertEqual(result["projected_top_cocycle_dimension"], 2)
        self.assertEqual(result["projected_top_coboundary_rank"], 1)
        self.assertEqual(result["quotient_dimension"], 1)
        self.assertEqual(result["lower_only_total_class_dimension"], 1)
        self.assertEqual(
            result["representative_coordinates"],
            [[{"numerator": 0, "denominator": 1}, {"numerator": 1, "denominator": 1}]],
        )
        self.assertEqual(
            result["dual_nontriviality_witness_coordinates"],
            [[{"numerator": 0, "denominator": 1}, {"numerator": 1, "denominator": 1}]],
        )
        self.assertEqual(result["dual_witness_pairings"], [
            {"numerator": 1, "denominator": 1}
        ])
        self.assertEqual(
            result["dual_witness_type"], "TRUNCATED_NONMEMBERSHIP_WITNESS"
        )
        self.assertEqual(result["closure_witnesses"][0]["residual_status"], "ZERO")

    def test_complete_witness_requires_explicit_exhaustiveness(self) -> None:
        result = certification_bicomplex().relative_cohomology(
            0, 1, basis_exhaustiveness_status="EXHAUSTIVE"
        )
        self.assertEqual(
            result["dual_witness_type"], "COMPLETE_NONTRIVIALITY_WITNESS"
        )
        with self.assertRaisesRegex(ValueError, "exhaustiveness"):
            certification_bicomplex().relative_cohomology(
                0, 1, basis_exhaustiveness_status="ASSUMED"
            )

    def test_lower_anchor_sees_the_lower_only_class(self) -> None:
        result = certification_bicomplex().relative_cohomology(1, 0)
        self.assertEqual(result["quotient_dimension"], 1)
        self.assertEqual(result["lower_only_total_class_dimension"], 0)

    def test_noncommuting_square_fails_closed(self) -> None:
        complex_ = certification_bicomplex()
        bad_d = dict(complex_.d_maps)
        bad_d[Bidegree(1, 0)] = SparseMatrix.from_dense(((2, 0),))
        bad = FiniteBicomplex(complex_.spaces, complex_.q_maps, bad_d)
        with self.assertRaisesRegex(ValueError, "do not commute"):
            bad.verify_bicomplex()

    def test_matrix_shape_and_float_free_exactness(self) -> None:
        matrix = SparseMatrix.from_dense(((1, 2), (0, 3)))
        self.assertEqual(matrix.apply((1, -1)), (-1, -3))
        self.assertEqual(matrix.canonical_payload()["entries"][0]["coefficient"], {"numerator": 1, "denominator": 1})
        with self.assertRaisesRegex(ValueError, "ragged"):
            SparseMatrix.from_dense(((1,), (1, 2)))

    def test_sparse_rank_and_nullspace_do_not_require_dense_rows(self) -> None:
        matrix = SparseMatrix.from_dense(((1, 2, 3), (0, 1, 1)))
        self.assertEqual(matrix.rank(), 2)
        self.assertEqual(matrix.nullspace(), ((-1, -1, 1),))
        self.assertEqual(
            SparseMatrix.zero(0, 2).nullspace(),
            ((1, 0), (0, 1)),
        )


if __name__ == "__main__":
    unittest.main()
