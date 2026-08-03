"""Falsification tests for the general-n closed forms."""

from __future__ import annotations

import json
import unittest

from reverse_physics.exact_linalg import rank_bareiss
from reverse_physics.hamiltonian_privilege_general_n import (
    CHECK_RANGE,
    OUTPUT,
    build,
    codim_sp_in_liouville,
    codim_sp_in_marginal,
    dim_liouville,
    dim_marginal,
    dim_symplectic,
)
from reverse_physics.hamiltonian_privilege_linear_g0 import (
    liouville_constraints,
    marginal_constraints,
    symplectic_constraints,
)


class TestClosedFormsAgainstBruteForce(unittest.TestCase):
    def test_all_three_dimensions_match_exact_rank(self):
        for n in range(1, 6):
            ambient = (2 * n) ** 2
            self.assertEqual(ambient - rank_bareiss(symplectic_constraints(n)), dim_symplectic(n))
            self.assertEqual(ambient - rank_bareiss(marginal_constraints(n)), dim_marginal(n))
            self.assertEqual(ambient - rank_bareiss(liouville_constraints(n)), dim_liouville(n))


class TestThreshold(unittest.TestCase):
    def test_separation_vanishes_exactly_at_n_zero_and_one(self):
        self.assertEqual(codim_sp_in_marginal(0), 0)
        self.assertEqual(codim_sp_in_marginal(1), 0)
        for n in range(2, 50):
            self.assertGreater(codim_sp_in_marginal(n), 0)

    def test_liouville_codimension_vanishes_exactly_at_n_one(self):
        self.assertEqual(codim_sp_in_liouville(1), 0)
        for n in range(2, 50):
            self.assertGreater(codim_sp_in_liouville(n), 0)

    def test_gap_grows_quadratically(self):
        # A linear or bounded gap would falsify the "less adequate as n grows" reading.
        self.assertEqual(codim_sp_in_marginal(10), 180)
        self.assertEqual(codim_sp_in_marginal(20), 760)
        self.assertGreater(codim_sp_in_marginal(20), 4 * codim_sp_in_marginal(10) - 1)

    def test_g0_numbers_are_recovered(self):
        self.assertEqual((dim_symplectic(2), dim_marginal(2), dim_liouville(2)), (10, 14, 15))
        self.assertEqual((dim_symplectic(1), dim_marginal(1), dim_liouville(1)), (3, 3, 3))


class TestPolynomialIdentityArgument(unittest.TestCase):
    def test_identities_hold_far_outside_the_evaluation_points(self):
        # The proof uses n in {0,1,2,3}; if the identity were merely sampled,
        # a large n would be free to disagree.
        for n in (17, 101, 1000):
            self.assertEqual(dim_marginal(n) - dim_symplectic(n), codim_sp_in_marginal(n))
            self.assertEqual(dim_liouville(n) - dim_symplectic(n), codim_sp_in_liouville(n))

    def test_a_wrong_closed_form_would_be_caught(self):
        wrong = lambda n: 2 * n * n - 2 * n + 1  # off by one
        disagreements = [n for n in range(0, 6) if wrong(n) != codim_sp_in_marginal(n)]
        self.assertTrue(disagreements, "the mutation control did not disagree anywhere")


class TestCertificateIsCurrent(unittest.TestCase):
    def test_certificate_matches_the_generator(self):
        self.assertTrue(OUTPUT.exists(), "certificate has not been written")
        expected = json.dumps(build(), indent=2, sort_keys=True) + "\n"
        self.assertEqual(OUTPUT.read_text(encoding="utf-8"), expected)

    def test_boundary_is_declared(self):
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertTrue(payload["claim_flags"]["GENERAL_N_COVERED"])
        self.assertFalse(payload["claim_flags"]["FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT"])
        self.assertFalse(payload["claim_flags"]["NONLINEAR_CARRIER_COVERED"])
        self.assertFalse(payload["claim_flags"]["QUANTUM_CLAIM"])
        self.assertEqual(payload["steps_rechecked_concretely_for_n_in"], list(CHECK_RANGE))


if __name__ == "__main__":
    unittest.main()
