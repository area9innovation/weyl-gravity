import unittest

from local_bv.filtered_complex import (
    LIFT_COMPARISON_STATUSES,
    FilteredDegree,
    FilteredLocalComplex,
)
from local_bv.relative_cohomology import SparseMatrix


class FilteredComplexTests(unittest.TestCase):
    def test_afn0_view_and_component_names(self) -> None:
        x = FilteredDegree(0, 0, 0)
        qx = FilteredDegree(0, 1, 0)
        complex_ = FilteredLocalComplex(
            {x: ("x",), qx: ("qx",)},
            {(x, 0): SparseMatrix.from_dense(((1,),))},
            {},
        )
        self.assertEqual(complex_.component_name(-1), "delta")
        self.assertEqual(complex_.component_name(0), "gamma")
        self.assertEqual(complex_.component_name(2), "Q_gt0[2]")
        self.assertEqual(
            complex_.afn0_view().verify_bicomplex()["Q_squared_zero"], "VERIFIED"
        )
        self.assertEqual(len(LIFT_COMPARISON_STATUSES), 4)

    def test_forbidden_shift_and_shape_fail_closed(self) -> None:
        x = FilteredDegree(0, 0, 0)
        with self.assertRaisesRegex(ValueError, "below delta"):
            FilteredLocalComplex(
                {x: ("x",)}, {(x, -2): SparseMatrix.zero(0, 1)}, {}
            )
        with self.assertRaisesRegex(ValueError, "shape"):
            FilteredLocalComplex(
                {x: ("x",)}, {(x, 0): SparseMatrix.from_dense(((1,),))}, {}
            )


if __name__ == "__main__":
    unittest.main()
