from __future__ import annotations

import sys
import unittest
from pathlib import Path

import sympy as sp
from sympy.tensor.array import MutableDenseNDimArray


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))

from transfer.homological_transfer import Contraction, transfer_through_arity_three


class HomologicalTransferTests(unittest.TestCase):
    def setUp(self) -> None:
        # Full basis (x_even, y_odd, a_even, b_odd).  The pair a -> b is
        # contractible; x and y are residual.  This is an implementation
        # fixture, not a conformal-gravity model.
        q1 = sp.zeros(4)
        q1[3, 2] = 1
        inclusion = sp.zeros(4, 2)
        inclusion[0, 0] = inclusion[1, 1] = 1
        projection = sp.zeros(2, 4)
        projection[0, 0] = projection[1, 1] = 1
        homotopy = sp.zeros(4)
        homotopy[2, 3] = 1
        self.contraction = Contraction.build(
            q1,
            inclusion,
            projection,
            homotopy,
            full_parities=(0, 1, 0, 1),
            residual_parities=(0, 1),
        )

    def test_contact_and_exchange_terms_are_transferred_exactly(self) -> None:
        q2 = MutableDenseNDimArray.zeros(4, 4, 4)
        q2[3, 0, 0] = 1  # q2(x,x)=b, hence I2(x,x)=-a.
        q2[1, 2, 0] = q2[1, 0, 2] = 1  # q2(a,x)=y.
        q3 = MutableDenseNDimArray.zeros(4, 4, 4, 4)
        q3[1, 0, 0, 0] = 2

        result = transfer_through_arity_three(self.contraction, q2, q3)

        self.assertEqual(result.ell2[1, 0, 0], 0)
        self.assertEqual(result.inclusion2[2, 0, 0], -1)
        # Contact 2y plus three exchange trees -y gives -y.
        self.assertEqual(result.ell3_contact[1, 0, 0, 0], 2)
        self.assertEqual(result.ell3_exchange[1, 0, 0, 0], -3)
        self.assertEqual(result.ell3[1, 0, 0, 0], -1)

    def test_koszul_asymmetry_is_rejected(self) -> None:
        q2 = MutableDenseNDimArray.zeros(4, 4, 4)
        q2[0, 1, 0] = 1
        q3 = MutableDenseNDimArray.zeros(4, 4, 4, 4)
        with self.assertRaisesRegex(ValueError, "Koszul symmetric"):
            transfer_through_arity_three(self.contraction, q2, q3)

    def test_floating_point_input_is_rejected(self) -> None:
        q2 = MutableDenseNDimArray.zeros(4, 4, 4)
        q2[3, 0, 0] = sp.Float("1.0")
        q3 = MutableDenseNDimArray.zeros(4, 4, 4, 4)
        with self.assertRaisesRegex(ValueError, "floating-point"):
            transfer_through_arity_three(self.contraction, q2, q3)

    def test_non_nilpotent_taylor_data_are_rejected(self) -> None:
        q2 = MutableDenseNDimArray.zeros(4, 4, 4)
        q2[1, 0, 0] = 1
        q2[0, 1, 0] = q2[0, 0, 1] = 1
        q3 = MutableDenseNDimArray.zeros(4, 4, 4, 4)
        with self.assertRaisesRegex(ValueError, "coderivation square is nonzero"):
            transfer_through_arity_three(self.contraction, q2, q3)

    def test_invalid_contraction_is_rejected(self) -> None:
        bad_homotopy = sp.zeros(4)
        with self.assertRaisesRegex(ValueError, "invalid strong deformation retract"):
            Contraction.build(
                self.contraction.q1,
                self.contraction.inclusion,
                self.contraction.projection,
                bad_homotopy,
                full_parities=self.contraction.full_parities,
                residual_parities=self.contraction.residual_parities,
            )


if __name__ == "__main__":
    unittest.main()
