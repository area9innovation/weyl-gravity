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
        self.assertEqual(differential.dense_rows(), ((1, 0, -1),))
        self.assertFalse(complex_.total_differential(2).compose(differential).entries)

    def test_exact_quotient_detects_one_isolated_class(self) -> None:
        result = certification_bicomplex().cohomology(1)
        self.assertEqual(result["ansatz_dimension"], 3)
        self.assertEqual(result["cocycle_dimension"], 2)
        self.assertEqual(result["coboundary_matrix_rank"], 1)
        self.assertEqual(result["quotient_dimension"], 1)
        self.assertEqual(len(result["proof_hash"]), 64)

    def test_noncommuting_square_fails_closed(self) -> None:
        complex_ = certification_bicomplex()
        bad_d = dict(complex_.d_maps)
        bad_d[Bidegree(1, 0)] = SparseMatrix.from_dense(((2,),))
        bad = FiniteBicomplex(complex_.spaces, complex_.q_maps, bad_d)
        with self.assertRaisesRegex(ValueError, "do not commute"):
            bad.verify_bicomplex()

    def test_matrix_shape_and_float_free_exactness(self) -> None:
        matrix = SparseMatrix.from_dense(((1, 2), (0, 3)))
        self.assertEqual(matrix.apply((1, -1)), (-1, -3))
        self.assertEqual(matrix.canonical_payload()["entries"][0]["coefficient"], {"numerator": 1, "denominator": 1})
        with self.assertRaisesRegex(ValueError, "ragged"):
            SparseMatrix.from_dense(((1,), (1, 2)))


if __name__ == "__main__":
    unittest.main()
