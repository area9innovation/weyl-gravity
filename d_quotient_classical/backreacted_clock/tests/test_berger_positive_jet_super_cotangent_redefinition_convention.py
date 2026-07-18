import json
import unittest

import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as result,
)


class PositiveJetCotangentConventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(result.OUTPUT.read_text())

    def test_certificate_replays(self):
        result.validate(self.value)

    def test_zero_word_restriction_is_complete(self):
        replay = result.zero_word_compatibility()
        self.assertEqual(replay["F2_labels_checked"], 934)
        self.assertEqual(replay["F3_labels_checked"], 5050)
        self.assertEqual(replay["defects"], 0)

    def test_odd_first_derivative_sign_mutation_is_rejected(self):
        inputs = ((27, ()), (27, (0,)))
        exact = result.cotangent_column(3, inputs)
        mutant = result.cotangent_column(
            3, inputs, omit_formal_adjoint_sign=True
        )
        self.assertNotEqual(exact, mutant)
        self.assertEqual(
            exact[(31, ((13, (0,)), (27, ())))],
            sp.Rational(1, 2),
        )

    def test_noncommuting_second_word_has_commutator_tail(self):
        lifted = result.cotangent_column(4, ((27, ()), (28, (2, 1))))
        self.assertTrue(
            any(
                sum(len(word) for _, word in atoms) == 1 and coefficient
                for (_, atoms), coefficient in lifted.items()
            )
        )


if __name__ == "__main__":
    unittest.main()
