import unittest

import sympy as sp

from local_bv.hodge import Signature, TwoFormHodge


class HodgeTests(unittest.TestCase):
    def test_signature_dependent_star_square(self) -> None:
        euclidean = TwoFormHodge(Signature.EUCLIDEAN)
        lorentzian = TwoFormHodge(Signature.LORENTZIAN)
        self.assertEqual(euclidean.star * euclidean.star, sp.eye(2))
        self.assertEqual(lorentzian.star * lorentzian.star, -sp.eye(2))
        self.assertEqual(euclidean.verify()["epsilon_contraction_coefficient"], 2)
        self.assertEqual(lorentzian.verify()["epsilon_contraction_coefficient"], -2)

    def test_exact_chiral_projectors(self) -> None:
        for signature in Signature:
            hodge = TwoFormHodge(signature)
            positive_value, negative_value = hodge.eigenvalues
            positive, negative = hodge.projectors()
            with self.subTest(signature=signature.value):
                self.assertEqual(positive + negative, sp.eye(2))
                self.assertEqual(positive * negative, sp.zeros(2))
                self.assertEqual(hodge.star * positive, positive_value * positive)
                self.assertEqual(hodge.star * negative, negative_value * negative)

    def test_parity_exchanges_chiralities(self) -> None:
        for signature in Signature:
            hodge = TwoFormHodge(signature)
            positive, negative = hodge.projectors()
            with self.subTest(signature=signature.value):
                self.assertEqual(hodge.parity * hodge.parity, sp.eye(2))
                self.assertEqual(
                    hodge.parity * hodge.star * hodge.parity,
                    -hodge.star,
                )
                self.assertEqual(
                    hodge.parity * positive * hodge.parity,
                    negative,
                )

    def test_wrong_projector_eigenvalue_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "wrong square"):
            TwoFormHodge(Signature.LORENTZIAN).projector(sp.Integer(1))


if __name__ == "__main__":
    unittest.main()
