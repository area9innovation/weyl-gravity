from __future__ import annotations

import unittest
from fractions import Fraction

from cartan.defect_complex import (
    ExactMatrix,
    FiniteGradedComplex,
    FirstOrderCartanData,
    HomogeneousOperator,
    classify_closed_defect,
    graded_commutator,
)


def acyclic_data(*, iota_correction: bool) -> FirstOrderCartanData:
    q = HomogeneousOperator(
        "Q", 1, ExactMatrix.from_rows(((0, 0), (1, 0)))
    )
    complex_ = FiniteGradedComplex((0, 1), q)
    iota = HomogeneousOperator(
        "iota_D", -1, ExactMatrix.from_rows(((0, 1), (0, 0)))
    )
    return FirstOrderCartanData(
        complex=complex_,
        iota_0=iota,
        lie_0=HomogeneousOperator("L_D", 0, ExactMatrix.identity(2)),
        q_1=HomogeneousOperator("Q_1", 1, ExactMatrix.zero(2, 2)),
        iota_1=(
            iota
            if iota_correction
            else HomogeneousOperator("iota_1", -1, ExactMatrix.zero(2, 2))
        ),
        lie_1=HomogeneousOperator("L_D_1", 0, ExactMatrix.zero(2, 2)),
    )


class ExactCartanDefectTests(unittest.TestCase):
    def test_graded_commutator_has_cartan_plus_sign(self) -> None:
        data = acyclic_data(iota_correction=False)
        bracket = graded_commutator(data.complex.q, data.iota_0)
        self.assertEqual(bracket.degree, 0)
        self.assertEqual(bracket.matrix, ExactMatrix.identity(2))

    def test_zero_defect_classification(self) -> None:
        data = acyclic_data(iota_correction=False)
        self.assertTrue(all(data.checks().values()))
        result = classify_closed_defect(data.complex, data.defect())
        self.assertEqual(result.status, "ZERO")
        self.assertIsNone(result.primitive)
        self.assertIsNone(result.dual_witness)

    def test_exact_defect_has_explicit_primitive(self) -> None:
        data = acyclic_data(iota_correction=True)
        result = classify_closed_defect(data.complex, data.defect())
        self.assertEqual(result.status, "EXACT_REMOVABLE")
        self.assertIsNotNone(result.primitive)
        assert result.primitive is not None
        self.assertEqual(
            graded_commutator(data.complex.q, result.primitive).matrix,
            data.defect().matrix,
        )
        self.assertEqual(data.complex.cohomology_dimension(0), 0)

    def test_nontrivial_defect_has_normalized_dual_witness(self) -> None:
        q = HomogeneousOperator("Q", 1, ExactMatrix.zero(1, 1))
        complex_ = FiniteGradedComplex((0,), q)
        zero_iota = HomogeneousOperator("iota", -1, ExactMatrix.zero(1, 1))
        zero_lie = HomogeneousOperator("L", 0, ExactMatrix.zero(1, 1))
        data = FirstOrderCartanData(
            complex=complex_,
            iota_0=zero_iota,
            lie_0=zero_lie,
            q_1=q,
            iota_1=zero_iota,
            lie_1=HomogeneousOperator(
                "L_1", 0, ExactMatrix.from_rows(((-1,),))
            ),
        )
        self.assertTrue(all(data.checks().values()))
        result = classify_closed_defect(complex_, data.defect())
        self.assertEqual(result.status, "NONTRIVIAL_ANOMALY")
        self.assertEqual(result.dual_witness, (Fraction(1),))
        self.assertEqual(complex_.cohomology_dimension(0), 1)

    def test_consistency_check_fails_if_ward_compatibility_fails(self) -> None:
        data = acyclic_data(iota_correction=False)
        bad_lie_1 = HomogeneousOperator(
            "bad_L_1", 0, ExactMatrix.from_rows(((1, 0), (0, 0)))
        )
        broken = FirstOrderCartanData(
            complex=data.complex,
            iota_0=data.iota_0,
            lie_0=data.lie_0,
            q_1=data.q_1,
            iota_1=data.iota_1,
            lie_1=bad_lie_1,
        )
        checks = broken.checks()
        self.assertFalse(checks["first_order_Ward_compatibility"])
        self.assertFalse(checks["defect_consistency_Q_closed"])

    def test_nonhomogeneous_operator_is_rejected(self) -> None:
        data = acyclic_data(iota_correction=False)
        bad = HomogeneousOperator(
            "bad", 0, ExactMatrix.from_rows(((0, 1), (0, 0)))
        )
        with self.assertRaisesRegex(ValueError, "nonhomogeneous"):
            data.complex.validate_operator(bad)


if __name__ == "__main__":
    unittest.main()
